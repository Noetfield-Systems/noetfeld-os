# NOOS Runtime Map — the motor, mapped

Status: ACTIVE (NOOS operational binding, Claude Code surface)
Law: the motor is **not redesigned, not rebuilt, not "improved"** from a chat
session. Wiring authority: `data/noos-motor-executor-wiring-v1.json` (LOCKED_v1,
PANEL_GOVERNANCE_2026-07-06). This file is a map for orientation and verification.

## Pattern

One clock POSTs one bounded tick to one swappable HTTP executor, secret-gated;
receipts at exit; an independent dead-man watches liveness.

```
CF cron (*/5) noos-loop-fleet-tick-v1 ──POST /loop (X-NOOS-Loop-Secret)──▶ Railway noos-loop-runner
        │ 14-target dispatch table                                             │ one bounded tick:
        │                                                                      │ scripts/noos_loop_runner_v1.py
CF cron (*/30) noos-deadman-v1 ──watches Supabase noos_loop_registry──▶ POST /motor-restart (recipes)
        │
GHA cron witnesses (verify-only) ──▶ receipts/proof/*.json
```

## Layer 1 — clocks / triggers

- `cloud/workers/noos-loop-fleet-tick-v1/` — primary motor. Cron `*/5`; iterates
  `cloud/workers/noos-loop-fleet-tick-v1/src/dispatch-table.json`
  (14 targets: inbox 5m, runtime 15m, surface 20m,
  chain 30m, self_heal 10m, sourcea_observe 30m, agent_nerve 60m,
  workflow_audit 15m, self_heal_safe_fixes 30m, researcher 60m, specialist 120m,
  orchestrator 180m, factory_autorun 10m, improve_kaizen_daily 1440m).
- `cloud/workers/noos-deadman-v1/` — independent dead-man switch, cron `*/30`;
  staleness = 2× interval per `cloud/workers/noos-deadman-v1/src/loop-intervals.json`;
  max 1 restart attempt;
  Telegram lane is DEADMAN_TELEGRAM_* only (send_alerts currently false).
- `cloud/workers/noos-factory-autorun-tick-v1/` — cron RETIRED 2026-07-05;
  factory autorun now flows through the fleet dispatch table.
- `.github/workflows/` — witness/verify crons only (autorun, gha-health,
  motor-sustain, stack-health, sourcea-spine, trustfield-observe,
  liveness-registry, sandbox-url-sweep, integrator-daily, machine-audit).
  Per-loop `noos-*-loop` workflows are `workflow_dispatch`-only by design —
  **GHA is not the drive train**; CF cron → Railway HTTP is.

## Layer 2 — executors

- **Canonical:** `ops/railway/noos-loop-runner/server.py` (Railway, CANONICAL_LIVE
  since the 2026-07-06 cutover). Routes: `GET /health`, `POST /loop` (per-event-type
  lock, 409 if already running, 900s timeout), `POST /motor-restart`.
- Secondary always-on Fly sidecars: `ops/fly/noos-inbox-runner/` (300s drain),
  `ops/fly/noos-self-heal-runner/` (60s reenqueue+heartbeat).
- `ops/fly/noos-loop-executor/` — app DESTROYED 2026-07-06 (teardown receipt);
  code remains in-tree, it is not a live plane. Teardown law: non-canonical
  executors are destroyed with receipt, never parked as fallback.
- Local same entrypoint: `python3 scripts/noos_loop_runner_v1.py --event-type <x> --json`.

## Layer 3 — state and receipts

- Per-loop runtime state: `.noos-runtime/loops/<loop_id>/state-v1.json`
  (CAS cycle_number before side effects).
- Liveness sink: Supabase `noos_loop_registry` (+ `noos_deadman_runs`).
- Org state snapshot: `noetfield-org/LOOP_STATE.json` (mission stack M1–M6;
  motor fields stale vs `data/noos-24-7-loops-v1.json` — trust the data file).
- Proof receipts: `receipts/proof/` (committed snapshots); Railway container
  receipts are not committed.

## Layer 4 — gates and verification

- Cycle gates inside the runner: sink invariant `sum(origin_counts) == sink_count`,
  op_key/CAS determinism, per-cycle cost block.
- Dead-man staleness + restart recipes (`data/noos-motor-restart-recipes-v1.json`).
- GHA witnesses re-verify health on cron and write receipts.
- `make determinism-verify` — external L13/D1–D8 gate.
- Deployment law: cron enablement is the LAST step; never disable the working
  motor while debugging a replacement; executor swap = CF secret change only;
  new compute vendor = founder gate.

## Evidence it runs (committed receipts)

- `receipts/proof/noos-motor-sustain-v1.json` — 2026-07-08, all 4 planes healthy,
  liveness stale_count=0 (freshest committed proof).
- `receipts/proof/noos-cf-railway-cutover-v1.json` — 2026-07-06 cutover to Railway.
- `receipts/proof/noos-cf-railway-dispatch-verify-v1.json` — 2026-07-06,
  14/14 fired, 5/14 execution_ok at verify time (known gap, see below).
- `receipts/proof/noos-loop-verify-all-v1.json` — 2026-07-05, per-loop smoke
  VERIFIED, sink_invariant PASS.
- `receipts/proof/noos-fly-executor-teardown-v1.json` — Fly executor destroyed.

## Known gaps (recorded, not chat-fixable)

- Dispatch-verify shows 9/14 targets not execution_ok on 2026-07-06; no newer
  all-targets execution receipt is committed.
- Deployed `noos-factory-autorun-tick-v1` appears to lag repo config (live worker
  still reports a cron and a legacy repo slug per the 2026-07-08 sustain receipt).
- Fly inbox runner and CF fleet inbox tick both drain the inbox (dual motor until
  UPG-0207 cutover is evidenced).
- Committed receipts are snapshots; live liveness truth is Supabase, checked via
  the deadman `/check` endpoint or witness receipts — not by re-running loops from chat.
