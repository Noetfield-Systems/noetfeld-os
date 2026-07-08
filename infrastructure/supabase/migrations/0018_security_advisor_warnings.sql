-- 0018 — Supabase Security Advisor warnings (function search_path, vector schema, gateway_leads RLS)
-- Project: Noetfield Systems (tkgpapowwplupyekpivy)

-- 1) Function search_path mutable (noetfield.*)
create or replace function noetfield.prevent_update_delete()
returns trigger
language plpgsql
set search_path = noetfield, public
as $$
begin
  raise exception 'append-only table % does not allow %', tg_table_name, tg_op;
end;
$$;

create or replace function noetfield.tle_entries_immutable_guard()
returns trigger
language plpgsql
set search_path = noetfield, public
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

create or replace function noetfield.current_tenant_id()
returns uuid
language sql
stable
set search_path = noetfield, public
as $$
  select nullif(current_setting('noetfield.tenant_id', true), '')::uuid;
$$;

-- 2) Extension in public → extensions schema (Supabase recommended)
create schema if not exists extensions;
grant usage on schema extensions to postgres, anon, authenticated, service_role;
alter extension vector set schema extensions;

-- 3) gateway_leads — replace always-true WITH CHECK (anon insert-only, field validation)
drop policy if exists "public insert only gateway leads" on public.gateway_leads;

create policy gateway_leads_anon_insert_v2
  on public.gateway_leads
  for insert
  to anon
  with check (
    coalesce(length(trim(name)), 0) > 0
    and identity is not null
    and intent is not null
    and consent_to_contact is not null
    and (
      coalesce(length(trim(email)), 0) > 0
      or coalesce(length(trim(contact)), 0) > 0
      or coalesce(length(trim(phone)), 0) > 0
    )
  );

comment on policy gateway_leads_anon_insert_v2 on public.gateway_leads is
  'Anon insert-only with minimal field validation (replaces WITH CHECK true).';

notify pgrst, 'reload schema';
