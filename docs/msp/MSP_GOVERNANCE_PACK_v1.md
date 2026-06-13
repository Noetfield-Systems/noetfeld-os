# MSP Governance Pack (LOCKED v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `[NF-LOCAL-REPO-AGENT]` |
| **Doc id** | `noetfield-msp-governance-pack-v1` |
| **Lane** | `msp` — Microsoft 365 CSP / managed service providers only |
| **Parent SSOT** | [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](../strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md) |
| **Locked** | 2026-06-02 |
| **Public page** | `/msp/` |

**Not legal advice** — orientation for MSP partners and internal GTM. Noetfield sells **through MSPs** in this lane — not direct end-customer scale in year 1.

---

## 0. MSP wedge (one sentence)

> MSPs run Phase 1 (Purview readiness, labels, DLP, Copilot assessment); Noetfield is Phase 2 — **governance decision receipts** for Copilot and Studio changes — evaluate → receipt → export, metadata-only, multi-tenant friendly. **Phase 1 readiness → Phase 2 signed TLE receipts.**

---

## 1. Scope

| In scope | Out of scope |
|----------|--------------|
| CSP / MSP multi-tenant Copilot attach | Direct federal GC (see `/federal/`) |
| Phase 2 governance after readiness | Replacing MSP baseline tooling or Purview administration |
| Partner LOI · wholesale · rev-share | Direct Vancouver SME wedge (MSP serves; Noetfield does not sell direct) |
| Readiness → Record funnel | Bank Pilot / FRFI (shadow SKU — not MSP default) |
| Per-tenant Governance Monitor MRR (orientation) | Payment, custody, MSB, engine SKU on www |
| GDAP-scoped metadata connectors | Cross-tenant Copilot grounding (impossible per Microsoft design) |

---

## 2. Market anchors (2026)

| Trigger | Date | Partner motion |
|---------|------|----------------|
| **Purview Suite 50% off** with Copilot | Feb 2025 → **Jun 30, 2026** | Attach Purview remediation + Phase 2 receipt |
| **Partner Center Copilot tab** | Jun 2026 | Propensity + security readiness side-by-side |
| **Business Premium + Copilot SKUs** | Jul 1, 2026 | B-SKU bundle attach |
| **Microsoft OSS readiness assessment** | Active | Import CSV → [READINESS_TO_RECORD_MAPPING_v1.md](./READINESS_TO_RECORD_MAPPING_v1.md) |
| **MSP Purview multi-tenant tooling** | 2026 | Complement — Phase 1 stays in partner stack |
| **MSP admin tooling** dual stack | 2026 | Phase 1 tooling — Noetfield after baselines |

**External references:**

- [Microsoft — Secure and govern M365 Copilot (partner assets)](https://partner.microsoft.com/en-us/marketing-center/assets/collection/secure-govern-m365-copilot)
- [Microsoft OSS — m365-copilot-automated-readiness-assessment](https://github.com/microsoft/m365-copilot-automated-readiness-assessment)
- [CSP sell-through — Defender & Purview](https://microsoftpartners.microsoft.com/Microsoft-Security-Partners/sell-through-csp/)

---

## 3. Two-tier model

| Tier | Owner | Work |
|------|-------|------|
| **Phase 1** | MSP | Readiness assessment · Purview deploy · labels · DLP · CA · Copilot enable |
| **Phase 2** | Noetfield | Evaluate operational intent · TLE v1 · board PDF · procurement ZIP |

Detail: [PHASE1_PHASE2_RACI_v1.md](./PHASE1_PHASE2_RACI_v1.md)

---

## 4. Partner SKUs

| SKU | Who invoices | Price band | Deliverable |
|-----|--------------|------------|-------------|
| **Governance Pack (via MSP)** | MSP prime · Noetfield sub | $2k–10k pilot | TLE + export per tenant |
| **Governance Monitor MRR** | MSP | Per-tenant/mo (TBD) | Monthly evaluate + QBR export |
| **Partner enablement** | Noetfield | Free with LOI | Partner one-pager · demo · handoff runbook |
| **Trust Brief (anchor client)** | Direct or co-deliver | $10k | Optional enterprise proof for MSP practice |

**Partner CTA:** `/trust-brief/intake/?interest=msp` · `operations@noetfield.com`

**W3-MSP PASS:** signed partner LOI + **1 live tenant** on Governance Pack.

---

## 5. Partner tiers (orientation)

| Tier | Requirements | Benefits |
|------|--------------|----------|
| **Registered** | LOI · 1 SE trained | Partner one-pager · intake routing |
| **Certified** | 3 tenants live | Co-marketing · office hours priority |
| **Premier** | 10+ tenants · MRR | Wholesale pricing · feature input |

---

## 6. Governance execution loop (MSP language)

| Step | End customer sees | MSP role | Noetfield role |
|------|-------------------|----------|----------------|
| **Assess** | Readiness report | Run assessment tool | Receive import / scope pilot |
| **Remediate** | Labels · DLP live | Configure Purview | — |
| **Evaluate** | Pre-production check | Facilitate | Governance API decision |
| **Record** | Signed go/no-go | Present in QBR | TLE v1 |
| **Export** | Audit bundle | Deliver to customer | PDF + ZIP |

---

## 7. Honest limits (partner discovery)

| Partner ask | Noetfield response |
|-------------|-------------------|
| “Replace our Phase 1 readiness stack?” | **No** — Phase 1 stays in your stack; we are Phase 2 receipts. |
| “Multi-tenant Copilot search across clients?” | **No** — Copilot is single-tenant per Microsoft design. |
| “White-label the whole product?” | Phase 2 exports can co-brand; API/workspace branding TBD by tier. |
| “We need Purview deployed for us” | Phase 1 — your MSP practice; not Noetfield. |
| “Certified Microsoft partner badge?” | We complement Solutions Partner Security motion — not a certifier. |

---

## 8. Implementation sprint (repo)

| Plan | Artifact | Path |
|------|----------|------|
| 451 | MSP www page | `/msp/index.html` |
| 452 | This document | `docs/msp/MSP_GOVERNANCE_PACK_v1.md` |
| 453 | RACI | `docs/msp/PHASE1_PHASE2_RACI_v1.md` |
| 454 | Readiness mapping | `docs/msp/READINESS_TO_RECORD_MAPPING_v1.md` |

---

## 9. Related docs

| Doc | Role |
|-----|------|
| [PHASE1_PHASE2_RACI_v1.md](./PHASE1_PHASE2_RACI_v1.md) | Delivery boundaries |
| [READINESS_TO_RECORD_MAPPING_v1.md](./READINESS_TO_RECORD_MAPPING_v1.md) | Assessment → pilot mapper |
| [SME_GOVERNANCE_PACK_ONE_PAGER.md](../copilot/SME_GOVERNANCE_PACK_ONE_PAGER.md) | End-customer artifact language |
| [FEDERAL_GOVERNANCE_PACK_v1.md](../federal/FEDERAL_GOVERNANCE_PACK_v1.md) | Separate lane — no overlap |
