-- 0021_software_repair_runway.sql
-- NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §4 — authoritative persistence for repair.
--
-- ADDITIVE + BACKWARD-COMPATIBLE. Creates the narrowest persistent schema for
-- the Software Repair product. Nothing existing is dropped or altered. Idempotent
-- (IF NOT EXISTS). Every table carries the deterministic execution contract so a
-- repair job's full lineage + provenance is queryable.
--
-- L5 / FOUNDER + PROTECTED-ENVIRONMENT GATE: applying a Supabase migration is a
-- schema (T3-class) change. This file is READY-TO-APPLY but is NOT applied by the
-- machine. Apply only via the gated workflow:
--     gh workflow run supabase-migrate-v1.yml -f migration=0021_software_repair_runway.sql
--   (the workflow targets the protected `production` environment => founder approval).

BEGIN;

CREATE TABLE IF NOT EXISTS public.repair_commissions (
  commission_id     text PRIMARY KEY,
  customer_id       text NOT NULL,
  repository        jsonb NOT NULL,
  failure           jsonb NOT NULL,
  recipe_id         text NOT NULL,
  recipe_version    text NOT NULL,
  constraints       jsonb,
  created_at        timestamptz NOT NULL DEFAULT now(),
  status            text NOT NULL DEFAULT 'accepted'
);

CREATE TABLE IF NOT EXISTS public.repair_jobs (
  job_id            text PRIMARY KEY,           -- == motor execution_id
  commission_id     text NOT NULL REFERENCES public.repair_commissions(commission_id),
  correlation_id    text NOT NULL,
  dispatch_id       text,
  idempotency_key   text NOT NULL,
  customer_id       text NOT NULL,
  repository_identity text,
  base_commit       text,
  target_branch     text,
  recipe_id         text NOT NULL,
  recipe_version    text NOT NULL,
  workflow_version  text NOT NULL,
  schema_version    text NOT NULL,
  model_provider    text,
  model_identifier  text,
  input_hash        text,
  patch_hash        text,
  output_bundle_hash text,
  producer          text NOT NULL,
  execution_plane   text NOT NULL,
  receipt_origin    text NOT NULL,              -- organic|local_reference|test|repair|replay|manual|migration|legacy_unknown
  lease_owner       text,
  retry_count       int NOT NULL DEFAULT 0,
  terminal_state    text,
  artifact_refs     jsonb,
  failure_classification text,
  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now(),
  UNIQUE (idempotency_key)
);

CREATE TABLE IF NOT EXISTS public.repair_attempts (
  attempt_id        text PRIMARY KEY,
  job_id            text NOT NULL REFERENCES public.repair_jobs(job_id),
  attempt_number    int NOT NULL,
  strategy          text,
  passed            boolean,
  created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.repair_lifecycle_events (
  id                bigserial PRIMARY KEY,
  job_id            text NOT NULL REFERENCES public.repair_jobs(job_id),
  state             text NOT NULL,
  note              text,
  at                timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.repair_leases (
  job_id            text PRIMARY KEY REFERENCES public.repair_jobs(job_id),
  owner             text NOT NULL,
  acquired_at       timestamptz NOT NULL,
  expires_at        timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS public.repair_idempotency (
  idempotency_key   text PRIMARY KEY,
  job_id            text NOT NULL REFERENCES public.repair_jobs(job_id),
  created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.repair_model_calls (
  id                bigserial PRIMARY KEY,
  job_id            text NOT NULL REFERENCES public.repair_jobs(job_id),
  provider          text NOT NULL,
  model             text,
  purpose           text,
  input_hash        text,
  output_hash       text,
  prompt_tokens     int,
  completion_tokens int,
  cost_usd          numeric,
  latency_ms        int,
  retries           int,
  schema_valid      boolean,
  ok                boolean,
  at                timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.repair_verifications (
  id                bigserial PRIMARY KEY,
  job_id            text NOT NULL REFERENCES public.repair_jobs(job_id),
  tests_before_exit int,
  tests_after_exit  int,
  passed            boolean,
  evidence          jsonb,
  at                timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.repair_artifacts (
  id                bigserial PRIMARY KEY,
  job_id            text NOT NULL REFERENCES public.repair_jobs(job_id),
  kind              text NOT NULL,              -- patch|report|bundle|draft_pr
  uri               text,
  sha256            text,
  at                timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.repair_dead_letters (
  job_id            text PRIMARY KEY REFERENCES public.repair_jobs(job_id),
  reason            text NOT NULL,
  at                timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.repair_replay_lineage (
  child_job_id      text PRIMARY KEY REFERENCES public.repair_jobs(job_id),
  parent_job_id     text NOT NULL,
  root_job_id       text NOT NULL,
  attempt_number    int NOT NULL,
  at                timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_repair_jobs_commission ON public.repair_jobs (commission_id);
CREATE INDEX IF NOT EXISTS idx_repair_jobs_origin ON public.repair_jobs (receipt_origin, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_repair_events_job ON public.repair_lifecycle_events (job_id, at);

COMMIT;

-- ROLLBACK (reversible): all objects are new; to revert,
--   DROP TABLE IF EXISTS public.repair_replay_lineage, public.repair_dead_letters,
--     public.repair_artifacts, public.repair_verifications, public.repair_model_calls,
--     public.repair_idempotency, public.repair_leases, public.repair_lifecycle_events,
--     public.repair_attempts, public.repair_jobs, public.repair_commissions CASCADE;
