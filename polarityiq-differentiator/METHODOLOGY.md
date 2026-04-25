# Methodology — How the dataset was built

> Filled in at submission time. Outline below.

## Discovery
- 20 SerpAPI queries across geography + sector + entity-type axes
- ~150 raw candidates, deduped by registrable domain to ~120

## Enrichment
- Homepage fetched per candidate (5s timeout, single retry)
- Description: meta description -> og:description -> first paragraph
- Sectors: keyword matching against curated list of 30 investment categories
- Location: regex for "City, ST" pattern + city name fallback
- LinkedIn URLs recorded but not scraped (ToS)

## Validation
- 7-point scoring rubric (see `scripts/3_validate.py`)
- Threshold: confidence >= medium
- Top 50 by score retained

## What I would improve
- Replace homepage-only fetch with a 2-page crawl (homepage + about/team)
- Add domain age check (WHOIS)
- Add a manual review queue for medium-confidence records before publishing
- For production: bring in Apollo/Hunter for principal-contact validation,
  and a person-level matching step against the FO's named team
