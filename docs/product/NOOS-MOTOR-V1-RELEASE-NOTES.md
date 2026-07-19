# NOOS Motor v1 — Release Notes (v1.0.0)

**NOOS Motor v1** — deterministic workflow execution with verifiable organic
completion evidence, recovery, and auditable outputs.

This is a **built** release, not a deployed one. Everything below that touches
cloud producers, the authoritative Supabase store, or migrations is marked
`EXTERNAL_ACTIVATION_REQUIRED` and is founder / L5-gated.

Release manifest schema: `noos-motor-v1-release-manifest-v1`
(build via `./bin/noos package`).

---

## The fix that motivated this release

The completion classifier keyed on receipt **age only**. Repair-labeled rows
(`cloud_trigger=noos_integrator_repair`) kept the newest row fresh, so the
classifier reported a false `RUNNING_CONFIRMED` while the organic cloud producer
(`cloud_trigger=http_loop`) had been stalled since **2026-07-12T13:50:49Z**.

The classifier is now **provenance-aware**:

- `RUNNING_CONFIRMED` requires **fresh ORGANIC** evidence.
- Repair rows classify as `DEGRADED_REPAIR_SUSTAINED` and **never** confirm.
- Repair never rewrites organic provenance.

---

## What shipped

- **Provenance-aware classifier** — `scripts/noos_observability_semantics_v1.py`
  (`classify_loop_state`, `normalize_receipt_origin`,
  `derive_completion_provenance`). Provenance origins: `organic`, `repair`,
  `replay`, `manual`, `migration`, `test`, `legacy_unknown`.
- **Cockpit projection wired to provenance** — `scripts/autorun_status_v1.py`
  now passes provenance through to the classifier.
- **Deterministic lifecycle FSM + invariants (pure)** —
  `scripts/noos_motor_state_machine_v1.py`.
- **Offline reference executor (the sellable vertical slice; no cloud)** —
  `scripts/noos_motor_local_executor_v1.py`.
- **Canonical verification** — `scripts/noos_motor_v1_verify_v1.py`.
- **Release packager** — `scripts/noos_motor_v1_package_v1.py` (manifest +
  `tar.gz` bundle).
- **CLI** — `bin/noos`: `install | start | status <id> | demo | verify |
  package | rollback`.
- **Additive provenance migration (NOT applied; founder/L5-gated)** —
  `infrastructure/supabase/migrations/0020_motor_provenance_fields.sql`.
- **Config reference (no secrets; local executor needs none)** — `.env.example`.

### Lifecycle states

`ACCEPTED → PLANNED → DISPATCHED → CLAIMED → RUNNING → OUTPUT_COMMITTED →
COMPLETED`
Terminals: `FAILED`, `TIMED_OUT`, `CANCELLED`, `DEAD_LETTERED`.
Recovery: `RETRY_SCHEDULED`, `REPLAY_REQUESTED`, `REPAIR_APPLIED`.

### Health / liveness states

`RUNNING_CONFIRMED`, `DEGRADED_REPAIR_SUSTAINED`, `COMPLETION_UNPROVEN`,
`EVIDENCE_INCONSISTENT`, `STOPPED_OR_IDLE`
(legacy: `DISPATCHING_COMPLETION_UNPROVEN`, `OBSERVER_DIVERGENCE_OR_REPLAY`,
`LOOP_EXECUTION_STALE`, `OBSERVER_UNAVAILABLE`).

### Reliability model

- Idempotency-key dedupe: same `task_kind` + input ⇒ one logical run.
- Lease has owner + expiry + deterministic reclaim.
- Bounded exponential backoff: `base 5s * 2^retry`, capped at `900s`;
  `max_retries` default `3`.
- Dead-letter is a real, inspectable, replayable terminal.
- Replay creates a **new attempt** preserving `root_execution_id` +
  `correlation_id` lineage.
- Repair never rewrites organic provenance.

### Contracts

- **Input (digest task):**
  `{"task_kind":"digest","title":"...","records":[{...},...]}`
  (sample: `docs/product/samples/sample-input.json`).
- **Output:** a normalized JSON artifact + a Markdown report + a lifecycle
  receipt carrying `output_hash` (integrity-checkable on retrieval).
- **Receipt fields:** `execution_id`, `attempt_id`, `correlation_id`,
  `dispatch_id`, `idempotency_key`, `producer`, `receipt_origin`,
  `execution_plane`, `workflow_version`, `schema_version`, `state`,
  `input_hash`, `output_hash`, `artifact_uri`, `error_code`, `error_summary`,
  `created_at`, `updated_at`, `history[]`.

---

## Release manifest contents (summary)

`./bin/noos package` writes `noos-motor-v1-release-manifest.json` and a
`noos-motor-v1-1.0.0.tar.gz` bundle. Key version fields:

| Field | Value |
|---|---|
| `product_version` | `1.0.0` |
| `schema_version` | `noos-motor-execution-v1` |
| `workflow_version` | `noos-motor-v1` |
| `migration_version` | `0020_motor_provenance_fields` |

The manifest also records `git_commit`, `build_time`, per-component SHA-256
checksums, the bundle SHA-256, the `external_activation_required` list, and the
tested rollback instructions. The manifest describes a **built artifact only —
not a deployment claim**.

---

## Verified offline (deterministic, no cloud)

Run with `./bin/noos verify` (`scripts/noos_motor_v1_verify_v1.py`). It exercises
the OFFLINE organic path and exits non-zero on any failure:

1. **3 consecutive LOCAL reference organic cycles** — each produces a real,
   retrievable, integrity-checked output artifact with a valid lifecycle and
   unique `execution_id`.
2. **Masking regression** — a fresh repair receipt
   (`noos_integrator_repair`) must classify as `DEGRADED_REPAIR_SUSTAINED`
   (never `RUNNING_CONFIRMED`); restoring organic (`http_loop`) evidence returns
   `RUNNING_CONFIRMED`.
3. **Truthful failure path** — deliberate invalid input (empty `records`) fails
   as `FAILED` and produces **no artifact**.

These verify the `local_reference` execution plane only. The verifier never uses
a repair-generated receipt as proof of organic execution and does not fabricate
cloud `http_loop` cycles.

---

## EXTERNAL_ACTIVATION_REQUIRED (not done in this release)

These need cloud credentials that are not on the build host and are
founder / L5-gated:

- **EXTERNAL_ACTIVATION_REQUIRED** — Restart the cloud `http_loop` producer
  (Railway `noos-loop-runner`).
- **EXTERNAL_ACTIVATION_REQUIRED** — Apply Supabase migration `0020`
  (`make supabase-migrate`). It is additive/nullable and delivered
  ready-to-apply, but is **not** applied by the machine.
- **EXTERNAL_ACTIVATION_REQUIRED** — Run **3 consecutive real cloud organic
  `http_loop` cycles** to confirm production liveness.

Production organic chain (for reference, all
`EXTERNAL_ACTIVATION_REQUIRED` to run):
Cloudflare cron worker `noos-loop-fleet-tick-v1` (`*/5`) `POST /loop` →
Railway executor `noos-loop-runner` →
`run_noetfield_factory_loop_v1.py --once` (env `GITHUB_EVENT_NAME=http_loop`) →
Supabase table `noetfield_factory_cycle_runs` →
`autorun_status_v1.py` projection → classifier.

**Authoritative store:** Supabase `noetfield_factory_cycle_runs` (+
`noos_loop_registry` dispatch heartbeat). Projections / mirrors are read
replicas.

---

## Known non-critical limitations

- The cloud organic 3-cycle confirmation and the classifier's production
  `RUNNING_CONFIRMED` are **not** demonstrable on the build host — they depend on
  the `EXTERNAL_ACTIVATION_REQUIRED` steps above.
- Migration `0020` is delivered ready-to-apply but **unapplied**; the authoritative
  store does not yet carry the additive provenance columns until a founder applies it.
- Historical rows are **not** rewritten by `0020` — rows with undeterminable
  provenance backfill to `legacy_unknown` (never guessed as organic).
- The sellable slice is the **offline** `local_reference` executor
  (stdlib-only); it is not a cloud service.
- No merge to `main` was performed; rollback is `git revert` of the motor
  commits on this branch, and the additive migration is reversed by the
  `DROP COLUMN IF EXISTS` block at the foot of the `.sql`.

---

## Security boundary

- No secrets committed. Real secrets live in `~/.noetfield-platform-secrets/`
  (outside the repo).
- The local executor is stdlib-only and fully offline.
- Deploy, migrate, spend, and commercial sends are founder-gated.

---

## Commands

```
./bin/noos demo         # run the representative customer input -> real output
./bin/noos verify       # 3 local cycles + masking regression + failure path
./bin/noos package      # build the versioned release bundle + manifest
./bin/noos status <execution_id>
python3 scripts/noos_motor_local_executor_v1.py --input docs/product/samples/sample-input.json --json
```

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
