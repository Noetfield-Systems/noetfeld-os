---
name: governed-autorun
description: Design, run, audit, and repair 24/7 multi-workflow autonomous execution systems — parallel sandboxes, cron loops, queue motors, receipt-backed cycles, ROI-governed spend, and self-improving pipelines under one reconciler. Use this skill whenever the user asks to build or fix autorun loops, cron workers, batch queues, multi-sandbox orchestration, cycle receipts, sink invariants, verification gates, cost/ROI attribution for agents, or says things like "make it run 24/7", "full automation", "parallel workflows", "self-improving system", "where is the spend going", "why did the agent report PASS but live is broken", "audit this agent report", or pastes an agent/worker report for review. Also trigger when writing dispatch prompts for coding agents operating in sandboxes.
---

# Governed Autorun v3

Operating system for continuous, parallel, self-improving multi-sandbox execution. Every law traces to a real production incident. v2 adds the ROI layer: the machine governs its own spend the way it governs its own state. v3 adds deterministic loop core (L13, D1–D8).

## The Thirteen Laws

**L1 — ONE reconciler.** One control authority per sandbox. New supervisors/registries extend the existing reconciler or emit desired-state artifacts it consumes. Independent run/lock/state authority = rejected at spec. Every consolidation report carries `reconciler authority: ONE / DUPLICATE`.

**L2 — IDLE_NO_WORK is healthy.** Empty queue → IDLE_NO_WORK receipt. Never manufactured work, never fake PASS, never silence. States: RUNNING · IDLE_NO_WORK · BLOCKED_WITH_REASON · COMPLETE · FAILED_WITH_RECEIPT · TRIAGE_REQUIRED · THROTTLED_ROI.

**L3 — No decision without a reason.** Every gate emission = `{decision, reason, evidence: command + output}`. Bare NO/BLOCKED is malformed and itself invalid. Summaries derive from actual row IDs; producer output validated against reality post-write, fail closed.

**L4 — Verify from outside.** PASS is valid only from a probe the building agent does not control: external runner, raw public hostname, redirects OFF, content markers + FULL-body hash, ≥60s after deploy. Local dist, same-machine curls, preview URLs = INVALID. Verify-time minus publish-time < 60s = auto-reject.

**L5 — Verifier freeze.** Verifiers and pass criteria are founder-gated. A failing agent fixes the system, never the test. Weakening a failing check = immutability violation = BLOCKED until founder approves the diff. The loop may add brakes; it may never remove or loosen one.

**L6 — Commit before deploy.** Deploys run from a clean committed SHA. Dirty guard fails closed; scoped exceptions only via founder-reviewed `dirty_scope_map`; `dirty_total > cap` → TRIAGE_REQUIRED on every scope. Receipts live in the repo, never home directories.

**L7 — Founder items never block, never vanish.** Status `founder_blocked` (never `cancelled`), excluded from machine scan, present in every cycle receipt with count/oldest/priority/age. Aging founder P0s get louder — escalate in heartbeat after age threshold.

**L8 — Sinks are acked or blocked.** Advance never decouples from sink ack. Retry with backoff; unacked = SHIP fails closed. Invariant per cycle: `Σ(origin counts) == sink_count`, provenance-tagged per row. Never fabricate origin receipts — tag true provenance.

**L9 — Fail-closed refill.** Expansion admits only rows passing the current rubric unmodified. No quantity target lowers the filter. 0 admitted is valid and reportable.

**L10 — Cross-sandbox reads via shared sink only.** No sandbox reads another's disk/repo. Status flows through the shared DB. Rows older than freshness window → STALE_DATA, never guessed.

**L11 — Every cycle has a cost; every loop earns its keep.** Each cycle receipt carries `cost` (provider, model, tokens in/out, unit cost, $ total) and `value_class` (revenue_path · proof_asset · risk_reduction · hygiene · none). Loops report rolling cost-per-COMPLETE and spend-by-value_class in the heartbeat. A loop whose trailing-window spend is >X% `value_class: none` auto-enters THROTTLED_ROI (frequency cut, founder notified) — it does not silently keep burning. Budget caps per workflow; cap breach = BLOCKED_WITH_REASON, not overdraft.

**L12 — Drift is detected, not discovered.** Each heartbeat compares deployed truth to committed truth: live config hash vs repo hash, worker version vs expected, cron last-fire vs schedule, route bindings vs manifest. Any mismatch → DRIFT receipt with the diff. Third disk-vs-live incident happens to someone else.

**L13 — Loops are deterministic.** Same inputs → same transitions → same receipts, replayable from the event log. Idempotency keys on every side effect, single writer + compare-and-swap per state cell, IDs from actuals never inference, advance as a pure function of acks, LLM output as proposal never transition, verification as a pure function. Full rules + legal-transition table: `references/deterministic-loops.md` (D1–D8) — read whenever designing, debugging, or auditing a loop.

## Parallel Orchestration

- **Lanes:** every workflow declares a lane (e.g. sourcea/noos/proof/queue/health/client). Lanes are isolation boundaries — one lane's failure never blocks another's scheduler slot.
- **Concurrency keys:** workflows sharing mutable state share a key; the scheduler runs at most one per key. Keys are declared in the registry, not inferred.
- **Lock ordering:** multi-lock operations acquire in registry order — deadlock prevented by construction. Stale lock = mark, safe-recover, receipt.
- **Priority within a tick:** P0 machine work → P1 → P2 → improvement backlog (§Kaizen). Founder items never occupy a slot (L7).
- **Jitter:** parallel loops on the same cron offset start with 0–60s random jitter — no thundering herd on shared sinks.
- **Backpressure:** sink write latency above threshold → loops shed to half frequency, receipt why. Smooth beats fast.

## Cycle Anatomy (per tick)

1. **Lock** (per-sandbox; ordering per above)
2. **Select** one eligible item or IDLE_NO_WORK
3. **Execute** inside sandbox scope
4. **Meter** — capture tokens/cost at the call site, not estimated after (L11)
5. **Verify** — internal checks may gate advance; only external proves ship (L4)
6. **Ack sink** (L8)
7. **Receipt** — full schema in `references/receipt-schemas.md`
8. **Heartbeat** (daily): all loops, states, sink invariants, cost table, drift check (L12), founder_blocked escalations

## Kaizen — ROI-Ranked Self-Improvement

The improvement backlog is a scored queue, not a wishlist:

1. Any failed check, DRIFT receipt, THROTTLED_ROI event, or audit finding auto-files an improvement candidate: `{diff_summary, expected_effect, expected_roi: (cost_saved + risk_reduced + revenue_unblocked) vs build_cost, rollback_command}`.
2. Classify: `machine_safe` (scoped code, additive checks, new receipts, retries, metering) vs `founder_gated` (verifiers, laws, gates, scope maps, schemas, spend caps — all L5/L6/L11 territory).
3. Each tick with a free improvement slot takes the **highest-expected-ROI** `machine_safe` item — one per cycle, never batched.
4. Apply → external-verify → before/after receipt pair. Any external-check regression = auto-rollback + receipt.
5. `founder_gated` items queue with ROI scores; weekly digest in heartbeat, sorted by ROI, so the founder spends review time where it pays most.

Result: the system converts its own failures into a prioritized, budgeted upgrade queue — and can prove each upgrade paid for itself.

## Auditing an Agent Report (adversarial pass)

- **Timestamp math:** verify − publish < 60s → reject (L4).
- **Self-verification:** agent verified its own work → demand external evidence.
- **Self-contradiction:** report line vs its own JSON (e.g. "heartbeat=yes" beside `no_heartbeat_today`).
- **Prose-as-proof:** "config live", "should work", "expected lag" → demand command + output.
- **Verifier edits in the diff** → L5 violation, hard stop.
- **Non-discriminating checks:** identical hashes across URLs, 200-only on SPA fallbacks, redirect-following on redirect tests.
- **Count/ID math:** contiguous ranges? sums match? gaps evidenced?
- **Cost sanity:** cycles with work but zero metered cost, or cost with no value_class → L11 gap.
- **Determinism gaps:** advance without sink ack, IDs from summaries, LLM prose becoming state → L13/D violation.
- **Spot-check:** public URLs → fetch 1–2 independently before accepting PASS.

## Dispatching Work to Sandbox Agents

```text
<VERB> <scope, ONE sandbox>.

Laws in force: governed-autorun L1–L13. Violations = BLOCKED.

Context: <2–4 lines observable state, receipts cited>

Tasks:
1..n <concrete; each with its own verify command>

Verify: external runner only (L4). Per-check timestamp + output.
Meter: cost fields on every receipt (L11).

Report only: <fixed fields — SHAs, receipts, counts,
before/after, cost table, dirty state>
```

One repo per prompt. ≤3-line reason/goal/outcome header for the founder. Fixed report fields kill narrative padding.

## Bootstrapping a New Loop (observe → control)

1. Registry entries (desired state) consumed by the existing reconciler (L1)
2. Read-only status integration (dashboard row, shared-sink telemetry)
3. Scheduled trigger proven: 2+ consecutive `schedule`-event runs. Manual green ≠ cron green.
4. External verifier wired (L4) + cost metering wired (L11) **before** write/deploy authority
5. 24h zero-manual window: scheduled receipts only, sink invariants every cycle, heartbeat with cost table + drift check present

A loop is DECLARED until its 24h window closes green on external receipts; only then VERIFIED. Reports must state which.
