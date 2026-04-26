# Methodology — How the dataset was built

## Approach

I started with automation, watched it fail in a specific way, and pivoted to manual curation. The failed scripts are kept in the repo as evidence of the first attempt and the lesson learned.

## Phase 1 — Automated discovery (failed in a useful way)

I wrote three scripts (`scripts/1_discover.py`, `2_enrich.py`, `3_validate.py`) that:

1. Ran 20 SerpAPI queries across geography, sector, and entity-type axes
2. Deduped 123 raw candidates by registrable domain
3. Fetched each candidate's homepage, extracted meta description, sectors (keyword match against a 30-term list), and a location hint
4. Scored each record on a 7-point rubric and kept the top 50

**The output passed my own rubric.** All 50 records were rated "high confidence."

**The output failed manual review.** When I opened the CSV and looked at the names, most were article titles — "Top 10 Family Offices in Texas," "Seven Considerations Before Creating a Family Office," "Family offices and venture capital: the new architecture of..." The rubric had no concept of "is this an entity or an article about entities," so it scored articles the same as real FOs as long as the keywords were present.

This is the failure mode the How We Work document warns about: output that looks correct because the rubric agrees with itself. The human validation layer caught what the automated layer missed.

## Phase 2 — Manual curation

I switched to curating 50 real FOs from public sources I could name:

- **SEC ADV filings** for US-registered investment advisers
- **Company homepages** verified by direct visit
- **Wikipedia** for biographical and historical context
- **FO Magazine, Trusted Insight, Forbes** for press coverage of named FOs
- **The Atlantic masthead** as a primary-source cross-check for Emerson Collective
- **Land Report rankings** as a cross-check for Cascade Investment
- **SEC 13G filings** for Cascade's portfolio holdings

I used Claude to help compile and format public information faster. Every record was then verified by me visiting the website to confirm it loads and matches the entity.

## Phase 3 — URL verification

I wrote `verify_urls.py` to GET each website and report status. First pass:

- **40/50 returned 200 OK**
- **10 failed** (timeouts, dead, SSL errors)

I manually checked each failure. 3 were transient. 7 needed replacement. I sourced 7 alternate FOs from the same public source set and re-verified. Final pass: 50/50 OK.

## Phase 4 — Embedding and RAG load

- Composed a "searchable text" per record combining name, location, sectors, and description so the embedding captures structured fields, not just narrative
- Embedded with `sentence-transformers/all-MiniLM-L6-v2` (local, free, 384 dimensions)
- Inserted into Supabase pgvector with the embedding stored alongside metadata for later filtering

## Validation depth

- All 50 records: website verified, sectors extracted, location confirmed
- 3 records (Bezos Expeditions, Cascade Investment, Emerson Collective): full validation chain documented in `deep_validation/three_records.md` with 3 independent sources each

## What I would do differently in v2

1. **Filter article-format results before scoring.** Drop anything with titles starting "Top," "How to," "Best," "Guide to," or containing question marks. This alone would eliminate 80% of the noise from the original output.
2. **Require entity-page signals, not keyword presence.** A homepage with an "About" section, a "Team" page, and direct contact info is much more likely to be an entity than a content site.
3. **Add domain age via WHOIS.** Most real FOs have domains older than 5 years. Most content farms do not.
4. **Insert a manual review checkpoint** between auto-discovery and validation rather than trusting the rubric end-to-end.
5. **For production:** bring Apollo and Hunter in for principal-contact enrichment, but accept low hit rates on high-privacy FOs and price the dataset accordingly.

## Honest limitations

- **No verified per-mailbox contact data.** Family offices of this size do not publish it.
- **50 records is below the size where statistical retrieval evaluation is meaningful.** Quality of the RAG layer is judged qualitatively in this submission.
- **Vector-only retrieval misses exact-string queries.** Production needs hybrid search (BM25 + vector) merged with reciprocal rank fusion.
