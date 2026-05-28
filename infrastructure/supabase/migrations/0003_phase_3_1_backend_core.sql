-- Noetfield Phase 3.1 backend durability core.
-- PostgreSQL is the governance system of record. Supabase is optional tooling.

set search_path = noetfield, public;

create table if not exists workflow_instances (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  workflow_type text not null,
  target_entity_type text not null,
  target_entity_id text not null,
  state text not null,
  payload jsonb not null default '{}'::jsonb,
  created_by text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists inspector_execution_runs (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  objective text not null,
  inspector_names text[] not null default '{}',
  status text not null default 'started'
    check (status in ('started', 'completed', 'failed', 'cancelled', 'waiting_for_review')),
  findings jsonb not null default '[]'::jsonb,
  requires_human_review boolean not null default true,
  started_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists copilot_governance_runs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  organization_id uuid not null references organizations(id),
  signal_id uuid,
  workflow_id uuid,
  objective text not null,
  status text not null default 'started'
    check (status in ('started', 'waiting_for_approval', 'completed', 'failed')),
  result jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table workflow_instances enable row level security;
alter table inspector_execution_runs enable row level security;
alter table copilot_governance_runs enable row level security;

create index if not exists idx_workflow_instances_tenant_state
  on workflow_instances (tenant_id, state, updated_at desc);

create index if not exists idx_inspector_execution_runs_tenant_status
  on inspector_execution_runs (tenant_id, status, started_at desc);

create index if not exists idx_copilot_governance_runs_tenant_status
  on copilot_governance_runs (tenant_id, status, created_at desc);

comment on table workflow_instances is 'Phase 3.1 durable workflow state machine instances.';
comment on table inspector_execution_runs is 'Phase 3.1 durable bounded inspector execution records.';
comment on table copilot_governance_runs is 'Use-case layer for Copilot Governance demo runs.';
