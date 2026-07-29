-- 0023 — Supabase Security Advisor WARN remediation (Noetfield Systems)
-- Project: tkgpapowwplupyekpivy
-- Clears: function_search_path_mutable, rls_policy_always_true (gateway_utm_clicks),
--         anon/authenticated_security_definer_function_executable on machine RPCs.

-- 1) function_search_path_mutable
create or replace function public.gallery_set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create or replace function graph_kernel.reject_run_events_mutation()
returns trigger
language plpgsql
set search_path = graph_kernel, public
as $$
begin
  raise exception 'graph_kernel.run_events is append-only (UPDATE/DELETE forbidden)'
    using errcode = '42501';
end;
$$;

-- 2) gateway_utm_clicks — replace always-true WITH CHECK
drop policy if exists "anon insert gateway utm clicks" on public.gateway_utm_clicks;

create policy gateway_utm_clicks_anon_insert_v2
  on public.gateway_utm_clicks
  for insert
  to anon
  with check (
    coalesce(length(trim(page_path)), 0) > 0
    and (
      coalesce(length(trim(session_id)), 0) > 0
      or coalesce(length(trim(visitor_id)), 0) > 0
    )
    and is_test is not null
  );

comment on policy gateway_utm_clicks_anon_insert_v2 on public.gateway_utm_clicks is
  'Anon UTM click insert with page_path + session/visitor validation (replaces WITH CHECK true).';

-- 3) Seal SECURITY DEFINER RPCs from anon/authenticated (service_role workers only)
revoke all on function public.claim_runway_plan_backlog_v1(text, text, integer) from public, anon, authenticated;
revoke all on function public.claim_runway_runtime_outbox_by_id_v1_1(text, text, integer) from public, anon, authenticated;
revoke all on function public.gateway_lane_counts() from public, anon, authenticated;
revoke all on function public.gateway_last_signal() from public, anon, authenticated;
revoke all on function public.gateway_utm_click_counts() from public, anon, authenticated;
revoke all on function public.mark_build_task_v1(text, text, text, jsonb) from public, anon, authenticated;
revoke all on function public.mark_runway_plan_enqueued_v1(text, text, text) from public, anon, authenticated;
revoke all on function public.pick_next_build_task_v1() from public, anon, authenticated;
revoke all on function public.seed_runway_build_backlog_v1(jsonb) from public, anon, authenticated;
revoke all on function public.trustfield_handle_new_user() from public, anon, authenticated;

grant execute on function public.claim_runway_plan_backlog_v1(text, text, integer) to service_role;
grant execute on function public.claim_runway_runtime_outbox_by_id_v1_1(text, text, integer) to service_role;
grant execute on function public.gateway_lane_counts() to service_role;
grant execute on function public.gateway_last_signal() to service_role;
grant execute on function public.gateway_utm_click_counts() to service_role;
grant execute on function public.mark_build_task_v1(text, text, text, jsonb) to service_role;
grant execute on function public.mark_runway_plan_enqueued_v1(text, text, text) to service_role;
grant execute on function public.pick_next_build_task_v1() to service_role;
grant execute on function public.seed_runway_build_backlog_v1(jsonb) to service_role;

notify pgrst, 'reload schema';
