# NOOS Motor v1 — Five-Minute Quick Start

**NOOS Motor v1** — deterministic workflow execution with verifiable organic
completion evidence, recovery, and auditable outputs.

This quick start runs the **offline reference executor** — the sellable vertical
slice. It is stdlib-only, needs no cloud, no secrets, and no network. Everything
below runs on the build host as-is.

> The cloud organic producer (`http_loop`) is a separate, production path and is
> **EXTERNAL_ACTIVATION_REQUIRED**. None of the steps here touch it.

---

## 0. Prerequisites

- Python **>= 3.10** (checked by `noos install`).
- No third-party runtime dependencies. The local executor is stdlib-only.
- Optional cloud features read config from `~/.noetfield-platform-secrets/`
  (outside the repo); see `.env.example`. Not required for this quick start.

---

## 1. Install (no network)

```bash
./bin/noos install
```

Expected (abridged):

```
noos install: checking runtime ...
Python 3.x.x
python OK
stdlib OK (no third-party runtime deps)
install OK — motor is stdlib-only; cloud features need ~/.noetfield-platform-secrets (see .env.example)
```

`install` performs a runtime + dependency check only. It makes no network calls.

---

## 2. Run the demo (sample input → real output)

The demo submits a representative customer input (a `digest` task) through the
full organic motor path:

```
CUSTOMER INPUT -> VALIDATION -> PLAN -> MOTOR EXECUTION (FSM) ->
REAL OUTPUT ARTIFACT -> AUTHORITATIVE RECEIPT -> RETRIEVAL -> REPLAY
```

```bash
./bin/noos demo
```

This runs `scripts/noos_motor_local_executor_v1.py --input docs/product/samples/sample-input.json --json`.

### Sample input (`docs/product/samples/sample-input.json`)

```json
{
  "task_kind": "digest",
  "title": "Q3 receipts digest",
  "records": [
    {"loop": "inbox", "cycles": 12, "status": "ok"},
    {"loop": "runtime", "cycles": 8, "status": "ok"},
    {"loop": "surface", "cycles": 5, "status": "degraded"}
  ]
}
```

**Input contract (digest task):** `{"task_kind":"digest","title":"...","records":[{...},...]}`.
`records` must be a non-empty list of JSON objects; otherwise the executor
returns a truthful `FAILED` result with `error_code=invalid_input` and writes
no artifact.

### Expected demo output (`--json`)

Identifiers marked *(per run)* are freshly generated each execution; the hashes
are deterministic for this input and are stable across runs.

```json
{
  "execution_id": "exe_0123456789abcdef",
  "status": "COMPLETED",
  "ok": true,
  "deduplicated": false,
  "artifact_uri": "file:///.../receipts/runway/artifacts/exe_0123456789abcdef.output.json",
  "json_artifact": ".../receipts/runway/artifacts/exe_0123456789abcdef.output.json",
  "md_artifact": ".../receipts/runway/artifacts/exe_0123456789abcdef.report.md",
  "output_hash": "adf3576e50596c87",
  "receipt_path": ".../receipts/runway/executions/exe_0123456789abcdef.receipt.json",
  "output": {
    "title": "Q3 receipts digest",
    "record_count": 3,
    "field_frequency": {"cycles": 3, "loop": 3, "status": 3},
    "numeric_totals": {"cycles": 25.0},
    "records_sha256": "d2b79b88f4a85bb0fa12d2ed18f175fca7750a91c0011a5f83afebb4aca1f2e4"
  },
  "validation_errors": []
}
```

The `output_hash` (`adf3576e50596c87`) and `records_sha256` are deterministic
for this input. `execution_id`, `correlation_id`, and file paths vary per run.

### The two output artifacts

**Output contract:** a normalized JSON artifact + a Markdown report + a lifecycle
receipt carrying `output_hash` (integrity-checkable on retrieval).

1. **Normalized JSON artifact** — `<execution_id>.output.json`, the `output`
   object shown above.

2. **Markdown report** — `<execution_id>.report.md`, shaped like:

   ```markdown
   # Q3 receipts digest

   - Execution ID: `exe_0123456789abcdef`
   - Correlation ID: `cor_0123456789abcdef`
   - Producer: `noos-motor-local-executor-v1` (plane: local_reference)
   - Records: **3**
   - Records SHA-256: `d2b79b88f4a85bb0fa12d2ed18f175fca7750a91c0011a5f83afebb4aca1f2e4`

   ## Field frequency

   | field | count |
   |---|---:|
   | cycles | 3 |
   | loop | 3 |
   | status | 3 |

   ## Numeric totals

   | field | total |
   |---|---:|
   | cycles | 25.0 |
   ```

3. **Lifecycle receipt** — `<execution_id>.receipt.json`, provenance-aware and
   carrying `receipt_origin=organic`, `execution_plane=local_reference`,
   `producer=noos-motor-local-executor-v1`. It is never stamped
   `cloud_trigger=http_loop` and must not be mistaken for cloud organic
   completion.

Receipt fields include: `execution_id`, `attempt_id`, `correlation_id`,
`dispatch_id`, `idempotency_key`, `producer`, `receipt_origin`,
`execution_plane`, `workflow_version`, `schema_version`, `state`, `input_hash`,
`output_hash`, `artifact_uri`, `error_code`, `error_summary`, `created_at`,
`updated_at`, `history[]`.

You can run the executor directly instead of via `bin/noos`:

```bash
python3 scripts/noos_motor_local_executor_v1.py --input docs/product/samples/sample-input.json --json
```

---

## 3. Retrieve status (output + provenance + integrity)

Use the `execution_id` printed by the demo:

```bash
./bin/noos status <execution_id>
```

This retrieves the stored receipt and artifact and recomputes the output hash to
verify integrity. Expected `--json` shape (abridged):

```json
{
  "ok": true,
  "execution_id": "exe_0123456789abcdef",
  "status": "COMPLETED",
  "artifact_uri": "file:///.../exe_0123456789abcdef.output.json",
  "output_integrity_ok": true,
  "output": { "...": "..." },
  "receipt": { "...": "..." }
}
```

`output_integrity_ok: true` means the artifact on disk still hashes to the
`output_hash` recorded in the receipt.

Re-running `./bin/noos demo` with the same input does **not** execute a duplicate
logical run: idempotency (same `task_kind` + input) returns the existing terminal
run with `deduplicated: true`.

---

## 4. Verify (deterministic self-verification)

```bash
./bin/noos verify
```

Runs `scripts/noos_motor_v1_verify_v1.py` — the canonical verification (3 local
cycles + masking regression). This is a deterministic gate, not a hand-written
verdict.

---

## 5. Package (versioned release bundle)

```bash
./bin/noos package
```

Runs `scripts/noos_motor_v1_package_v1.py` — the release packager, which builds a
manifest plus a `tar.gz` bundle.

---

## Reference

### CLI commands (`bin/noos`)

| Command | What it does |
|---|---|
| `noos install` | Runtime + dependency check (no network) |
| `noos start` | Print how to start the on-demand local executor |
| `noos status <id>` | Retrieve an execution's status, provenance, and integrity |
| `noos demo` | Run the representative input → real output |
| `noos verify` | Deterministic self-verification (3 cycles + masking) |
| `noos package` | Build the versioned release bundle + manifest |
| `noos rollback` | Print the tested rollback commands |

### Components (all in-repo)

- `scripts/noos_motor_state_machine_v1.py` — deterministic lifecycle FSM +
  invariants (pure).
- `scripts/noos_motor_local_executor_v1.py` — OFFLINE reference executor (the
  sellable vertical slice; no cloud).
- `scripts/noos_observability_semantics_v1.py` — provenance-aware classifier
  (`classify_loop_state`, `normalize_receipt_origin`,
  `derive_completion_provenance`).
- `scripts/autorun_status_v1.py` — live cockpit projection (passes provenance to
  the classifier).
- `scripts/noos_motor_v1_verify_v1.py` — canonical verification.
- `scripts/noos_motor_v1_package_v1.py` — release packager (manifest + tar.gz).
- `bin/noos` — CLI: `install | start | status <id> | demo | verify | package | rollback`.
- `infrastructure/supabase/migrations/0020_motor_provenance_fields.sql` —
  additive provenance columns. **NOT applied; founder / L5-gated.**
- `.env.example` — config reference (no secrets; the local executor needs none).

### Lifecycle states

`ACCEPTED -> PLANNED -> DISPATCHED -> CLAIMED -> RUNNING -> OUTPUT_COMMITTED -> COMPLETED`

- Terminals: `FAILED`, `TIMED_OUT`, `CANCELLED`, `DEAD_LETTERED`.
- Recovery: `RETRY_SCHEDULED`, `REPLAY_REQUESTED`, `REPAIR_APPLIED`.

### Health / liveness states

`RUNNING_CONFIRMED`, `DEGRADED_REPAIR_SUSTAINED`, `COMPLETION_UNPROVEN`,
`EVIDENCE_INCONSISTENT`, `STOPPED_OR_IDLE`
(plus legacy `DISPATCHING_COMPLETION_UNPROVEN`, `OBSERVER_DIVERGENCE_OR_REPLAY`,
`LOOP_EXECUTION_STALE`, `OBSERVER_UNAVAILABLE`).

### Provenance origins

`organic`, `repair`, `replay`, `manual`, `migration`, `test`, `legacy_unknown`.

### Reliability model

- **Idempotency-key dedupe** — same `task_kind` + input => one logical run.
- **Lease** — owner + expiry + deterministic reclaim.
- **Backoff** — bounded exponential, base `5s * 2^retry`, capped at `900s`;
  `max_retries` default `3`.
- **Dead-letter** — a real, inspectable, replayable terminal.
- **Replay** — creates a NEW attempt preserving `root_execution_id` +
  `correlation_id` lineage.
- **Repair never rewrites organic provenance.**

### Why the completion classifier changed

Previously the completion classifier keyed on receipt **age only**, so
repair-labeled rows (`cloud_trigger=noos_integrator_repair`) kept the newest row
fresh and produced a false `RUNNING_CONFIRMED` while the organic cloud producer
(`cloud_trigger=http_loop`) was stalled since `2026-07-12T13:50:49Z`. It is now
**provenance-aware**: `RUNNING_CONFIRMED` requires FRESH ORGANIC evidence; repair
rows classify as `DEGRADED_REPAIR_SUSTAINED` and never confirm.

---

## Cloud organic chain (production) — EXTERNAL_ACTIVATION_REQUIRED

The steps in this quick start do **not** run any of the following. This chain is
the production organic path and requires cloud credentials that are not on the
build host:

```
Cloudflare cron worker noos-loop-fleet-tick-v1 (*/5)
  -> POST /loop
  -> Railway executor noos-loop-runner
  -> run_noetfield_factory_loop_v1.py --once  (env GITHUB_EVENT_NAME=http_loop)
  -> Supabase table noetfield_factory_cycle_runs
  -> autorun_status_v1.py projection
  -> classifier
```

- **Authoritative store:** Supabase `noetfield_factory_cycle_runs`
  (+ `noos_loop_registry` dispatch heartbeat). Projections / mirrors are read
  replicas.
- **EXTERNAL_ACTIVATION_REQUIRED** (needs cloud creds not on the build host):
  - Restart the cloud `http_loop` producer.
  - Apply Supabase migration `0020` (`make supabase-migrate`).
  - Run 3 consecutive real cloud organic `http_loop` cycles.

### Security boundary

- No secrets are committed. Real secrets live in
  `~/.noetfield-platform-secrets/` (outside the repo).
- The local executor is stdlib-only and fully offline.
- Deploy / migrate / spend / commercial actions are founder-gated.

---

SUBMITTED for independent verification (author != subject). canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
