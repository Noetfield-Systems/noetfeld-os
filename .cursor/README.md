# Cursor agent layer (Noetfield)

**Doc hub:** [../docs/DOC_UNIFIED_INDEX_LOCKED_v1.md](../docs/DOC_UNIFIED_INDEX_LOCKED_v1.md)

## Session start (NF-GAOS W1)

```bash
make nf-onboard
```

1. [../reports/agent-auto/LIVE-STATUS.md](../reports/agent-auto/LIVE-STATUS.md)
2. [../entry/START_HERE_LOCKED_v1.md](../entry/START_HERE_LOCKED_v1.md)
3. [../ROUTING_CARD.md](../ROUTING_CARD.md)
4. [../docs/ops/NF_GAOS_W1_LOCKED_v1.md](../docs/ops/NF_GAOS_W1_LOCKED_v1.md)

## AlwaysApply rules (4 core)

| Rule | File |
|------|------|
| Authority + scope | [rules/nf-authority-stack.mdc](./rules/nf-authority-stack.mdc) |
| Boot ladder | [rules/nf-routing-card.mdc](./rules/nf-routing-card.mdc) |
| Ask before edit | [rules/noetfield-ask-before-edit.mdc](./rules/noetfield-ask-before-edit.mdc) |
| Ship bundle | [rules/nf-ship-bundle.mdc](./rules/nf-ship-bundle.mdc) |

Retired rules → MOVED stubs (`noetfield-ship-first.mdc`, etc.)

## Verify

```bash
make verify-nf-gaos-w1
make verify-agent-scope
make verify-doc-ssot
```

## Skills

| ID | File | When |
|----|------|------|
| SKILL-001 | [skills/SKILL-001-scope-gate-before-work.md](./skills/SKILL-001-scope-gate-before-work.md) | Before any work |
| SKILL-006 | [skills/SKILL-006-ask-before-implement.md](./skills/SKILL-006-ask-before-implement.md) | Default ask-first |
| SKILL-007 | [skills/SKILL-007-auto-conflict-resolution.md](./skills/SKILL-007-auto-conflict-resolution.md) | Rule conflicts |
| SKILL-008 | [skills/SKILL-008-agentic-commercial-boundary.md](./skills/SKILL-008-agentic-commercial-boundary.md) | Commercial boundary |

## Scoped rules

no-vendor-names · confidential-research · ingest-yaml · agent-doc-tagging · prompt-os-reply · tracking · sina-command-readonly
