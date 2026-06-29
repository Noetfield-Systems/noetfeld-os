# AGENTS.md — noetfeld-os repo

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-AGENTS-MD
doc_type: AGENT_ENTRYPOINT
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
-->

## If you are a Cursor agent in **this repo** (`noetfeld-os`)

0. Read **`docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md`** + **`NOETFIELD_OS_SSOT_v1_LOCKED.md`** + **`PRODUCT_TRUTH.md`**
0b. Commercial / NW1 tasks: also read **`[NOOS-AGENT-20260615-010]_BUSINESS_STRATEGY_PROOF_DENSITY_v1.md`**
0c. Build / upgrade tasks: read **`[NOOS-AGENT-20260615-014]_UPGRADE_PLAN_300_STEPS_v1.md`** + track in **`UPGRADE_MANIFEST.json`**
1. Read **`docs/_NOOS_AGENT/[NOOS-AGENT-20260608-005]_ORIENTATION_START_HERE.md`**
2. Search tagged docs: `grep -r "NOOS-AGENT-DOC" docs/_NOOS_AGENT/`
3. Check `docs/_NOOS_AGENT/MANIFEST.json` for trace IDs before editing any essay or internal note.

### Live sync / nerve gate

- Before claiming current Noetfield live state, run `bash scripts/check_noos_live_sync_gate.sh`. The wrapper refreshes the website live nerve first; do not rely on an old receipt unless you are explicitly doing read-only archaeology.
- The gate is scope-aware. Set `NOOS_LIVE_SYNC_SCOPE=runtime|public|studio|foundation|ecosystem|all` when the task has a narrow focus. Default scope is `ecosystem`.
- This NOOS receipt consumes the fresh website live nerve receipt, SourceA live surfaces, Noetfield GEL/API health, public website health, and Studio Supabase boundary existence.
- `DEGRADED` means the selected scope's required surfaces are usable but warnings remain; do not report "fully green" until warnings are repaired.

### SAVE / LOCK routing in this repo

- If ASF says `SAVE`, `SAVE AND LOCK`, `LOCK`, or `FILE` for Noetfield / Noetfield OS / noetfeld-os work, the file belongs in this repo, not SourceA.
- Agent-authored internal docs go under `docs/_NOOS_AGENT/` with a `NOOS-AGENT-DOC` block, `[NOOS-AGENT-YYYYMMDD-NNN]_` filename prefix, and a `MANIFEST.json` row.
- Product code changes stay in this repo's code paths. Do not save Noetfield implementation docs into `~/Desktop/SourceA/docs/` unless ASF explicitly names that SourceA path.

## If you are a **different** agent (mono, Noetfield Runtime, SourceA, TrustField)

- **Do not** edit `docs/_NOOS_AGENT/**` unless your task explicitly says merge from `NOOS-AGENT-DOC`.
- Use your own tag (`NFRT-AGENT-DOC`, etc.) in your own repo/lane.
- Ecosystem SSOT: `~/Desktop/sourceA/SINA_OS_SSOT_LOCKED.md` (DESIGN plane).

## This repo's role

FastAPI governance decisioning prototype (DELIVERY lane). Isolated from SinaaiRuntime `:8000`.

## Tagged internal references (this agent)

| trace_id | document |
|----------|----------|
| `NOETFIELD-UNIFIED-MASTER-V1` | **Unified Master — read first** |
| `NOETFIELD-OS-SSOT-V1` | **Product SSOT — build/GTM law** |
| `NOOS-AGENT-PRODUCT-TRUTH` | **Live product state** |
| `NOOS-AGENT-20260608-005` | ORIENTATION — session start |
| `NOOS-AGENT-20260615-006` | **90-day execution plan (active)** |
| `NOOS-AGENT-20260529-002` | Business, product & client definition |
| `NOOS-AGENT-20260615-007` | Glossary, plane tags & anti-ICP |
| `NOOS-AGENT-20260608-003` | Ten market success models |
| `NOOS-AGENT-20260529-001` | Governance drift essay |
| `NOOS-AGENT-20260608-004` | 1000-step roadmap |
| `NOOS-AGENT-20260615-008` | noetfield.com/gel URL structure (draft) |
| `NOOS-AGENT-20260615-009` | Pitch & PDF alignment notes |
| `NOOS-AGENT-20260615-010` | **Business strategy — proof density & NW1/SW1 motion** |
| `NOOS-AGENT-20260615-011` | **Founding pilot one-pager — NW1 Copilot attach** |
| `NOOS-AGENT-20260615-013` | **Founding pilot one-pager — SW1 agents attach** |
| `NOOS-AGENT-20260615-012` | **Chain tools — `noetfield gate` / `noetfield decide`** |
| `NOOS-AGENT-20260615-014` | **300-step upgrade plan — UPG-0001–0300** |
