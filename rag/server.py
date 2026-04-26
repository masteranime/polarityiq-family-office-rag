"""
rag/server.py — FastAPI app exposing /query for natural-language search.

Flow:
  user query -> embed -> Supabase pgvector match -> top-K records
  -> compose prompt with grounded context -> Groq LLM
  -> return answer + sources

Why hybrid would be better but I didn't ship it:
  pgvector alone misses exact-string queries (e.g., user types a fund name).
  In production I'd add a Postgres full-text search and merge with RRF.
  At 50 records the difference is small, so I'm shipping vector-only and
  documenting the gap honestly.
"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer
from groq import Groq

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"
TOP_K = 5
SIM_THRESHOLD = 0.3

app = FastAPI(title="PolarityIQ FO RAG")
model = SentenceTransformer(EMBED_MODEL)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
groq = Groq(api_key=GROQ_API_KEY)


class Query(BaseModel):
    question: str


@app.get("/")
def root():
    return FileResponse(Path(__file__).parent / "index.html")


@app.post("/query")
def query(q: Query):
    if not q.question.strip():
        raise HTTPException(400, "Empty question")

    # 1. Embed question
    q_emb = model.encode(q.question).tolist()

    # 2. Retrieve from Supabase
    try:
        result = supabase.rpc("match_family_offices", {
            "query_embedding": q_emb,
            "match_threshold": SIM_THRESHOLD,
            "match_count": TOP_K,
        }).execute()
        matches = result.data or []
    except Exception as e:
        raise HTTPException(500, f"Retrieval error: {e}")

    if not matches:
        return {
            "answer": "I could not find any family offices in my dataset that match this query.",
            "sources": [],
        }

    # 3. Compose grounded prompt
    context_blocks = []
    for i, m in enumerate(matches, 1):
        block = (
            f"[FO_{i}] {m['name']}\n"
            f"  Location: {m['location']}, {m['country_guess']}\n"
            f"  Sectors: {m['sectors']}\n"
            f"  Description: {m['description']}\n"
            f"  Website: {m['website']}\n"
            f"  Similarity: {m['similarity']:.3f}"
        )
        context_blocks.append(block)
    context = "\n\n".join(context_blocks)

    system = (
        "You are an analyst answering questions about a private dataset of "
        "family offices. Use ONLY the records provided in the context. "
        "If the context does not contain enough information to answer, say so plainly. "
        "Do not invent firms, locations, or sectors. Cite each fact with the [FO_N] tag."
    )
    user = f"Context (top {len(matches)} matched records):\n\n{context}\n\nQuestion: {q.question}\n\nAnswer:"

    # 4. Generate
    try:
        completion = groq.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            max_tokens=600,
        )
        answer = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    return {
        "answer": answer,
        "sources": [
            {
                "id": m["id"],
                "name": m["name"],
                "website": m["website"],
                "linkedin_url": m["linkedin_url"],
                "location": m["location"],
                "sectors": m["sectors"],
                "similarity": round(m["similarity"], 3),
            }
            for m in matches
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok", "model": LLM_MODEL, "embed_model": EMBED_MODEL}
