---
name: cursor-local-mac
description: Cursor Local Mac T2 operator playbook for noetfeld-os. Use when opening/closing scoped edit lanes on Mac, integrator claims, heartbeat during long sessions, worktree sync, or routing kaizen through worker kernel. Do not use for GHA loops, deploys, verifier edits, or merge without founder gate.
---

# Cursor Local Mac (T2)

Operator card: `docs/_NOOS_AGENT/[NOOS-AGENT-20260703-004]_CURSOR_LOCAL_MAC_OPERATOR_v1.md`  
Subagent: `.cursor/agents/noetfield-os-local-operator.md`

## Session flow

```bash
make local-lane TASK=NOOS-LANE-<id> SCOPE=path1,path2
make local-status
# edit (≤5 files direct; larger → kernel)
make local-heartbeat TASK=NOOS-LANE-<id>
make local-closeout TASK=NOOS-LANE-<id>
```

Copilot CLI on same Mac:

```bash
AGENT_ID=copilot-cli-mac IDE=copilot-cli make local-lane TASK=... SCOPE=...
```

## Commands

| Command | Purpose |
|---------|---------|
| `make local-boot` | Init + register agents + governance checks |
| `make local-lane` | Boot + integrator claim |
| `make local-status` | Human session digest |
| `make local-heartbeat` | Refresh claim before 30m stale |
| `make local-sweep-stale` | Release abandoned lanes |
| `make local-closeout` | pytest + clean tree + complete |
| `make local-patch-proposal` | Kernel T2 sandbox for larger kaizen |

Receipts: `WRITE_RECEIPT=1` on boot or closeout.

## Do NOT

- Deploy (`gha-deploy-noos-cloud-workers`)
- Re-run GHA loops or T3 automation machine delegates (L-P4)
- Edit `scripts/verify_*`, laws docs, registries, `noetfield_gate/`
- Merge PRs without founder gate

## Worktree blocked on main?

```bash
bash scripts/noos_mac_worktree_sync_v1.sh
```
