"""
1_discover.py — Discover candidate family offices.

Strategy:
- Use SerpAPI with targeted queries against high-signal domains
- Pull entity name + website from organic results
- Dedupe by domain
- Output: data/raw/candidates.csv

What I assumed:
- A site with "family office" in title + a credible domain age is more likely real
- I'll over-collect (target ~120 candidates) so the validation step can drop weak ones
- I'm NOT scraping LinkedIn directly. ToS issues. I use SerpAPI to find LinkedIn URLs only.

What could be wrong:
- Some "family office" results are MFOs, wealth managers, or RIAs that don't fit the strict SFO definition
- I handle this in 3_validate.py with a category check
"""

import os
import csv
import time
import json
from pathlib import Path
from urllib.parse import urlparse

import requests
import tldextract
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OUTPUT = Path("data/raw/candidates.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Targeted queries — designed to surface real FOs across regions/sectors
QUERIES = [
    '"family office" -jobs -careers site:linkedin.com/company',
    '"single family office" investments',
    '"multi-family office" private investments',
    '"family office" venture capital',
    '"family office" real estate investments',
    '"family office" private equity portfolio',
    '"family office" Texas',
    '"family office" California',
    '"family office" New York',
    '"family office" Florida',
    '"family office" London',
    '"family office" Singapore',
    '"family office" Switzerland',
    '"family office" Dubai',
    '"family office" Hong Kong',
    '"family office" climate investments',
    '"family office" healthcare investments',
    '"family office" technology investments',
    '"family office" impact investing',
    '"family office" recent investment',
]

EXCLUDE_DOMAINS = {
    "wikipedia.org", "investopedia.com", "linkedin.com", "wsj.com",
    "bloomberg.com", "reuters.com", "ft.com", "forbes.com",
    "businessinsider.com", "crunchbase.com", "pitchbook.com",
    "youtube.com", "twitter.com", "x.com", "facebook.com",
    "indeed.com", "glassdoor.com", "ziprecruiter.com",
}


def domain_of(url: str) -> str:
    """Return registrable domain (e.g., 'example.co.uk')."""
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}".lower() if ext.domain and ext.suffix else ""


def serpapi_search(query: str, num: int = 10) -> list:
    """Single SerpAPI call. Returns organic_results list or []."""
    params = {
        "engine": "google",
        "q": query,
        "num": num,
        "api_key": SERPAPI_KEY,
    }
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=30)
        r.raise_for_status()
        return r.json().get("organic_results", [])
    except Exception as e:
        print(f"  ERROR on '{query}': {e}")
        return []


def main():
    if not SERPAPI_KEY or SERPAPI_KEY.startswith("your_"):
        print("ERROR: Set SERPAPI_KEY in .env")
        return

    seen_domains = set()
    candidates = []

    print(f"Running {len(QUERIES)} queries...")
    for i, q in enumerate(QUERIES, 1):
        print(f"[{i}/{len(QUERIES)}] {q}")
        results = serpapi_search(q, num=10)
        for r in results:
            url = r.get("link", "")
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            domain = domain_of(url)

            if not domain or domain in EXCLUDE_DOMAINS or domain in seen_domains:
                continue

            # If the result is a LinkedIn company page, keep it but mark it
            source_type = "linkedin" if "linkedin.com" in url else "website"

            seen_domains.add(domain)
            candidates.append({
                "discovery_query": q,
                "discovery_source": source_type,
                "url": url,
                "domain": domain,
                "title": title,
                "snippet": snippet,
            })
        time.sleep(1)  # be nice to SerpAPI

    # Write
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=candidates[0].keys())
        writer.writeheader()
        writer.writerows(candidates)

    print(f"\nDone. {len(candidates)} unique candidates written to {OUTPUT}")
    print("Next: run scripts/2_enrich.py")


if __name__ == "__main__":
    main()
