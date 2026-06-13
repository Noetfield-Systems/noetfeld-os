# Readiness → Record Mapping (MSP v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `[NF-LOCAL-REPO-AGENT]` |
| **Doc id** | `noetfield-msp-readiness-to-record-v1` |
| **Parent** | [MSP_GOVERNANCE_PACK_v1.md](./MSP_GOVERNANCE_PACK_v1.md) |
| **Updated** | 2026-06-02 |

**Purpose:** Map Copilot **readiness assessment** outputs (Microsoft OSS tool or manual) to **Phase 2** Noetfield Governance Pack scope and SKU triggers.

**Sources:**

- [Microsoft — m365-copilot-automated-readiness-assessment](https://github.com/microsoft/m365-copilot-automated-readiness-assessment) (CSV/Excel export columns)

---

## 1. Assessment export fields (Microsoft OSS tool)

| Export column | Example values | Phase 1 owner | Phase 2 action |
|---------------|----------------|---------------|----------------|
| **Service Area** | M365, Entra, Defender, Purview, Copilot Studio | MSP | Scope evidence connectors |
| **Feature** | Licensing, Security, Compliance, Governance | MSP | Map to TLE metadata |
| **Status** | Compliant, Warning, Not Configured | MSP | See priority table below |
| **Priority** | High, Medium, Low | Both | High → defer Copilot or pilot only |
| **Observation** | Free text finding | MSP | Attach to Trust Brief / SOW |
| **Recommendation** | Remediation step | MSP | Phase 1 work order |

**Import orientation:** Timestamped CSV (e.g. `m365_recommendations_YYYYMMDD.csv`) stored by MSP; tenant ID + file hash handed to Noetfield at Phase 2 kickoff.

---

## 2. Status → Phase 2 trigger matrix

| Readiness status | Priority | Copilot enable? | Noetfield SKU |
|------------------|----------|-----------------|---------------|
| Not Configured | **High** (Purview/DLP/labels) | **No** — remediate first | Defer; optional Trust Brief only |
| Warning | **High** | **Pilot only** — named users | Governance Pack **limited** pilot |
| Warning | Medium | Phased dept rollout | Governance Pack **standard** |
| Compliant | Low | Scale with receipts | Governance Pack + **Monitor MRR** |
| Compliant | — + Studio agents | Per-agent evaluate | Governance Pack + **agent add-on** |

---

## 3. Service area → evidence connector map

| Service area | Readiness domain | Noetfield connector (metadata) | TLE evidence ref |
|--------------|------------------|-------------------------------|------------------|
| **Purview** | Labels, DLP, retention | `m365-purview` | Label policy summary ID |
| **Entra** | CA, MFA, guest policies | `m365-entra` | CA policy IDs |
| **Defender** | Endpoint, OAuth apps | Orientation | Audit export slice |
| **M365** | Licensing, Copilot seats | Intake metadata | License count field |
| **Copilot Studio** | Agent inventory | Evaluate per agent | Agent RID |
| **Power Platform** | Environment DLP | Orientation | Customer attestation |

---

## 4. High-priority gaps → Phase 1 SOW lines (MSP revenue)

| Finding (typical) | MSP deliverable | Before Phase 2 |
|-------------------|-----------------|----------------|
| No sensitivity labels | Label design + auto-apply | Required |
| DLP not Copilot-aware | DLP policy pack | Required |
| Guest oversharing | Access review + remediation | Required |
| No CA for Copilot users | CA baseline | Required |
| Copilot licensed without Purview Suite | Purview Suite attach (promo thru Jun 30, 2026) | Recommended |
| No readiness re-run process | Quarterly assessment cadence | Recommended for MRR |

---

## 5. Phase 2 kickoff payload (minimum)

| Field | Source | Required |
|-------|--------|----------|
| `tenant_id` | Azure AD | Yes |
| `customer_legal_name` | MSP CRM | Yes |
| `readiness_report_uri` or CSV hash | Assessment tool | Yes |
| `readiness_date` | Report timestamp | Yes |
| `copilot_seats_licensed` | M365 admin | Yes |
| `copilot_enabled_users` | Actual enable count | Yes |
| `phase1_exception_signoff` | Customer if High items waived | Conditional |
| `msp_partner_id` | Noetfield partner registry | Yes |
| `primary_approver_email` | Customer | Yes |

---

## 6. Readiness → Governance Pack scope mapper

| Pilot tier | Criteria | Price band | NF deliverables |
|------------|----------|------------|-----------------|
| **Limited** | High warnings waived · ≤25 Copilot users | $2k–4k | Evaluate + 1 TLE + export |
| **Standard** | Compliant or medium only · dept rollout | $4k–7k | Evaluate + 3 TLE + board PDF |
| **Scale** | Multi-dept · Studio agents | $7k–10k | Evaluate + agent receipts + ZIP |

*MSP sets end-customer price; wholesale per [MSP_GOVERNANCE_PACK_v1.md](./MSP_GOVERNANCE_PACK_v1.md).*

---

## 7. Recurring Readiness → Record (MRR)

| Cadence | MSP activity | NF activity |
|---------|--------------|-------------|
| **Monthly** | Monitor Purview drift | Evaluate on material changes |
| **Quarterly** | Re-run readiness assessment | TLE refresh export for QBR |
| **Annual** | License true-up | Procurement ZIP update |

---

## 8. Sample handoff record (orientation)

```yaml
handoff:
  tenant_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  readiness:
    tool: "microsoft-oss-assessment"
    report_hash: "sha256:..."
    report_date: "2026-06-01"
    summary:
      high: 0
      medium: 2
      low: 14
  copilot:
    seats_licensed: 50
    users_enabled: 12
  pilot_tier: standard
  msp_partner_id: "msp-example-bc"
  phase1_signoff: "customer-vcio@example.com"
```

---

## 9. Limits

- Noetfield does not run Phase 1 assessments or deploy Purview policies.
- CSV import to workspace is **orientation** — automated ingest API is a future plan (442).
- Readiness tools vary by vendor; map by **Priority + Service Area**, not exact row count.
- Single-tenant Copilot boundary applies to every tenant separately.

---

## 10. Related

| Doc | Role |
|-----|------|
| [PHASE1_PHASE2_RACI_v1.md](./PHASE1_PHASE2_RACI_v1.md) | Who owns each step |
| [copilot-readiness-pilot-runbook.md](../spec/copilot-readiness-pilot-runbook.md) | Design-partner E2E |
