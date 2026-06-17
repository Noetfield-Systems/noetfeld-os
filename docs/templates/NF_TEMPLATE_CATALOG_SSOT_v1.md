# Template Catalog SSOT

**Version:** 1.0.0 · **Plan:** pf-0062 · **SKU:** NF-QS (platform) · **Phase:** 5  
**Law:** Templates are runtime demos — three contract SKUs on www unchanged

---

## One line

Single source of truth for `/templates/` catalog cards — matches `packages/templates/REGISTRY.json` and `OFFERINGS_LOCKED.md`.

---

## Registry mirror

| template_id | Title | policy_pack | status | badge |
|-------------|-------|-------------|--------|-------|
| `copilot-governance` | Copilot Governance Template | `copilot-governance-v1` | `active` | **Active** |
| `osfi-e23-bank` | OSFI E-23 Bank Shadow Template | `bank-pilot-v1` | `stub` | **Design partner** |

---

## Contract SKU cards (not templates)

| Card | SKU | Price | badge |
|------|-----|-------|-------|
| Trust Brief | NF-TB | $10,000 | **Contract SKU** |
| Copilot Governance Pack | NF-CG | $2k–10k | (via template deploy CTA) |
| Bank Pilot | NF-BP | Enterprise | (via shadow template) |

---

## Status badge law

| Badge class | Label | When |
|-------------|-------|------|
| `nf-signal-badge--available` | Active | `REGISTRY.json` status `active` |
| `nf-signal-badge--orientation` | Design partner | `REGISTRY.json` status `stub` |
| `nf-signal-badge--roadmap` | Contract SKU | Fixed-fee www offerings (Trust Brief) |

---

## Deploy CTAs

| template_id | deploy_cta |
|-------------|------------|
| `copilot-governance` | `/start/?template=copilot-governance-v1` |
| `osfi-e23-bank` | `/trust-brief/intake/?interest=pilot&vector=bank-pilot` |

---

## www alignment

- `/templates/index.html` — `nf-signal-badge` pills on each catalog card
- Hero CTA: `/start/?template=copilot-governance-v1`
- SSOT doc link in section lead (optional footer)

---

## Not in scope

- Invented vertical packs not on disk
- Agent factory marketplace claims
- TrustField blend in same SOW

---

## Verify

```bash
test -f packages/templates/REGISTRY.json
grep -q 'nf-signal-badge' templates/index.html
grep -q 'Trust Brief' docs/templates/NF_TEMPLATE_CATALOG_SSOT_v1.md
```
