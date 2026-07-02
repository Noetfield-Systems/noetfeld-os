-- NOOS factory autorun schedule self-register (A1 proof sink)
set search_path = public;

create table if not exists noetfield_truth_log (
  id bigserial primary key,
  recorded_at timestamptz not null default now(),
  source text not null default 'noos-factory-autorun',
  run_id text not null,
  event text not null,
  conclusion text not null,
  workflow text,
  metadata jsonb not null default '{}'::jsonb,
  constraint noetfield_truth_log_run_source_unique unique (run_id, source)
);

create index if not exists noetfield_truth_log_event_recorded_idx
  on noetfield_truth_log (event, recorded_at desc);

comment on table noetfield_truth_log is
  'Proof-grade run registry; factory autorun self-registers every GHA run.';
