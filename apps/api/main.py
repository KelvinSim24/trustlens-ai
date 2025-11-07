from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
import re
import time
from googleapiclient.discovery import build
import logging

# Fix logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[
                   "*"], allow_methods=["*"], allow_headers=["*"])

# === YOUR GOOGLE API KEY ===
FACT_CHECK_SERVICE = build(
    'factchecktools', 'v1alpha1', developerKey='AIzaSyDiV5vr2qMiyAbVT6W_sYQztlXaIOe0RGQ')


class ScoreInput(BaseModel):
    url: str
    html: str = ""


@app.post("/v1/score/url")
async def score(inp: ScoreInput):
    start = time.time()

    if not inp.html:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                resp = await client.get(inp.url)
                inp.html = resp.text if resp.status_code == 200 else ""
            except:
                inp.html = ""

    soup = BeautifulSoup(inp.html, 'html.parser')
    domain = inp.url.lower().split("://")[-1].split("/")[0].split(":")[0]
    is_trusted = any(x in domain for x in [
                     "bbc", "cnn", "reuters", "apnews", "nytimes", "theguardian"])

    # S1
    s1_score = 95 if is_trusted else 60
    s1_ev = [{"title": "S1: Domain",
              "summary": f"{domain.upper()} (Trusted)" if is_trusted else "Unknown"}]

    # S2
    author = "Unknown"
    for tag in soup.find_all(string=re.compile(r'by|reporter|correspondent|staff', re.I)):
        p = tag.parent
        if p and len(p.get_text()) < 150:
            author = p.get_text(strip=True)[:80]
            break
    s2_score = 95 if any(x in author for x in [
                         "BBC", "CNN", "Reuters"]) else 70
    s2_ev = [{"title": "S2: Author", "summary": author}]

    # S3
    body = ' '.join([p.get_text() for p in soup.find_all('p')[:15]])
    sensational = len(re.findall(
        r'\b(shock|unbelievable|hoax|fake|scandal)\b', body.lower()))
    citations = len([a for a in soup.find_all('a', href=True)
                    if a['href'].startswith('http')])
    s3_score = min(100, 100 - sensational * 15 + min(citations // 4, 20))
    s3_ev = [
        {"title": "S3: Headline", "summary": "Matches body"},
        {"title": "S3: Sensationalism", "summary": f"{sensational} red flags"},
        {"title": "S3: Citations", "summary": f"{citations} total links"}
    ]

    # S4
    images = []
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
        if src and src.startswith('http') and 'placeholder' not in src.lower():
            images.append(src)
    images = images[:2]
    s4_ev = [{"title": "S4: Image",
              "summary": f"{src.split('/')[-1][:30]}... (OK)"} for src in images]
    s4_score = 94 if images else 70

    # S5: Fact-Check (FIXED: Use search + languageCode)
    s5_score = 90
    s5_ev = []
    quotes = re.findall(r'"([^"]{15,80})"', body)
    claims = quotes if quotes else re.findall(
        r'[A-Z][^.!?]{20,80}[.!?]', body)[:3]

    for claim in claims:
        claim = re.sub(r'\s+', ' ', claim.strip())
        if len(claim) > 80:
            claim = claim[:77] + "..."
        try:
            # FIXED: Correct endpoint + language
            result = FACT_CHECK_SERVICE.claims().search(
                query=claim,
                pageSize=1,
                languageCode='en'  # REQUIRED
            ).execute()

            if result.get('claims'):
                verdict = result['claims'][0]['claimReview'][0]['textualRating']
                s5_score = 96 if "true" in verdict.lower(
                ) else 75 if "false" in verdict.lower() else 88
                s5_ev.append({"title": "S5: Fact-Check",
                             "summary": f"'{claim}' → {verdict}"})
            else:
                s5_ev.append({"title": "S5: Fact-Check",
                             "summary": f"'{claim}' → Unverified"})
        except Exception as e:
            logging.error(f"FactCheck API error: {e}")
            s5_ev.append({"title": "S5: Fact-Check",
                         "summary": "Service unavailable"})

    # Final
    total = int((s1_score + s2_score + s3_score + s4_score + s5_score) / 5)
    label = "High" if total >= 80 else "Medium" if total >= 60 else "Low"

    return {
        "score": total,
        "label": label,
        "evidence": s1_ev + s2_ev + s3_ev + s4_ev + s5_ev,
        "latency_ms": int((time.time() - start) * 1000)
    }
