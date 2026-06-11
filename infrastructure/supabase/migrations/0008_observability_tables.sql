-- Observability tables for pilot SLO / request tracing (tenant-scoped RLS)
set search_path = noetfield, public;

create table if not exists observability_api_requests (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id),
  organization_id uuid references organizations(id),
  service text not null,
  route text not null,
  method text not null default 'GET',
  status_code integer not null check (status_code between 100 and 599),
  duration_ms numeric(12, 4) not null check (duration_ms >= 0),
  request_id text,
  actor_id text,
  metadata jsonb not null default '{}'::jsonb,
  recorded_at timestamptz not null default now()
);

create table if not exists observability_health_checks (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id),
  check_name text not null,
  status text not null default 'ok'
    check (status in ('ok', 'degraded', 'fail')),
  details jsonb not null default '{}'::jsonb,
  checked_at timestamptz not null default now()
);

create table if not exists observability_slo_windows (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id),
  service text not null,
  route_pattern text not null,
  window_start timestamptz not null,
  window_end timestamptz not null,
  request_count integer not null default 0 check (request_count >= 0),
  error_count integer not null default 0 check (error_count >= 0),
  p95_ms numeric(12, 4),
  created_at timestamptz not null default now(),
  check (window_end > window_start)
);

create index if not exists idx_observability_api_requests_tenant_time
  on observability_api_requests (tenant_id, recorded_at desc);

create index if not exists idx_observability_api_requests_route_time
  on observability_api_requests (service, route, recorded_at desc);

create index if not exists idx_observability_health_checks_name_time
  on observability_health_checks (check_name, checked_at desc);

create index if not exists idx_observability_slo_windows_tenant_window
  on observability_slo_windows (tenant_id, window_start desc);

alter table observability_api_requests enable row level security;
alter table observability_health_checks enable row level security;
alter table observability_slo_windows enable row level security;

-- Session tenant from app connection (service role omits setting → full access)
create or replace function noetfield.current_tenant_id()
returns uuid
language sql
stable
as $$
  select nullif(current_setting('noetfield.tenant_id', true), '')::uuid;
$$;

create policy observability_api_requests_tenant_access
  on observability_api_requests
  for all
  using (
    noetfield.current_tenant_id() is null
    or tenant_id = noetfield.current_tenant_id()
  )
  with check (
    noetfield.current_tenant_id() is null
    or tenant_id = noetfield.current_tenant_id()
  );

create policy observability_health_checks_tenant_access
  on observability_health_checks
  for all
  using (
    noetfield.current_tenant_id() is null
    or tenant_id is null
    or tenant_id = noetfield.current_tenant_id()
  )
  with check (
    noetfield.current_tenant_id() is null
    or tenant_id is null
    or tenant_id = noetfield.current_tenant_id()
  );

create policy observability_slo_windows_tenant_access
  on observability_slo_windows
  for all
  using (
    noetfield.current_tenant_id() is null
    or tenant_id = noetfield.current_tenant_id()
  )
  with check (
    noetfield.current_tenant_id() is null
    or tenant_id = noetfield.current_tenant_id()
  );

comment on table observability_api_requests is 'Append-only API request metrics for pilot SLO dashboards.';
comment on table observability_health_checks is 'Periodic health probe results (platform + tenant scoped).';
comment on table observability_slo_windows is 'Rollup windows for error rate and p95 latency by route.';
