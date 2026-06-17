# GEL + Trust Ledger Tier Spec (~$120K)

**Version:** 1.0.0 · **Plan:** pf-0060 · **SKU:** NF-RD (platform) · **Phase:** 4  
**Law:** Enterprise runtime + Trust Ledger program — separate from TrustField TF-001 attestation

---

## One line

GEL + Trust Ledger (~**$120K CAD**) — quarterly export cadence, drift scoring, board-ready governance pack for enterprise AI control plane buyers.

---

## Tier summary

| Field | Value |
|-------|-------|
| Price | ~$120,000 CAD (orientation) |
| Tenancy | Multi-tenant enterprise |
| Trust Ledger | Append-only TLE store · quarterly export bundle |
| Drift scoring | Policy/version drift orientation |
| Board pack | Quarterly board PDF + procurement ZIP |
| SLA | Enterprise orientation · named support |

---

## Included (above Standard)

- Quarterly governance export schedule
- Drift scoring on policy pack versions
- Board-ready quarterly pack for risk committee
- Trust Ledger verify integration (`/trust-ledger/verify/`)
- GEL adapter credit-lane adjacency (optional)

---

## Boundary vs TrustField TF-001

| Question | GEL + Trust Ledger | TrustField TF-001 |
|----------|-------------------|-------------------|
| Role | Platform governance runtime | RPAA/FINTRAC program evidence |
| Export | Quarterly TLE + board pack | Partner attestation |
| SOW | Separate | Separate — never blend |

---

## Not included

- MSB/RPAA program delivery
- Payment rails · custody · settlement
- FINTRAC KYB pack
- Fourth www contract SKU claim

---

## Verify

```bash
test -f docs/runtime/GEL_TRUST_LEDGER_TIER_SPEC_v1.md
grep -q '\$120' docs/runtime/GEL_TRUST_LEDGER_TIER_SPEC_v1.md
grep -q 'quarterly' docs/runtime/GEL_TRUST_LEDGER_TIER_SPEC_v1.md
grep -q 'Trust Ledger' docs/runtime/GEL_TRUST_LEDGER_TIER_SPEC_v1.md
```

---

## Related

- [GEL_STARTER_TIER_SPEC_v1.md](./GEL_STARTER_TIER_SPEC_v1.md)
- [GEL_STANDARD_TIER_SPEC_v1.md](./GEL_STANDARD_TIER_SPEC_v1.md)
- [NF_BP_VS_TF001_BOUNDARY_FAQ_v1.md](../bank-pilot/NF_BP_VS_TF001_BOUNDARY_FAQ_v1.md)
