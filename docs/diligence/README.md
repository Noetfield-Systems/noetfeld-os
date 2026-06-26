# Bank Pilot — due diligence pack (internal)

**Audience:** Regulated buyers (bank, MSB, enterprise) under NDA.  
**Public positioning:** [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md) · [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md)

---

## Contents (this folder)

| Artifact | Path |
|----------|------|
| **Governance sources (LOCKED)** | [../references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md](../references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md) |
| **Drift detection sources (LOCKED)** | [../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md) |
| Sample audit export (redacted) | [sample-audit-export.redacted.json](./sample-audit-export.redacted.json) |
| OpenAPI (filtered, institutional) | [../api/openapi.json](../api/openapi.json) · live `/openapi.json` on platform |
| RPAA-safe positioning | [rpaa-positioning-onepager.md](./rpaa-positioning-onepager.md) |
| **Competitive landscape (sales)** | [COMPETITIVE_LANDSCAPE_LOCKED_v1.md](./COMPETITIVE_LANDSCAPE_LOCKED_v1.md) |
| Battle card vs Purview | [battlecards/BATTLECARD_VS_PURVIEW_LOCKED_v1.md](./battlecards/BATTLECARD_VS_PURVIEW_LOCKED_v1.md) |
| Battle card vs Credo | [battlecards/BATTLECARD_VS_CREDO_LOCKED_v1.md](./battlecards/BATTLECARD_VS_CREDO_LOCKED_v1.md) |
| Battle card vs Securiti | [battlecards/BATTLECARD_VS_SECURITI_LOCKED_v1.md](./battlecards/BATTLECARD_VS_SECURITI_LOCKED_v1.md) |
| Canadian OSFI E-23 orientation | [CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md](./CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md) |
| Proof case (redacted) | [PROOF_CASE_COPILOT_EVALUATE_TLE_v1.md](./PROOF_CASE_COPILOT_EVALUATE_TLE_v1.md) |
| Procurement competitive FAQ | [../copilot/PROCUREMENT_COMPETITIVE_FAQ_v1.md](../copilot/PROCUREMENT_COMPETITIVE_FAQ_v1.md) |
| Print / board PDF styles | [../../assets/noetfield-print.css](../../assets/noetfield-print.css) · [../collateral/](../collateral/) |
| MSB partner templates | [../../ops/templates/msb/](../../ops/templates/msb/) |
| E-23 vendor evidence API | `GET /api/v1/governance/vendor-evidence` |

---

## Demo path (production)

1. `POST /api/v1/governance/evaluate` with `mode: shadow` and pilot Bearer token.
2. Note `request_id` (RID) in response.
3. `GET /api/v1/governance/audit-export?request_id=RID-…` — or `make trust-brief-export RID=…`.

Runbook: [GOVERNANCE_PILOT_RUNBOOK.md](../GOVERNANCE_PILOT_RUNBOOK.md).

---

## Regenerate OpenAPI

```bash
make generate-openapi
```

Commit `docs/api/openapi.json` when governance routes change.
