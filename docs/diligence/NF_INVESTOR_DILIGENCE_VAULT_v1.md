# Investor Diligence Vault

**Version:** 1.0.0 · **Plan:** pf-0069 · **SKU:** — (platform) · **Phase:** 6  
**Law:** Honest ARR · no logo inflation · artifact vault not deck claims

---

## One line

`/investors/diligence/` is the evidence vault for VCs — shadow evaluate, TLE samples, 18-item checklist — with explicit **no ARR inflation** copy on `/investors/`.

---

## Canonical URLs

| Surface | URL |
|---------|-----|
| Investors hub | `/investors/` |
| Diligence vault | `/investors/diligence/` |
| VC scenario | `/?lane=investor#nfLiveProofHero` |
| TLE samples | `/trust-ledger/sample-report/` |
| Procurement ZIP | `/copilot/procurement/` |

---

## Honest copy law (locked)

On `/investors/`:

> We do not inflate ARR or logo count. Product is shipped and demoable today — capital accelerates **first contracted Governance Pack** and **referenceable board PDF** on the three locked SKUs.

**Do not say:** ARR figures · logo wall · ISO/SOC certification from Noetfield · custody · MSB execution.

---

## Vault checklist (18-item orientation)

| # | Item |
|---|------|
| 1–6 | Product shipped · evaluate API · TLE v1 · board PDF path · procurement ZIP · shadow mode |
| 7–12 | Three SKUs · metadata-only M365 · fail-closed export · separate TrustField boundary |
| 13–18 | Capital use · first reference customer · board PDF success signal · honest competitive posture |

Full checklist rendered on `/investors/diligence/` as `nf-vault-checklist`.

---

## www alignment

- Shell v43 per [`NF_SHELL_V43_COHERENCE_v1.md`](../www/NF_SHELL_V43_COHERENCE_v1.md)
- Link to this SSOT from diligence vault hero or rail
- `verify-static-www.sh` — `Investor Diligence Vault` · `18-item checklist`

---

## Not in scope

- Term sheet or cap table disclosure on public www
- TrustField RPAA program in same vault thread
- FINTRAC KYB claims

---

## Verify

```bash
grep -q 'do not inflate ARR' investors/index.html
grep -q 'NF_INVESTOR_DILIGENCE_VAULT' investors/diligence/index.html
bash scripts/verify-static-www.sh
```
