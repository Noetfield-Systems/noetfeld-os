-- Noetfield v3.1 Phase 3 runtime activation.
-- Durable support for live event tracing, dead-letter handling, graph
-- reflections, and runtime approval queue projections.

set search_path = noetfield, public;

create table if not exists event_traces (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id),
  organization_id uuid references organizations(id),
  event_id uuid not null,
  event_type text not null,
  trace_id uuid not null,
  span_id uuid not null,
  correlation_id uuid not null,
  published_at timestamptz not null,
  dispatch_duration_ms numeric(12,4),
  created_at timestamptz not null default now()
);

create table if not exists dead_letter_events (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id),
  organization_id uuid references organizations(id),
  event_id uuid not null,
  event_type text not null,
  subscriber_name text not null,
  error_type text not null,
  error_message text not null,
  payload jsonb not null,
  trace jsonb not null default '{}'::jsonb,
  status text not null default 'open'
    check (status in ('open', 'replayed', 'ignored', 'resolved')),
  failed_at timestamptz not null,
  resolved_at timestamptz
);

create table if not exists graph_reflection_cycles (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  relationship_count integer not null,
  inferred_count integer not null,
  low_confidence_count integer not null,
  low_confidence_threshold numeric(5,4) not null,
  governance_event_id uuid references governance_events(event_id),
  generated_at timestamptz not null default now()
);

create table if not exists approval_queue_projection (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  approval_id uuid not null unique,
  requested_by text not null,
  action text not null,
  resource_type text not null,
  resource_id text not null,
  reason text not null,
  status text not null default 'pending'
    check (status in ('pending', 'approved', 'denied', 'cancelled')),
  payload jsonb not null default '{}'::jsonb,
  requested_at timestamptz not null,
  decided_at timestamptz
);

alter table event_traces enable row level security;
alter table dead_letter_events enable row level security;
alter table graph_reflection_cycles enable row level security;
alter table approval_queue_projection enable row level security;

create index if not exists idx_event_traces_correlation
  on event_traces (correlation_id, published_at desc);

create index if not exists idx_dead_letter_events_status
  on dead_letter_events (status, failed_at desc);

create index if not exists idx_graph_reflection_cycles_tenant_time
  on graph_reflection_cycles (tenant_id, generated_at desc);

create index if not exists idx_approval_queue_projection_tenant_status
  on approval_queue_projection (tenant_id, status, requested_at desc);

comment on table event_traces is 'Phase 3 event tracing projection for runtime observability.';
comment on table dead_letter_events is 'Phase 3 dead-letter queue for failed subscriber execution.';
comment on table graph_reflection_cycles is 'Temporal graph reflection cycle history.';
comment on table approval_queue_projection is 'Operational projection of pending human approvals.';
