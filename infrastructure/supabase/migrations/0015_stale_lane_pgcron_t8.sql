-- T8 nerve: pg_cron stale-lane detector + spine event feed (NOETFIELD spec §1 T8)
-- Requires: Supabase Dashboard → Database → Extensions → pg_cron (enable once per project)
-- Optional: enable Realtime on noetfield_stale_lane_events + noetfield_factory_cycle_runs for browser clients

set search_path = public;

create table if not exists noetfield_stale_lane_events (
  id bigserial primary key,
  recorded_at timestamptz not null default now(),
  lane_id text not null,
  factory_id text,
  last_seen_at timestamptz,
  stale_threshold_minutes int not null default 30,
  event text not null default 'stale_lane',
  source text not null default 'pg_cron_t8',
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists noetfield_stale_lane_events_lane_recorded_idx
  on noetfield_stale_lane_events (lane_id, recorded_at desc);

create index if not exists noetfield_stale_lane_events_event_recorded_idx
  on noetfield_stale_lane_events (event, recorded_at desc);

comment on table noetfield_stale_lane_events is
  'T8 DB-triggered nerve: stale lane receipts emitted by pg_cron detector.';

create or replace function noetfield_detect_stale_lanes_v1()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  lane record;
  inserted int := 0;
  result jsonb := '[]'::jsonb;
begin
  for lane in
    select
      coalesce(factory_id, 'unknown') as lane_id,
      factory_id,
      max(coalesce(finished_at, started_at, recorded_at)) as last_seen_at
    from noetfield_factory_cycle_runs
    group by factory_id
  loop
    if lane.last_seen_at is null then
      continue;
    end if;
    if lane.last_seen_at < now() - interval '30 minutes' then
      insert into noetfield_stale_lane_events (
        lane_id, factory_id, last_seen_at, stale_threshold_minutes, event, metadata
      )
      select
        lane.lane_id,
        lane.factory_id,
        lane.last_seen_at,
        30,
        'stale_lane',
        jsonb_build_object(
          'age_minutes', round(extract(epoch from (now() - lane.last_seen_at)) / 60.0, 2),
          'detector', 'noetfield_detect_stale_lanes_v1'
        )
      where not exists (
        select 1
        from noetfield_stale_lane_events e
        where e.lane_id = lane.lane_id
          and e.event = 'stale_lane'
          and e.recorded_at > now() - interval '30 minutes'
      );
      if found then
        inserted := inserted + 1;
        perform pg_notify(
          'noetfield_spine_feed',
          json_build_object(
            'event', 'stale_lane',
            'lane_id', lane.lane_id,
            'factory_id', lane.factory_id,
            'last_seen_at', lane.last_seen_at
          )::text
        );
        result := result || jsonb_build_array(
          jsonb_build_object(
            'lane_id', lane.lane_id,
            'factory_id', lane.factory_id,
            'last_seen_at', lane.last_seen_at
          )
        );
      end if;
    end if;
  end loop;
  return jsonb_build_object('inserted', inserted, 'lanes', result, 'at', now());
end;
$$;

-- pg_cron schedule (no-op if extension unavailable — apply_supabase_migration logs warning)
do $$
declare
  job_id bigint;
begin
  if exists (select 1 from pg_extension where extname = 'pg_cron') then
    for job_id in select jobid from cron.job where jobname = 'noetfield-stale-lane-detector-v1'
    loop
      perform cron.unschedule(job_id);
    end loop;
    perform cron.schedule(
      'noetfield-stale-lane-detector-v1',
      '*/15 * * * *',
      $$select noetfield_detect_stale_lanes_v1();$$
    );
  end if;
exception
  when undefined_table or undefined_function then
    raise notice 'pg_cron not enabled — enable in Supabase Dashboard then re-run migration';
end;
$$;
