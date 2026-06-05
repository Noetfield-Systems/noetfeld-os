# SKILL-004 — File incident when boundary crossed

**When:** Agent planned, implemented, committed, or repeatedly suggested work outside Noetfield scope.

## Steps

1. **Stop** all work immediately.
2. Create `.cursor/incidents/INCIDENT-YYYY-MM-DD-###-<slug>.md` from this template:

```markdown
# INCIDENT-YYYY-MM-DD-### — <title>
| Severity | P0 / P1 / P2 |
| Status | open |
| Agent | NF-CLOUD-AGENT |

## Summary
<what went wrong>

## Root cause
<why>

## Corrective actions
- [ ] ...

## Prevention
<rule to add to MEMORY_LOCKED.yaml>
```

3. Add row to [.cursor/incidents/REGISTRY.md](../incidents/REGISTRY.md).
4. Add `hard_rules` + `lessons` + `recurring_mistakes` to [MEMORY_LOCKED.yaml](../agent-memory/MEMORY_LOCKED.yaml); bump `version`.
5. If gap in cursor rules → add/update `.cursor/rules/*.mdc`.
6. Apologize once to founder; do not repeat the wrong work.

## P0 triggers (mandatory incident)

- TrustField / trustfield.ca implementation or deploy plan
- VIRLUX work in Noetfield repo
- Committed `ops/private/` or `docs/internal/`
