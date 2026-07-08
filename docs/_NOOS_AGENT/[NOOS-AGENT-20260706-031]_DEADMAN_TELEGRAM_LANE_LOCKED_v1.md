<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260706-031
doc_type: DEADMAN_TELEGRAM_LANE_LOCKED
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
lock_state: LOCKED_v1
authority: FOUNDER_GATE_2026-07-06
-->

# Deadman Telegram Lane — LOCKED v1

**Status:** LOCKED · deployed live 2026-07-06  
**PR:** #29 · branch `lane/phase-b-deadman` · head `7dc79d9`

## One law

**NOOS deadman Telegram is a dedicated lane only.** Never @Gateway_A, NF Probe Bot, Signal Factory, Noetfield Ops, or generic `TELEGRAM_*` env vars.

## Locked settings

| Setting | Value |
|---------|--------|
| `telegram_lane.send_alerts` | `false` (default until founder enables dedicated bot) |
| Probe path | `POST /check?telegram=0` only |
| Cron path | sends only when `send_alerts: true` AND bot passes `getMe` forbidden check |
| Deploy | skips `DEADMAN_TELEGRAM_*` upload unless `ALLOW_DEADMAN_TELEGRAM_SECRET_UPLOAD=1` |

## Forbidden bots (hard block)

- `Gateway_A`
- `NFProbeBot` / NF Probe Bot
- `NoetfieldOpsBot`
- Any non-`DEADMAN_TELEGRAM_*` secret name

## Evidence

- Config: `data/noos-deadman-config-v1.json`
- Worker: `cloud/workers/noos-deadman-v1/src/index.js`
- Verifier: `scripts/verify_noos_deadman_telegram_lane_v1.py`
- Receipt: `receipts/proof/noos-deadman-telegram-lane-lock-v1.json`

## GHA note

Loop **execution** is retired from GHA (CF→Railway). PR merge gates (`gel-ci.yml`, `noos-agent-vault.yml`) still trigger on push — unrelated to deadman Telegram.
