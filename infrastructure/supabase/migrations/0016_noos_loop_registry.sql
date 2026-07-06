-- Phase B — loop liveness registry + deadman run receipts
set search_path = public;

create table if not exists noos_loop_registry (
  loop_id text primary key,
  event_type text,
  interval_minutes integer not null default 5,
  last_fired_at timestamptz,
  last_cycle_status text,
  host text not null default 'unknown',
  updated_at timestamptz not null default now()
);

create index if not exists noos_loop_registry_last_fired_idx
  on noos_loop_registry (last_fired_at desc nulls last);

create table if not exists noos_deadman_runs (
  run_id text primary key,
  run_at timestamptz not null default now(),
  receipt jsonb not null
);

create index if not exists noos_deadman_runs_run_at_idx
  on noos_deadman_runs (run_at desc);

comment on table noos_loop_registry is
  'Living System Phase B — last_fired_at per loop for dead-man staleness checks';
comment on table noos_deadman_runs is
  'Deadman worker receipts (CF cannot write repo paths; Supabase sink)';
