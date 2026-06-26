# Pilot Pricing Alignment — www vs Procurement FAQ

**Version:** 1.0.0 · **Plan:** pf-0028 · **SKU:** NF-RD · **Brand:** Noetfield only  
**Law:** Three SKUs only · QuickScan is sub-lane of Copilot Governance Pack

---

## Aligned pricing bands

| Tier | Code | Price (CAD) | Duration | Success signal |
|------|------|-------------|----------|----------------|
| **QuickScan** | NF-QS | **$2,000–$3,500** | 3–5 days active · up to 4 weeks | Sample TLE + export walkthrough |
| **Readiness Pilot** | NF-RD | **$5,000–$10,000** | 4–6 weeks · 90-day program | **Board PDF in governance meeting** |
| **Trust Brief** | NF-TB | **$10,000** | 6 weeks | Policy map + risk exposure |

---

## Surface alignment matrix

| Surface | QuickScan | Readiness | Source |
|---------|-----------|-----------|--------|
| `/copilot/pilot/` pricing cards | $2k–$3.5k | $5k–$10k | This doc |
| `/trust-brief/intake/` band options | $2k–$3.5k · 4 weeks | $5k–$10k · 90 days | intake JS |
| [`PROCUREMENT_COMPETITIVE_FAQ_v1.md`](./PROCUREMENT_COMPETITIVE_FAQ_v1.md) | MSP readiness vs productized pilot | Board PDF success signal (FAQ § MSP) | FAQ |
| [`OFFERINGS_LOCKED.md`](../../OFFERINGS_LOCKED.md) | Sub-lane QuickScan | Copilot Governance Pack $2k–$10k | SSOT |
| [`NF_QS_QUICKSCAN_OFFER_ONE_PAGER_v1.md`](../msp/NF_QS_QUICKSCAN_OFFER_ONE_PAGER_v1.md) | $2k–$3.5k MSP handoff | Upgrade to Readiness | MSP |

---

## Milestone ladder (pilot page)

| Step | Tag | Price | CTA |
|------|-----|-------|-----|
| Lead | Copilot Governance Pack | $2k–$10k | `/trust-brief/intake/?interest=pilot&vector=copilot-governance` |
| Land | Trust Brief | $10k | `/trust-brief/` |
| Expand | Bank Pilot | Custom | `/bank-pilot/` |

**FAQ alignment:** Procurement FAQ states fixed-fee pilot $2k–$10k with board PDF success signal — matches Readiness tier; QuickScan is entry sub-band within same SKU.

---

## Anti-paths

- No fourth SKU · QuickScan is not a separate contract
- No FINTRAC KYB pack claims
- No TrustField vocabulary on Noetfield pilot surfaces

---

## Verify

- `grep -r '2,000–3,500\|2k–3.5k' copilot/pilot/ trust-brief/intake/ assets/noetfield-intake-pilot-mode.js`
- Procurement FAQ line 28: board PDF in real governance meeting
