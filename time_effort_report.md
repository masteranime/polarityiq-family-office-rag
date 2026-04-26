# Time and Effort Report

**Total elapsed time:** ~24 hours from when the brief arrived.
**Actual focused working time:** ~6 hours of the 24, spread across two sessions. The rest was sleep, breaks, and waiting on long-running steps (model downloads, SerpAPI throttling, manual URL checks).

## Phase breakdown

| Phase | Hours | What I did |
|---|---|---|
| Reading brief, planning, setup | 0.5 | Read both docs twice. Set up Python venv, Supabase project, GitHub repo, .env. |
| Discovery scripts (1, 2, 3) | 1.0 | Wrote SerpAPI query set, homepage enricher, scoring rubric. Ran end-to-end. |
| Catching the failure | 0.25 | Manually reviewed output. Found that "names" were article titles, not entities. Documented the failure. |
| Manual curation of 50 FOs | 1.5 | Switched to manual curation from public sources (SEC, Wikipedia, FO Magazine, company sites). |
| URL verification + replacements | 0.75 | Wrote a verifier script. 7 URLs broken on first pass. Replaced with verified alternates. Re-ran. |
| Supabase load + RAG server | 1.0 | Embedded with all-MiniLM-L6-v2 (local, free), loaded to pgvector, built FastAPI server with grounded prompts. |
| Demo testing + screen recording | 0.5 | Ran 3 query types (good match, edge match, no match). Recorded silent screen video. |
| Deep validation (3 records) | 0.5 | Sourced and documented the validation chain for Bezos Expeditions, Cascade Investment, Emerson Collective. |

**Subtotal: ~6 hours focused work.**

## How I used AI

I used Claude as a development pair throughout. Specifically:

- **Code scaffolding** for the 4 discovery scripts and the FastAPI server. I reviewed every file before running it.
- **Curation acceleration** when I switched to manual sourcing. I named the public sources (SEC ADV, Wikipedia, FO Magazine) and verified each entry by visiting the website myself.
- **Documentation drafts** that I rewrote in my own voice before submission.

## Where I caught AI doing the wrong thing

- **Discovery script logic.** The first scoring rubric trusted keyword presence and scored article titles as valid FO names. I caught this on manual review and pivoted to curation. The script stayed in the repo as evidence.
- **Generated FO entries.** The first curated list had 7 dead URLs. The verifier script caught all 7. Replacements were re-verified before adding.
- **RAG retrieval coverage.** Vector-only search missed records that explicitly listed "climate" as a sector. I documented the gap rather than tune the threshold to hide it.

## Honest limits

- 50 records is too small for a rigorous retrieval evaluation. Quality is judged qualitatively.
- No verified per-mailbox emails or phone numbers. Large FOs do not publish contact data by design. I did not invent any.
- Vector-only retrieval is the weak link. Production version needs hybrid search and a reranker. I scoped to vector-only for the 48-hour window and documented what I would change.
