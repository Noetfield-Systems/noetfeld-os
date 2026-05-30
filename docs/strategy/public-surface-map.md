# Public surface map (internal)

**Principle:** Each URL owns **one slice** of the story. Visitors self-select; we do not lead the brand with API labels, vertical slogans, or loud “we do / we do not” lists. Boundary facts appear where procurement needs them (API page, Trust Ledger, contracts) — not repeated on every hero.

**Pattern (Canadian regulated-tech):** Segment like mature infrastructure vendors — brand home for narrative, product pages for buyers, **developer/API corner** for engineers, partner page for channel. Avoid homepage API bars and avoid duplicating endpoint tables on five pages.

---

## Surface roles

| URL | Owns | Does not duplicate |
|-----|------|---------------------|
| **/** | Governance · AI systems · risk intelligence; three offerings; Trust Brief CTA | Endpoint tables, partner verticals, curl samples |
| **/enterprise/** | Institutional problem / risk / solution; three offerings; console pointer | Full API reference (link only) |
| **/trust-brief/** | $10k diagnostic scope; board-ready outputs | API, partners |
| **/copilot/** | M365 Copilot governance pack | API detail (optional single footer link) |
| **/console/** | Evaluation UI; RID + compliance log | OpenAPI |
| **/trust-ledger/** | Audit lineage brand; how evidence is produced (concept) | Full route catalog |
| **/partners/** | Programs, intakes, Canada timing; who to call | Endpoint catalog → **/docs/api/** |
| **/docs/api/** | **All HTTP contracts**, OpenAPI, SDK, status | Sales narrative, fintech positioning |
| **/bank-pilot/** | Shadow simulation story + one sample curl | MSB/PSP product marketing |
| **/status/** | Live health | Product pitch |

---

## Tone

- **Show** structure (evaluate → log → export), do not **announce** category membership (MSB, PSP, fintech) on the homepage.
- **Do not** stack negative disclaimers on every page; one factual line on API or ledger pages is enough for diligence.
- **Expand** after the simple narrative: Trust Brief → pilot → API keys → annual license ([GO_FORWARD_NOW.md](./GO_FORWARD_NOW.md)).

---

## Navigation

- **Header (5):** Home, Enterprise, Trust Brief, Copilot, Governance Console — unchanged.
- **Footer:** Offerings + **Governance API** + Status — API is discoverable, not primary nav.
