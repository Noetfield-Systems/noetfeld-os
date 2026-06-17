# NF Governance Unification Engine (LOCKED v1)

```yaml
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-17"
status: LOCKED
```

## Purpose

When new rules, docs, or governance prose arrives, run **once per intake**:

```text
INTAKE → INVENTORY → SCORE → MAP → MERGE → ARCHIVE → VERIFY
```

**Policy:** No new alwaysApply cursor rules without founder order + SKILL. New LOCKED docs need `os/NF_SSOT_INVENTORY.json` row + `os/plan.json` locked_reference.

## In-charge registry

| Need | Canonical |
|------|-----------|
| Role picker | `entry/START_HERE_LOCKED_v1.md` |
| Daily boot | `ROUTING_CARD.md` |
| Spine | `docs/ops/NF_GAOS_W0_LOCKED_v1.md` · `docs/ops/NF_GAOS_W1_LOCKED_v1.md` |
| Queue | `os/plan.json` · `os/SHIP_NOW.md` |
| GTM | `docs/ops/plans/no-asf/GTM_NEXT.md` |
| Memory | `.cursor/agent-memory/MEMORY_LOCKED.yaml` |
| Incidents | `.cursor/incidents/REGISTRY.md` |
| Inventory | `os/NF_SSOT_INVENTORY.json` |

## Machine

```bash
python3 scripts/nf_governance_unify_v1.py --scan --json
```

## Intake classes

| Class | Default action |
|-------|----------------|
| Founder order | Execute if explicit |
| New cursor rule | Reject — merge into nf-ship-bundle or skill |
| Duplicate LOCKED doc | MOVED stub → `OLD-VERSIONS/` |
| Product lock bump | Update inventory + plan.json row |

*NF Governance Unification v1 · 2026-06-17*
