-- 0017 — Enable RLS on machine-only public tables (Supabase Security Advisor rls_disabled_in_public)
-- Project: Noetfield Systems (tkgpapowwplupyekpivy)
-- Access model: service_role via PostgREST (workers/scripts); anon/authenticated denied.

set search_path = public;

do $$
declare
  t text;
  tables text[] := array[
    'noetfield_truth_log',
    'probe_cron_receipts',
    'improvement_queue',
    'noos_loop_registry',
    'noos_deadman_runs',
    'workflow_census_v1',
    'workflow_census_runs_v1',
    'trustfield_loop_registry',
    'trustfield_loop_receipts',
    'trustfield_verify_recipe_runs'
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

comment on table public.noetfield_truth_log is
  'Proof-grade run registry; RLS on — service_role only (0017).';
comment on table public.noos_loop_registry is
  'Loop liveness registry; RLS on — service_role only (0017).';
comment on table public.noos_deadman_runs is
  'Deadman receipts; RLS on — service_role only (0017).';

notify pgrst, 'reload schema';
