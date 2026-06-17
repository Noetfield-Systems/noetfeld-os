# GEL Starter Tier Spec (~$10K)

**Version:** 1.0.0 · **Plan:** pf-0058 · **SKU:** NF-RD (platform) · **Phase:** 2  
**Law:** GEL is Governance Execution Layer / runtime — **not** a fourth www contract SKU

---

## One line

GEL Starter (~**$10K CAD**) — sandbox environment, **one** policy pack (`copilot-governance-v1` or `bank-pilot-v1`), audit portal — upgrade path from `/start/` or NF-RD pilot.

---

## Tier summary

| Field | Value |
|-------|-------|
| Price | ~$10,000 CAD (orientation) |
| Environment | Dedicated sandbox · 14-day trial extendable |
| Policy packs | 1 pack loaded |
| Storage | Audit portal · TLE export |
| Tenancy | Single org |
| SLA | Best-effort · business hours |

---

## Included

- Governance evaluate API (`POST /api/v1/governance/evaluate`)
- TLE v1 generation + compliance log
- Board PDF · procurement ZIP export (orientation)
- `/console/` workspace access
- Policy pack deploy via `/templates/`

---

## Not included

- Multi-tenant isolation (→ GEL Standard)
- Postgres production event store SLA (→ GEL Standard)
- Quarterly drift scoring + board pack (→ GEL Trust Ledger)
- Payment rails · custody · MSB execution
- TrustField RPAA program delivery

---

## Upgrade path

```text
/start/ sandbox (free) → NF-RD pilot ($2k–10k) → GEL Starter (~$10k) → GEL Standard (~$50k) → GEL Trust Ledger (~$120k)
```

**Three contract SKUs on www unchanged:** Trust Brief · Copilot Governance Pack · Bank Pilot.

---

## Verify

```bash
test -f docs/runtime/GEL_STARTER_TIER_SPEC_v1.md
grep -q '\$10' docs/runtime/GEL_STARTER_TIER_SPEC_v1.md
grep -q 'sandbox' docs/runtime/GEL_STARTER_TIER_SPEC_v1.md
grep -q 'policy pack' docs/runtime/GEL_STARTER_TIER_SPEC_v1.md
```

---

## Related

- [GEL_STANDARD_TIER_SPEC_v1.md](./GEL_STANDARD_TIER_SPEC_v1.md)
- [GEL_TRUST_LEDGER_TIER_SPEC_v1.md](./GEL_TRUST_LEDGER_TIER_SPEC_v1.md)
- [NOETFIELD_GOVERNANCE_RUNTIME_CONTRACT_LOCKED_v1.md](../strategy/NOETFIELD_GOVERNANCE_RUNTIME_CONTRACT_LOCKED_v1.md)
