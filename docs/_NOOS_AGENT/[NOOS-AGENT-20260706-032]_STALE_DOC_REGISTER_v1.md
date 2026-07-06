<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260706-032
doc_type: STALE_DOC_REGISTER
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
lock_state: LOCKED_v1
-->

# Stale Doc Register v1

**Updated:** 2026-07-06 · **Rule:** Do not execute superseded plans; cite replacement only.

## Current authority (loop / autonomy / deadman)

| Topic | Canonical doc |
|-------|----------------|
| Living System 99 (Phases A–G) | `[NOOS-AGENT-20260705-029]_LIVING_SYSTEM_99_PLAN_LOCKED_v1.md` |
| Deadman Telegram lane | `[NOOS-AGENT-20260706-031]_DEADMAN_TELEGRAM_LANE_LOCKED_v1.md` |
| 48h retro (when run) | `[NOOS-AGENT-20260706-030]_LIVING_SYSTEM_48H_RETRO_v1.md` |
| Loop execution | CF `noos-loop-fleet-tick-v1` → Railway — **GHA schedule retired** |
| Product / GTM | `NOETFIELD_OS_SSOT_v1_LOCKED.md`, `NOOS-AGENT-20260615-010` |
| 300-step upgrades | `NOOS-AGENT-20260615-014` + `UPGRADE_MANIFEST.json` |

## Superseded for loop/autonomy execution

| Doc | trace_id | Superseded by | Notes |
|-----|----------|---------------|-------|
| Three-Track 10-Step Upgrade | `NOOS-AGENT-20260702-025` | `NOOS-AGENT-20260705-029` | Track A GHA schedule wins obsolete |
| Unified Autonomy Upgrade Master | `NOOS-AGENT-20260702-027` | `029` + backlog JSON | Backlog still useful; autonomy steps use 029 |
| Ecosystem Next Plan LOCKED | `NOOS-AGENT-20260702-024` | Partial — PyPI/commercial rows still valid | Loop rows → 029 |
| System Fix 100-Plan | `NOOS-AGENT-20260629-022` | Audit register — do not re-open closed items | Reference only |
| Governed Autorun Laws v2 | `docs/GOVERNED_AUTORUN_LAWS_v2.md` | `GOVERNED_AUTORUN_LAWS_v3.md` | Already marked superseded |

## Stale claims to ignore

- GHA `schedule` as primary loop trigger (retired 2026-07-05)
- `telegram_ready` without `telegram_send_alerts` (use 031 lane law)
- Telegram to @Gateway_A, NF Probe Bot, or Noetfield Ops for deadman
- `founder confirms alert reaches phone` before dedicated deadman bot configured
- PR merge blocked = loops broken (GHA billing ≠ CF/Railway motor)

## 90-day plan scope

`NOOS-AGENT-20260615-006` remains active for **GEL product / pilot / commercial** tracks. **Loop autonomy execution** defers to Living System 99 (029).
