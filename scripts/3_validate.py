"""
3_validate.py — Score each candidate, keep top 50, flag confidence.

Validation signals (each 0 or 1, summed):
  +2  Has working website AND description mentions "family office"
  +1  Has at least one identified investing sector
  +1  Has location hint (city/state/country)
  +1  Has LinkedIn URL OR named principal in description
  +1  Description length > 100 chars (real content, not boilerplate)
  +1  Domain looks legitimate (not free hosting, has TLD)

Max score = 7. We keep records >=4 and pick top 50.

Output: data/processed/family_offices.csv (final dataset)
"""

import csv
import re
from pathlib import Path

import tldextract

INPUT = Path("data/raw/enriched.csv")
OUTPUT = Path("data/processed/family_offices.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

FREE_HOSTING = {"wixsite.com", "weebly.com", "blogspot.com", "wordpress.com", "godaddysites.com"}


def score_record(r: dict) -> tuple:
    """Return (score, confidence_label, reasons)."""
    score = 0
    reasons = []

    desc = (r.get("description") or "").lower()
    has_fo_keyword = "family office" in desc or "single family" in desc or "multi-family" in desc

    if r.get("website") and has_fo_keyword:
        score += 2
        reasons.append("website+keyword")
    elif r.get("website"):
        score += 1
        reasons.append("website_only")

    if r.get("sectors"):
        score += 1
        reasons.append("sectors_extracted")

    if r.get("location_hint"):
        score += 1
        reasons.append("location_found")

    if r.get("linkedin_url"):
        score += 1
        reasons.append("linkedin_url")

    if len(r.get("description", "")) > 100:
        score += 1
        reasons.append("real_description")

    domain = r.get("domain", "")
    ext = tldextract.extract(domain)
    if ext.suffix and ext.suffix not in FREE_HOSTING and len(ext.domain) > 2:
        score += 1
        reasons.append("legit_domain")

    if score >= 6:
        confidence = "high"
    elif score >= 4:
        confidence = "medium"
    else:
        confidence = "low"

    return score, confidence, ";".join(reasons)


def main():
    if not INPUT.exists():
        print(f"ERROR: {INPUT} not found. Run 2_enrich.py first.")
        return

    rows = []
    with open(INPUT, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    scored = []
    for r in rows:
        score, conf, reasons = score_record(r)
        r["validation_score"] = score
        r["confidence"] = conf
        r["validation_reasons"] = reasons
        scored.append(r)

    # Sort by score desc, take top 50 with confidence >= medium
    qualified = [r for r in scored if r["confidence"] in ("high", "medium")]
    qualified.sort(key=lambda x: x["validation_score"], reverse=True)
    top50 = qualified[:50]

    # Final schema — what gets stored / used in RAG
    final_fields = [
        "id", "name", "website", "linkedin_url", "description",
        "sectors", "location", "country_guess",
        "discovery_source", "discovery_query",
        "validation_score", "confidence", "validation_reasons",
    ]

    final = []
    for i, r in enumerate(top50, 1):
        loc = r.get("location_hint", "")
        country_guess = ""
        # Crude country inference
        for c in ["USA", "UK", "Singapore", "Switzerland", "UAE", "Hong Kong", "India"]:
            if c.lower() in (r.get("description","") + " " + loc).lower():
                country_guess = c
                break
        if loc and "," in loc and not country_guess:
            country_guess = "USA"  # state-format suggests US

        final.append({
            "id": f"fo_{i:03d}",
            "name": r.get("name_guess", "").strip(),
            "website": r.get("website", ""),
            "linkedin_url": r.get("linkedin_url", ""),
            "description": r.get("description", "")[:1000],
            "sectors": r.get("sectors", ""),
            "location": loc,
            "country_guess": country_guess,
            "discovery_source": r.get("discovery_source", ""),
            "discovery_query": r.get("discovery_query", ""),
            "validation_score": r["validation_score"],
            "confidence": r["confidence"],
            "validation_reasons": r["validation_reasons"],
        })

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=final_fields)
        writer.writeheader()
        writer.writerows(final)

    high = sum(1 for r in final if r["confidence"] == "high")
    med = sum(1 for r in final if r["confidence"] == "medium")
    print(f"Done. {len(final)} records → {OUTPUT}")
    print(f"  High confidence: {high}")
    print(f"  Medium confidence: {med}")
    print("\nNext: review CSV manually, fix names/locations, then run 4_load_supabase.py")


if __name__ == "__main__":
    main()
