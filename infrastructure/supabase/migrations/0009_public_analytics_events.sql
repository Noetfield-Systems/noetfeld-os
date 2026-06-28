-- First-party public analytics events for traction and funnel tracking.
set search_path = noetfield, public;

create table if not exists analytics_events (
  event_id text primary key,
  event_name text not null check (event_name ~ '^[a-z0-9_.:-]{2,80}$'),
  request_id text,
  session_id text,
  page_path text,
  page_url text,
  referrer text,
  utm_source text,
  utm_medium text,
  utm_campaign text,
  component text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_analytics_events_name_time
  on analytics_events (event_name, created_at desc);

create index if not exists idx_analytics_events_path_time
  on analytics_events (page_path, created_at desc);

create index if not exists idx_analytics_events_session_time
  on analytics_events (session_id, created_at desc);

create index if not exists idx_analytics_events_request_id
  on analytics_events (request_id);

alter table analytics_events enable row level security;

create policy analytics_events_service_access
  on analytics_events
  for all
  using (noetfield.current_tenant_id() is null)
  with check (noetfield.current_tenant_id() is null);

comment on table analytics_events is
  'First-party public website and product interaction events for Noetfield traction dashboards.';
