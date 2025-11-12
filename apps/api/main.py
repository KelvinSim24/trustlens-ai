""" apps/api/main.py """
from signals.s4_corroboration import s4_corroboration
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from functools import lru_cache

from signals.s1_provenance import s1_provenance
from signals.s3_content import s3_content

app = FastAPI(title="TrustLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CACHING — NO COROUTINE REUSE


@lru_cache(maxsize=200)
def cached_s1_sync(url: str):
    return asyncio.run(s1_provenance(url))


@lru_cache(maxsize=200)
def cached_s3_sync(url: str):
    return asyncio.run(s3_content(url))


class ScoreRequest(BaseModel):
    url: str


class Evidence(BaseModel):
    title: str
    summary: str


class ScoreResponse(BaseModel):
    score: int
    signal: str
    evidence: List[Evidence]


@app.get("/health")
async def health():
    return {"status": "healthy", "region": "global"}


@app.post("/v1/score", response_model=ScoreResponse)
async def score_url(request: ScoreRequest):
    url = request.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    loop = asyncio.get_event_loop()
    s1_result = await loop.run_in_executor(None, cached_s1_sync, url)
    s3_result = await loop.run_in_executor(None, cached_s3_sync, url)
    s4_result = await loop.run_in_executor(None, lambda: asyncio.run(s4_corroboration(url)), url)

    s1_score = s1_result["score"] if isinstance(s1_result, dict) else 30
    s3_score = s3_result["score"] if isinstance(s3_result, dict) else 30
    s4_score = s4_result["score"] if isinstance(s4_result, dict) else 50

    total_score = int(s1_score * 0.3 + s3_score * 0.4 + s4_score * 0.3)
    evidence = []

    for r in [s1_result, s3_result, s4_result]:
        if isinstance(r, dict):
            evidence.extend(r["evidence"])
        else:
            evidence.append({"title": "Error", "summary": str(r)})

    return ScoreResponse(
        score=total_score,
        signal="S1+S3+S4",
        evidence=[Evidence(**e) for e in evidence]
    )
