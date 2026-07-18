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
| 2026-07-18T04:05Z | 3 | `noos_motor_state_machine_v1.py` FSM + invariants 1-13; 15/15 tests | yes (new file) |
| 2026-07-18T04:10Z | 5 | `noos_motor_local_executor_v1.py` offline slice; real artifact+receipt; 8/8 tests | yes (new file) |
| 2026-07-18T04:20Z | 4b | Migration `0020_motor_provenance_fields.sql` (additive; NOT applied, founder-gated) | yes (drop-column block) |
| 2026-07-18T04:25Z | 6 | `noos_motor_v1_verify_v1.py`, `noos_motor_v1_package_v1.py`, `bin/noos`, `.env.example`, Makefile motor-* targets | yes (new files) |
| 2026-07-18T04:35Z | 6 | 7 product docs + product README (parallel authored, accuracy-reviewed) | yes (new files) |
| 2026-07-18T04:40Z | 8 | Release bundle built (dist/, 16 components, sha recorded); runway receipts emitted (3 local cycles, masking, repair, e2e, cloud-external-activation, release-verification, release-manifest) | yes |
| 2026-07-18T04:45Z | — | Full repo suite 324 passed; motor+affected 59 passed; `noos verify` OVERALL ALL_OK | — |
| 2026-07-18T04:55Z | 8 | Adversarial verification (4 skeptics): false-green fix / receipts / docs NOT REFUTED; FSM invariant-2 bug FOUND (terminal lease-reclaim resurrection) and FIXED (lease cleared on terminal, reclaim gated to live states, replay=new-attempt, DEAD_LETTERED inert) + BFS property test. Full suite 327 passed | yes (revert) |

## Result

**In-repo runway: COMPLETE and test-proven offline.** The false-green bug is
fixed at the classifier AND the live projection; the motor has an explicit
deterministic FSM with all 13 invariants enforced; a real customer input runs
end-to-end to a hash-bound output artifact; the release bundle is built.

**Cloud steps remain `EXTERNAL_ACTIVATION_REQUIRED`** (objectively — no
cloud CLI/creds on this host): restart the `http_loop` producer, apply migration
0020, and run 3 real cloud organic cycles. Exact commands in
[`receipts/runway/noos-motor-v1-cloud-cycles-external-activation.json`](../../receipts/runway/noos-motor-v1-cloud-cycles-external-activation.json).

Final state: **PRODUCT_RELEASE_BUILT_EXTERNAL_ACTIVATION_REQUIRED**.
