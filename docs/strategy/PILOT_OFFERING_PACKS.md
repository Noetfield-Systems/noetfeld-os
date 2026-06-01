# Pilot offering packs (Bank / Copilot)

**Internal delivery guide** — public scope remains [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md).

---

## Bank Pilot v6.1

| Item | Delivery |
|------|----------|
| Narrative | Read-only governance overlay — no execution authority |
| Demo | [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md) · www `/bank-pilot/` |
| API | Shadow `POST /api/v1/governance/evaluate` with `mode=shadow` |
| Evidence | `audit-export` + RID for E-23 adjacency (not payment rails) |

---

## Copilot Readiness Pack

| Item | Delivery |
|------|----------|
| Narrative | M365 Copilot policy alignment — pre-execution |
| Intake | `/trust-brief/intake/?vector=copilot-governance` |
| API | Evaluate Copilot-typed actions in shadow mode |
| Evidence | Policy refs in evaluate response + ledger export |

---

## Shared technical path

1. Intake → **RID** (`operations@noetfield.com`)
2. Production: `platform.noetfield.com` — [GOVERNANCE_PILOT_RUNBOOK.md](../GOVERNANCE_PILOT_RUNBOOK.md)
3. Trust Brief export: `./scripts/trust_brief_audit_export.sh`

**Not in scope:** custody, routing, settlement, PSP registration claims on Noetfield surfaces.
