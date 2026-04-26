# PolarityIQ Differentiator — Family Office RAG Pipeline

Submission for the PolarityIQ Senior AI Engineer Differentiator (Stage 1, Task 1).

## What this is

A working pipeline that:
1. Discovers and validates 50 real family office (FO) records
2. Stores them in Supabase (Postgres + pgvector)
3. Exposes them via a natural-language query interface (RAG)

## Stack

| Layer | Choice | Why |
|---|---|---|
| Vector DB | Supabase pgvector | Matches PolarityIQ's stated stack |
| LLM | Groq (Llama 3.3 70B) | Free tier, fast. Architecture identical with Claude API. |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` (local) | No API cost, 384-dim, fast |
| Discovery | SerpAPI + targeted manual research | Free tier, controllable cost |
| Backend | FastAPI | Minimal surface area |

## Repo structure

```
.
├── PLAN.md                  Visible reasoning + assumptions log
├── METHODOLOGY.md           How the dataset was built (filled at end)
├── data/
│   └── processed/
│       └── family_offices.csv     Final 50-record dataset
├── scripts/
│   ├── 1_discover.py         Search + extract candidate FOs
│   ├── 2_enrich.py           Pull website, LinkedIn, principal contact
│   ├── 3_validate.py         Score each record, flag low-confidence
│   └── 4_load_supabase.py    Embed + insert into Supabase
├── rag/
│   ├── server.py             FastAPI app — POST /query
│   └── index.html            Minimal demo UI
└── deep_validation/
    └── three_records.md      Full validation chain for 3 selected records
```

## How to run

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # fill in real keys

# Build the dataset (one time)
python scripts/1_discover.py
python scripts/2_enrich.py
python scripts/3_validate.py
python scripts/4_load_supabase.py

# Run the demo
uvicorn rag.server:app --reload
# Open http://localhost:8000
```

## Live demo

[Add Vercel/Render URL or screen recording link before submission]

## Documentation

- [`PLAN.md`](./PLAN.md) — what I assumed, what I was uncertain about
- [`METHODOLOGY.md`](./METHODOLOGY.md) — dataset construction
- [`deep_validation/three_records.md`](./deep_validation/three_records.md) — full chain for 3 records

## Honest limitations

- 50 records is too small for a real retrieval eval. Quality is judged qualitatively.
- LinkedIn validation is manual — I do not scrape LinkedIn for ToS reasons.
- Email/phone validation is at the domain level (does the domain accept mail) — not per-mailbox.

## Contact

Muhammad Shaheer · shaheerawan001@gmail.com
