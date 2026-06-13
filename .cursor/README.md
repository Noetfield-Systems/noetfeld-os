# Cursor agent layer (Noetfield)

**Doc hub:** [../docs/DOC_UNIFIED_INDEX_LOCKED_v1.md](../docs/DOC_UNIFIED_INDEX_LOCKED_v1.md)

## Session start (in order)

1. [agent-memory/MEMORY_LOCKED.yaml](./agent-memory/MEMORY_LOCKED.yaml) — hard rules R-001–R-011 · **packaging_v16**
2. [../docs/WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](../docs/WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) — sandbox funnel · tiers · agentic
3. [incidents/REGISTRY.md](./incidents/REGISTRY.md) — open incidents
4. [AGENT_TRACKING.md](./AGENT_TRACKING.md) — task priority
5. [../docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](../docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md)

**Pick next task:** `make pick-wise` · **Inbox:** [COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md](../docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md)

## Skills

| ID | File | When |
|----|------|------|
| SKILL-001 | [skills/SKILL-001-scope-gate-before-work.md](./skills/SKILL-001-scope-gate-before-work.md) | Before any work — Noetfield scope |
| SKILL-002 | [skills/SKILL-002-pre-commit-audit.md](./skills/SKILL-002-pre-commit-audit.md) | Before commit |
| SKILL-003 | [skills/SKILL-003-session-end-report.md](./skills/SKILL-003-session-end-report.md) | Session end |
| SKILL-004 | [skills/SKILL-004-incident-when-boundary-crossed.md](./skills/SKILL-004-incident-when-boundary-crossed.md) | Boundary crossed |
| SKILL-005 | [skills/SKILL-005-doc-tagging.md](./skills/SKILL-005-doc-tagging.md) | Agent-written docs |
| SKILL-006 | [skills/SKILL-006-ask-before-implement.md](./skills/SKILL-006-ask-before-implement.md) | Default ask-first |
| SKILL-007 | [skills/SKILL-007-auto-conflict-resolution.md](./skills/SKILL-007-auto-conflict-resolution.md) | Rule conflicts |
| SKILL-008 | [skills/SKILL-008-agentic-commercial-boundary.md](./skills/SKILL-008-agentic-commercial-boundary.md) | Commercial / no auto-run |

## Rules (always-on highlights)

| Rule | File |
|------|------|
| Read order | [rules/noetfield-read-order.mdc](./rules/noetfield-read-order.mdc) |
| Scope | [rules/noetfield-scope.mdc](./rules/noetfield-scope.mdc) |
| Ask before edit | [rules/noetfield-ask-before-edit.mdc](./rules/noetfield-ask-before-edit.mdc) |
| No ASF plans | [rules/noetfield-no-asf-plans.mdc](./rules/noetfield-no-asf-plans.mdc) |
| Ship first | [rules/noetfield-ship-first.mdc](./rules/noetfield-ship-first.mdc) |
| Self audit | [rules/noetfield-self-audit.mdc](./rules/noetfield-self-audit.mdc) |

## Verify before commit

```bash
make verify-agent-scope
make verify-doc-ssot
```
