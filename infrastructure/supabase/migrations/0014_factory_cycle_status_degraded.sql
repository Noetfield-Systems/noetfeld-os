-- Allow true degraded status on factory cycle rows (D5 — no alias flattening)
set search_path = public;

alter table noetfield_factory_cycle_runs
  drop constraint if exists noetfield_factory_cycle_runs_status_check;

alter table noetfield_factory_cycle_runs
  add constraint noetfield_factory_cycle_runs_status_check
  check (status in (
    'ok',
    'degraded',
    'recoverable_error',
    'recoverable_exception'
  ));

comment on column noetfield_factory_cycle_runs.status is
  'ok=success; degraded=partial/failed steps (truth preserved); recoverable_*=hard errors';

-- Backfill: rows aliased recoverable_error when cycle was degraded (loop fleet)
update noetfield_factory_cycle_runs
set status = 'degraded'
where status = 'recoverable_error'
  and exit_code = 1
  and factory_id like 'loop-%';
