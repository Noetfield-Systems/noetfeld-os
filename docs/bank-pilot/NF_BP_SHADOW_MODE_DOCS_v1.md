# Bank Pilot — Shadow Mode Documentation (NF-BP)

**Version:** 1.0.0 · **Plan:** pf-0049 · **SKU:** NF-BP · **Policy pack:** `bank-pilot-v1`  
**Route:** `/bank-pilot/` · intake `/gate/intake/?vector=bank-pilot`  
**Law:** Read-only · no execution rights · no custody · no payment rails

---

## One line

Bank Pilot is a **read-only governance simulation** for FRFI and regulated institutions — evaluate operational intent, produce RID-keyed audit lineage, export compliance logs — **without** transaction authority or custody.

**Buyer line:** *Noetfield does not move funds; licensed institutions execute externally.*

---

## Shadow mode definition

| Property | Bank Pilot shadow | Out of scope |
|----------|-------------------|--------------|
| **Mode** | `shadow` evaluate only | Production payment initiation |
| **Authority** | Policy allow / review / reject | Custody · settlement · MSB execution |
| **Data** | Metadata-only evidence orientation | Content exfiltration |
| **Output** | Compliance log · TLE orientation · audit export | Core banking write APIs |
| **Partner stack** | Runs beside your environment | Replaces bank core or TrustField rails |

---

## What shadow evaluate does

1. **Ingest intent** — operational action described for governance review (no execution).
2. **Evaluate** — `POST /api/v1/governance/evaluate` with `mode: shadow`.
3. **Decide** — PROCEED · REQUIRE_HUMAN_REVIEW · REJECT per `bank-pilot-v1` policy pack.
4. **Record** — RID lineage · compliance log append.
5. **Export** — `GET /api/v1/governance/audit-export?request_id=RID-…` for diligence.

---

## Institutional buyer fit

| Segment | Use case | Timing |
|---------|----------|--------|
| FRFI / OSFI-adjacent FI | AI model risk governance orientation (E-23 May 2027) | Long cycle |
| Credit union | Copilot + data governance shadow | Scoped pilot |
| Federal / public sector | Read-only simulation before enforce mode | `/federal/` adjacency |

**OSFI orientation:** Independent-style decision records — not replacement for OSFI program. See [NF_BP_OSFI_E23_CROSS_LINK_v1.md](./NF_BP_OSFI_E23_CROSS_LINK_v1.md) · [CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md](../diligence/CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md).

---

## Commercial terms (orientation)

| Term | Value |
|------|-------|
| SKU | NF-BP · Bank Pilot (third contract offering) |
| Price | Custom scoped SOW · design partner band CAD $2k–$10k orientation |
| Duration | 12-week pilot orientation (v6.1 brief) |
| Upgrade from | Trust Brief (NF-TB) or Copilot Pack (NF-RD) — **separate SOWs** |

---

## Explicit exclusions

- Payment initiation · custody · settlement · money transmission
- FINTRAC KYB pack (wrong SKU — Noetfield does not offer)
- TrustField TF-001 RPAA program delivery in same SOW
- VIRLUX payment rails
- Production enforce mode without separate SOW

---

## Demo path

See [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md) — 30-minute script · Governance Console · shadow evaluate API.

| Step | Surface |
|------|---------|
| 1 | `/bank-pilot/` positioning |
| 2 | `/console/` shadow simulation |
| 3 | Audit export by RID |
| 4 | Intake `vector=bank-pilot` |

---

## Boundary vs TrustField (dual institutional deals)

| Question | Noetfield NF-BP | TrustField TF-001 |
|----------|-----------------|-------------------|
| Role | Govern before execution | Deliver RPAA/FINTRAC program evidence |
| Mode | Shadow simulation | Partner attestation · MSB evidence |
| SOW | Separate | Separate — never blend hero lines |

Handoff: MSB/RPAA evidence → TrustField TF-001 (separate plan pf-0055 boundary FAQ).

---

## Anti-paths

- No FINTRAC KYB pack claims on Noetfield
- No fourth SKU
- Founder never sends — Hub approves institutional outreach

---

## Related

- [NF_BP_CREDIT_UNION_INTAKE_VECTOR_v1.md](./NF_BP_CREDIT_UNION_INTAKE_VECTOR_v1.md)
- [NF_BP_DEMO_ENVIRONMENT_v1.md](./NF_BP_DEMO_ENVIRONMENT_v1.md)
- [NF_BP_VS_TF001_BOUNDARY_FAQ_v1.md](./NF_BP_VS_TF001_BOUNDARY_FAQ_v1.md)
- [NF_BP_RBC_NBC_INSTITUTIONAL_PITCH_v1.md](./NF_BP_RBC_NBC_INSTITUTIONAL_PITCH_v1.md)
- [NF_BP_OSFI_E23_CROSS_LINK_v1.md](./NF_BP_OSFI_E23_CROSS_LINK_v1.md)
- [BANK_PILOT_V1_POLICY_PACK_EXPLAINER_v1.md](./BANK_PILOT_V1_POLICY_PACK_EXPLAINER_v1.md)
- [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md)
- [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md)
