---
name: machine-loops
description: Zero-founder machine loops for noetfeld-os — worker, critic, repair, research, outside audit, autonomy expansion. Use when validating merges without founder, routing failures to repair/critic/research, recording shadow decisions, or retiring founder triggers. Default question — how does the process solve this without Sina?
---

# Machine Loops v1

Canon: `docs/_NOOS_AGENT/[NOOS-AGENT-20260703-005]_FOUNDER_CANON_INTERFACE_v1.md`  
Loops: `docs/_NOOS_AGENT/[NOOS-AGENT-20260703-006]_MACHINE_LOOPS_v1.md`

## Default question

**How does the process solve this without Sina?**

Route to founder only for: capital/legal, irreversible L5, phase unlock — and only with a decision memo attached.

## Commands

```bash
make machine-status
make machine-reconcile
make machine-audit
make machine-verify
make machine-validate-merge
```

## Failure routing

| Signal | Loop |
|--------|------|
| CI/governance fail | repair dispatch via reconcile |
| Critic REJECT | repair lane (fresh context) |
| Critic UNCERTAIN | research memo |
| 2× repair fail | research + outside audit |
| Shadow match ×10 | autonomy expansion proposal |

## Do NOT

- Ask founder to validate normal merges (use `machine-validate-merge`)
- Read receipts manually for approval (use critic loop)
- Dispatch repair from failed agent's chat (R1 — fresh context only)
- Edit `.agent-policy/` or trigger ledger without L5 gate

## Fresh context (R1)

Every loop actor gets: canon pointer line + dispatch JSON + live repo state. Never prior chat or compaction summaries.
