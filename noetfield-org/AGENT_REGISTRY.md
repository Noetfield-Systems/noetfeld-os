# Agent Registry

Status: active
Plane: L17 org sync

## Registered agent surfaces

Parallel law: `data/noos-parallel-agent-registry-v1.json` · `docs/_NOOS_AGENT/[NOOS-AGENT-20260703-003]_PARALLEL_AGENT_GOVERNANCE_v1.md`

| Agent surface | Tier | Primary role | Write scope | Receipts |
|---|---|---|---|---|
| GitHub Actions | T0 | deterministic execution, CI, schedules, loop ticks | workflow-defined paths only | workflow runs, artifacts, cycle receipts |
| Copilot | T1 | coding agent, repo implementation, machine-safe changes | repo-local branch/worktree | git diff, tests, PR |
| Cursor local | T2 | local operator + fast repo edits | repo-local branch/worktree | git diff, tests, session output |
| Codex | T3 reasoning | architecture, planning, deep reasoning, arbitration support | repo-local branch/worktree | plans, diffs, tests, receipts |
| Cloud integrator | T3 merge | cross-repo sync, arbitration, merge-plane coordination | registry + receipt coordination only | sync receipts, registry updates |

## Shared rules

1. Every agent writes receipts in its own repo lane.
2. The integrator protocol may coordinate ownership, but it does not override repo-local law.
3. T3 roles may reason and route; they do not create a second authority plane.
