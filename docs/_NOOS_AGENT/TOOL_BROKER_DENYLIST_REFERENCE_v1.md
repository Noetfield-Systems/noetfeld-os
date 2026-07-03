# Tool Broker — Denylist Reference (documentation only)

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-007
doc_type: TOOL_BROKER_DENYLIST
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — reference only, not enforcement wall
-->

**Not enforced as a wall.** Enforcement is **allowlist-only** named wrappers in `scripts/noos_tool_broker_v1.py`. This document records forbidden classes for audits and negative-proof tests.

## Forbidden classes

| Class | Why blocked | Enforcement |
|-------|-------------|-------------|
| Raw shell strings | Arbitrary command injection | Broker rejects `shell`, `command`, `cmd` params |
| Non-allowlist tool names | Escape hatch | `tool_not_in_allowlist` |
| Network egress (non-git) | Data exfil / uncontrolled deps | `egress_denied` — only `git` remote allowed |
| Push to `main` / `master` | Direct production write | `protected_branch` in `git_push_task_branch` |
| Branch outside task pattern | Scope escape | `branch_pattern_violation` |
| Tainted SHA or descendant | Poisoned history | `tainted_commit` via `data/tainted-commits-v1.json` |
| Aider shell suggestions | Bypass broker | `config/aider-broker-v1.yml` disables shell; use `aider_auto_commit` wrapper |

## Allowed wrappers (allowlist)

`grep` · `check` · `pytest_q` · `git_status` · `git_rev_parse` · `git_log_oneline` · `open_pr_task_branch` · `git_push_task_branch` · `aider_auto_commit`

## Agents bound to broker

- Healer Layer 2 — execute tools **only** via `noos_tool_broker_v1.invoke`
- P1 agents — same

Receipt stream: `noos-tool-broker-receipt-v1` with L11 `cost` fields (shared with worker kernel budget).
