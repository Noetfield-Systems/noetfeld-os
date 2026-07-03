# [NOOS-AGENT-20260703-007] Tool Broker v1

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-007
doc_type: TOOL_BROKER
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — kernel tool execution wall
-->

**Status:** ACTIVE · 2026-07-03  
**Module:** `scripts/noos_tool_broker_v1.py` (kernel submodule)

## Law (M1–M5)

| Rule | Implementation |
|------|----------------|
| M1 Broker = kernel module | Healer L2 + P1 invoke `broker.invoke` only |
| M2 Allowlist-only | No shell strings; egress deny-all except git remote |
| M3 Git branch wrappers | `open_pr_task_branch`, `git_push_task_branch` + pattern |
| M4 Tainted commits | `data/tainted-commits-v1.json` founder-append-only |
| M5 Aider | `config/aider-broker-v1.yml` — shell off; `aider_auto_commit` wrapper |

Denylist reference (docs only): `docs/_NOOS_AGENT/TOOL_BROKER_DENYLIST_REFERENCE_v1.md`

## Commands

```bash
python3 scripts/noos_tool_broker_v1.py invoke --agent-id healer-l2 --tool grep --params '{"pattern":"kernel","path":"scripts"}' --json
make broker-invoke AGENT_ID=healer-l2 TOOL=git_status PARAMS='{}'
pytest -q tests/test_noos_tool_broker_v1.py
```

## Acceptance

Negative-proof tests per forbidden class in `tests/test_noos_tool_broker_v1.py` (isolated git fixture) — run before cycle 1.
