# RBAC + Approval Matrix (v1 — markdown policy)

Enforced in code incrementally; Copilot pilot uses config + workflow HITL first.

| Action | Role | Approval |
|--------|------|----------|
| `governance.evaluate` | compliance_analyst | none (shadow) |
| QuickScan signoff | compliance_owner | single_human |
| Readiness pack approve | compliance_owner + exec_sponsor | dual_human |
| Policy pack bind | policy_admin | dual_human |
| Agent publish / ledger write | governance_admin | dual_human + `verification_status=verified` |
| Audit export (full) | compliance_owner | single_human |
| Payment / transfer (any) | — | **denied (Lane C)** |

## Severity → HITL

| risk_score | decision | HITL |
|------------|----------|------|
| &lt; 40 | allow | optional |
| 40–69 | review | single_human |
| ≥ 70 | deny | dual_human to override |

## Tenant isolation

All roles scoped by `tenant_id` / `X-Tenant-ID`. Pilot slug: `copilot-pilot-01`.
