# TrustField vs Noetfield — conflict matrix (corpus vs product)

**Task:** `nf-trustfield-conflicts-003`  
**Status:** LOCKED reference  
**Last updated:** 2026-06-03  

---

## Rule

| Entity | Repo / chat | Noetfield may implement? |
|--------|---------------|---------------------------|
| **Noetfield** | `kazemnezhadsina144-dot/Noetfield` | **Yes** |
| **TrustField Technologies** | TrustField repo / private ops | **No** |
| **VIRLUX** | VIRLUX repo | **No** |

---

## Conflict matrix

| Topic | TrustField / corpus risk | Noetfield product position | Action |
|-------|--------------------------|---------------------------|--------|
| Payment execution | MSB, corridors, settlement | Pre-execution only; no money movement | **Reject** in Noetfield PRs |
| Custody / wallets | Execution narratives | Governance overlay only | **Reject** |
| TrustField corporate GTM | Parent brand bleed | Noetfield standalone on www | **Separate** docs |
| Trust Ledger brand | Shared marketing term | Noetfield audit export + RID (not TF product) | **Clarify** in copy |
| Copilot governance | May appear in TF decks | **Primary** Noetfield SKU (Lane A) | **Build** here |
| Bank pilot shadow | TF execution stories | FRFI vendor layer; no RPAA claims | **Build** evaluate/export only |
| KYC / member ledger | Credit union ops | Phase C / partner; not MVP | **Defer** Lane C |
| VIRLUX FX | Payment product | Zero VIRLUX env/copy in Noetfield | **Block** |
| `todolist/` public | TF task bleed | GitHub Issues only | **No** root todolist |
| SourceA SSOT bulk | Multi-entity corpus | Read-only context; PRODUCT_TRUTH governs code | **Filter** at implement |

---

## Safe imports from corpus

- Governance vocabulary (allow/deny/review, RID, evidence)
- OSFI E-23 readiness **narrative** (not licensing claims)
- Microsoft 365 Copilot **policy** patterns (not deployment execution)

---

## Verification

```bash
test -f docs/spec/trustfield-noetfield-conflict-matrix.md
grep -q "Noetfield may implement" docs/spec/trustfield-noetfield-conflict-matrix.md
```

---

**END**
