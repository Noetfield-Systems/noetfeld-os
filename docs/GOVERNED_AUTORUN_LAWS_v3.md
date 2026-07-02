# Governed Autorun Laws v3

**Authority:** NOETFELD-OS runtime · applies to all autorun/loop work in `noetfeld-os`  
**Skill:** `.cursor/skills/governed-autorun/SKILL.md` (canonical L1–L13)  
**Schema refs:** `.cursor/skills/governed-autorun/references/receipt-schemas.md`  
**Determinism:** `.cursor/skills/governed-autorun/references/deterministic-loops.md` (D1–D8)  
**Gap audit:** `receipts/proof/noos-determinism-gap-audit-v1.json`  
**CI gate:** `scripts/verify_loop_determinism_external_v1.py` · `make determinism-verify`  
**Upgrade planes:** `data/noos-upgrade-planes-v1.json` · `make planes` · `docs/_NOOS_AGENT/[NOOS-AGENT-20260702-028]_TEN_UPGRADE_PLANES_v1.md`

Operating system for continuous, parallel, self-improving multi-sandbox execution. v2 adds ROI governance (L11). v3 adds deterministic loop core (L13, D1–D8).

---

## The Thirteen Laws

### L1 — ONE reconciler

One control authority per sandbox. New supervisors/registries extend the existing reconciler or emit desired-state artifacts it consumes. Independent run/lock/state authority = rejected at spec.

In NOOS: `phase_reconciler_v1` (SourceA) remains sole control authority. The autorun dashboard (`scripts/autorun_status_v1.py`) is **read-only**.

### L2 — IDLE_NO_WORK is healthy

Empty queue → `IDLE_NO_WORK` receipt. Never manufactured work, never fake PASS, never silence.

States: `RUNNING` · `IDLE_NO_WORK` · `BLOCKED_WITH_REASON` · `COMPLETE` · `FAILED_WITH_RECEIPT` · `TRIAGE_REQUIRED` · `THROTTLED_ROI`.

### L3 — No decision without a reason

Every gate emission = `{decision, reason, evidence: command + output}`. Bare NO/BLOCKED is malformed.

### L4 — Verify from outside

PASS is valid only from a probe the building agent does not control: external runner, raw public hostname, redirects OFF, content markers + FULL-body hash, ≥60s after deploy.

**Cron proof:** GitHub Actions runs with `event=schedule` on `main`. Manual `workflow_dispatch` and local `make` runs do **not** count as autonomous proof.

**Schedule proof sink:** Every `noos-factory-autorun.yml` run self-registers `{run_id, event, conclusion, at}` into Supabase `noetfield_truth_log`. `make schedule-verify` reads Supabase only (no GitHub API polling). Private-repo cron lags 10–30+ min; absence in a short window is not failure evidence.

### L5 — Verifier freeze

A failing agent fixes the system, never the test. Weakening a failing check = BLOCKED until founder approves.

### L6 — Commit before deploy

Deploys run from a clean committed SHA. Receipts live in the repo, never home directories. Branches must land on `main` before any schedule claim.

**Proof vs runtime receipts:**

| Tier | Path | Use |
|------|------|-----|
| **Proof** | `receipts/proof/` or Supabase | Migration apply, schedule proof, VERIFIED-window, determinism gate |
| **Runtime** | `.noos-runtime/` | Cycle churn, heartbeat mirrors — never cite as closeout evidence |

Proof-grade writers: `apply_supabase_migration_v1.py`, `verify_noos_github_schedule_v1.py`, `open_noos_verified_window_v1.py`, `verify_loop_determinism_external_v1.py`.

### L7 — Founder items never block, never vanish

Status `founder_blocked` (never `cancelled`), present in every cycle receipt with count/oldest/priority/age.

### L8 — Sinks are acked or blocked

Invariant per cycle: `Σ(origin counts) == sink_count`, provenance-tagged per row.

### L9 — Fail-closed refill

0 admitted is valid and reportable.

### L10 — Cross-sandbox reads via shared sink only

NOOS reads SourceA state via Supabase (`portfolio-spine` profile) only — never SourceA repo or `~/.sina` disk.

### L11 — Every cycle has a cost; every loop earns its keep

Each cycle receipt carries `cost` and `value_class`. >30% `none` spend → `THROTTLED_ROI`.

### L12 — Drift is detected, not discovered

Heartbeat compares deployed truth to committed truth (config, worker version, cron, routes, migrations).

### L13 — Loops are deterministic

Same inputs → same transitions → same receipts. Full rules: `.cursor/skills/governed-autorun/references/deterministic-loops.md` (D1–D8).

---

## Deterministic loop core (D1–D8)

| Rule | Requirement | Module |
|------|-------------|--------|
| D1 | Idempotency `op_key` on every side effect | `scripts/noos_loop_determinism_v1.py` |
| D2 | Single writer + CAS advance | `cas_advance()` — wire in runner (pending) |
| D3 | IDs from max(actual)+1 | cycle_number from state file — partial |
| D4 | Advance := execute ∧ validate ∧ sink_ack | `advance_state()` in loop runner |
| D5 | Event log truth; state = fold(events) | `fold_cycle_events()` + replay test |
| D6 | Time/random at scheduling edge only | partial — `trigger_source` recorded |
| D7 | LLM proposal only | N/A (no LLM in loop runner) |
| D8 | Verify pure function | `verify_loop_determinism_external_v1.py` |

**CI determinism gate (UPG-0214):** `pytest tests/test_loop_determinism_ci.py` via `make determinism-verify` in `gel-ci.yml`.

---

## Parallel orchestration, cycle anatomy, Kaizen, audit pass

See `.cursor/skills/governed-autorun/SKILL.md`.

---

## Dispatch template (sandbox agents)

```text
Laws in force: governed-autorun L1–L13. Violations = BLOCKED.
Verify: external runner only (L4). Meter: cost on every receipt (L11).
```

---

## Bootstrapping a new loop

1. Registry entries consumed by existing reconciler (L1)
2. Read-only status integration
3. 2+ consecutive `schedule` success runs on the **same workflow**
4. External verifier (L4) + cost metering (L11) before write/deploy authority
5. 24h zero-manual window green · determinism gate green (L13)

A loop is **DECLARED** until 24h VERIFIED + determinism gate pass.

---

## NOOS loop specialist

See `.cursor/agents/noetfield-os-loop-specialist.md`.
