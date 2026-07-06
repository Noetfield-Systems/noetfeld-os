<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260705-029
doc_type: LIVING_SYSTEM_99_PLAN_LOCKED
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
lock_state: LOCKED_v1
authority: FOUNDER_REVIEW_2026-07-05
-->

# Living System 99-Plan — Locked v1

**Status:** LOCKED v1 (founder-reviewed 2026-07-05)
**Authority:** Advisor synthesis (5-layer autonomy model + cloud-trigger / dead-man diagnosis) on 2026-07-05
**Branch:** `docs/living-system-99-plan`
**Supersedes:** none — extends `NOOS-AGENT-20260703-006` (Machine Loops v1) and `NOOS-AGENT-20260702-027` (Unified Autonomy Upgrade Master)
**Pre-condition:** PR #26 merged (CF cron → Railway loop motor, zero GHA minutes for loops)

---

## 0. Reframe (the actual problem)

The system is **agentic, not yet autonomous**. Not because layers are missing — Layers 1–4 shipped this week — but because of two mechanical gaps:

1. **Triggers still route through the founder's Mac.** Cloud cron can't die when the founder sleeps; Mac-dependent loops must.
2. **No dead-man switch.** Repair fixes code defects from a queue; nothing detects "the probe worker itself stopped firing" and restarts it.

The honest test is not any architecture diagram. It is: **close the laptop for 48 hours and read the heartbeats from your phone.** This plan makes that test pass.

**Doctrine (locked, do not cross):**
- Autonomy in execution. **Human sovereignty over architecture.** No unsupervised Evolution layer.
- Founder-gated items queue and wait — correct per L5/L7.
- The fix is **widening `machine_safe`**, not removing gates.
- A system that redesigns its own architecture unsupervised is the system that deletes its own brakes.
- The 48h laptop-closed test runs **in parallel** with the 25 commercial offers out. A perfectly self-healing system with zero revenue motion is a beautiful machine idling in neutral.

---

## Phase map (99 steps across 7 phases)

| Phase | Theme | Steps | Owner | Why |
|-------|-------|-------|-------|-----|
| **A** | Trigger host inventory & cloud migration | 01–15 | machine | Close the "Mac-dependent loop" gap |
| **B** | Dead-man switch + liveness registry | 16–30 | machine | Watch the watchers |
| **C** | Repair loop can restart its own motors | 31–45 | machine | Close the missing repair class |
| **D** | Widen `machine_safe` recipe library | 46–60 | machine + founder ratify | More autonomy at night |
| **E** | 48-hour laptop-closed live test | 61–75 | machine runs, founder observes | Definition of "live" |
| **F** | Commercial motion in parallel | 76–90 | founder (machine prepares) | Revenue ≠ idle neutral |
| **G** | Lock-down, receipts, manifest, retro | 91–99 | machine + founder sign-off | Close the lane cleanly |

---

## Phase A — Trigger host inventory & cloud migration (01–15)

**Goal:** Every scheduled loop either fires from cloud (CF/Railway/GHA-only-CI) with the laptop closed, or is marked `founder-manual-by-design`.

1. Inventory every scheduled loop in `data/noos-24-7-loops-v1.json` and `data/noos-cf-dispatch-table-v1.json`; tag each row `trigger_host ∈ {cf, railway, gha, mac, cursor, script, supabase_cron}`.
2. For each `mac`/`cursor`/`script` row: classify as `migrate_to_cloud` or `founder_manual_by_design`. Write `data/noos-trigger-host-inventory-v1.json`.
3. Audit `~/.sina/` paths referenced by any loop script; list which state files would die with the laptop.
4. Audit Cursor-agent-authored commits in the last 14 days for implicit scheduler code (sleep loops, watchers tied to a session).
5. Migrate any `script`-triggered heartbeat to CF cron entries in `data/noos-cf-dispatch-table-v1.json`.
6. Confirm `noos-loop-fleet-tick-v1` CF worker is on the Paid plan ($5/mo) — predictable cost, no per-run metering.
7. Verify CF worker `LOOP_RUNNER_URL` + `LOOP_RUNNER_SECRET` are set on the worker (not on the laptop env).
8. Deploy Railway `noos-loop-runner` from merged `main`; confirm `GET /health` 200 from the Railway public URL.
9. Confirm Supabase service role key is set as a Railway secret (not read from `~/.sourcea-secrets/` on the Mac).
10. Confirm Fly `noos-inbox-runner` + `noos-self-heal-runner` secrets are wired for `fly auth` independent of the Mac session (or mark `fly_l4_deferred`).
11. Mark every Mac-only loop in the inventory with `founder_manual_by_design: true` and a one-line reason.
12. Write `receipts/proof/noos-trigger-host-inventory-v1.json` with the migrate/keep table.
13. Reconcile inventory vs `data/autorun-workflows-v1.json` — no orphan Mac-only triggers.
14. Run `make loop-registry-reconcile` after migration; expect `ok=true` with cloud-hosted triggers only.
15. **Phase A gate:** zero `mac`/`cursor` rows that aren't `founder_manual_by_design`. Founder signs the inventory.

---

## Phase B — Dead-man switch + liveness registry (16–30)

**Goal:** Every loop upserts `last_fired_at` to Supabase; an independent CF worker watches the watchers.

16. Add Supabase table `noos_loop_registry` (`loop_id`, `last_fired_at`, `last_cycle_status`, `host`, `updated_at`) via `scripts/apply_supabase_migration_v1.py --migration 0013`.
17. Update `noos_loop_runner_v1.py` to upsert `last_fired_at` on every successful cycle (Supabase sink extension, fail-open if Supabase down).
18. Update Railway `noos-loop-runner` factory path to upsert the same row.
19. New CF worker `cloud/workers/noos-deadman-v1/` with cron `*/30 * * * *` — independent trigger path from the loop motor.
20. Deadman logic: read all `noos_loop_registry` rows; for each, `stale = now - last_fired_at > 2 * interval_minutes`; emit `stale_loops[]`.
21. On staleness: (a) one automated restart attempt via `POST /loop` to the loop runner; (b) Telegram alert via `DEADMAN_TELEGRAM_BOT_TOKEN` + `DEADMAN_TELEGRAM_CHAT_ID` secrets.
22. Deadman writes `receipts/proof/noos-deadman-<UTC>.json` per run with `stale_count`, `restart_attempts`, `alert_sent`.
23. Add `data/noos-deadman-config-v1.json` with `interval_multipliers`, `alert_channels`, `restart_attempts_max: 1`.
24. Add Makefile target `deadman-deploy` → `bash scripts/deploy_noos_deadman_cf_v1.sh`.
25. Add Makefile target `deadman-probe` → manual `curl POST /check` on the deadman worker.
26. Add tests `tests/test_noos_deadman_v1.py` for staleness math and restart-attempt cap.
27. Deploy deadman CF worker; verify `GET /health` 200.
28. Simulate a stale loop (block one cycle); confirm deadman fires alert + restart within 30 min.
29. Update `noetfield-org/REPO_REGISTRY.md` with the deadman worker row.
30. **Phase B gate:** deadman detects and restarts a deliberately-stalled loop within 2× interval. Founder confirms alert reaches phone.

---

## Phase C — Repair loop can restart its own motors (31–45)

**Goal:** The repair layer doesn't just fix code defects — it can restart a dead motor (CF worker, Railway service, Fly machine).

31. Add `motor_status` probes to `scripts/autorun_status_v1.py`: CF `/health`, Railway `/health`, Fly `/health` + `/ready`.
32. Define `motor_restart_recipes` in `data/noos-motor-restart-recipes-v1.json`: one locked recipe per motor (CF `wrangler deploy`, Railway `railway up`, Fly `fly deploy`).
33. Mark each recipe `machine_safe` or `founder_gated`. Restart of a CF worker = `machine_safe`; Railway redeploy = `machine_safe`; Fly redeploy = `founder_gated` (auth-dependent).
34. Extend `scripts/noos_improve_kaizen_runner_v1.py` to also pick `motor_restart` class candidates.
35. New script `scripts/noos_motor_restart_v1.py` — executes a recipe by id, writes receipt, fails closed on missing auth.
36. Wire deadman → `noos_motor_restart_v1.py` for CF worker restarts (machine_safe only).
37. Add `receipts/proof/noos-motor-restart-<motor>-<UTC>.json` schema.
38. Add tests `tests/test_noos_motor_restart_v1.py` for recipe selection + auth-gated fail-closed.
39. Document `motor_restart` recipe authoring rules in `docs/ops/NOOS_MOTOR_RESTART_RECIPES_v1.md`.
40. Founder ratifies the recipe set (one-time gate).
41. Run a sandbox drill: kill the CF loop motor → deadman detects → restart recipe fires → motor recovers.
42. Receipt for the drill: `receipts/proof/noos-motor-restart-drill-20260705.json`.
43. Update `docs/ops/NOOS_FACTORY_AUTORUN_DEPRECATION_v1.md` with the motor-restart section.
44. Update `data/noos-machine-loops-config-v1.json` with `motor_restart_recipes_path`.
45. **Phase C gate:** sandbox drill passes end-to-end without founder keystrokes. Founder signs the drill receipt.

---

## Phase D — Widen `machine_safe` recipe library (46–60)

**Goal:** More fix-classes run at night with locked recipes + external verification. Founder ratifies; machine executes.

46. Audit existing `receipts/proof/noos-kaizen-*.json` for `machine_safe` classes already proven.
47. List candidate `machine_safe` fix-classes not yet recipe-locked: docs typos, generated receipt refresh, deterministic test fixes, dependency pin bumps within semver.
48. For each candidate: write a recipe in `data/noos-kaizen-recipes-v1.json` with `class`, `match_pattern`, `fix_command`, `external_verify_command`, `rollback_command`.
49. Each recipe requires `external_verify_command` (gate / pytest / live probe) — no recipe merges without external verify.
50. Add `scripts/noos_kaizen_recipe_apply_v1.py` — applies a recipe by id, runs external verify, writes receipt, auto-rolls back on verify failure.
51. Tests `tests/test_noos_kaizen_recipe_apply_v1.py` for apply + verify + rollback paths.
52. Founder ratifies the v1 recipe set (one-time gate, documented in receipt).
53. Wire `noos_improve_kaizen_runner_v1.py` to prefer recipe-locked candidates over ad-hoc fixes.
54. Add nightly GHA-dispatch (via CF, not GHA cron) for `make improve-kaizen-daily` — runs once per day, recipe-locked only.
55. Daily Kaizen receipt `receipts/proof/noos-improve-kaizen-daily-v1.json` records recipe_id, verify_passed, rollback_triggered.
56. Weekly digest `receipts/proof/noos-kaizen-weekly-digest-<W>.json` — top recipes applied, ROI estimate, founder_gated queue size.
57. Add `founder_gated` queue growth alert: if queue > 10 items, deadman pings Telegram once per day.
58. Update `docs/GOVERNED_AUTORUN_LAWS_v3.md` with the recipe authoring rules.
59. Update `data/noos-machine-loops-config-v1.json` with `kaizen_recipes_path`.
60. **Phase D gate:** ≥5 recipe-locked `machine_safe` classes applied at night without founder, all with external verify. Founder reviews weekly digest.

---

## Phase E — 48-hour laptop-closed live test (61–75)

**Goal:** Prove the system stays alive without the founder's Mac for 48 hours. Heartbeats readable from phone.

61. Pre-flight: confirm all Phase A–D gates signed. Confirm CF Paid active, Railway running, deadman deployed, recipes ratified.
62. Snapshot `data/noos-living-system-baseline-20260705.json` — every loop's `last_fired_at`, every motor's health URL.
63. Founder closes laptop at T0. Sends one Telegram message "T0 closed" to deadman chat for timestamp.
64. Machine runs 48h. Every 30 min, deadman emits `receipts/proof/noos-deadman-<slot>.json`.
65. At T+6h, T+12h, T+24h, T+36h, T+48h: deadman posts a heartbeat summary to Telegram (loop count, stale count, restart attempts).
66. Any stale loop triggers restart recipe (Phase C). Any motor death triggers restart recipe.
67. Any founder_gated item queues (correct behavior). No founder-gated item is auto-resolved.
68. Commercial offers (Phase F) continue in parallel — machine prepares, founder clicks send from phone when ready.
69. At T+48h, founder reopens laptop. Runs `make loop-verify-all` and `make deadman-probe`.
70. Diff baseline vs final: `scripts/verify_noos_living_system_48h_v1.py --baseline ... --final ... --write-receipt`.
71. Receipt `receipts/proof/noos-living-system-48h-<UTC>.json` with `loops_fired`, `motors_restarted`, `recipes_applied`, `founder_gated_queued`, `ok`.
72. Honest failure report if any loop died and wasn't restarted. No "pass" cosmetics.
73. Retro doc `docs/_NOOS_AGENT/[NOOS-AGENT-20260707-030]_LIVING_SYSTEM_48H_RETRO_v1.md` (date adjusted to actual test day).
74. Update `noetfield-org/LOOP_STATE.json` with `autonomous_mode: true` if and only if 48h receipt `ok=true`.
75. **Phase E gate:** 48h receipt `ok=true` AND founder signs retro. If false, return to Phase A–D; do not advance.

---

## Phase F — Commercial motion in parallel (76–90)

**Goal:** The 25 offers out + ACG founder send run alongside the autonomy test. A perfectly self-healing idle system is not the goal.

76. Confirm ACG lane state `PUBLIC_PAGE_LIVE + PROSPECT_PACKET_READY` (already true).
77. Founder: review SourceA packet `bfc05dbb` → first NW1 send from phone during the 48h test.
78. Record `~/.sina/nw1-outbound-send-receipt-v1.json` with `sent_at`, status `sent`.
79. Machine updates `noetfield-org/SERVICE_LANES.md` → `FIRST_OUTREACH_SENT` only after valid receipt.
80. Queue the remaining 24 offers in `data/noos-acg-outbound-queue-v1.json` with `send_at` slots.
81. Each offer has a `packet_path`, `recipient`, `founder_gated: true` flag — machine prepares, founder sends.
82. Machine drafts follow-up templates in `noetfield-org/templates/` for any reply.
83. ACG lane dashboard: `scripts/noos_acg_lane_status_v1.py` shows `sent / queued / replied` counts.
84. Weekly commercial digest `receipts/proof/noos-acg-weekly-digest-<W>.json`.
85. If a reply arrives: machine classifies, drafts response, queues for founder send.
86. No commercial action is `machine_safe` — every send is founder-gated by design.
87. Update `data/noos-unified-upgrade-backlog-v1.json` UPG-0001 evidence on first send.
88. Update `noetfield-org/SERVICE_LANES.md` with `FIRST_OUTREACH_SENT` + send count.
89. Update `docs/_NOOS_AGENT/PRODUCT_TRUTH.md` commercial section with first-receipt evidence.
90. **Phase F gate:** ≥1 NW1 send completed during the 48h test. Founder confirms revenue motion started.

---

## Phase G — Lock-down, receipts, manifest, retro (91–99)

**Goal:** Close the lane cleanly. Lock the doctrine. Update authority files.

91. Run `pytest -q` — expect all green.
92. Run `bash scripts/check_noos_clean_tree.sh` — expect OK.
93. Run `bash scripts/check_noos_live_sync_gate.sh` — expect ecosystem PASS.
94. Update `docs/_NOOS_AGENT/UPGRADE_MANIFEST.json` with completed steps + evidence paths.
95. Update `data/noos-unified-upgrade-backlog-v1.json` summary (`open_t2`, `open_t3` reduced).
96. Write closeout receipt `receipts/proof/noos-living-system-99-closeout-v1.json`.
97. Add this doc's row to `docs/_NOOS_AGENT/MANIFEST.json` (trace_id `NOOS-AGENT-20260705-029`, doc_type `LIVING_SYSTEM_99_PLAN_LOCKED`).
98. Founder signs the closeout receipt. Lock state = `LOCKED_v1`.
99. Merge to `main` via `make machine-validate-merge`. Branch deleted on clean merge.

---

## Execution discipline

| Rule | Application |
|------|-------------|
| L-P5 Claim | `make local-lane TASK=NOOS-LANE-living-system-99 SCOPE=data,scripts,cloud,docs,noetfield-org` before edits |
| One lane per pass | Max 20–40 files per commit; one atomic commit per phase |
| L-P4 Delegate | Do not re-run GHA trigger sweeps; use receipts + `make loop-verify-all` |
| Founder gates | Steps 40, 52, 61, 76–90 — machine prepares, founder acts |
| Scaffold honesty | No step marked done without external verify receipt |
| 48h test honesty | Step 72 forbids "pass" cosmetics — honest failure report if any loop died |
| Commercial parallelism | Phase F runs **alongside** Phase E, not after |

---

## Out of scope (deliberate)

- **Unsupervised Evolution layer.** A system that redesigns its own architecture unsupervised deletes its own brakes. L5 forbids it. Machine proposes (ROI-ranked founder_gated queue, weekly digest); founder ratifies; machine executes.
- **Removing founder gates.** Founder-gated items queue and wait — correct per L5/L7. The fix is widening `machine_safe`, not removing gates.
- **Rewriting loops in JS to run pure-CF.** Considered (Option C in CF options analysis); rejected for now — Python runtime + Railway/Fly executor keeps the existing code surface.
- **Multi-region canary (UPG-0209).** Deferred — needs Phase A–D stable first.
- **gel-api Railway → Fly migration (UPG-0213).** Deferred — not on the autonomy critical path.

---

## Authority cross-references

| Trace ID | Why relevant |
|----------|--------------|
| `NOOS-AGENT-20260703-006` | Machine Loops v1 — critic, repair, audit, autonomy E2E |
| `NOOS-AGENT-20260702-027` | Unified Autonomy Upgrade Master — tiered backlog |
| `NOOS-AGENT-20260703-005` | Founder Canon Interface — zero-founder validation law |
| `NOOS-AGENT-20260703-004` | Cursor Local Mac operator — claim/closeout |
| `NOOS-AGENT-20260729-022` | System Fix and Upgrade 100-Plan (predecessor pattern) |
| `NOOS-AGENT-20260702-028` | Ten upgrade planes — execution matrix |

---

## Lock sign-off

**Lock state:** `LOCKED_v1`
**Locked at:** 2026-07-05
**Locked by:** founder review (this is the founder ratification line)
**Unlock condition:** founder explicit `UNLOCK` order; otherwise this plan is canon for the lane.

> The honest one-line reframe of the advisor synthesis: you don't lack layers — you lack **cloud-hosted triggers and a dead-man switch**. Two dispatches, two phases, then close the laptop for 48 hours and read the heartbeats from your phone. That test — not any architecture diagram — is the definition of the "live" feeling you're describing. And per this week's doctrine: run that test *while* the 25 offers from §7 are out, because a perfectly self-healing system with zero revenue motion is a beautiful machine idling in neutral.
