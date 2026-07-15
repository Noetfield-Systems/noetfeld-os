-- 0019 — NOOS incident log (repair fix 7: minimal persistent forensics)
-- Project: Noetfield Systems (tkgpapowwplupyekpivy)
-- Access model: service_role via PostgREST (workers/scripts); anon/authenticated denied.
-- Why: Railway stdout is ephemeral and server.py explicitly no-ops log_message,
-- so post-incident forensics on an unhandled exception / non-200 was previously
-- impossible. This table gives the loop runner and Railway server one shared,
-- durable place to record what actually went wrong.

set search_path = public;

create table if not exists noos_incident_log (
  id bigint generated always as identity primary key,
  occurred_at timestamptz not null default now(),
  source text not null,
  loop_id text,
  event_type text,
  severity text not null default 'error',
  message text not null,
  detail jsonb,
  run_id text
);

create index if not exists noos_incident_log_occurred_at_idx
  on noos_incident_log (occurred_at desc);
create index if not exists noos_incident_log_source_idx
  on noos_incident_log (source);

alter table public.noos_incident_log enable row level security;
alter table public.noos_incident_log force row level security;
revoke all on table public.noos_incident_log from anon, authenticated;
grant select, insert, update, delete on table public.noos_incident_log to service_role;

comment on table noos_incident_log is
  'Post-incident forensics — one row per unhandled exception / non-200 in the NOOS loop pipeline (repair fix 7). RLS on — service_role only.';

notify pgrst, 'reload schema';
