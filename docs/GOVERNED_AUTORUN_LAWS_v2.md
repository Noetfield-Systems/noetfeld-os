# Governed Autorun Laws v2

**Authority:** NOETFELD-OS runtime · applies to all autorun/loop work in `noetfeld-os`  
**Schema refs:** `governed-autorun/references/receipt-schemas.md` (cycle, gate, heartbeat, drift)

Operating system for continuous, parallel, self-improving multi-sandbox execution. Every law traces to a real production incident. v2 adds the ROI layer: the machine governs its own spend the way it governs its own state.

---

## The Twelve Laws

### L1 — ONE reconciler

One control authority per sandbox. New supervisors/registries extend the existing reconciler or emit desired-state artifacts it consumes. Independent run/lock/state authority = rejected at spec. Every consolidation report carries `reconciler authority: ONE / DUPLICATE`.

In NOOS: `phase_reconciler_v1` (SourceA) remains sole control authority. The autorun dashboard (`scripts/autorun_status_v1.py`) is **read-only**.

### L2 — IDLE_NO_WORK is healthy

Empty queue → `IDLE_NO_WORK` receipt. Never manufactured work, never fake PASS, never silence.

States: `RUNNING` · `IDLE_NO_WORK` · `BLOCKED_WITH_REASON` · `COMPLETE` · `FAILED_WITH_RECEIPT` · `TRIAGE_REQUIRED` · `THROTTLED_ROI`.

### L3 — No decision without a reason

Every gate emission = `{decision, reason, evidence: command + output}`. Bare NO/BLOCKED is malformed and itself invalid. Summaries derive from actual row IDs; producer output validated against reality post-write, fail closed.

### L4 — Verify from outside

PASS is valid only from a probe the building agent does not control: external runner, raw public hostname, redirects OFF, content markers + FULL-body hash, ≥60s after deploy.

**Cron proof:** GitHub Actions runs with `event=schedule` on `main`. Manual `workflow_dispatch` and local `make` runs do **not** count as autonomous proof.

Local dist, same-machine curls, preview URLs = INVALID. Verify-time minus publish-time < 60s = auto-reject.

### L5 — Verifier freeze

Verifiers and pass criteria are founder-gated. A failing agent fixes the system, never the test. Weakening a failing check = immutability violation = BLOCKED until founder approves the diff. The loop may add brakes; it may never remove or loosen one.

### L6 — Commit before deploy

Deploys run from a clean committed SHA. Dirty guard fails closed; scoped exceptions only via founder-reviewed `dirty_scope_map`; `dirty_total > cap` → TRIAGE_REQUIRED on every scope. Receipts live in the repo, never home directories. Branches must land on `main` before any schedule claim — stranded branches = loop specialist defect.

**Proof vs runtime receipts:**

| Tier | Path | Use |
|------|------|-----|
| **Proof** | `receipts/proof/` or Supabase | Migration apply, schedule proof, VERIFIED-window closes — cite in closeout |
| **Runtime** | `.noos-runtime/` | Cycle churn, heartbeat mirrors, execution state — never cite as closeout evidence |

Proof-grade writers: `apply_supabase_migration_v1.py`, `verify_noos_github_schedule_v1.py`, `open_noos_verified_window_v1.py`.

### L7 — Founder items never block, never vanish

Status `founder_blocked` (never `cancelled`), excluded from machine scan, present in every cycle receipt with count/oldest/priority/age. Aging founder P0s get louder — escalate in heartbeat after age threshold.

### L8 — Sinks are acked or blocked

Advance never decouples from sink ack. Retry with backoff; unacked = SHIP fails closed. Invariant per cycle: `Σ(origin counts) == sink_count`, provenance-tagged per row. Never fabricate origin receipts — tag true provenance.

### L9 — Fail-closed refill

Expansion admits only rows passing the current rubric unmodified. No quantity target lowers the filter. 0 admitted is valid and reportable.

### L10 — Cross-sandbox reads via shared sink only

No sandbox reads another's disk/repo. Status flows through the shared DB. Rows older than freshness window → `STALE_DATA`, never guessed.

NOOS reads SourceA state via Supabase (`portfolio-spine` profile) only — never SourceA repo or `~/.sina` disk.

### L11 — Every cycle has a cost; every loop earns its keep

Each cycle receipt carries `cost` (provider, model, tokens in/out, unit cost, $ total) and `value_class` (`revenue_path` · `proof_asset` · `risk_reduction` · `hygiene` · `none`).

Loops report rolling cost-per-COMPLETE and spend-by-value_class in the heartbeat. A loop whose trailing-window spend is >30% `value_class: none` auto-enters `THROTTLED_ROI` (frequency cut, founder notified).

Budget caps per workflow; cap breach = `BLOCKED_WITH_REASON`, not overdraft.

### L12 — Drift is detected, not discovered

Each heartbeat compares deployed truth to committed truth: live config hash vs repo hash, worker version vs expected, cron last-fire vs schedule, route bindings vs manifest, migration state vs schema.

Any mismatch → DRIFT receipt with the diff.

---

## Parallel orchestration

- **Lanes:** every workflow declares a lane. Lanes are isolation boundaries.
- **Concurrency keys:** at most one per key per tick.
- **Lock ordering:** multi-lock operations acquire in registry order.
- **Priority within a tick:** P0 machine work → P1 → P2 → Kaizen backlog. Founder items never occupy a slot (L7).
- **Jitter:** 0–60s random jitter on shared cron offsets.
- **Backpressure:** sink write latency above threshold → half frequency + receipt.

---

## Cycle anatomy (per tick)

1. Lock
2. Select one eligible item or `IDLE_NO_WORK`
3. Execute inside sandbox scope
4. Meter — capture tokens/cost at call site (L11)
5. Verify — internal checks may gate advance; only external proves ship (L4)
6. Ack sink (L8)
7. Receipt — full schema in receipt-schemas reference
8. Heartbeat (daily): all loops, states, sink invariants, cost table, drift (L12), founder_blocked escalations

---

## Kaizen — ROI-ranked self-improvement

1. Failed check, DRIFT, THROTTLED_ROI, or audit finding → improvement candidate with ROI score.
2. Classify: `machine_safe` vs `founder_gated` (L5/L6/L11 territory).
3. Each free improvement slot: highest-expected-ROI `machine_safe` item — one per cycle.
4. Apply → external-verify → before/after receipt pair. Regression = auto-rollback.
5. `founder_gated` → weekly digest in heartbeat, sorted by ROI.

---

## Auditing an agent report (adversarial pass)

- Timestamp math: verify − publish < 60s → reject (L4)
- Self-verification → demand external evidence
- Self-contradiction in report vs JSON
- Prose-as-proof → demand command + output
- Verifier edits in diff → L5 violation, hard stop
- Non-discriminating checks
- Count/ID math gaps
- Cost sanity: work with zero metered cost
- Spot-check public URLs independently

---

## Dispatch template (sandbox agents)

```text
<VERB> <scope, ONE sandbox>.

Laws in force: governed-autorun L1–L12. Violations = BLOCKED.

Context: <2–4 lines observable state, receipts cited>

Tasks:
1..n <concrete; each with its own verify command>

Verify: external runner only (L4). Per-check timestamp + output.
Meter: cost fields on every receipt (L11).

Report only: <fixed fields — SHAs, receipts, counts, before/after, cost table, dirty state>
```

---

## Bootstrapping a new loop

1. Registry entries consumed by existing reconciler (L1)
2. Read-only status integration
3. Scheduled trigger proven: 2+ consecutive `schedule`-event success runs on the **same workflow** (factory autorun: two consecutive `noos-factory-autorun.yml` runs ~10m apart; canary does not substitute)
4. External verifier (L4) + cost metering (L11) before write/deploy authority
5. 24h zero-manual window green on external receipts

A loop is **DECLARED** until its 24h window closes green; only then **VERIFIED**.

---

## NOOS loop specialist standing assignment

See `.cursor/agents/noetfield-os-loop-specialist.md` for session duties, report template, and close checklist.
