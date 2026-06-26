# MSP Partner Program — Apply → Enable → Earn (NF-RD)

**Version:** 1.0.0 · **Plan:** pf-0056 · **SKU:** NF-RD · **Lane:** MSP white-label  
**Public page:** `/msp/` · **Intake:** `/gate/partners/intake/`  
**Law:** Sell through MSPs — not direct end-customer scale in year 1

---

## One line

Microsoft 365 CSP partners **Apply** for enablement, **Enable** Phase 2 TLE attach on client tenants, **Earn** via Governance Pack resale and monitor MRR.

---

## Program ladder

| Stage | Partner action | Noetfield deliverable | Success signal |
|-------|----------------|----------------------|----------------|
| **Apply** | Submit partner intake · sign LOI | Enablement kit · demo · RACI | Hub-approved partner slot |
| **Enable** | Phase 1 readiness (Purview) → Phase 2 attach | `copilot-governance-v1` evaluate + TLE | **1 live tenant** on Governance Pack |
| **Earn** | Prime client SOW · wholesale/resale | TLE + board PDF + procurement ZIP per tenant | Paid pilot $2k–10k or monitor MRR |

**W3-MSP PASS:** signed partner LOI + **1 live tenant** on Governance Pack.

---

## Apply — intake and enablement

| Step | Surface | URL |
|------|---------|-----|
| 1 | Partner overview | `/msp/` |
| 2 | Partner intake | `/gate/partners/intake/` |
| 3 | MSP SSOT | [MSP_GOVERNANCE_PACK_v1.md](./MSP_GOVERNANCE_PACK_v1.md) |
| 4 | QuickScan handoff | [NF_QS_QUICKSCAN_OFFER_ONE_PAGER_v1.md](./NF_QS_QUICKSCAN_OFFER_ONE_PAGER_v1.md) |
| 5 | Assessment kit | [MSP_WHITELABEL_ASSESSMENT_KIT_v1.md](./MSP_WHITELABEL_ASSESSMENT_KIT_v1.md) |

**Intake vector:** `?interest=msp` · `operations@noetfield.com` · Hub approve before outbound.

---

## Enable — Phase 1 → Phase 2 attach

| Phase | Owner | Work |
|-------|-------|------|
| **Phase 1** | MSP | Purview readiness · labels · DLP · Copilot enable |
| **Phase 2** | Noetfield | Evaluate intent · TLE v1 · board PDF · procurement ZIP |

Detail: [PHASE1_PHASE2_RACI_v1.md](./PHASE1_PHASE2_RACI_v1.md) · [READINESS_TO_RECORD_MAPPING_v1.md](./READINESS_TO_RECORD_MAPPING_v1.md)

**Client intake (via MSP):** `/trust-brief/intake/?interest=pilot&vector=copilot-governance`

---

## Earn — commercial model

| SKU | Who invoices | Price band | Deliverable |
|-----|--------------|------------|-------------|
| Governance Pack (via MSP) | MSP prime · Noetfield sub | $2k–10k pilot | TLE + export per tenant |
| Governance Monitor MRR | MSP | Per-tenant/mo (TBD) | Monthly evaluate + QBR export |
| NF-QS QuickScan | MSP handoff | $2k–$3.5k | Gap scan → pilot upgrade |
| Trust Brief (anchor) | Co-deliver optional | $10k | Enterprise proof for practice |

**Assessment band:** $3k–12k/client scope per [MSP_WHITELABEL_ASSESSMENT_KIT_v1.md](./MSP_WHITELABEL_ASSESSMENT_KIT_v1.md)

---

## Partner tiers (orientation)

| Tier | Requirement | Benefit |
|------|-------------|---------|
| Registered | Intake approved | Demo · docs · async support |
| Enabled | LOI + enablement complete | Wholesale pricing · co-marketing |
| Certified | 1 live tenant + board PDF used | Priority Hub queue · case study slot |

---

## Anti-paths

- No direct Vancouver SME wedge at scale (MSP serves end customer)
- No Bank Pilot / FRFI as MSP default SKU
- No FINTRAC KYB · no custody · no payment rails
- No TrustField in same MSP SOW or hero line
- Founder never sends — Hub approves per `N_P4_HUB_QUEUE.yaml`
- GEL tiers are platform/runtime — not fourth contract SKU on www

---

## Verify

```bash
test -f docs/msp/MSP_PARTNER_PROGRAM_FLOW_v1.md
grep -q 'Apply' docs/msp/MSP_PARTNER_PROGRAM_FLOW_v1.md
grep -q 'Enable' docs/msp/MSP_PARTNER_PROGRAM_FLOW_v1.md
grep -q 'Earn' docs/msp/MSP_PARTNER_PROGRAM_FLOW_v1.md
grep -q 'gate/partners/intake' docs/msp/MSP_PARTNER_PROGRAM_FLOW_v1.md
```

---

## Related

- [MSP_GOVERNANCE_PACK_v1.md](./MSP_GOVERNANCE_PACK_v1.md)
- [MSP_WHITELABEL_ASSESSMENT_KIT_v1.md](./MSP_WHITELABEL_ASSESSMENT_KIT_v1.md)
- [PHASE1_PHASE2_RACI_v1.md](./PHASE1_PHASE2_RACI_v1.md)
