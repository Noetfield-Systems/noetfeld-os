# Phase 1 / Phase 2 RACI (MSP Lane v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `[NF-LOCAL-REPO-AGENT]` |
| **Doc id** | `noetfield-msp-phase1-phase2-raci-v1` |
| **Parent** | [MSP_GOVERNANCE_PACK_v1.md](./MSP_GOVERNANCE_PACK_v1.md) |
| **Updated** | 2026-06-02 |

**Legend:** **R** = Responsible · **A** = Accountable · **C** = Consulted · **I** = Informed · **—** = Out of scope

**Parties:**

- **MSP** — CSP partner (Phase 1 lead)
- **NF** — Noetfield (Phase 2 lead)
- **Customer** — End tenant (sign-off authority)

---

## 1. Program setup

| Activity | MSP | NF | Customer |
|----------|-----|----|---------| 
| Partner LOI / tier enrollment | **R/A** | C | — |
| GDAP relationship to tenant | **R/A** | I | C |
| Pilot SOW (MSP prime, NF sub) | **R/A** | C | **A** (sign) |
| Named customer contacts (vCIO, security) | **R** | I | **A** |

---

## 2. Phase 1 — Readiness & Purview (MSP-owned)

| Activity | MSP | NF | Customer |
|----------|-----|----|---------| 
| Copilot readiness assessment | **R/A** | I | C |
| License optimization review | **R/A** | — | C |
| Sensitivity labels design & deploy | **R/A** | — | C |
| DLP policies for Copilot | **R/A** | — | C |
| Conditional Access baseline | **R/A** | — | C |
| SharePoint/Teams oversharing remediation | **R/A** | — | C |
| Lighthouse / CIPP / Inforcer baseline push | **R/A** | — | I |
| Copilot license provision (CSP) | **R/A** | — | C |
| User training & change management | **R/A** | — | **A** |
| Readiness report delivery | **R/A** | C | I |

**Phase 1 exit criteria:** Readiness report with no **High** unresolved items (or documented exceptions accepted by customer).

---

## 3. Phase 2 handoff

| Activity | MSP | NF | Customer |
|----------|-----|----|---------| 
| Trigger Phase 2 (readiness green or exception signed) | **R** | I | **A** |
| Provide tenant ID + readiness report / CSV | **R/A** | I | — |
| Scope Governance Pack pilot | C | **R/A** | C |
| Metadata connector consent (GDAP scopes) | **R** | **A** | **A** |
| Joint kickoff (MSP leads) | **R/A** | **R** | I |

---

## 4. Phase 2 — Governance receipts (Noetfield-owned)

| Activity | MSP | NF | Customer |
|----------|-----|----|---------| 
| Operational intent evaluate (pre-production) | I | **R/A** | C |
| Policy rule configuration in Noetfield workspace | C | **R/A** | C |
| Human approval chain capture | C | **R/A** | **A** (approvers) |
| TLE v1 sign-off | I | **R** | **A** |
| Board pack PDF generation | I | **R/A** | I |
| Procurement ZIP export | I | **R/A** | I |
| Tamper integrity verification demo | C | **R/A** | I |

---

## 5. Copilot enablement & scale

| Activity | MSP | NF | Customer |
|----------|-----|----|---------| 
| Enable Copilot per-user / dept | **R/A** | C | **A** |
| Pre-scale evaluate batch | I | **R/A** | C |
| Copilot Studio agent publish evaluate | I | **R/A** | C |
| Monthly governance QBR | **R/A** | **R** (export) | I |
| Quarterly readiness re-run | **R/A** | C (TLE refresh) | I |

---

## 6. Ongoing operations & support

| Activity | MSP | NF | Customer |
|----------|-----|----|---------| 
| Purview policy change in tenant | **R/A** | I | I |
| Receipt for material policy change | C | **R/A** | I |
| Connector token / GDAP renewal | **R/A** | C | I |
| Incident — Copilot data exposure | **R/A** | C | **A** |
| Escalation — evaluate deny dispute | C | **R/A** | **A** |

---

## 7. Escalation matrix

| Situation | Lead | Action |
|-----------|------|--------|
| Labels misconfigured · oversharing | **MSP** | Remediate Phase 1; defer Phase 2 scale |
| Evaluate returns **deny** | **NF** | Receipt to customer; MSP implements fix |
| Customer wants Purview re-architecture | **MSP** | SOW change; NF paused until handoff |
| Cross-tenant data concern | **MSP** | Clarify single-tenant Copilot boundary |
| Export integrity fail | **NF** | Support; tamper investigation |
| Billing / rev-share dispute | **NF + MSP leadership** | LOI terms |

---

## 8. Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1 (MSP)                                               │
│  Assess → Remediate → Purview baseline → Copilot licensed   │
└───────────────────────────┬─────────────────────────────────┘
                            │ handoff: tenant ID + report
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2 (Noetfield)                                         │
│  Evaluate → Decide → Record (TLE) → Export (PDF/ZIP)        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  MRR (MSP bills · NF delivers)                               │
│  Governance Monitor · quarterly readiness · QBR export       │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Related

| Doc | Role |
|-----|------|
| [MSP_GOVERNANCE_PACK_v1.md](./MSP_GOVERNANCE_PACK_v1.md) | Lane SSOT |
| [READINESS_TO_RECORD_MAPPING_v1.md](./READINESS_TO_RECORD_MAPPING_v1.md) | Handoff field mapping |
