""" apps/api/signals/s3_content.py """
import httpx
from bs4 import BeautifulSoup
import re
from textstat import flesch_reading_ease
from urllib.parse import urlparse

# Global client — reuse connections
client = httpx.AsyncClient(
    follow_redirects=True,
    timeout=15.0,
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=50),
    headers={"User-Agent": "TrustLens/1.0 (+https://trustlens.ai)"}
)


async def fetch_page(url: str) -> str:
    try:
        # Respect robots.txt
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            robots = await client.get(robots_url, timeout=5.0)
            if "Disallow: /" in robots.text:
                raise Exception("Blocked by robots.txt")
        except:
            pass  # Ignore robots check if fails

        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[S3 FETCH ERROR] {url}: {e}")
        raise


def extract_clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text)[:15000]  # Limit


def detect_clickbait(title: str, text: str) -> dict:
    patterns = [
        r"\b(you won'?t believe|shocking|this one trick|secret)\b",
        r"\b\d+ (ways|things|reasons|facts|signs)\b",
        r"\b(breaking|urgent|now)\b"
    ]
    matches = sum(
        bool(re.search(p, title + " " + text[:500], re.I)) for p in patterns)
    score = max(30, 100 - matches * 25)
    return {"clickbait": matches > 0, "score": score}


def count_citations(text: str, soup: BeautifulSoup) -> dict:
    # Count [1], (Source), cited
    citations = len(re.findall(r"\[\d+\]|\bcited?\b|\(source\)", text, re.I))
    # Count links to trusted fact-checkers
    fact_sites = ["snopes.com", "factcheck.org",
                  "politifact.com", "reuters.com/fact-check"]
    links = [a.get("href", "") for a in soup.find_all("a", href=True)]
    fact_links = sum(1 for site in fact_sites if any(site in l for l in links))
    total = citations + fact_links * 3
    score = min(100, 50 + total * 8)  # ← FIXED LINE
    return {"citations": citations, "fact_links": fact_links, "score": score}


def readability_score(text: str) -> dict:
    if len(text) < 200:
        return {"readability": "Too short", "score": 50}
    score = flesch_reading_ease(text[:5000])
    level = "Easy" if score > 60 else "Hard" if score < 30 else "Medium"
    return {"readability": f"{score:.1f} ({level})", "score": min(100, int(score))}


async def s3_content(url: str):
    try:
        html = await fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title"
        text = extract_clean_text(soup)

        clickbait = detect_clickbait(title, text)
        citations = count_citations(text, soup)
        readability = readability_score(text)

        # Weighted score
        score = int(
            clickbait["score"] * 0.3 +
            citations["score"] * 0.4 +
            readability["score"] * 0.3
        )

        return {
            "score": min(max(score, 0), 100),
            "evidence": [
                {"title": "Clickbait",
                    "summary": "Suspicious" if clickbait["clickbait"] else "Clean title"},
                {"title": "Citations",
                    "summary": f"{citations['citations']} refs, {citations['fact_links']} fact-checks"},
                {"title": "Readability", "summary": readability["readability"]}
            ]
        }
    except Exception as e:
        print(f"[S3 ERROR] {url}: {e}")
        return {
            "score": 30,
            "evidence": [{"title": "S3 Error", "summary": "Failed to analyze content"}]
        }
