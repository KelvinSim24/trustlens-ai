""" apps/api/signals/s4_corroboration.py """
import httpx
from urllib.parse import urlparse, quote
import re

client = httpx.AsyncClient(timeout=10.0)


async def search_wikipedia(query: str) -> dict:
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}"
        r = await client.get(url)
        if r.status_code == 200:
            data = r.json()
            return {"source": "Wikipedia", "summary": data.get("extract", "")[:200], "score": 100}
    except:
        pass
    return {"source": "Wikipedia", "summary": "No match", "score": 50}


async def search_reuters(query: str) -> dict:
    try:
        url = "https://www.reuters.com/search/news"
        params = {"blob": query, "sortBy": "date"}
        r = await client.get(url, params=params)
        if "No results" not in r.text:
            return {"source": "Reuters", "summary": "Mentioned in Reuters", "score": 95}
    except:
        pass
    return {"source": "Reuters", "summary": "No mention", "score": 40}


async def google_fact_check(query: str) -> dict:
    try:
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        # ← Get free at console.cloud.google.com
        params = {"query": query, "key": "YOUR_GOOGLE_API_KEY"}
        r = await client.get(url, params=params)
        if r.status_code == 200:
            data = r.json()
            claims = data.get("claims", [])
            if claims:
                return {"source": "Google Fact Check", "summary": f"{len(claims)} claims found", "score": 90}
    except:
        pass
    return {"source": "Google Fact Check", "summary": "No data", "score": 50}


async def s4_corroboration(url: str):
    domain = urlparse(url).netloc
    query = domain.replace("www.", "")

    wiki = await search_wikipedia(query)
    reuters = await search_reuters(query)
    factcheck = await google_fact_check(query)

    score = int(wiki["score"] * 0.4 + reuters["score"]
                * 0.3 + factcheck["score"] * 0.3)

    return {
        "score": min(max(score, 0), 100),
        "evidence": [
            {"title": wiki["source"], "summary": wiki["summary"]},
            {"title": reuters["source"], "summary": reuters["summary"]},
            {"title": factcheck["source"], "summary": factcheck["summary"]},
        ]
    }
