-- Trust Ledger connectors + PendingApproval status
set search_path = noetfield, public;

create table if not exists trust_ledger_connectors (
  connector_id text primary key,
  type text not null,
  required_scopes text[] not null default '{}',
  ingest_mode text not null default 'metadata_only'
    check (ingest_mode in ('metadata_only', 'full_capture')),
  last_sync timestamptz,
  status text not null default 'registered'
    check (status in ('registered', 'active', 'error', 'disabled')),
  registered_at timestamptz not null default now()
);

-- Allow PendingApproval on TLE rows (multi-approver flow)
alter table tle_entries drop constraint if exists tle_entries_status_check;
alter table tle_entries add constraint tle_entries_status_check
  check (status in ('Draft', 'PendingApproval', 'Approved', 'Rejected', 'Conditional'));
