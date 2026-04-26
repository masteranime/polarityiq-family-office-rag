# PolarityIQ Differentiator — Working Plan

**Candidate:** Muhammad Shaheer
**Started:** [add timestamp when you start]

## What I observed in the brief

Brian is testing two things in parallel:
1. Can I produce real, validated FO data — not scraped junk
2. Can I think through retrieval architecture for messy, heterogeneous data

The "How We Work" doc tells me what matters more than the deliverables: visible reasoning at every step. Polished output without thinking will be rejected. So this file exists to make my thinking visible from minute one.

## What I'm assuming, and what could be wrong

**Assumption 1:** A "real" family office record means the entity actually exists, the website resolves, the contact person actually works there, and at least one signal is verifiable.
*Could be wrong if:* Brian considers third-party aggregator data (e.g., from existing FO databases) as "real." I'm assuming he does not, based on the line "entirely original records sourced through your own work."

**Assumption 2:** 50 records with high validation depth beats 100 records with shallow validation.
*Could be wrong if:* Brian is also implicitly testing speed/scale. I'm betting on quality because his framework rewards judgment over volume.

**Assumption 3:** The RAG demo doesn't need to be production-grade. It needs to demonstrate that I understand chunking, retrieval, and grounding.
*Could be wrong if:* He's testing production readiness specifically. I'll mitigate by documenting what I'd do differently for production.

## Discovery strategy (Task 1)

I'm choosing breadth over a single source to avoid concentration risk in any one channel.

**Primary sources I plan to use:**
- SEC IAPD/ADV filings — public, verifiable, US-focused
- Targeted Google searches with operators ("family office" site:linkedin.com/company)
- LinkedIn company search filtered for "family office" + size + location
- Public press coverage (FO Magazine, Trusted Insight, Family Wealth Report)

**Sources I am explicitly NOT using:**
- The provided sample dataset (against the brief)
- Paid FO databases (FINTRX, Bloomberg) — even if I had access, can't show provenance
- Random aggregator scrapes — too noisy

## Validation strategy

For each record I will check:
1. Website resolves and matches the entity name
2. Entity has a LinkedIn page or named principal with LinkedIn
3. At least one independent secondary source confirms the entity
4. Domain registration age (older = lower fraud risk)

For the 3 deep-dive records, I'll show the full chain.

## RAG architecture choices (Task 1)

**Stack:** Python, Supabase pgvector, Groq (Llama 3.3 70B), `sentence-transformers/all-MiniLM-L6-v2` for embeddings (free, local, 384 dims).

**Why these:**
- Supabase pgvector matches PolarityIQ's stack from the JD
- Groq because no Anthropic credits available right now (noted as a real constraint, not a choice). Architecture works identically with Claude API — only the client call changes.
- Local embeddings to avoid API cost and demonstrate I think about cost

**Chunking strategy:** Each FO record becomes one chunk. FO records are short, structured, and self-contained — splitting them would destroy context. Metadata fields (sectors, country, AUM band) become filterable.

**Retrieval:** Hybrid (vector + keyword). Vector for semantic queries ("FOs interested in climate"), keyword for exact terms (specific names, regions).

**What I will not do:**
- I will not pretend the eval is rigorous on 50 records. With this dataset size, retrieval quality is qualitative, not statistical.

## What I learned and what I would improve

The biggest lesson came from watching my own discovery script return 50 "high confidence" records that were all wrong. The rubric agreed with itself but had no concept of "is this an entity or an article about entities." Manual review caught what the rubric missed. In v2 I would filter article-format titles before scoring, require entity-page signals (About, Team, contact), add WHOIS domain age, and insert a manual review checkpoint between auto-discovery and validation. The discovery scripts stay in the repo as evidence of the failure and the pivot.

## Hours log

| Phase | Planned | Actual | Notes |
|---|---|---|---|
| Setup + plan | 1.5 | 0.5 | Faster than planned. |
| Discovery + dataset | 12 | 2.75 | Auto-discovery failed, switched to manual curation. |
| Validation + 3 deep records | 4 | 1.25 | URL verifier + 7 replacements + deep records. |
| RAG build | 6 | 1.0 | Simpler than planned because chunking was trivial (one record = one chunk). |
| Demo + deploy | 3 | 0.5 | Local demo + screen recording. Deploy skipped (recording sufficed per brief). |
| Task 2 writeup | 2 | 0.5 | |
| Documentation + submission | 2 | 0.5 | |
| **Total focused work** | **30.5** | **~6** | Spread across two sessions over 24 hours. |
