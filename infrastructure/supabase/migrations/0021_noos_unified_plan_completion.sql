-- NOOS unified plan-completion event log + derived backlog (D5).
-- Append-only events are authored truth; backlog rows are derived/CAS projections.

create table if not exists public.noos_plan_completion_events (
  id bigserial primary key,
  op_key text not null,
  event_type text not null,
  plan_id text not null,
  item_id text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (op_key, event_type)
);

create index if not exists noos_plan_completion_events_item_idx
  on public.noos_plan_completion_events (plan_id, item_id, created_at desc);

create table if not exists public.noos_plan_completion_backlog (
  op_key text primary key,
  plan_id text not null,
  item_id text not null,
  status text not null check (status in (
    'READY', 'DISPATCHED', 'COMPLETE', 'BLOCKED_WITH_REASON', 'FOUNDER_BLOCKED'
  )),
  role text,
  value_class text,
  job_id text,
  content_hash text not null,
  fencing_token bigint not null default 1,
  updated_at timestamptz not null default now(),
  unique (plan_id, item_id)
);

create index if not exists noos_plan_completion_backlog_status_idx
  on public.noos_plan_completion_backlog (status, updated_at);

comment on table public.noos_plan_completion_events is
  'Append-only plan-completion events; backlog is derived.';
comment on table public.noos_plan_completion_backlog is
  'Derived backlog with CAS fencing_token; single writer = NOOS reconciler.';
