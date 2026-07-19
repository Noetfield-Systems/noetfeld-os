# NOOS Motor v1

**NOOS Motor v1 — deterministic workflow execution with verifiable organic
completion evidence, recovery, and auditable outputs.**

---

## Product promise

The Motor runs a workflow through an explicit, deterministic lifecycle and
proves the run happened with organic completion evidence — not with a fresh row
of unknown origin. Every output is content-hashed and bound to the execution
that produced it, so completion is checkable, not asserted.

The offline reference path (`noos demo` / `noos verify`) runs today with no
cloud dependency. The production cloud organic chain is
`EXTERNAL_ACTIVATION_REQUIRED`.

## Customer problem

The completion classifier keyed on receipt **age only**. Repair-labeled rows
(`cloud_trigger=noos_integrator_repair`) kept the newest row fresh, so the
cockpit reported a false `RUNNING_CONFIRMED` while the organic cloud producer
(`cloud_trigger=http_loop`) had been stalled since `2026-07-12T13:50:49Z`. A
"green" liveness signal was being produced by the repair path masking a dead
producer.

The fix makes classification **provenance-aware**: `RUNNING_CONFIRMED` now
requires **fresh organic** evidence. Repair rows classify as
`DEGRADED_REPAIR_SUSTAINED` and can never confirm a run — however fresh they are
by age.

## Intended customer

Operators who run a scheduled/dispatched workflow and need a trustworthy answer
to "is it actually running, and did this job really complete?" — where a
repair, replay, or manual touch must never read as live organic execution.

## Supported use cases

- Run a workflow job through a deterministic lifecycle and retrieve a real,
  integrity-checkable output artifact plus a lifecycle receipt.
- Classify loop liveness with provenance separated from freshness (organic vs
  repair/replay/manual).
- Recover failed runs (retry with bounded backoff, dead-letter, replay) without
  losing lineage or rewriting provenance.
- Verify the whole offline path deterministically (`noos verify`) including the
  masking regression.
- The representative v1 task is `digest`: a deterministic normalized summary
  over a set of records.

## Exact v1 feature set

Offline-ready today (stdlib-only, no cloud):

- `scripts/noos_motor_state_machine_v1.py` — deterministic lifecycle FSM +
  enforced invariants (pure; clock injected).
- `scripts/noos_motor_local_executor_v1.py` — OFFLINE reference executor; the
  sellable vertical slice. Runs input → validate → plan → FSM → real artifact →
  receipt → retrieval → replay.
- `scripts/noos_observability_semantics_v1.py` — provenance-aware classifier
  (`classify_loop_state`, `normalize_receipt_origin`,
  `derive_completion_provenance`).
- `scripts/autorun_status_v1.py` — live cockpit projection (now passes
  provenance to the classifier).
- `scripts/noos_motor_v1_verify_v1.py` — canonical verification.
- `scripts/noos_motor_v1_package_v1.py` — release packager (manifest + `.tar.gz`
  bundle).
- `bin/noos` — CLI: `install | start | status <id> | demo | verify | package |
  rollback`.
- `.env.example` — config reference (no secrets; the local executor needs none).

Delivered but gated:

- `infrastructure/supabase/migrations/0020_motor_provenance_fields.sql` —
  additive, nullable provenance columns. **NOT applied; founder/L5-gated.**

## Input contract

Digest task input is a JSON object:

```json
{"task_kind": "digest", "title": "...", "records": [{...}, {...}]}
```

- `task_kind` must be `"digest"` (the only supported v1 task).
- `records` must be a non-empty list of JSON objects.
- Invalid input fails **truthfully** — validation rejects it before any
  plan/dispatch, and no artifact is written.

Sample: `docs/product/samples/sample-input.json`.

## Output contract

A completed run produces:

- A normalized **JSON artifact** (the deterministic digest).
- A human-readable **Markdown report**.
- A **lifecycle receipt** carrying `output_hash`, so output integrity is
  checkable on retrieval.

Receipt fields: `execution_id`, `attempt_id`, `correlation_id`, `dispatch_id`,
`idempotency_key`, `producer`, `receipt_origin`, `execution_plane`,
`workflow_version`, `schema_version`, `state`, `input_hash`, `output_hash`,
`artifact_uri`, `error_code`, `error_summary`, `created_at`, `updated_at`,
`history[]`.

## Reliability model

- **Idempotency-key dedupe** — same `task_kind` + input ⇒ one logical run; a
  duplicate submission returns the existing run.
- **Lease** — has an owner + expiry; an expired lease is reclaimed
  deterministically.
- **Bounded exponential backoff** — `base 5s * 2^retry`, capped at `900s`.
- **Retries** — `max_retries` default `3`; retry count is finite and visible.
- **Dead-letter** — a real terminal state that is inspectable and replayable.
- **Replay** — creates a NEW attempt while preserving `root_execution_id` +
  `correlation_id` lineage.
- Repair never rewrites organic provenance.

## Provenance model

Every completion carries a normalized origin: `organic`, `repair`, `replay`,
`manual`, `migration`, `test`, or `legacy_unknown` (unknown is never guessed as
organic).

Liveness states from the classifier:

- `RUNNING_CONFIRMED` — requires **fresh organic** evidence.
- `DEGRADED_REPAIR_SUSTAINED` — a repair row is keeping the row fresh; never
  confirms.
- `COMPLETION_UNPROVEN` — dispatch active, no fresh organic proof.
- `EVIDENCE_INCONSISTENT` — signals disagree.
- `STOPPED_OR_IDLE` — inactivity is expected by configuration.

Legacy states remain for the age-only path:
`DISPATCHING_COMPLETION_UNPROVEN`, `OBSERVER_DIVERGENCE_OR_REPLAY`,
`LOOP_EXECUTION_STALE`, `OBSERVER_UNAVAILABLE`. A missing or stale sample is
surfaced as insufficient evidence — never as a fabricated `success_rate` of
`0.0`.

## Recovery model

Lifecycle states:

```
ACCEPTED -> PLANNED -> DISPATCHED -> CLAIMED -> RUNNING
         -> OUTPUT_COMMITTED -> COMPLETED
```

- Terminals: `FAILED`, `TIMED_OUT`, `CANCELLED`, `DEAD_LETTERED`.
- Recovery: `RETRY_SCHEDULED`, `REPLAY_REQUESTED`, `REPAIR_APPLIED`.

A run cannot complete before it starts; a terminal run cannot return to
`RUNNING`; failure terminals may enter recovery, and replay re-enters via a new
attempt with lineage preserved.

## Deployment model

**Offline reference path (runs today, no cloud):**

```
./bin/noos demo
./bin/noos verify
./bin/noos package
./bin/noos status <execution_id>
python3 scripts/noos_motor_local_executor_v1.py \
  --input docs/product/samples/sample-input.json --json
```

**Cloud organic chain (production — `EXTERNAL_ACTIVATION_REQUIRED` to run):**

```
Cloudflare cron worker noos-loop-fleet-tick-v1 (*/5)
  -> POST /loop
  -> Railway executor noos-loop-runner
  -> run_noetfield_factory_loop_v1.py --once  (env GITHUB_EVENT_NAME=http_loop)
  -> Supabase table noetfield_factory_cycle_runs
  -> autorun_status_v1.py projection
  -> classifier
```

Authoritative store: Supabase `noetfield_factory_cycle_runs` (+
`noos_loop_registry` dispatch heartbeat). Projections/mirrors are read replicas.

**`EXTERNAL_ACTIVATION_REQUIRED`** (needs cloud creds not on the build host):

- `EXTERNAL_ACTIVATION_REQUIRED` — restart the cloud `http_loop` producer.
- `EXTERNAL_ACTIVATION_REQUIRED` — apply Supabase migration `0020`
  (`make supabase-migrate`); founder/L5-gated.
- `EXTERNAL_ACTIVATION_REQUIRED` — run 3 consecutive real cloud organic
  `http_loop` cycles.

## Current limitations

- The only supported v1 task is `digest`.
- The local executor is a **reference** path: real organic work, but it is not
  the cloud `http_loop` producer (`producer=noos-motor-local-executor-v1`,
  `execution_plane=local_reference`).
- Migration `0020` is delivered ready-to-apply but **not applied** — provenance
  columns are not yet live in the authoritative store until the founder-gated
  apply runs.
- Confirmed cloud organic liveness requires the 3 real `http_loop` cycles above,
  which are `EXTERNAL_ACTIVATION_REQUIRED`.

## Security boundaries

- No secrets committed. Real secrets live in `~/.noetfield-platform-secrets/`
  (outside the repo).
- The local executor is stdlib-only and fully offline.
- Deploy, migrate, spend, and commercial actions are founder-gated.

## Support boundary

- Supported today: the offline reference path and its deterministic
  verification.
- Not covered by the offline path: running the cloud producer, applying the
  migration, and the 3-cycle cloud confirmation — each is
  `EXTERNAL_ACTIVATION_REQUIRED` and founder-gated.

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
