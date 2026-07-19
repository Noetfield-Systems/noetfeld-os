# NOOS Motor v1 — Receipt & Evidence Schema Reference

Deterministic workflow execution with verifiable **organic** completion
evidence, recovery, and auditable outputs.

Every lifecycle transition emits a **receipt**: a self-describing record that
carries execution identity, provenance, integrity hashes, and state history. A
receipt is the unit of proof. Liveness is decided from the *provenance* of
completion receipts, not merely their age — a repair-labeled receipt, however
recent, can never stand in for organic liveness (see
[Why a repair row is not organic liveness](#why-a-repair-row-is-not-organic-liveness)).

- Authoritative store: Supabase `noetfield_factory_cycle_runs`
  (+ `noos_loop_registry` dispatch heartbeat). Projections and mirrors are
  read replicas.
- Classifier: `scripts/noos_observability_semantics_v1.py`
  (`normalize_receipt_origin`, `derive_completion_provenance`,
  `classify_loop_state`).
- Provenance columns: `infrastructure/supabase/migrations/0020_motor_provenance_fields.sql`
  (additive; **NOT applied** — founder/L5-gated).

---

## Receipt fields

All timestamps are ISO 8601 UTC. Migration 0020 declares each provenance column
as SQL `text` (see [Migration 0020 columns](#migration-0020-columns)).

| Field | Type | Meaning | Example |
|---|---|---|---|
| `execution_id` | string | Stable identity of one logical run. Shared by every attempt of that run; the reclaim/retry lineage anchor. | `"exec-digest-2026-07-17-0007"` |
| `attempt_id` | string | Identity of a single attempt within a run. A replay creates a **new** `attempt_id` under the same `execution_id`. | `"attempt-2"` |
| `correlation_id` | string | Cross-attempt lineage key. Preserved across retry/replay so an audit can join every record for the run. | `"corr-9f2a1c"` |
| `dispatch_id` | string | Identity of the dispatch that scheduled the run (ties the receipt back to the dispatch heartbeat row). | `"disp-2026-07-17-tick-3341"` |
| `idempotency_key` | string | Dedupe key derived from `task_kind` + input. Same key ⇒ one logical run (no duplicate execution). | `"digest:sha256:4b1e…"` |
| `producer` | string | The component that wrote the receipt (e.g. the offline reference executor, or the cloud runner). | `"noos-loop-runner"` |
| `receipt_origin` | enum | Normalized provenance origin. One of `organic`, `repair`, `replay`, `manual`, `migration`, `test`, `legacy_unknown`. Governs liveness. | `"organic"` |
| `execution_plane` | string | Where the run executed — the offline reference plane vs. the cloud organic chain. (Contract field; **not** part of migration 0020.) | `"cloud"` |
| `workflow_version` | string | Version of the workflow/pipeline definition that produced this receipt. | `"v1"` |
| `schema_version` | string | Version of the receipt schema itself, so readers can parse deterministically. | `"1"` |
| `state` | enum | Lifecycle state at the moment the receipt was written (see [Lifecycle states](#lifecycle-states)). | `"COMPLETED"` |
| `input_hash` | string | Content hash of the run input. Ties the receipt to exactly the input that was processed. | `"sha256:a1b2…"` |
| `output_hash` | string | Content hash of the produced artifact. Integrity-checkable on retrieval — recompute and compare. | `"sha256:c3d4…"` |
| `artifact_uri` | string | Locator for the normalized output artifact (JSON) and/or report. | `"artifacts/exec-…/output.json"` |
| `error_code` | string | Machine-readable failure code on a terminal error state; empty/null on success. | `"TIMEOUT"` |
| `error_summary` | string | Short human-readable failure description; empty/null on success. | `"lease expired before OUTPUT_COMMITTED"` |
| `created_at` | timestamp | When this receipt/attempt record was first written. | `"2026-07-17T13:50:49Z"` |
| `updated_at` | timestamp | When this record last changed state. | `"2026-07-17T13:51:04Z"` |
| `history[]` | array | Ordered append-only list of prior `{state, at}` transitions for this record — the auditable trail. | `[{"state":"RUNNING","at":"…"}, {"state":"OUTPUT_COMMITTED","at":"…"}]` |

> `execution_plane`, `state`, `created_at`, `updated_at`, and `history[]` are
> part of the receipt contract but are **not** among the columns added by
> migration 0020 — do not assume 0020 provisions them.

---

## Lifecycle states

Written into the receipt `state` field and appended to `history[]`.

- **Progression:** `ACCEPTED → PLANNED → DISPATCHED → CLAIMED → RUNNING →
  OUTPUT_COMMITTED → COMPLETED`
- **Terminals:** `FAILED`, `TIMED_OUT`, `CANCELLED`, `DEAD_LETTERED`
- **Recovery:** `RETRY_SCHEDULED`, `REPLAY_REQUESTED`, `REPAIR_APPLIED`

Dead-letter (`DEAD_LETTERED`) is a real, inspectable, replayable terminal. A
replay creates a **new** attempt that preserves `root_execution_id` +
`correlation_id` lineage; **repair never rewrites organic provenance**.

Lifecycle FSM + invariants: `scripts/noos_motor_state_machine_v1.py` (pure).

---

## Provenance origins

`receipt_origin` is normalized from the raw producer label (Supabase
`runner_output.cloud_trigger`, a top-level `cloud_trigger`, or an existing
`receipt_origin`) by `normalize_receipt_origin()`.

| Origin | Assigned when | Counts as organic liveness? |
|---|---|---|
| `organic` | raw label is `http_loop` (the genuine cloud producer) | **Yes** — the only value that can |
| `repair` | raw label is `noos_integrator_repair` or `noos_motor_receipt_writer_repair`, or contains `repair` | No |
| `replay` | raw label contains `replay` | No |
| `manual` | raw label is `manual` / `workflow_dispatch`, or contains `manual` | No |
| `migration` | raw label contains `migration` or `backfill` | No |
| `test` | raw label contains `test` | No |
| `legacy_unknown` | label is missing/empty, or unrecognized | **No — never guessed as organic** |

`is_organic_origin()` returns true **only** for `organic`. Every other origin —
including `legacy_unknown` — is treated as non-organic by construction.

---

## Migration 0020 columns

`infrastructure/supabase/migrations/0020_motor_provenance_fields.sql` is
**additive and backward-compatible**: it adds nullable columns to
`public.noetfield_factory_cycle_runs`, drops/renames nothing, and is written
idempotently (`IF NOT EXISTS`) so re-runs are safe.

**Applying it is EXTERNAL_ACTIVATION_REQUIRED** — a schema (T3-class) change
under verifier freeze / founder gate. It is delivered ready-to-apply but is
**not** applied by the machine. Apply with `make supabase-migrate` after founder
approval.

Columns added (all SQL `text`, all nullable):

`execution_id`, `attempt_id`, `correlation_id`, `dispatch_id`,
`idempotency_key`, `producer`, `receipt_origin`, `workflow_version`,
`schema_version`, `input_hash`, `output_hash`, `artifact_uri`, `error_code`,
`error_summary`.

Supporting indexes:

- `idx_factory_cycle_runs_receipt_origin` on `(factory_id, receipt_origin, recorded_at DESC)` — makes the organic-only liveness query cheap.
- `idx_factory_cycle_runs_execution_id` on `(execution_id)`.

### `legacy_unknown` backfill rule (never guess)

The migration backfills `receipt_origin` from the existing
`runner_output->>'cloud_trigger'` **only where truthfully determinable**;
everything else stays `legacy_unknown`. Historical rows are **not** rewritten.

| `runner_output.cloud_trigger` | Backfilled `receipt_origin` |
|---|---|
| `http_loop` | `organic` |
| `noos_integrator_repair` or `noos_motor_receipt_writer_repair` | `repair` |
| matches `%replay%` | `replay` |
| `NULL` | `legacy_unknown` |
| anything else | `legacy_unknown` |

The rule never infers `organic` from an ambiguous or missing label — an unknown
provenance is recorded as `legacy_unknown`, not promoted to organic.

---

## Example: organic receipt

A genuine cloud producer cycle (`cloud_trigger = http_loop`). This is the only
kind of completion evidence that can promote a loop to `RUNNING_CONFIRMED`.

```json
{
  "execution_id": "exec-digest-2026-07-17-0007",
  "attempt_id": "attempt-1",
  "correlation_id": "corr-9f2a1c",
  "dispatch_id": "disp-2026-07-17-tick-3341",
  "idempotency_key": "digest:sha256:4b1e8c…",
  "producer": "noos-loop-runner",
  "receipt_origin": "organic",
  "execution_plane": "cloud",
  "workflow_version": "v1",
  "schema_version": "1",
  "state": "COMPLETED",
  "input_hash": "sha256:a1b2c3…",
  "output_hash": "sha256:c3d4e5…",
  "artifact_uri": "artifacts/exec-digest-2026-07-17-0007/output.json",
  "error_code": null,
  "error_summary": null,
  "created_at": "2026-07-17T13:50:12Z",
  "updated_at": "2026-07-17T13:50:49Z",
  "history": [
    {"state": "DISPATCHED", "at": "2026-07-17T13:50:00Z"},
    {"state": "CLAIMED", "at": "2026-07-17T13:50:05Z"},
    {"state": "RUNNING", "at": "2026-07-17T13:50:07Z"},
    {"state": "OUTPUT_COMMITTED", "at": "2026-07-17T13:50:44Z"},
    {"state": "COMPLETED", "at": "2026-07-17T13:50:49Z"}
  ]
}
```

Raw source row would carry `runner_output.cloud_trigger = "http_loop"`, which
`normalize_receipt_origin()` maps to `organic`.

---

## Example: repair row

A receipt written by the integrator repair path
(`cloud_trigger = noos_integrator_repair`). It is a legitimate, fresh record —
but it is **not** organic completion evidence.

```json
{
  "execution_id": "exec-digest-repair-2026-07-17-0031",
  "attempt_id": "attempt-1",
  "correlation_id": "corr-repair-1e77",
  "dispatch_id": "disp-2026-07-17-repair-0031",
  "idempotency_key": "digest:sha256:4b1e8c…",
  "producer": "noos-integrator",
  "receipt_origin": "repair",
  "execution_plane": "cloud",
  "workflow_version": "v1",
  "schema_version": "1",
  "state": "REPAIR_APPLIED",
  "input_hash": "sha256:a1b2c3…",
  "output_hash": "sha256:c3d4e5…",
  "artifact_uri": "artifacts/exec-digest-repair-2026-07-17-0031/output.json",
  "error_code": null,
  "error_summary": null,
  "created_at": "2026-07-17T13:58:20Z",
  "updated_at": "2026-07-17T13:58:20Z",
  "history": [
    {"state": "REPAIR_APPLIED", "at": "2026-07-17T13:58:20Z"}
  ]
}
```

Raw source row would carry `runner_output.cloud_trigger =
"noos_integrator_repair"`, which `normalize_receipt_origin()` maps to `repair`
(a member of `NON_ORGANIC_ORIGINS`).

---

## Why a repair row is not organic liveness

This is the exact defect the provenance model fixes. The old completion
classifier keyed on receipt **age only**. Repair-labeled rows
(`cloud_trigger = noos_integrator_repair`) kept the newest row fresh, so the
cockpit reported a false `RUNNING_CONFIRMED` while the organic cloud producer
(`cloud_trigger = http_loop`) had been stalled since
**2026-07-12T13:50:49Z**.

The classifier is now provenance-aware:

- `RUNNING_CONFIRMED` requires **fresh ORGANIC completion evidence** — computed
  from the newest *organic* row, not the newest row of any kind.
- A repair row yields `organic_completion_fresh = False` and
  `repair_sustained_fresh = True`, so the state resolves to
  **`DEGRADED_REPAIR_SUSTAINED`** — a repair-labeled receipt can never confirm.
- `derive_completion_provenance()` separates the streams: it tracks
  `last_organic_completion_at`, `last_repair_receipt_at`, and
  `repair_receipts_since_last_organic`, so a run of repair rows since the last
  organic completion is visible rather than masked.
- `DEGRADED_REPAIR_SUSTAINED` reports `success_rate = null` (no trustworthy
  organic sample — never a fabricated `0.0`), `evidence_state =
  INSUFFICIENT_RECENT_EVIDENCE`, and routes to
  `organic_producer_reconcile_escalation` — which **escalates and surfaces** and
  deliberately does **not** loop back to receipt-writer repair (the loop that
  masked the 2026-07-12 stall).

Restarting the stalled cloud `http_loop` producer, applying migration 0020, and
running 3 consecutive real cloud organic `http_loop` cycles are all
**EXTERNAL_ACTIVATION_REQUIRED** (cloud credentials not present on the build
host; producer restart is founder-gated and off-host).

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
