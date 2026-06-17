# Live Proof Hero Receipt — Illustrative Label Law

**Version:** 1.0.0 · **Plan:** pf-0066 · **SKU:** — (platform) · **Phase:** 6  
**Law:** Homepage live-proof panel is sandbox illustration — never a live production receipt claim

---

## One line

`#nfLiveProofHero` shows an illustrative TLE mock — artifact badge **Illustrative**, footer **not a live receipt**.

---

## DOM contract

| Element | Attribute / class | Law |
|---------|-------------------|-----|
| Panel host | `#nfLiveProofHero` · `data-live-proof-hero` | Governance playground container |
| Artifact badge | `.nf-artifact-panel-badge` | Must read **Illustrative** — not Verified |
| Receipt footer | `.nf-receipt-mock-footer` | Must include `not a live receipt` |
| Live evaluate | `noetfield-live-proof.js` | Sandbox evaluate only |

---

## Copy law (locked)

```text
Badge: Illustrative
Footer: Illustrative sample — not a live receipt · Download TLE YAML
```

**Do not say:** "Verified" · "Live receipt" · "Production TLE" on homepage mock without pilot keys.

---

## www alignment

- `/index.html` — hero panel in section 01 · Pilot
- SSOT link in footer optional: `/docs/www/NF_LIVE_PROOF_HERO_RECEIPT_v1.md`
- `verify-static-www.sh` — needle `Illustrative` in homepage check

---

## Upgrade path

```text
Homepage playground → /start/ sandbox → Copilot Governance Pack → production TLE
```

---

## Not in scope

- Replacing mock with live platform receipt on public homepage
- Payment rails · custody claims
- TrustField RPAA investor narrative

---

## Verify

```bash
grep -q 'Illustrative' index.html
grep -q 'not a live receipt' index.html
grep -q 'data-live-proof-hero' index.html
```
