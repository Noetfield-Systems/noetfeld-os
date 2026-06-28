-- First-party funnel tables for sessions, conversions, and lead profiles.
set search_path = noetfield, public;

create table if not exists visitor_sessions (
  session_id text primary key,
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  request_id text,
  landing_page text,
  last_page text,
  referrer text,
  utm_source text,
  utm_medium text,
  utm_campaign text,
  user_agent text,
  metadata jsonb not null default '{}'::jsonb,
  check (last_seen_at >= first_seen_at)
);

create table if not exists conversion_events (
  conversion_id text primary key,
  event_id text references analytics_events(event_id) on delete set null,
  session_id text references visitor_sessions(session_id) on delete set null,
  request_id text,
  conversion_type text not null check (conversion_type ~ '^[a-z0-9_.:-]{2,80}$'),
  conversion_value numeric(12, 2),
  currency text,
  page_path text,
  source_event_name text,
  lead_id text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists lead_profiles (
  lead_id text primary key,
  primary_email text,
  organization text,
  contact_name text,
  status text not null default 'new'
    check (status in ('new', 'qualified', 'active', 'nurture', 'disqualified', 'closed')),
  source_session_id text references visitor_sessions(session_id) on delete set null,
  first_request_id text,
  latest_request_id text,
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  lead_score integer not null default 0 check (lead_score between 0 and 100),
  tags text[] not null default '{}',
  metadata jsonb not null default '{}'::jsonb,
  check (last_seen_at >= first_seen_at)
);

create unique index if not exists idx_lead_profiles_primary_email_unique
  on lead_profiles (lower(primary_email))
  where primary_email is not null;

create index if not exists idx_visitor_sessions_last_seen
  on visitor_sessions (last_seen_at desc);

create index if not exists idx_visitor_sessions_utm
  on visitor_sessions (utm_source, utm_medium, utm_campaign);

create index if not exists idx_conversion_events_type_time
  on conversion_events (conversion_type, created_at desc);

create index if not exists idx_conversion_events_session_time
  on conversion_events (session_id, created_at desc);

create index if not exists idx_lead_profiles_status_score
  on lead_profiles (status, lead_score desc, last_seen_at desc);

alter table visitor_sessions enable row level security;
alter table conversion_events enable row level security;
alter table lead_profiles enable row level security;

create policy visitor_sessions_service_access
  on visitor_sessions
  for all
  using (noetfield.current_tenant_id() is null)
  with check (noetfield.current_tenant_id() is null);

create policy conversion_events_service_access
  on conversion_events
  for all
  using (noetfield.current_tenant_id() is null)
  with check (noetfield.current_tenant_id() is null);

create policy lead_profiles_service_access
  on lead_profiles
  for all
  using (noetfield.current_tenant_id() is null)
  with check (noetfield.current_tenant_id() is null);

comment on table visitor_sessions is
  'Anonymous first-party visitor sessions for Noetfield traction and source attribution.';

comment on table conversion_events is
  'Normalized conversion moments such as form submits, chat-assisted intake, demo requests, and pilot applications.';

comment on table lead_profiles is
  'Noetfield lead profile rollups derived from public intakes, conversions, and qualified interactions.';
