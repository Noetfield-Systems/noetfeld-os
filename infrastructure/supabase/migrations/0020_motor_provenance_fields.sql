-- 0020_motor_provenance_fields.sql
-- NF-NOOS-MOTOR-V1-FULL-RUNWAY, Phase 4b — provenance-aware evidence model.
--
-- ADDITIVE + BACKWARD-COMPATIBLE. Adds nullable provenance columns to the
-- authoritative completion table so organic liveness can be told apart from
-- repair/replay/manual freshness at the SOURCE, not just inferred from
-- runner_output JSON. No column is dropped or renamed; existing rows keep
-- working. Historical rows are NOT rewritten — unknown provenance backfills to
-- 'legacy_unknown' (never guessed as organic).
--
-- L5 / FOUNDER GATE: applying a Supabase migration is a verifier-freeze /
-- schema (T3-class) change and is founder-gated. This file is delivered
-- READY-TO-APPLY but is NOT applied by the machine. Apply with:
--     make supabase-migrate   (or the repo's canonical migration runner)
-- after founder approval. It is written idempotently (IF NOT EXISTS) so a
-- re-run is safe.

BEGIN;

-- Deterministic execution-contract columns (directive Phase 4 field set).
ALTER TABLE IF EXISTS public.noetfield_factory_cycle_runs
  ADD COLUMN IF NOT EXISTS execution_id      text,
  ADD COLUMN IF NOT EXISTS attempt_id        text,
  ADD COLUMN IF NOT EXISTS correlation_id    text,
  ADD COLUMN IF NOT EXISTS dispatch_id       text,
  ADD COLUMN IF NOT EXISTS idempotency_key   text,
  ADD COLUMN IF NOT EXISTS producer          text,
  -- receipt_origin: organic | repair | replay | manual | migration | test | legacy_unknown
  ADD COLUMN IF NOT EXISTS receipt_origin    text,
  ADD COLUMN IF NOT EXISTS workflow_version  text,
  ADD COLUMN IF NOT EXISTS schema_version    text,
  ADD COLUMN IF NOT EXISTS input_hash        text,
  ADD COLUMN IF NOT EXISTS output_hash       text,
  ADD COLUMN IF NOT EXISTS artifact_uri      text,
  ADD COLUMN IF NOT EXISTS error_code        text,
  ADD COLUMN IF NOT EXISTS error_summary     text;

-- Backfill receipt_origin from the existing runner_output.cloud_trigger, ONLY
-- where truthfully determinable. Everything else stays NULL / legacy_unknown.
UPDATE public.noetfield_factory_cycle_runs
   SET receipt_origin = CASE
     WHEN runner_output->>'cloud_trigger' = 'http_loop' THEN 'organic'
     WHEN runner_output->>'cloud_trigger' IN ('noos_integrator_repair','noos_motor_receipt_writer_repair') THEN 'repair'
     WHEN runner_output->>'cloud_trigger' ILIKE '%replay%' THEN 'replay'
     WHEN runner_output->>'cloud_trigger' IS NULL THEN 'legacy_unknown'
     ELSE 'legacy_unknown'
   END
 WHERE receipt_origin IS NULL;

-- Indexes that make the organic-only liveness query cheap.
CREATE INDEX IF NOT EXISTS idx_factory_cycle_runs_receipt_origin
  ON public.noetfield_factory_cycle_runs (factory_id, receipt_origin, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_factory_cycle_runs_execution_id
  ON public.noetfield_factory_cycle_runs (execution_id);

COMMIT;

-- ROLLBACK (reversible): the added columns are nullable and additive; to revert
--   ALTER TABLE public.noetfield_factory_cycle_runs
--     DROP COLUMN IF EXISTS execution_id, DROP COLUMN IF EXISTS attempt_id,
--     DROP COLUMN IF EXISTS correlation_id, DROP COLUMN IF EXISTS dispatch_id,
--     DROP COLUMN IF EXISTS idempotency_key, DROP COLUMN IF EXISTS producer,
--     DROP COLUMN IF EXISTS receipt_origin, DROP COLUMN IF EXISTS workflow_version,
--     DROP COLUMN IF EXISTS schema_version, DROP COLUMN IF EXISTS input_hash,
--     DROP COLUMN IF EXISTS output_hash, DROP COLUMN IF EXISTS artifact_uri,
--     DROP COLUMN IF EXISTS error_code, DROP COLUMN IF EXISTS error_summary;
--   DROP INDEX IF EXISTS idx_factory_cycle_runs_receipt_origin;
--   DROP INDEX IF EXISTS idx_factory_cycle_runs_execution_id;
