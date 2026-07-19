# NOOS Motor v1 — Operational Runbook

Deterministic workflow execution with verifiable **organic** completion
evidence, recovery, and auditable outputs.

This runbook covers day-to-day operation: health checks, reading the liveness
states, the route each state takes, migration and cloud-producer deploy/rollback,
backup/restore, and incident escalation. Every cloud or deploy step is marked
**EXTERNAL_ACTIVATION_REQUIRED** — it needs cloud credentials that are not
present on the build host (real secrets live in `~/.noetfield-platform-secrets/`,
outside the repo) and is founder-gated.

The offline reference executor (`scripts/noos_motor_local_executor_v1.py`) is
stdlib-only and fully offline; none of its commands require activation.

---

## 1. Health checks

Local, no network:

```
./bin/noos verify        # deterministic self-verification (3 local cycles + masking regression)
./bin/noos demo          # representative customer input -> real output artifact
./bin/noos status <execution_id>   # retrieve status + provenance + integrity (output_hash)
python3 scripts/noos_motor_local_executor_v1.py --input docs/product/samples/sample-input.json --json
```

Live cockpit projection (reads the authoritative store when creds are present;
otherwise reports evidence-insufficient rather than failing):

```
python3 scripts/autorun_status_v1.py     # prints the dashboard JSON; exits non-zero on a critical finding
```

`autorun_status_v1.py` now passes provenance to the classifier
(`scripts/noos_observability_semantics_v1.py`), so the organic-vs-repair split is
rendered in every projection.

Cloud end-to-end (**EXTERNAL_ACTIVATION_REQUIRED**):

```
make cloud-motor-e2e     # CF motor -> Railway executor -> liveness -> deadman
```

---

## 2. Reading the liveness states

Classification comes from two **independent** freshness signals — the dispatch
heartbeat (`noos_loop_registry.last_fired_at`) and the per-loop completion
receipt (`noetfield_factory_cycle_runs.recorded_at`) — plus **completion
provenance**. Nothing is collapsed; the cockpit shows each signal separately.

### RUNNING_CONFIRMED vs DEGRADED_REPAIR_SUSTAINED (the false-green fix)

The completion classifier used to key on receipt **age only**. Repair-labeled
rows (`cloud_trigger=noos_integrator_repair`) kept the newest row fresh, so it
reported **RUNNING_CONFIRMED** while the organic cloud producer
(`cloud_trigger=http_loop`) had been stalled since **2026-07-12T13:50:49Z**.

The classifier is now **provenance-aware** (`derive_completion_provenance`,
`normalize_receipt_origin`, `classify_loop_state`):

- **RUNNING_CONFIRMED requires FRESH ORGANIC completion evidence.** A repair /
  replay / manual / migration / test completion, however fresh by age, can
  **never** promote a loop to RUNNING_CONFIRMED.
- A fresh **repair** row while the organic producer is stalled classifies as
  **DEGRADED_REPAIR_SUSTAINED** — it never confirms.
- No trustworthy organic sample is reported as `success_rate: null` with
  `evidence_state: INSUFFICIENT_RECENT_EVIDENCE`, **never** as a fabricated `0.0`.

Provenance origins recognized: `organic`, `repair`, `replay`, `manual`,
`migration`, `test`, `legacy_unknown`. Only `organic` satisfies the confirm gate;
unknown provenance is never guessed as organic.

### State → meaning → route

| State | Meaning | success_rate | Route | Auto-restart? |
|---|---|---|---|---|
| `RUNNING_CONFIRMED` | Dispatch fresh **and** fresh organic completion | `1.0` | (none) | n/a |
| `DEGRADED_REPAIR_SUSTAINED` | Repair rows keep the row fresh; organic producer stalled | `null` | `organic_producer_reconcile_escalation` | **No — escalate** |
| `COMPLETION_UNPROVEN` | Dispatch fresh, no fresh organic proof, no repair masking | `null` | `organic_producer_reconcile_escalation` | **No — escalate** |
| `EVIDENCE_INCONSISTENT` | Signals disagree / consistency check failed | `null` | `observer_reconciliation` | No |
| `STOPPED_OR_IDLE` | Inactivity expected by configuration | `null` | (none) | No |
| `DISPATCHING_COMPLETION_UNPROVEN` (legacy) | Dispatch fresh, completion receipt stale | `null` | `receipt_writer_completion_evidence_repair` | No |
| `OBSERVER_DIVERGENCE_OR_REPLAY` (legacy) | Completion fresh, dispatch stale | `null` | `observer_reconciliation` | No |
| `LOOP_EXECUTION_STALE` (legacy) | Both signals confirm real execution staleness | `0.0` | `execution_reconcile_self_heal` | Yes (self-heal) |
| `OBSERVER_UNAVAILABLE` (legacy) | An authoritative source could not be read | `null` | `monitoring_availability` | No |

**Design law:** only `execution_reconcile_self_heal` may trigger an execution
restart / redeploy from the machine. The organic-producer-escalation route
deliberately does **not** loop back to receipt-writer repair — that loop-back is
exactly what masked the 2026-07-12 stall.

---

## 3. The organic cloud chain (production)

**EXTERNAL_ACTIVATION_REQUIRED** to run end-to-end:

```
Cloudflare cron worker  noos-loop-fleet-tick-v1  (*/5)  POST /loop
  -> Railway executor    noos-loop-runner
  -> run_noetfield_factory_loop_v1.py --once   (env GITHUB_EVENT_NAME=http_loop)
  -> Supabase table      noetfield_factory_cycle_runs
  -> autorun_status_v1.py projection
  -> classifier          (noos_observability_semantics_v1.py)
```

Authoritative store: **Supabase `noetfield_factory_cycle_runs`** (plus
`noos_loop_registry` dispatch heartbeat). All projections and mirrors are read
replicas — never a source of truth.

---

## 4. Migration 0020 — apply and rollback

`infrastructure/supabase/migrations/0020_motor_provenance_fields.sql` adds
nullable, additive provenance columns (`execution_id`, `attempt_id`,
`correlation_id`, `dispatch_id`, `idempotency_key`, `producer`, `receipt_origin`,
`workflow_version`, `schema_version`, `input_hash`, `output_hash`, `artifact_uri`,
`error_code`, `error_summary`) and backfills `receipt_origin` only where truthfully
determinable (unknown → `legacy_unknown`). It is **not applied by the machine**.

Apply (**EXTERNAL_ACTIVATION_REQUIRED**; founder / L5 schema gate):

```
make supabase-migrate MIGRATION=0020
```

The file is written idempotently (`IF NOT EXISTS`), so a re-run is safe.

Rollback (reversible — columns are additive/nullable): run the `DROP COLUMN`
block at the foot of the same SQL file (also drops
`idx_factory_cycle_runs_receipt_origin` and `idx_factory_cycle_runs_execution_id`).

---

## 5. Cloud producer — deploy and rollback

All steps below are **EXTERNAL_ACTIVATION_REQUIRED** (cloud creds not on the
build host; deploy is founder-gated).

Deploy / restart the Railway loop-runner (the `http_loop` executor):

```
make deploy-railway-loop-runner
```

Verify after deploy:

```
make cloud-motor-e2e
```

Rollback:

- **Code:** `git log --oneline | grep NF-NOOS-MOTOR-V1` then `git revert <commit>`
  on the branch only — **no main merge was performed**.
- **Migration:** `0020` is additive/nullable; run its `DROP COLUMN` block (§4).

`./bin/noos rollback` prints these tested commands.

---

## 6. Backup / restore

- **Source of truth:** Supabase `noetfield_factory_cycle_runs` (+
  `noos_loop_registry`). Back up and restore truth here; then re-run
  `autorun_status_v1.py` to re-project. Restoring a mirror never restores truth —
  mirrors are read replicas.
- **Local executor artifacts** are file-backed under `receipts/runway/`
  (`executions/<id>.receipt.json`, `artifacts/<id>.output.json`,
  `artifacts/<id>.report.md`). Each receipt carries an `output_hash`; retrieval
  (`./bin/noos status <id>`) recomputes it and reports `output_integrity_ok`, so
  a restored artifact is integrity-checkable.
- **Secrets are never in the repo.** Real secrets live in
  `~/.noetfield-platform-secrets/`; `.env.example` is a config reference with no
  secrets and the local executor needs none.

---

## 7. Reliability model (operator reference)

- **Idempotency:** same `task_kind` + input ⇒ one logical run (dedupe returns the
  existing terminal run rather than executing a duplicate).
- **Lease:** owner + expiry + deterministic reclaim.
- **Backoff:** bounded exponential, `base 5s * 2^retry`, capped `900s`;
  `max_retries` default `3`.
- **Dead-letter:** a real, inspectable and replayable terminal state.
- **Replay:** creates a **new** attempt preserving `root_execution_id` +
  `correlation_id` lineage.
- **Repair never rewrites organic provenance.**

Lifecycle: `ACCEPTED -> PLANNED -> DISPATCHED -> CLAIMED -> RUNNING ->
OUTPUT_COMMITTED -> COMPLETED`; terminals `FAILED / TIMED_OUT / CANCELLED /
DEAD_LETTERED`; recovery `RETRY_SCHEDULED / REPLAY_REQUESTED / REPAIR_APPLIED`.

---

## 8. Incident escalation — organic producer stall

When the projection shows **DEGRADED_REPAIR_SUSTAINED** or **COMPLETION_UNPROVEN**
(route `organic_producer_reconcile_escalation`):

1. **Do not auto-restart.** This route does not permit execution mutation and
   does not loop back to receipt-writer repair. Restarting the cloud `http_loop`
   producer is **EXTERNAL_ACTIVATION_REQUIRED** and founder-gated.
2. **Surface and escalate** the stall (organic producer down while the
   sink/writer is healthy and repair rows keep landing). Confirm the split in the
   projection: `organic_completion_fresh: false`, `repair_sustained_fresh: true`.
3. **Founder-gated remediation** (each step **EXTERNAL_ACTIVATION_REQUIRED**,
   needs cloud creds not on the build host):
   - Restart the cloud `http_loop` producer (`make deploy-railway-loop-runner`,
     then `make cloud-motor-e2e`).
   - If not yet applied, apply Supabase migration `0020`
     (`make supabase-migrate MIGRATION=0020`).
   - Run **3 consecutive real cloud organic `http_loop` cycles** and confirm the
     projection returns to `RUNNING_CONFIRMED` on **organic** evidence.
4. Non-founder failures route to the scheduled loops (`make machine-reconcile`),
   never to the founder by default.

Deploy, merge to main, spend, external/commercial sends, and schema/L5 changes
remain founder-gated.

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
