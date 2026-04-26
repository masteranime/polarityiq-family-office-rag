"""
2_enrich.py — Enrich candidates with website data, principal contact, signals.

Strategy:
- For each candidate, fetch homepage HTML
- Extract: description, sectors mentioned, location hints
- For LinkedIn URLs: just record the URL (manual lookup later for the 3 deep records)
- Output: data/raw/enriched.csv

What I assumed:
- The homepage usually has enough text to determine if it's a real FO
- I do NOT scrape LinkedIn (ToS) — I record the URL and validate manually
- For principal contact, I look for "About" / "Team" pages but don't crawl deep

What could be wrong:
- Some FOs have minimal websites (intentionally — they're private)
- These show as "low signal" candidates and get scored down in 3_validate.py
"""

import os
import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

INPUT = Path("data/raw/candidates.csv")
OUTPUT = Path("data/raw/enriched.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

# Sector keywords — used to extract investing focus from page text
SECTOR_KEYWORDS = [
    "private equity", "venture capital", "real estate", "hedge fund",
    "public equities", "fixed income", "private credit", "private debt",
    "infrastructure", "healthcare", "technology", "fintech", "biotech",
    "climate", "esg", "impact", "energy", "agriculture", "consumer",
    "industrial", "manufacturing", "media", "education",
    "crypto", "blockchain", "ai", "artificial intelligence",
]


def fetch_html(url: str, timeout: int = 15) -> str:
    """GET the URL. Return text or empty string on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code == 200 and "text/html" in r.headers.get("content-type", ""):
            return r.text
    except Exception as e:
        print(f"    fetch error: {e}")
    return ""


def extract_description(soup: BeautifulSoup) -> str:
    """Try meta description, then first paragraph."""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"].strip()[:500]
    og = soup.find("meta", attrs={"property": "og:description"})
    if og and og.get("content"):
        return og["content"].strip()[:500]
    p = soup.find("p")
    if p:
        return p.get_text(strip=True)[:500]
    return ""


def extract_sectors(text: str) -> list:
    """Find sector keywords in lowercase text."""
    text_l = text.lower()
    found = []
    for kw in SECTOR_KEYWORDS:
        if kw in text_l:
            found.append(kw)
    return list(dict.fromkeys(found))  # preserve order, dedupe


def extract_location_hint(soup: BeautifulSoup) -> str:
    """Best-effort location string from footer or contact page."""
    # Look for common patterns
    text = soup.get_text(" ", strip=True)
    # US state pattern
    us_match = re.search(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)?),\s*([A-Z]{2})\b", text)
    if us_match:
        return f"{us_match.group(1)}, {us_match.group(2)}"
    # Look for major financial cities
    cities = ["London", "Singapore", "Hong Kong", "Dubai", "Zurich", "Geneva",
              "New York", "San Francisco", "Boston", "Chicago", "Mumbai", "Tokyo"]
    for city in cities:
        if city in text:
            return city
    return ""


def is_linkedin(url: str) -> bool:
    return "linkedin.com" in url


def main():
    if not INPUT.exists():
        print(f"ERROR: {INPUT} not found. Run 1_discover.py first.")
        return

    rows_in = []
    with open(INPUT, encoding="utf-8") as f:
        rows_in = list(csv.DictReader(f))

    print(f"Enriching {len(rows_in)} candidates...")
    enriched = []

    for i, row in enumerate(rows_in, 1):
        url = row["url"]
        domain = row["domain"]
        print(f"[{i}/{len(rows_in)}] {domain}")

        record = {
            "name_guess": "",
            "domain": domain,
            "website": "",
            "linkedin_url": "",
            "description": row.get("snippet", ""),
            "sectors": "",
            "location_hint": "",
            "discovery_query": row["discovery_query"],
            "discovery_source": row["discovery_source"],
            "enrich_status": "",
        }

        if is_linkedin(url):
            record["linkedin_url"] = url
            # Try to derive a guess for the website from the company name in title
            record["name_guess"] = row["title"].replace(" | LinkedIn", "").strip()
            record["enrich_status"] = "linkedin_only_needs_manual_website"
        else:
            record["website"] = url
            record["name_guess"] = row["title"].split("|")[0].split("-")[0].strip()
            html = fetch_html(url)
            if html:
                soup = BeautifulSoup(html, "lxml")
                record["description"] = extract_description(soup) or record["description"]
                page_text = soup.get_text(" ", strip=True)[:5000]
                record["sectors"] = ", ".join(extract_sectors(page_text))
                record["location_hint"] = extract_location_hint(soup)
                record["enrich_status"] = "ok"
            else:
                record["enrich_status"] = "fetch_failed"

        enriched.append(record)
        time.sleep(0.5)

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=enriched[0].keys())
        writer.writeheader()
        writer.writerows(enriched)

    ok = sum(1 for r in enriched if r["enrich_status"] == "ok")
    print(f"\nDone. {ok}/{len(enriched)} enriched successfully → {OUTPUT}")
    print("Next: run scripts/3_validate.py")


if __name__ == "__main__":
    main()
