# TrustField vs Noetfield — conflict matrix (corpus vs product)

**Task:** `nf-trustfield-conflicts-003`  
**Status:** LOCKED reference  
**Last updated:** 2026-06-06  

---

## Rule

| Entity | Repo / chat | Noetfield may implement? |
|--------|---------------|---------------------------|
| **Noetfield** | `kazemnezhadsina144-dot/Noetfield` | **Yes** |
| **TrustField Technologies** | TrustField repo / private ops | **No** |
| **VIRLUX** | VIRLUX repo | **No** |

---

## Dual-brand narrative (govern-first handoff)

**Public line (safe):**

> Noetfield defines governance and trust requirements for AI-enabled financial programs. TrustField Technologies delivers RPAA-aligned readiness and partner execution in Canada.

**Internal line:**

> Noetfield is the **control layer** (policy, evidence, allow/reject before execution). TrustField is the **regulated-delivery layer** (RPAA pilots, MSP partners, operational path). Separate brands; explicit handoff when both are in a deal.

**When both in a deal:**

1. Noetfield ships governance evidence (Trust Brief, TLE, audit export) — **no payment execution**.
2. TrustField ships RPAA readiness pilot / partner execution — **TrustField repo only**.
3. SOW must name which entity owns which deliverable; no blended “one company does both” without written boundary.

---

## Conflict matrix

| Topic | TrustField / corpus risk | Noetfield product position | Action |
|-------|--------------------------|---------------------------|--------|
| Payment execution | MSB, corridors, settlement | Pre-execution only; no money movement | **Reject** in Noetfield PRs |
| Custody / wallets | Execution narratives | Governance overlay only | **Reject** |
| TrustField corporate GTM | Parent brand bleed | Coordinated narrative / **separate repos** | **Clarify** in copy; no TF implementation here |
| Trust Ledger brand | Shared marketing term | Noetfield audit export + RID (not TF product) | **Clarify** in copy |
| Copilot governance | May appear in TF decks | **Primary** Noetfield SKU (Lane A) | **Build** here |
| Bank pilot shadow | TF execution stories | FRFI vendor layer; no RPAA claims | **Build** evaluate/export only |
| KYC / member ledger | Credit union ops | Phase C / partner; not MVP | **Defer** Lane C |
| VIRLUX FX | Payment product | Zero VIRLUX env/copy in Noetfield | **Block** |
| `todolist/` public | TF task bleed | GitHub Issues only | **No** root todolist |
| SourceA SSOT bulk | Multi-entity corpus | Read-only context; PRODUCT_TRUTH governs code | **Filter** at implement |
| Govern-first sequencing | TF pilot without evidence | Noetfield evaluates + records before partner execute | **Lead** with TLE / shadow evaluate |

---

## Safe imports from corpus

- Governance vocabulary (allow/deny/review, RID, evidence)
- OSFI E-23 readiness **narrative** (not licensing claims)
- Microsoft 365 Copilot **policy** patterns (not deployment execution)
- Dual-brand **public line** in outreach (Noetfield repo docs only — no TrustField code)

---

## Verification

```bash
./scripts/verify-boundary-matrix.sh
test -f docs/spec/trustfield-noetfield-conflict-matrix.md
grep -q "Noetfield may implement" docs/spec/trustfield-noetfield-conflict-matrix.md
```

---

**END**
