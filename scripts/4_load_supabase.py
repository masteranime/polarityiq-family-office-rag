"""
4_load_supabase.py — Embed records and insert into Supabase.

Schema (run in Supabase SQL Editor before this script):

    create extension if not exists vector;

    create table family_offices (
        id text primary key,
        name text,
        website text,
        linkedin_url text,
        description text,
        sectors text,
        location text,
        country_guess text,
        discovery_source text,
        discovery_query text,
        validation_score int,
        confidence text,
        validation_reasons text,
        embedding vector(384),
        searchable_text text
    );

    create index on family_offices using ivfflat (embedding vector_cosine_ops) with (lists = 10);

    create or replace function match_family_offices(
      query_embedding vector(384),
      match_threshold float,
      match_count int
    )
    returns table (
      id text, name text, website text, linkedin_url text,
      description text, sectors text, location text, country_guess text,
      similarity float
    )
    language plpgsql as $$
    begin
      return query
      select fo.id, fo.name, fo.website, fo.linkedin_url, fo.description,
             fo.sectors, fo.location, fo.country_guess,
             1 - (fo.embedding <=> query_embedding) as similarity
      from family_offices fo
      where 1 - (fo.embedding <=> query_embedding) > match_threshold
      order by fo.embedding <=> query_embedding
      limit match_count;
    end;
    $$;

Chunking note:
  Each FO record is one chunk. The "searchable_text" we embed is a composed
  string that mixes the most queryable fields. We do this because users will
  ask things like "FOs in Texas investing in real estate" — the embedding
  must contain location AND sectors, not just description.
"""

import os
import csv
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer

load_dotenv()

INPUT = Path("data/processed/family_offices.csv")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384 dims, free, fast


def compose_searchable_text(r: dict) -> str:
    """The text we actually embed. Includes structured fields so semantic search
    can match on location/sectors, not just description."""
    parts = [
        f"Name: {r['name']}",
        f"Location: {r['location']}, {r['country_guess']}".strip().rstrip(","),
        f"Investing sectors: {r['sectors']}" if r['sectors'] else "",
        f"Description: {r['description']}",
    ]
    return ". ".join(p for p in parts if p)


def main():
    if not SUPABASE_URL or SUPABASE_URL.startswith("https://yourproject"):
        print("ERROR: Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        return

    if not INPUT.exists():
        print(f"ERROR: {INPUT} not found. Run 3_validate.py first.")
        return

    print(f"Loading model {EMBED_MODEL}...")
    model = SentenceTransformer(EMBED_MODEL)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    rows = []
    with open(INPUT, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Embedding {len(rows)} records...")
    texts = [compose_searchable_text(r) for r in rows]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    print("Inserting into Supabase...")
    inserted = 0
    for r, text, emb in zip(rows, texts, embeddings):
        record = {
            "id": r["id"],
            "name": r["name"],
            "website": r["website"],
            "linkedin_url": r["linkedin_url"],
            "description": r["description"],
            "sectors": r["sectors"],
            "location": r["location"],
            "country_guess": r["country_guess"],
            "discovery_source": r["discovery_source"],
            "discovery_query": r["discovery_query"],
            "validation_score": int(r["validation_score"]),
            "confidence": r["confidence"],
            "validation_reasons": r["validation_reasons"],
            "embedding": emb,
            "searchable_text": text,
        }
        try:
            supabase.table("family_offices").upsert(record).execute()
            inserted += 1
        except Exception as e:
            print(f"  Insert error for {r['id']}: {e}")

    print(f"Done. {inserted}/{len(rows)} inserted.")
    print("Next: uvicorn rag.server:app --reload")


if __name__ == "__main__":
    main()
