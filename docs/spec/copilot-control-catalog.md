# Copilot Governance — Control Catalog (v1)

Design-first control test procedures for **Copilot QuickScan** and **Readiness** narratives. Maps to `packages/schemas/control.schema.json` and evaluate `reason[]` via `evaluate_reason_map`.

## COP-DLP-001 — Data loss prevention alignment

| Field | Value |
|-------|--------|
| Domain | `copilot_oversharing` |
| Severity | high |
| Evaluate reason map | `pii_exposure`, `unverified` |

**Test procedure**

1. Export M365 DLP policy summary (read-only connector or manual upload).
2. Run QuickScan intake with `metadata.pii_exposure=true` if gaps found.
3. Confirm evaluate returns `review` or `deny` with RID; attach export to evidence bundle.

## COP-SCOPE-002 — Copilot scope and workload boundary

| Field | Value |
|-------|--------|
| Domain | `copilot_oversharing` |
| Severity | medium |
| Evaluate reason map | `Context is minimal`, `unknown` |

**Test procedure**

1. Document licensed Copilot workloads (Teams, M365 apps).
2. Submit evaluate with action `copilot_publish` and context describing scope.
3. Verify `control_id` citation in readiness report (when pack bound).

## COP-PII-003 — PII exposure before agent execution

| Field | Value |
|-------|--------|
| Domain | `copilot_oversharing` |
| Severity | critical |
| HITL | yes |
| Evaluate reason map | `pii_exposure`, `Human review required` |

**Test procedure**

1. Flag sample oversharing scenario in QuickScan.
2. Require dual approval per `docs/spec/rbac-approval-matrix.md` before workflow `approved`.
3. Ledger write only after signoff → `audit_events`.

## COP-AUDIT-004 — Append-only audit trail

| Field | Value |
|-------|--------|
| Domain | `evidence_retention` |
| Severity | high |

**Test procedure**

1. `POST /evaluate` with `X-Tenant-ID: copilot-pilot-01`.
2. `GET /audit/export` — every row has `tenant_id` and `integrity_hash`.
3. Confirm no UPDATE/DELETE path in governance-console API.

## COP-EXPORT-005 — Exportable diligence bundle

| Field | Value |
|-------|--------|
| Domain | `evidence_retention` |
| Severity | medium |

**Test procedure**

1. Run `scripts/trust_brief_audit_export.sh` or `/audit/export`.
2. Redact PII for design-partner sample under `docs/diligence/`.
3. Include policy version and control IDs in bundle manifest.

## Risk linkage

| risk_id | title | controls |
|---------|-------|----------|
| RISK-COP-001 | Uncontrolled Copilot oversharing | COP-DLP-001, COP-SCOPE-002, COP-PII-003 |
| RISK-COP-002 | Non-auditable governance decisions | COP-AUDIT-004, COP-EXPORT-005 |
