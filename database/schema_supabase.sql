-- Enable pgvector
create extension if not exists vector;

-- Documents table
create table if not exists documents (
  id uuid primary key,
  filename text not null,
  mime_type text,
  created_at timestamptz default now()
);

-- Chunks table with vector embeddings (384-dim for MiniLM)
create table if not exists chunks (
  id bigserial primary key,
  doc_id uuid references documents(id) on delete cascade,
  content text not null,
  embedding vector(384)
);

-- Speed up ANN search (HNSW index); requires Supabase postgres >= 15 with pgvector
create index if not exists idx_chunks_embedding on chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index if not exists idx_chunks_doc on chunks (doc_id);

-- Similarity RPC function
create or replace function match_chunks(
  query_embedding vector(384),
  match_count int,
  filter_doc uuid default null
)
returns table (
  id bigint,
  doc_id uuid,
  content text,
  similarity double precision
)
language sql stable
as $$
  select
    c.id,
    c.doc_id,
    c.content,
    1 - (c.embedding <=> query_embedding) as similarity
  from chunks c
  where (filter_doc is null or c.doc_id = filter_doc)
  order by c.embedding <-> query_embedding
  limit match_count;
$$;
