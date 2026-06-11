-- Trust Ledger v1 — evidence index + TLE entries (append-only after sign-off)
set search_path = noetfield, public;

create table if not exists trust_ledger_evidence (
  evidence_id text primary key,
  source text not null,
  title text not null,
  hash text not null,
  link text,
  sensitivity text,
  ingest_mode text not null default 'metadata_only'
    check (ingest_mode in ('metadata_only', 'full_capture')),
  ingested_at timestamptz not null default now(),
  tenant_id uuid references tenants(id)
);

create table if not exists tle_entries (
  tle_id text primary key,
  status text not null default 'Draft'
    check (status in ('Draft', 'Approved', 'Rejected', 'Conditional')),
  body jsonb not null,
  created_at timestamptz not null default now(),
  approved_at timestamptz,
  immutable boolean not null default false
);

create index if not exists idx_tle_entries_status on tle_entries (status);
create index if not exists idx_trust_ledger_evidence_tenant on trust_ledger_evidence (tenant_id);

-- Prevent mutation of signed TLE rows (append-only after approval)
create or replace function noetfield.tle_entries_immutable_guard()
returns trigger
language plpgsql
as $$
begin
  if tg_op = 'UPDATE' and old.immutable = true then
    raise exception 'tle_entries row is immutable after approval';
  end if;
  if tg_op = 'UPDATE' and old.status in ('Approved', 'Rejected') and new.body is distinct from old.body then
    raise exception 'tle_entries body cannot change after terminal status';
  end if;
  if tg_op = 'UPDATE' and new.status in ('Approved', 'Rejected') then
    new.immutable := true;
    new.approved_at := coalesce(new.approved_at, now());
  end if;
  return new;
end;
$$;

drop trigger if exists tle_entries_immutable_guard on tle_entries;
create trigger tle_entries_immutable_guard
  before update on tle_entries
  for each row
  execute function noetfield.tle_entries_immutable_guard();
