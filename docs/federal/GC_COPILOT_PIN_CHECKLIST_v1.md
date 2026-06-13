# GC Copilot for Work — PIN Compliance Checklist (v1)

| Field | Value |
|-------|--------|
| **Doc id** | `noetfield-gc-copilot-pin-checklist-v1` |
| **Parent** | [FEDERAL_GOVERNANCE_PACK_v1.md](./FEDERAL_GOVERNANCE_PACK_v1.md) |
| **Updated** | 2026-06-02 |

**Source:** [Policy Implementation Notice — Microsoft Copilot for Work](https://www.canada.ca/en/government/system/digital-government/policies-standards/microsoft-copilot-for-work-policy-implementation-notice.html) (TBS, effective **February 1, 2025**).

**Scope lock:** **Unclassified information only.** Protected B/C/S, classified, and NATO information are **out of scope** for Copilot for Work under this PIN. Noetfield orients buyers — departmental CISO and TBS remain authoritative.

**Usage:** Trust Brief discovery · design-partner scoping · TLE evidence index planning. Check `[x]` when verified in tenant; link evidence IDs in Noetfield workspace where applicable.

---

## 1. Eligibility & scope

| # | Requirement | Status | Evidence / notes |
|---|-------------|--------|------------------|
| 1.1 | Copilot used only for **unclassified** GC workflows | ☐ | Departmental data classification sign-off |
| 1.2 | No protected B/C/S, classified, or NATO data in Copilot grounding | ☐ | Purview labels + DLP · sensitivity policy review |
| 1.3 | System listed or planned for **GC AI Register** (if applicable) | ☐ | Register entry URL / draft |
| 1.4 | **AIA** completed or in progress for in-scope AI use | ☐ | See [AIA_TLE_MAPPING_v1.md](./AIA_TLE_MAPPING_v1.md) |
| 1.5 | Copilot for Work — not consumer Copilot or unapproved gen-AI | ☐ | License SKU verification |

---

## 2. Identity & access (Entra ID)

| # | Requirement | Status | Evidence / notes |
|---|-------------|--------|------------------|
| 2.1 | **GC identities only** — no personal Microsoft accounts in production | ☐ | Entra sign-in log review |
| 2.2 | Conditional Access baseline enforced for Copilot users | ☐ | Entra CA policy IDs in evidence index |
| 2.3 | MFA required for Copilot-enabled accounts | ☐ | CA policy · compliance report |
| 2.4 | Guest/B2B access reviewed — Copilot respects guest permissions only | ☐ | Guest inventory · oversharing scan |
| 2.5 | Privileged roles separated from broad Copilot pilot groups | ☐ | Role assignment export (metadata) |

---

## 3. Endpoint & client configuration

| # | Requirement | Status | Evidence / notes |
|---|-------------|--------|------------------|
| 3.1 | **Microsoft Edge** sidebar / enterprise browser controls per PIN | ☐ | Intune or GPO configuration ref |
| 3.2 | Managed devices for Copilot users where required by departmental policy | ☐ | Intune compliance |
| 3.3 | Microsoft 365 Apps current channel per SSC guidance | ☐ | Update ring summary |

---

## 4. Data protection (Purview & M365)

| # | Requirement | Status | Evidence / notes |
|---|-------------|--------|------------------|
| 4.1 | **Sensitivity labels** deployed and applied before broad Copilot rollout | ☐ | Purview label policy IDs |
| 4.2 | **DLP policies** aligned to Copilot data movement | ☐ | Purview DLP rule summary |
| 4.3 | Oversharing remediation — SharePoint/OneDrive/Teams permissions reviewed | ☐ | Readiness assessment output |
| 4.4 | Copilot respects existing permissions — no elevation beyond user access | ☐ | Architecture acknowledgment |
| 4.5 | Retention/lifecycle policies documented for Copilot-adjacent content | ☐ | Purview retention labels |

---

## 5. Licensing & SSC reporting

| # | Requirement | Status | Evidence / notes |
|---|-------------|--------|------------------|
| 5.1 | Valid **Microsoft 365 Copilot** licenses for enabled users | ☐ | License assignment report |
| 5.2 | Enterprise agreement / SSC channel where applicable | ☐ | Procurement record |
| 5.3 | Usage reporting capability for **SSC → TBS** compliance reports | ☐ | Admin center usage export |
| 5.4 | **180-day** M365 E5 / standardized tools implementation timeline tracked (if under E5 PIN) | ☐ | Program plan milestone |

---

## 6. Governance & audit (Noetfield layer)

| # | Requirement | Status | Evidence / notes |
|---|-------------|--------|------------------|
| 6.1 | Operational intent **evaluated before production** policy changes | ☐ | Governance API evaluate log |
| 6.2 | Go/no-go captured in **signed TLE v1** | ☐ | `/workspace/` approved entry |
| 6.3 | Board- or deputy-ready **PDF export** for governance meeting | ☐ | Board pack download |
| 6.4 | **Procurement ZIP** with integrity check (tamper fail closed) | ☐ | `/copilot/procurement/` orientation |
| 6.5 | RID lineage on every engagement milestone | ☐ | Request ID in exports |
| 6.6 | Metadata-only M365 connectors — no payment/custody claims | ☐ | [CANADA_TRUST.md](../api/CANADA_TRUST.md) |

---

## 7. Operational readiness

| # | Requirement | Status | Evidence / notes |
|---|-------------|--------|------------------|
| 7.1 | Named **system owner** and **security contact** | ☐ | RACI in Trust Brief |
| 7.2 | User training plan — Copilot acceptable use | ☐ | Departmental LMS (orientation) |
| 7.3 | Incident response path for Copilot data exposure | ☐ | IR playbook reference |
| 7.4 | Change management for Copilot Studio agents (if used) | ☐ | Agent inventory + evaluate receipts |
| 7.5 | TBS audit readiness — records available on request | ☐ | Export bundle retained |

---

## 8. Contacts (official — not Noetfield)

| Topic | Contact |
|-------|---------|
| Copilot for Work PIN interpretation | TBS digital policy channels (see PIN document) |
| AIA / ADM | `ai-ia@tbs-sct.gc.ca` |
| SSC M365 enterprise | SSC client executive |

**Noetfield intake:** `/trust-brief/intake/?interest=federal` · `operations@noetfield.com`

---

## 9. Quick verdict

| Outcome | Criteria |
|---------|----------|
| **Ready for phased pilot** | Sections 1–4 critical items checked · AIA in progress · governance receipt layer planned |
| **Not ready** | Missing labels/DLP · unclassified scope not confirmed · no system owner |
| **Escalate** | Protected data suspected in scope · Level IV ADM · classified workflow |

---

## 10. Related

| Doc | Role |
|-----|------|
| [FEDERAL_GOVERNANCE_PACK_v1.md](./FEDERAL_GOVERNANCE_PACK_v1.md) | Federal lane SSOT |
| [AIA_TLE_MAPPING_v1.md](./AIA_TLE_MAPPING_v1.md) | AIA evidence crosswalk |
| [Standardized Microsoft Tools PIN](https://www.canada.ca/en/government/system/digital-government/policies-standards/policy-service-digital-announcements/standardized-use-microsoft-tools.html) | E5 rollout companion |
