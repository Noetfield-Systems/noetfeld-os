# Procurement ZIP Integrity Walkthrough

**Version:** 1.0.0 · **Plan:** pf-0030 · **SKU:** NF-RD  
**Audience:** Procurement · legal · GRC diligence reviewers

---

## ZIP contents (orientation)

| File | Role |
|------|------|
| `tle.json` | Signed Trust Ledger Entry record |
| `board-pack.pdf` | Governance meeting artifact |
| `README.md` | Export integrity verification steps |
| `audit-slice.json` | Tenant-scoped audit bundle orientation |

---

## Integrity walkthrough (demo script)

1. **Generate** procurement ZIP from approved TLE in pilot tenant.
2. **Verify** fail-closed export integrity check (orientation — not eIDAS cert).
3. **Inspect** README for reviewer diligence steps.
4. **Confirm** metadata-only evidence IDs — no content exfiltration claims.
5. **Attach** to procurement thread or board packet.

---

## Buyer line

> One-click diligence bundle — JSON + PDF + README + audit slice for reviewers who will not run the API.

---

## Out of scope

- Payment · custody · settlement
- ISO/SOC certification claims from Noetfield
