# Bank Pilot — OSFI E-23 Orientation Cross-Link (NF-BP)

**Version:** 1.0.0 · **Plan:** pf-0051 · **SKU:** NF-BP  
**Law:** Orientation only — not legal advice · not OSFI program replacement

---

## One line

`/bank-pilot/` must **cross-link** to the Canadian OSFI E-23 orientation doc so FRFI buyers can move from shadow simulation positioning to supervisory context in one click.

---

## Canonical link map

| From | To | Purpose |
|------|-----|---------|
| `/bank-pilot/` | `/docs/diligence/CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md` | Primary diligence cross-link |
| `/bank-pilot/` | `/copilot/governance-audit-trail/` | Public summary · TLE + board PDF context |
| `/bank-pilot/` | `/copilot/procurement/` § OSFI FAQ | Procurement FAQ adjacency |
| Orientation doc | `/bank-pilot/` | Shadow simulation lane back-link |
| `NF_BP_SHADOW_MODE_DOCS_v1.md` | This file | Internal SSOT for www placement |

**Public URL (orientation):** `https://www.noetfield.com/docs/diligence/CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md`

---

## `/bank-pilot/` placement (locked)

| Element | Requirement |
|---------|-------------|
| Hero badge | `OSFI E-23 orientation` pill visible |
| Dedicated section | `OSFI E-23 orientation` h2 with lead + link |
| Primary link text | **Canadian OSFI E-23 orientation** |
| Secondary link | Governance audit trail page |
| CTA unchanged | `/gate/intake/?vector=bank-pilot&interest=bank-pilot` |

**Buyer line on page:** *Independent-style decision records oriented toward OSFI E-23 evidence (effective May 2027) — not regulatory certification.*

---

## What the cross-link explains

| OSFI E-23 question | Bank Pilot answer |
|--------------------|-------------------|
| Shadow before production? | Read-only `bank-pilot-v1` evaluate — no execution rights |
| Independent evidence? | RID-keyed TLE + audit export |
| Third-party AI vendor? | Governance vendor layer (B-10 adjacency) — separate from bank core |
| Board oversight? | Go/no-go records via board PDF orientation |

Full framework table lives in the orientation doc — do not duplicate legal claims on `/bank-pilot/`.

---

## Explicit exclusions (anti-paths)

- No claim that Noetfield **certifies** OSFI E-23 compliance
- No FINTRAC KYB pack · no custody · no payment rails on this lane
- No TrustField TF-001 RPAA delivery in same SOW or hero block
- No fourth Noetfield contract SKU

---

## Verify (docs-only)

```bash
# Cross-link doc on disk
test -f docs/bank-pilot/NF_BP_OSFI_E23_CROSS_LINK_v1.md

# /bank-pilot/ links to orientation
grep -q 'CANADIAN_OSFI_E23_COPILOT_ORIENTATION' bank-pilot/index.html
grep -q 'OSFI E-23 orientation' bank-pilot/index.html

# Orientation doc links back to Bank Pilot
grep -q '/bank-pilot/' docs/diligence/CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md
```

---

## Related

- [CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md](../diligence/CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md)
- [NF_BP_SHADOW_MODE_DOCS_v1.md](./NF_BP_SHADOW_MODE_DOCS_v1.md)
- [BANK_PILOT_V1_POLICY_PACK_EXPLAINER_v1.md](./BANK_PILOT_V1_POLICY_PACK_EXPLAINER_v1.md)
- [BANK_PILOT_DEMO.md](../BANK_PILOT_DEMO.md)
