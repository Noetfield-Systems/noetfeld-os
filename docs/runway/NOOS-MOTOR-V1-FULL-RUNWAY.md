# NOOS Motor v1 — Full Runway Execution Ledger

**Task:** NF-NOOS-MOTOR-V1-FULL-RUNWAY · **Lane:** NOOS-LANE-motor-v1-runway
**Canon:** `LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.`
`canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1`

> Builder ledger. Every claim here is **SUBMITTED for independent verification**
> (author ≠ subject). No PASS/DONE verdict is self-issued; deterministic gates
> (pytest) and the receipts under `receipts/runway/` are the evidence.

## 0. Starting state (captured before mutation)

| Field | Value |
|---|---|
| Commit SHA | `8ba1af9ca89499330603047e00a6ddcfb7fa9fd3` |
| Branch | `nf-noos-repin-gateway-v2-b72f5a3` |
| origin/main | `291789bc3d40dad8ea165f68a29ff026a000bd26` |
| Dirty worktree | 24 files |
| Authoritative store | Supabase `noetfield_factory_cycle_runs` (+ `noos_loop_registry`) |
| Organic producer | cloud `cloud_trigger=http_loop` (`ops/railway/noos-loop-runner/server.py`, `ops/fly/noos-loop-executor/server.py`) |
| Dispatch | 5-min heartbeat (`noos_loop_registry.last_fired_at`) |
| Completion writer (repair) | `noos_integrator_repair` + `noos-motor-route-owner-v1` |
| Projection | `scripts/autorun_status_v1.py` → Supabase |
| Critic | `scripts/noos_observability_semantics_v1.py::classify_loop_state` |
| Schema | migrations `0000`–`0019`; next free = `0020` |
| Rollback point | `git reset --hard 8ba1af9ca89499330603047e00a6ddcfb7fa9fd3` (+ `git stash` runway files) |

Full capture: [`receipts/runway/noos-motor-v1-before-state.json`](../../receipts/runway/noos-motor-v1-before-state.json).

## 1. Known failure (revalidated)

- **Failed hop:** organic worker execution → completion callback. The cloud
  `http_loop` producer stalled at `2026-07-12T13:50:49Z`. Sink, dispatch, and
  projection are healthy.
- **Detection gap (in-repo fixable):** `classify_loop_state` is provenance-blind
  (age-only, `noos_observability_semantics_v1.py:177-180`). Repair-labeled rows
  refresh row age → false `RUNNING_CONFIRMED`.

Full analysis: [`receipts/runway/noos-motor-v1-root-cause.json`](../../receipts/runway/noos-motor-v1-root-cause.json).

## Reachability boundary (why parts are EXTERNAL_ACTIVATION_REQUIRED)

No `supabase`/`fly`/`psql` CLI and no cloud credential env vars are present on
this host; platform secrets live outside the repo (`~/.noetfield-platform-secrets/`)
and are not loaded. Therefore: **cloud producer restart, Supabase migration
apply, and real cloud organic cycles are objectively unreachable from here** and
are delivered as exact activation commands, not executed.

## Acceptance criteria

In-repo (must be true & test-proven this run):
- [ ] Provenance-aware classifier: no `repair`/`replay`/`manual` completion can yield `RUNNING_CONFIRMED`.
- [ ] Deterministic motor FSM with invariants 1–13 enforced + rejected invalid transitions.
- [ ] Local reference executor: real input → real output artifact → organic receipt → retrieval → replay → truthful failure, fully offline.
- [ ] Additive backward-compatible provenance migration file (not applied).
- [ ] Unit + integration + failure-path + masking-regression tests pass.
- [ ] Product package: docs, `bin/noos` CLI, Makefile ops, release manifest.
- [ ] 3 consecutive LOCAL reference organic cycles + masking regression captured as receipts.

External-activation (delivered as commands, gated on cloud creds):
- [ ] Restart cloud `http_loop` producer; apply Supabase migration; 3 real cloud organic cycles.

## Material mutations log (append-only)

| UTC | Phase | Change | Reversible? |
|---|---|---|---|
| 2026-07-18T03:40Z | 0 | Claimed lane NOOS-LANE-motor-v1-runway | yes (closeout) |
| 2026-07-18T03:41Z | 0/1 | before-state + root-cause receipts + this ledger | yes (new files) |
| 2026-07-18T03:50Z | 4 | Provenance-aware classifier in `noos_observability_semantics_v1.py` (new states DEGRADED_REPAIR_SUSTAINED/COMPLETION_UNPROVEN/EVIDENCE_INCONSISTENT/STOPPED_OR_IDLE, `normalize_receipt_origin`, `derive_completion_provenance`); backward-compatible (14/14 legacy fixtures green) | yes (revert file) |
| 2026-07-18T03:52Z | 4 | Wired live projection `autorun_status_v1.py` to pass provenance (fetch 50-row window, organic-only liveness); 13/13 autorun tests green | yes (revert file) |
| 2026-07-18T03:54Z | 4 | Gate `tests/test_noos_motor_provenance_v1.py` — 11/11 incl. property: no non-organic origin ever RUNNING_CONFIRMED | yes (new file) |
