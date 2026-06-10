# Agent incident registry

| ID | Date | Severity | Status | Title |
|----|------|----------|--------|-------|
| [INCIDENT-2026-06-06-005](./INCIDENT-2026-06-06-005-always-ask-next-move.md) | 2026-06-06 | **P0** | **closed** | Founder law — always ask next move before action |
| [INCIDENT-2026-06-06-002](./INCIDENT-2026-06-06-002-unauthorized-disk-edits.md) | 2026-06-06 | **P1** | **closed** | Unauthorized disk edits without founder permission |
| [INCIDENT-2026-06-06-003](./INCIDENT-2026-06-06-003-mandatory-sourcea-not-read.md) | 2026-06-06 | **P2** | **closed** | Mandatory SourceA files not read — partial ACK |
| [INCIDENT-2026-06-06-004](./INCIDENT-2026-06-06-004-open-recommendations-not-closed.md) | 2026-06-06 | **P2** | **closed** | Open recommendations — completion overstated |
| [INCIDENT-2026-06-06-001](./INCIDENT-2026-06-06-001-trustfield-scope-bleed.md) | 2026-06-06 | **P0** | **closed** | TrustField scope bleed — agent touched/planned TrustField repeatedly |

**Full summary:** [.cursor/reports/2026-06-06-full-incident-summary.md](../reports/2026-06-06-full-incident-summary.md)

## Severity

| Level | Meaning |
|-------|---------|
| P0 | Wrong company / legal-brand boundary — stop all work until fixed |
| P1 | Committed wrong scope to git — revert + incident |
| P2 | Suggested wrong scope in chat only — memory bump + apology |

## Filing new incidents

Use [SKILL-004](../skills/SKILL-004-incident-when-boundary-crossed.md). Add row above. Bump `MEMORY_LOCKED.yaml`.
