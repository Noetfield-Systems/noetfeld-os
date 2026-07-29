-- 0022 — Enable RLS on remaining machine-only public tables (Supabase Security Advisor rls_disabled_in_public)
-- Project: Noetfield Systems (tkgpapowwplupyekpivy)
-- Access model: service_role via PostgREST (workers/scripts); anon/authenticated denied.
-- Applied live: 2026-07-28 via Supabase MCP (security alert remediation).

set search_path = public;

do $$
declare
  t text;
  tables text[] := array[
    'gallery_ingest_leases_v1',
    'gallery_loop_receipts_v1',
    'gallery_loop_registry_v1',
    'gallery_budget_ledger_v1',
    'gallery_assets_v1',
    'runway_plan_backlog_claims_v1',
    'runway_dispatcher_events_v1',
    'noos_plan_completion_backlog',
    'noos_plan_completion_events',
    'nf_code_factory_rules'
  ];
begin
  foreach t in array tables
  loop
    if to_regclass('public.' || t) is null then
      raise notice 'skip missing table: %', t;
      continue;
    end if;
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    execute format('revoke all on table public.%I from anon, authenticated', t);
    execute format('grant select, insert, update, delete on table public.%I to service_role', t);
    raise notice 'rls enabled: %', t;
  end loop;
end $$;

notify pgrst, 'reload schema';
