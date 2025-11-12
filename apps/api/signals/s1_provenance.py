""" apps/api/signals/s1_provenance.py """
import httpx
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime
import whois  # pip install python-whois
import re

# NEW: Free + Reliable WHOIS API
WHOIS_API = "https://api.whois.freemom.com/whois"
client = httpx.AsyncClient(timeout=10.0, headers={
                           "User-Agent": "TrustLens/1.0"})


def get_root_domain(url: str) -> str:
    domain = urlparse(url).netloc
    parts = domain.split('.')
    if len(parts) > 2:
        return '.'.join(parts[-2:])  # cnn.com
    return domain


async def get_domain_age(domain: str) -> dict:
    try:
        # Try FreeMom WHOIS API
        r = await client.get(f"{WHOIS_API}/{domain}")
        if r.status_code == 200:
            text = r.text
            created_match = re.search(
                r"Creation Date:?\s*([0-9\-TZ:]+)", text, re.I)
            if created_match:
                created = created_match.group(1).split('T')[0]
                year = int(created[:4])
                age_years = 2025 - year
                score = min(100, 60 + age_years * 3)
                return {"age": f"{age_years} years", "score": score}
    except:
        pass

    # Fallback: python-whois
    try:
        w = whois.whois(domain)
        if w.creation_date:
            if isinstance(w.creation_date, list):
                created = w.creation_date[0]
            else:
                created = w.creation_date
            age_years = (datetime.now() - created).days // 365
            score = min(100, 60 + age_years * 3)
            return {"age": f"{age_years} years", "score": score}
    except Exception as e:
        print(f"[WHOIS FALLBACK ERROR] {domain}: {e}")

    return {"age": "Unknown", "score": 40}


async def check_https(url: str) -> dict:
    parsed = urlparse(url)
    domain = parsed.netloc
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expiry = datetime.strptime(
                    cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                days_left = (expiry - datetime.utcnow()).days
                score = 100 if days_left > 30 else 70
                return {
                    "https": True,
                    "valid_cert": True,
                    "expiry": f"{days_left} days left",
                    "score": score
                }
    except Exception as e:
        print(f"[SSL ERROR] {domain}: {e}")
        return {"https": False, "valid_cert": False, "score": 20}


async def s1_provenance(url: str):
    root_domain = get_root_domain(url)
    age_data = await get_domain_age(root_domain)
    https_data = await check_https(url)

    score = int(age_data["score"] * 0.6 + https_data["score"] * 0.4)

    return {
        "score": min(max(score, 0), 100),
        "evidence": [
            {"title": "Domain Age", "summary": age_data["age"]},
            {"title": "HTTPS", "summary": https_data.get(
                "expiry", "Valid SSL") if https_data["https"] else "No SSL"}
        ]
    }
