# OSFI E-23 Diligence Refresh

**Version:** 1.0.0 · **Plan:** pf-0071 · **SKU:** — (federal adjacency) · **Phase:** 7  
**Law:** Orientation only — not legal advice · not OSFI program replacement · not FINTRAC KYB

---

## One line

Refresh SSOT for Canadian FRFI Copilot diligence — OSFI E-23 effective **May 1, 2027** — links orientation doc, bank-pilot cross-link, and federal/FRFI www surfaces.

---

## Canonical documents

| Doc | Path |
|-----|------|
| Primary orientation | [CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md](../diligence/CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md) |
| Bank Pilot cross-link | [NF_BP_OSFI_E23_CROSS_LINK_v1.md](../bank-pilot/NF_BP_OSFI_E23_CROSS_LINK_v1.md) |
| This refresh | `docs/federal/NF_OSFI_E23_DILIGENCE_REFRESH_v1.md` |

---

## www link map

| Surface | Link |
|---------|------|
| `/federal/` | Proof card → this refresh SSOT |
| `/bank-pilot/` | OSFI section → this refresh + orientation doc |
| `/copilot/procurement/` | OSFI FAQ → orientation doc |
| `/templates/` | OSFI E-23 bank shadow template |

---

## Refresh checklist (2026-06)

- [x] OSFI E-23 effective May 2027 cited consistently
- [x] Metadata-only M365 evidence index referenced
- [x] Bank Pilot shadow mode as FRFI entry
- [x] No FINTRAC KYB · no custody · no TrustField blend
- [x] Orientation-only disclaimer on all public surfaces

---

## Not in scope

- OSFI certification or supervisory approval claims
- TrustField RPAA program delivery
- Payment rails or MSB execution

---

## Verify

```bash
test -f docs/federal/NF_OSFI_E23_DILIGENCE_REFRESH_v1.md
grep -q 'NF_OSFI_E23_DILIGENCE_REFRESH' federal/index.html
grep -q 'NF_OSFI_E23_DILIGENCE_REFRESH' bank-pilot/index.html
```
