# NOOS Motor v1 — Troubleshooting

NOOS Motor v1 — deterministic workflow execution with verifiable organic
completion evidence, recovery, and auditable outputs.

This guide maps a **symptom → cause → action**, and gives the **exact command**
to inspect each case. Two inspection surfaces are referenced throughout:

- **Cockpit projection** — `python3 scripts/autorun_status_v1.py`
  Prints the JSON dashboard and passes provenance to the classifier
  (`scripts/noos_observability_semantics_v1.py`). Read-only. Exits non-zero on a
  critical finding. Each loop carries `execution_state`, `evidence_state`,
  `route`, and a `provenance` block that splits **organic** from **repair**
  freshness.
- **Execution retrieval** — `./bin/noos status <execution_id>`
  (equivalent: `python3 scripts/noos_motor_local_executor_v1.py --status <execution_id> --json`).
  Returns `status`, `output_integrity_ok`, `artifact_uri`, the receipt, and the
  output.

Key design law (do not regress): `RUNNING_CONFIRMED` requires **fresh ORGANIC
completion evidence**. A repair/replay/manual completion — however fresh by age —
can never promote a loop to `RUNNING_CONFIRMED`. No stale/absent sample is ever
reported as `success_rate=0.0`; it is `None` with
`evidence_state=INSUFFICIENT_RECENT_EVIDENCE`.

## Fast triage

| Symptom | State | Inspect with | Action |
|---|---|---|---|
| (a) Cockpit shows `DEGRADED_REPAIR_SUSTAINED` | repair masking a stalled organic producer | `python3 scripts/autorun_status_v1.py` | Escalate; **do not auto-restart** |
| (b) Cockpit shows `COMPLETION_UNPROVEN` | dispatch fresh, no fresh organic proof | `python3 scripts/autorun_status_v1.py` | Escalate to organic-producer reconcile |
| (c) Cockpit shows `EVIDENCE_INCONSISTENT` | observations disagree | `python3 scripts/autorun_status_v1.py` | Reconcile observers vs authoritative store |
| (d) `output_integrity_ok: false` | tampered/corrupt artifact | `./bin/noos status <execution_id>` | Distrust artifact; replay |
| (e) Invalid input → `FAILED` | validation rejected the job | `python3 scripts/noos_motor_local_executor_v1.py --input <job.json> --json` | Fix input to the contract, resubmit |
| (f) Duplicate submit `deduplicated: true` | idempotency dedupe (expected) | same `--input … --json` run | None — change input to force a new run |
| (g) `./bin/noos verify` exits non-zero | a verify check failed | `python3 scripts/noos_motor_v1_verify_v1.py --json` | Fix the system, never the test (L5) |

---

## (a) Cockpit shows `DEGRADED_REPAIR_SUSTAINED`

**Cause.** The newest completion row keeping the loop "fresh" is a **repair** row
(`cloud_trigger=noos_integrator_repair` or `noos_motor_receipt_writer_repair`),
while there is **no fresh ORGANIC (`http_loop`) completion**. The organic cloud
producer is stalled. This is the exact class that previously produced a false
`RUNNING_CONFIRMED`: the old classifier keyed on receipt **age** only, so the
newest repair row read as fresh while the organic producer had been stalled since
`2026-07-12T13:50:49Z`. The classifier is now provenance-aware and reports the
honest state.

- `route`: `organic_producer_reconcile_escalation`
- `route_permits_execution_mutation`: `false`
- `success_rate`: `None` (`evidence_state=INSUFFICIENT_RECENT_EVIDENCE`)

**Inspect.**

```
python3 scripts/autorun_status_v1.py
```

Read the loop's `provenance` block: `completion_origin` will be a repair origin,
`organic_completion_fresh: false`, `repair_sustained_fresh: true`, plus
`last_organic_completion_at`, `repair_receipt_age_minutes`, and
`repair_receipts_since_last_organic`.

**Action.** Escalate and surface. **Do not auto-restart.** The route deliberately
does not loop back to receipt-writer repair (that is what masked the stall). The
machine must not restart the cloud runner: restarting the cloud `http_loop`
producer is **EXTERNAL_ACTIVATION_REQUIRED** (founder-gated, off-host, needs cloud
creds not on the build host). After restart, run **3 consecutive real cloud
organic `http_loop` cycles** (also EXTERNAL_ACTIVATION_REQUIRED) to return to
`RUNNING_CONFIRMED`.

---

## (b) Cockpit shows `COMPLETION_UNPROVEN`

**Cause.** The dispatch heartbeat is fresh, but there is **no fresh organic
completion and no fresh repair row** either — the organic completion is simply
unproven (not a confirmed run, not a confirmed stall, not repair-masked).

- `route`: `organic_producer_reconcile_escalation`
- `success_rate`: `None` (never a fabricated `0.0`)
- `evidence_state`: `INSUFFICIENT_RECENT_EVIDENCE`

**Inspect.**

```
python3 scripts/autorun_status_v1.py
```

In `presentation`: `dispatch_freshness=FRESH`,
`completion_evidence_freshness=STALE`, and `organic_completion_fresh` is
`false`/`null` with `repair_sustained_fresh: false`.

**Action.** Route to organic-producer reconcile/escalation. Do not treat as a
success and do not treat as a hard execution failure. Confirm whether the cloud
producer is emitting `http_loop` cycles into
`noetfield_factory_cycle_runs`; restarting it is **EXTERNAL_ACTIVATION_REQUIRED**.

---

## (c) Cockpit shows `EVIDENCE_INCONSISTENT`

**Cause.** The provenance signals were supplied with `consistency_ok=false`: the
two authoritative observations (dispatch heartbeat and completion receipts)
disagree in a way that cannot be reconciled to a single truthful state.

- `route`: `observer_reconciliation`
- `success_rate`: `None`; `observation_confidence`: `LOW`

**Inspect.**

```
python3 scripts/autorun_status_v1.py
```

Read the `presentation` block (dispatch vs completion freshness shown separately)
and `provenance.consistency_ok: false`.

**Action.** Reconcile the observers. The **authoritative store** is Supabase
`noetfield_factory_cycle_runs` (plus the `noos_loop_registry` dispatch
heartbeat); projections/mirrors are read replicas. Trust the authoritative store
over any mirror when they diverge.

---

## (d) `output_integrity_ok: false`

**Cause.** On retrieval, the recomputed hash of the stored JSON artifact does not
match the receipt's `output_hash` — the artifact was **tampered with or
corrupted** after commit. (`output_integrity_ok: null` means there is no output
artifact present to check, not a mismatch.)

**Inspect.**

```
./bin/noos status <execution_id>
```

or

```
python3 scripts/noos_motor_local_executor_v1.py --status <execution_id> --json
```

Read `output_integrity_ok` and compare `output_hash` in the receipt against the
artifact at `artifact_uri`.

**Action.** Do not trust the artifact. The receipt `output_hash` is the source of
truth. Regenerate a fresh, integrity-checked artifact via **replay** — replay
creates a **new attempt** that preserves the `root_execution_id` and
`correlation_id` lineage; it does not rewrite organic provenance.

---

## (e) Invalid input → `FAILED`

**Cause.** `validate_input` rejected the job **before any plan or dispatch**, so
the execution fails truthfully with `error_code=invalid_input` and **no artifact
is written**. Triggers: `task_kind` not `digest`; a `digest` job whose `records`
is missing, empty, or not a list; any record that is not a JSON object; or an
input that is not a JSON object.

**Inspect.**

```
python3 scripts/noos_motor_local_executor_v1.py --input <job.json> --json
```

The result shows `"status": "FAILED"` and a populated `validation_errors[]`. For a
prior run: `./bin/noos status <execution_id>` → `status: FAILED`.

**Action.** Fix the input to satisfy the input contract and resubmit:

```json
{"task_kind": "digest", "title": "...", "records": [{ ... }, ...]}
```

Reference sample: `docs/product/samples/sample-input.json`.

---

## (f) Duplicate submit `deduplicated: true`

**Cause.** Idempotency-key dedupe: the same `task_kind` + input already ran, so
the ledger returns the **existing terminal run** instead of executing a duplicate
logical job. This is expected behavior, not an error.

**Inspect.**

```
python3 scripts/noos_motor_local_executor_v1.py --input <job.json> --json
```

Look for `"deduplicated": true`; the returned `execution_id`, `status`, and
`artifact_uri` are those of the original run.

**Action.** None required. To force a new logical run, change the input (e.g.
`title` or `records`) so the idempotency key differs. Retrieve the original run's
output with `./bin/noos status <execution_id>`.

---

## (g) `./bin/noos verify` exits non-zero

**Cause.** One of the three verification checks failed:

1. `local_organic_cycles` — three consecutive local organic cycles must each
   produce a real, retrievable, integrity-checked artifact with a valid
   lifecycle and unique `execution_id`s (`consecutive_pass`).
2. `masking_regression` — a fresh repair receipt must classify as
   `DEGRADED_REPAIR_SUSTAINED` (never `RUNNING_CONFIRMED`), and restoring organic
   evidence must return `RUNNING_CONFIRMED`.
3. `truthful_failure` — deliberately invalid input must end `FAILED` with no
   artifact.

**Inspect.**

```
./bin/noos verify
```

prints `[OK]`/`[FAIL]` per check and an `OVERALL` line. For per-check detail:

```
python3 scripts/noos_motor_v1_verify_v1.py --json
```

Read `checks[].ok` / `checks[].consecutive_pass` to see which check failed.

**Action.** A failing check means the **system** is broken — diagnose and repair
the underlying component (`noos_motor_local_executor_v1.py`,
`noos_observability_semantics_v1.py`, or `noos_motor_state_machine_v1.py`). Under
the verifier freeze (L5), **fix the system, never weaken the test**; do not edit
`scripts/verify_*` or the verification script to make it pass.

---

## Cloud activation notes (EXTERNAL_ACTIVATION_REQUIRED)

These steps need cloud credentials that are **not** on the build host (real
secrets live in `~/.noetfield-platform-secrets/`, outside the repo). The local
reference executor is stdlib-only and fully offline; deploy/migrate/spend are
founder-gated.

- **Restart the cloud `http_loop` producer.** Organic chain:
  Cloudflare cron worker `noos-loop-fleet-tick-v1` (`*/5`) POSTs `/loop` →
  Railway executor `noos-loop-runner` →
  `run_noetfield_factory_loop_v1.py --once` (env `GITHUB_EVENT_NAME=http_loop`) →
  Supabase `noetfield_factory_cycle_runs` → `autorun_status_v1.py` → classifier.
- **Apply Supabase migration `0020`** (`make supabase-migrate`) — additive
  provenance columns in `infrastructure/supabase/migrations/0020_motor_provenance_fields.sql`;
  NOT applied (founder/L5-gated).
- **Run 3 consecutive real cloud organic `http_loop` cycles** to clear
  `DEGRADED_REPAIR_SUSTAINED` / `COMPLETION_UNPROVEN` back to
  `RUNNING_CONFIRMED`.

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
