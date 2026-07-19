-- 0020 — NOOS durable health incident (Mission 2: durable + routable supervision)
-- Project: Noetfield Systems (tkgpapowwplupyekpivy)
-- Access model: service_role via PostgREST (workers/scripts); anon/authenticated denied.
-- Why: the stack-health reconciler previously scanned committed receipts in its own
-- ephemeral checkout (run 29664358570 reported pending=0), had no durable queue and
-- invoked no worker. This table is the durable authority for one incident per
-- stack-health fix_queue entry: reconciler reads OPEN rows, a registered handler or
-- external owner is dispatched, and the terminal state + worker run id are recorded.
-- .noos-runtime/** and GHA artifacts are NOT the durable queue (Mission 2 rule 4).

set search_path = public;

create table if not exists noos_health_incident (
  id bigint generated always as identity primary key,
  incident_id text not null,
  idempotency_key text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  -- provenance
  source_receipt text,
  source_run_url text,
  source_sha text,
  -- classification + routing
  failure_type text not null,
  fix_queue_key text not null,
  target_owner text not null,
  target_repository text,
  handler_id text not null,
  authority_class text not null,
  -- lifecycle
  attempt int not null default 0,
  retry_ceiling int not null default 3,
  state text not null default 'OPEN',
  worker_run_id text,
  terminal_receipt text,
  detail jsonb,
  -- idempotency: one live incident per (idempotency_key)
  constraint noos_health_incident_idem_uniq unique (idempotency_key)
);

create index if not exists noos_health_incident_state_idx
  on noos_health_incident (state);
create index if not exists noos_health_incident_owner_idx
  on noos_health_incident (target_owner);
create index if not exists noos_health_incident_created_idx
  on noos_health_incident (created_at desc);

alter table public.noos_health_incident enable row level security;
alter table public.noos_health_incident force row level security;
revoke all on table public.noos_health_incident from anon, authenticated;
grant select, insert, update, delete on table public.noos_health_incident to service_role;

comment on table noos_health_incident is
  'Durable NOOS supervision incidents — one row per stack-health fix_queue entry. OPEN→DISPATCHED→(RESOLVED|BLOCKED_EXTERNAL|RETRY_EXHAUSTED). RLS on — service_role only. Authority store for the reconciler (Mission 2).';

notify pgrst, 'reload schema';
