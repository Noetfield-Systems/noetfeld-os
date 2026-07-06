-- Operations inbox Gmail sweep — processed message ledger + sweep run receipts.

set search_path = noetfield, public;

create table if not exists operations_gmail_processed (
  gmail_message_id text primary key,
  gmail_thread_id text,
  signal_id uuid not null,
  processed_at timestamptz not null default now(),
  subject text,
  from_addr text,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_operations_gmail_processed_at
  on operations_gmail_processed (processed_at desc);

create table if not exists operations_gmail_sweep_runs (
  id uuid primary key default gen_random_uuid(),
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  messages_seen integer not null default 0,
  messages_ingested integer not null default 0,
  messages_skipped integer not null default 0,
  status text not null default 'running'
    check (status in ('running', 'completed', 'failed', 'skipped')),
  error text,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_operations_gmail_sweep_runs_started
  on operations_gmail_sweep_runs (started_at desc);

comment on table operations_gmail_processed is 'Gmail message ids ingested into signals — idempotency ledger for operations@ sweep.';
comment on table operations_gmail_sweep_runs is 'Scheduled Gmail sweep receipts (triage layer follows).';
