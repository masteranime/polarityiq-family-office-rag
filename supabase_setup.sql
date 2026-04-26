-- Run this in Supabase SQL Editor BEFORE running scripts/4_load_supabase.py

-- 1. Enable pgvector extension
create extension if not exists vector;

-- 2. Create the family_offices table
drop table if exists family_offices;

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

-- 3. Create index for fast cosine similarity search
create index family_offices_embedding_idx
  on family_offices
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 10);

-- 4. Create the RPC function the FastAPI server calls
create or replace function match_family_offices(
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  id text,
  name text,
  website text,
  linkedin_url text,
  description text,
  sectors text,
  location text,
  country_guess text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    fo.id,
    fo.name,
    fo.website,
    fo.linkedin_url,
    fo.description,
    fo.sectors,
    fo.location,
    fo.country_guess,
    1 - (fo.embedding <=> query_embedding) as similarity
  from family_offices fo
  where 1 - (fo.embedding <=> query_embedding) > match_threshold
  order by fo.embedding <=> query_embedding
  limit match_count;
end;
$$;
