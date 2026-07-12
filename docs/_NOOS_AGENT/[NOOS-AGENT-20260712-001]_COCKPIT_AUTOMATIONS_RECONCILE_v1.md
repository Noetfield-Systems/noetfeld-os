<!--
NOOS-AGENT-DOC
agent_id: claude-code-noos
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260712-001
doc_type: COCKPIT_AUTOMATIONS_RECONCILE
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
lock_state: DRAFT_v1
status: SUBMITTED for independent verification
canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1
-->

# Cockpit Automations Reconcile v1 — Claude scheduled automations vs NOOS doctrine

**Lane:** `NOOS-LANE-cockpit-automations` · **Date:** 2026-07-12 · **Author:** claude-code-noos
**Verdict style:** SUBMITTED for independent verification (no self-issued PASS).

## 1. Incident — dead-path failures (repaired)

~11 Claude (Cowork) automations against `noetfeld-os` failed every run with
`Failed to read current branch from /Users/sinakazemnezhad/Projects/noetfeld-os: No such file
or directory`. Root cause: automations were configured against the retired Projects clone
(classified DIVERGED in `noetfield-org/NOOS_CONTROL_PANEL_AUTHORITY_REPORT_2026-07-04.md`);
`~/Projects` was deleted in the 2026-07-09 local cleanup.

**Repair (2026-07-12):** `~/Projects/noetfeld-os` recreated as a symlink →
`/Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS` (canonical control panel).
Verified: `git -C ~/Projects/noetfeld-os` resolves to canon `main`. Effect: the retired path
now *is* canon — the fragmentation risk is closed, and all automations heal without touching
their stored configs. Rollback: `rm ~/Projects/noetfeld-os`.

## 2. Portfolio classification — all cockpit-class, none executor-class

The ~21 Claude automations (integrator arbitration, integrator sync audit, bug triage,
implementation planner, PR readiness, deployment boundary, evidence pack audit, proof demo
audit, runtime contract review, release readiness, test+package audit, commercial unblock,
daily: autorun status / production surfaces / proof drift / repo health, weekly: workflow
effectiveness / security dependency / roadmap reconciliation / docs integrity / upgrade
sweep / live sync gate) are **all read-only audits, digests, or arbitration** — T3 cockpit
class. Several map 1:1 to rows already registered in `data/noos-parallel-agent-registry-v1.json`
(cursor-daily-autorun-status, cursor-daily-production-surfaces, cursor-daily-proof-drift,
cursor-weekly-*). None dispatch the motor; none violate L-P4 (machines own execution; the
cockpit reads receipts). **KEEP ALL. No automation is an executor of daily tasks.**

## 3. Gap closed — the ONE founder digest

`docs/NOETFIELD_COHERENT_SYSTEM_SPEC_v1.md`: *"FOUNDER SURFACE: one daily brain digest …
One artifact replaces reading N agent reports."* No automation provided it. Added:

- **`noos-founder-cockpit-digest`** — Claude scheduled task, cron `0 7,19 * * *` (local,
  morning + evening), strictly read-only, composes one ≤40-line digest:
  COMPLETED / FAILED→MACHINE / LIVE (PRs+CI+motor) / FOUNDER GATES PENDING (only ask) /
  COST. Delegates all machine proof to registered loops+witnesses (L-P4); labels stale
  receipts STALE_DATA; reports DEGRADED honestly; issues no verdicts.
- Observe-first sequencing honored (spec P5): digest runs READ+DIGEST only. Any dispatch
  authority (P6) is founder-gated and not requested here.
- **Proposed registry row** (founder-gated `data/*.json` change, NOT applied):
  `claude-founder-cockpit-digest` · plane T3 read-only · cadence 2×daily ·
  `delegates_machine_to`: gha-self-heal-autorun-step, gha-noos-surface-loop,
  gha witnesses (health/motor-sustain/liveness/spine/observe) · mutex: none (read-only).

## 4. Founder decision surfaced (not processed)

`data/noos-integrator-role-v1.json`: *"NOOS Copilot … may not run recurring Copilot
automation."* The Copilot account currently carries recurring NOOS automations.
Options (founder gate): (a) retire Copilot recurring automations and keep the Claude
cockpit portfolio as the single T3 automation surface, or (b) amend the role registry
(founder-gated edit). No action taken — surfaced per L7.

## 5. Consolidation candidate (later, founder call)

Once `noos-founder-cockpit-digest` runs clean for 3 days (spec P5 criterion), the three
narrow dailies (autorun status, production surfaces, proof drift) become candidates for
consolidation into the unified digest to reduce N-report reading — their machine-proof
owners are unaffected either way.

## 6. Evidence

- Receipt: `receipts/proof/noos-cockpit-automations-reconcile-v1.json`
- Doctrine basis: `.claude/noos/SYSTEM_IDENTITY.md`, `.claude/noos/RUNTIME_MAP.md`,
  `.claude/noos/PROJECT_RULES.md`, `docs/GOVERNED_AUTORUN_LAWS_v3.md` (L1, L2, L7, L-P4),
  `docs/NOETFIELD_COHERENT_SYSTEM_SPEC_v1.md`, `data/noos-parallel-agent-registry-v1.json`,
  `data/noos-integrator-role-v1.json`, `data/noos-gha-secondary-witness-manifest-v1.json`.

LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
