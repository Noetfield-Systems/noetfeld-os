# Federal Lane — FFIEC Orientation Refresh (v1)

**Version:** 1.0.0 · **Plan:** pf-0057 · **SKU:** NF-RD · **Lane:** Federal / US-adjacent  
**Use:** Orientation for US federally regulated institutions and FFIEC-adjacent buyers — **not legal advice**

---

## One line

FFIEC and US federal-adjacent institutions evaluating Copilot need **pre-execution governance receipts** — Noetfield provides TLE + board PDF orientation; GC Canada lane stays on [`FEDERAL_GOVERNANCE_PACK_v1.md`](./FEDERAL_GOVERNANCE_PACK_v1.md).

---

## Scope boundary

| Lane | Buyer | Primary framework | Public route |
|------|-------|-----------------|--------------|
| **GC Canada** | Schedule I/II · AoP | ADM · AIA · Copilot PIN | `/federal/` |
| **FFIEC / US-adjacent** | US banks · credit unions · FI partners | FFIEC · OCC · Fed SR | This doc + `/copilot/pilot/` |
| **FRFI shadow** | Canadian banks | OSFI E-23 | `/bank-pilot/` (NF-BP) |

**Law:** Do not blend GC hero with FFIEC hero on same page block.

---

## FFIEC orientation map

| FFIEC / supervisory question | Noetfield artifact |
|------------------------------|-------------------|
| Board oversight of AI adoption? | Board PDF from TLE export |
| Independent evidence beyond vendor logs? | RID-keyed TLE v1 + evidence index |
| Third-party AI vendor governance? | Metadata-only M365 index · B-10-style adjacency |
| Model risk before production? | Pre-execution evaluate · shadow mode orientation |

**Orientation only** — not FFIEC examination prep or regulatory certification.

---

## Noetfield deliverables (US-adjacent)

| SKU | Price band | Deliverable |
|-----|------------|-------------|
| Copilot Governance Pack | $2k–10k · 90 days | TLE + board PDF + procurement ZIP |
| Trust Brief | $10k · 6 weeks | Policy map · risk exposure summary |
| Bank Pilot shadow | Scoped | Read-only — separate NF-BP SKU |

**Intake:** `/trust-brief/intake/?interest=pilot&vector=copilot-governance`  
**Federal GC intake (separate):** `/trust-brief/intake/?interest=federal`

---

## Cross-links (refresh)

| From | To |
|------|-----|
| `/federal/` | This doc (FFIEC adjacency note) |
| `/copilot/procurement/` | FFIEC / OSFI FAQ |
| `/copilot/governance-audit-trail/` | TLE + board PDF context |
| [FEDERAL_GOVERNANCE_PACK_v1.md](./FEDERAL_GOVERNANCE_PACK_v1.md) | GC lane SSOT — unchanged |

---

## Anti-paths

- No claim as federal or FFIEC certifier
- No FINTRAC KYB pack on Noetfield
- No TrustField MSB/RPAA in same SOW
- No payment rails · no custody
- MSP lane serves US FIs through partner — not direct scale

---

## Verify

```bash
test -f docs/federal/FFIEC_ORIENTATION_REFRESH_v1.md
grep -q 'FFIEC' docs/federal/FFIEC_ORIENTATION_REFRESH_v1.md
grep -q 'FEDERAL_GOVERNANCE_PACK' docs/federal/FFIEC_ORIENTATION_REFRESH_v1.md
```

---

## Related

- [FEDERAL_GOVERNANCE_PACK_v1.md](./FEDERAL_GOVERNANCE_PACK_v1.md)
- [AIA_TLE_MAPPING_v1.md](./AIA_TLE_MAPPING_v1.md)
- [CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md](../diligence/CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md)
