# Noetfield plan library (1000 plans)

**Lane:** `noetfield_cloud` · **Thread:** THREAD-PORTFOLIO  
**Use when:** Founder or agent says **PLAN WITH NO ASF** — do not wait for ASF; pick from agent-ready backlog.

## Start here

| File | Purpose |
|------|---------|
| [../NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md](../NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md) | **LOCKED** — 1000 prompt pack master index |
| [PROMPT_PACK_LOCKED/](./PROMPT_PACK_LOCKED/) | GTM 100, agent ops 50, drift 100, tier gates, sources |
| [no-asf/QUICK_PICK.md](./no-asf/QUICK_PICK.md) | **PLAN WITH NO ASF** — `make pick-wise` (v14 WISE) |
| [BRIDGE_NF_PLAN_TO_NF_FUTURE.json](./BRIDGE_NF_PLAN_TO_NF_FUTURE.json) | NF-PLAN ↔ nf-future crosswalk |
| [INDEX.md](./INDEX.md) | Counts, phase/tier map |
| [registry.json](./registry.json) | All 1000 plans (machine-readable, v2 prompt-ready) |
| [by-phase/](./by-phase/) | 100 plans per phase P0–P9 |
| [by-tier/](./by-tier/) | 200 plans per tier T1–T5 |

## Phases (P0–P9)

| Phase | Theme |
|-------|--------|
| P0 | Foundation — ship, dev stack, ops, CI |
| P1 | Trust Ledger — TLE, evidence, export |
| P2 | Governance API — evaluate, audit, pilot |
| P3 | Connectors live — Purview, Entra, M365 |
| P4 | Workspace & GTM — UI, www |
| P5 | Enterprise — tenant, RBAC, KMS |
| P6 | Compliance — retention, SOC narratives |
| P7 | Customer & demo GTM — outreach, rehearsal |
| P8 | Integrations — MSB, partners |
| P9 | Horizon — research, ML confidence |

## Tiers (T1–T5)

| Tier | Horizon |
|------|---------|
| T1 | Critical — revenue / prod ship |
| T2 | Near-term — 1–2 sprints |
| T3 | Medium — quarters 2–4 |
| T4 | Strategic — 12–24 months |
| T5 | Horizon — experimental |

## Update policy (agents must follow)

**Registry 1000/1000 done** in [INDEX.md](./INDEX.md) means the NF-PLAN grid is fully enumerated — **not** that shipping is finished. Active execution: [os/plan.json](../../os/plan.json) · [no-asf/GTM_NEXT.md](./no-asf/GTM_NEXT.md) · `make pick-wise`.

1. **After each ship session** — sync done status from plan.json:
   ```bash
   python3 scripts/sync-prompt-pack-status.py
   ```
2. **Regenerate pack** (only when structure changes):
   ```bash
   python3 scripts/generate-prompt-pack-v2.py
   python3 scripts/sync-prompt-pack-status.py
   ```
3. **Do not** delete the registry; append status changes only.
4. **ASF-only** items have `"asf_only": true` in registry — skip for no-ASF plans.
5. Align active execution with [os/plan.json](../../os/plan.json) and [lane_a_sprint_map.md](../lane_a_sprint_map.md); use this library for **long-term** backlog.

## Relation to SourceA

- Desktop canonical index: `~/Desktop/SourceA/founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md`
- This directory is the **in-repo** long-term plan bank for cloud agents.
- Never copy registry to SourceA (direction: SourceA → `ops/private/` only).
