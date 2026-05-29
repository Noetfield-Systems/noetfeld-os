-- Public ecosystem: durable intake queue + optional knowledge chunks (RAG-ready).

set search_path = noetfield, public;

create table if not exists public_intakes (
  intake_id text primary key,
  created_at timestamptz not null default now(),
  request_id text,
  organization text not null,
  contact_name text,
  contact_email text not null,
  sku text not null default 'trust_brief',
  vector text not null default 'web-intake',
  source text not null default 'api',
  message text not null,
  metadata jsonb not null default '{}'::jsonb
);

create unique index if not exists idx_public_intakes_request_id
  on public_intakes (request_id)
  where request_id is not null;

create index if not exists idx_public_intakes_created_at
  on public_intakes (created_at desc);

create index if not exists idx_public_intakes_contact_email
  on public_intakes (contact_email, created_at desc);

comment on table public_intakes is 'Public website/Telegram intake leads for operations@noetfield.com.';

-- Optional RAG chunks (embedding column for future pgvector indexing).
create table if not exists knowledge_chunks (
  id uuid primary key default gen_random_uuid(),
  source_path text not null,
  section_title text,
  content text not null,
  content_hash text not null,
  updated_at timestamptz not null default now(),
  unique (content_hash)
);

create index if not exists idx_knowledge_chunks_source
  on knowledge_chunks (source_path);

comment on table knowledge_chunks is 'Indexed public knowledge for assistant RAG (populate via scripts/sync_knowledge_chunks.py).';
