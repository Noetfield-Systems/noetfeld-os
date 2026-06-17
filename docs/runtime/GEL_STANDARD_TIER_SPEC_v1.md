# GEL Standard Tier Spec (~$50K)

**Version:** 1.0.0 · **Plan:** pf-0059 · **SKU:** NF-RD (platform) · **Phase:** 3  
**Law:** Platform/runtime tier — MSP and enterprise multi-tenant — not fourth contract SKU

---

## One line

GEL Standard (~**$50K CAD**) — **multi-tenant** Governance Runtime, Postgres event store, SLA-backed evaluate + export for MSP practices and mid-market enterprise.

---

## Tier summary

| Field | Value |
|-------|-------|
| Price | ~$50,000 CAD (orientation) |
| Tenancy | Multi-tenant · org isolation |
| Database | `RUNTIME_EVENT_STORE=postgres` |
| Policy packs | Up to 2 packs (e.g. `copilot-governance-v1` + `bank-pilot-v1`) |
| SLA | 99.5% uptime orientation · business-day support |
| MSP fit | Per-tenant evaluate + QBR export |

---

## Included (above Starter)

- Multi-tenant org boundaries
- Postgres audit lineage (credible pilot exports)
- MSP partner tenant provisioning orientation
- API rate limits for production keys
- Quarterly health review (orientation)

---

## Not included

- Quarterly drift scoring board pack (→ GEL Trust Ledger)
- FINTRAC/RPAA evidence (→ TrustField TF-001)
- Payment execution · custody

---

## Buyer fit

| Segment | Use case |
|---------|----------|
| MSP (N-P4) | Multiple client tenants after Phase 2 attach |
| Enterprise | Division-level Copilot governance at scale |
| SI partner | White-label evaluate layer |

**Intake:** `/gate/partners/intake/` (MSP) · `/trust-brief/intake/?interest=pilot` (enterprise)

---

## Verify

```bash
test -f docs/runtime/GEL_STANDARD_TIER_SPEC_v1.md
grep -q '\$50' docs/runtime/GEL_STANDARD_TIER_SPEC_v1.md
grep -q 'multi-tenant' docs/runtime/GEL_STANDARD_TIER_SPEC_v1.md
grep -q 'Postgres' docs/runtime/GEL_STANDARD_TIER_SPEC_v1.md
```

---

## Related

- [GEL_STARTER_TIER_SPEC_v1.md](./GEL_STARTER_TIER_SPEC_v1.md)
- [GEL_TRUST_LEDGER_TIER_SPEC_v1.md](./GEL_TRUST_LEDGER_TIER_SPEC_v1.md)
- [MSP_PARTNER_PROGRAM_FLOW_v1.md](../msp/MSP_PARTNER_PROGRAM_FLOW_v1.md)
