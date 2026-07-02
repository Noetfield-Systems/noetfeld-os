# Governed Autorun Laws v3

**Authority:** NOETFELD-OS runtime · applies to all autorun/loop work in `noetfeld-os`  
**Schema refs:** `docs/governed-autorun/references/receipt-schemas.md`  
**Determinism refs:** `docs/governed-autorun/references/deterministic-loops.md` (D1–D8)

Operating system for continuous, parallel, self-improving multi-sandbox execution. Every law traces to a real production incident. v2 added the ROI layer; v3 adds deterministic loop core (L13).

---

## The Thirteen Laws

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

**Cron proof:** Factory runs self-register `{run_id, event, conclusion, at}` into Supabase `noetfield_truth_log`. `make schedule-verify` reads Supabase only (no GitHub API polling). Private-repo cron lags 10–30+ min; absence in a short window is not failure evidence.

Manual `workflow_dispatch` and local `make` runs do **not** count as autonomous proof.

Local dist, same-machine curls, preview URLs = INVALID. Verify-time minus publish-time < 60s = auto-reject.

### L5 — Verifier freeze

Verifiers and pass criteria are founder-gated. A failing agent fixes the system, never the test. Weakening a failing check = immutability violation = BLOCKED until founder approves the diff.

### L6 — Commit before deploy

Deploys run from a clean committed SHA. Dirty guard fails closed. Receipts live in the repo, never home directories. Branches must land on `main` before schedule claims.

**Proof vs runtime receipts:**

| Tier | Path | Use |
|------|------|-----|
| **Proof** | `receipts/proof/` or Supabase | Migration apply, schedule proof, VERIFIED-window closes |
| **Runtime** | `.noos-runtime/` | Cycle churn, heartbeat mirrors — never cite as closeout evidence |

Proof-grade writers: `apply_supabase_migration_v1.py`, `verify_noos_github_schedule_v1.py`, `open_noos_verified_window_v1.py`.

### L7 — Founder items never block, never vanish

Status `founder_blocked` (never `cancelled`), excluded from machine scan, present in every cycle receipt with count/oldest/priority/age. Aging founder P0s escalate in heartbeat.

### L8 — Sinks are acked or blocked

Advance never decouples from sink ack (D4). Invariant per cycle: `Σ(origin counts) == sink_count`, provenance-tagged per row.

### L9 — Fail-closed refill

Expansion admits only rows passing the current rubric unmodified. 0 admitted is valid and reportable.

### L10 — Cross-sandbox reads via shared sink only

No sandbox reads another's disk/repo. Status flows through the shared DB. Rows older than freshness window → `STALE_DATA`, never guessed.

NOOS reads SourceA via Supabase (`portfolio-spine` profile) only.

### L11 — Every cycle has a cost; every loop earns its keep

Each cycle receipt carries `cost` and `value_class`. Trailing-window spend >30% `none` → `THROTTLED_ROI`.

### L12 — Drift is detected, not discovered

Each heartbeat compares deployed truth to committed truth. Any mismatch → DRIFT receipt with the diff.

### L13 — Loops are deterministic

Same inputs → same transitions → same receipts, replayable from the event log. Idempotency keys on every side effect (D1), single writer + CAS per state cell (D2), IDs from actuals (D3), advance as pure function of acks (D4), LLM output as proposal never transition (D7), verification as pure function (D8).

Full rules + legal-transition table: `docs/governed-autorun/references/deterministic-loops.md`.

Cycle receipts carry `transition_log_tail` (last transition auditable inline).

---

## Parallel orchestration

Lanes · concurrency keys · lock ordering · P0→P1→P2→Kaizen priority · jitter · backpressure (see skill v3).

---

## Cycle anatomy (per tick)

Lock → Select → Execute → Meter (L11) → Verify (L4) → Ack sink (L8) → Receipt → Heartbeat (L12).

---

## Kaizen — ROI-ranked self-improvement

Failed check / DRIFT / THROTTLED_ROI → improvement candidate. One `machine_safe` item per free cycle, highest ROI first.

---

## Dispatch template

```text
Laws in force: governed-autorun L1–L13. Violations = BLOCKED.
Verify: external runner only (L4). Meter: cost on every receipt (L11).
Report only: fixed fields — SHAs, receipts, counts, cost table, dirty state.
```

---

## Bootstrapping a new loop

1. Registry entries consumed by reconciler (L1)
2. Read-only status integration
3. Schedule proof via Supabase truth_log (≥2 `event=schedule` rows)
4. External verifier (L4) + metering (L11) before write/deploy authority
5. 24h zero-manual window → **VERIFIED**

---

## NOOS loop specialist

See `.cursor/agents/noetfield-os-loop-specialist.md`.

**Supersedes:** `docs/GOVERNED_AUTORUN_LAWS_v2.md` (archived pointer only).
