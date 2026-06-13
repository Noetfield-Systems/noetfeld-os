# Noetfield www design reference goals (LOCKED v1)

**Status:** LOCKED — visual and UX targets for public GTM surfaces.  
**Not for:** competitor battlecards, “vs” pages, or saved third-party teardown docs.  
**Use for:** building and reviewing `www.noetfield.com` — pick these patterns and ship them in HTML/CSS.

---

## Locked reference patterns (follow, do not copy logos or copy)

| ID | Pattern | Goal on Noetfield |
|----|---------|-------------------|
| **R1** | **Receipt-first proof** | Hero includes a live **TLE receipt mock** — monospace fields, verified badge, `export_integrity: PASS`. Proof before pitch. |
| **R2** | **Institutional dark + gold** | Bank-grade palette: `#07070b` base, gold accent, IBM Plex serif headlines, glass sticky nav. No startup-bright SaaS gradients. |
| **R3** | **Honest scope strip** | **Shipped / Orientation / Roadmap / Out of scope** badges on every GTM hub — no certifier or custody claims. |
| **R4** | **Numbered narrative** | Sections **01–06**: loop → scope → buyers → lanes → proof → SKUs. One story, scroll depth like premium institutional sites. |
| **R5** | **Split premium hero** | Left: kicker + H1 + buyer line + CTAs. Right: artifact panel (receipt mock or governance loop). |
| **R6** | **Procurement-ready proof grid** | Demo · TLE samples · Procurement ZIP · Enterprise lane — cards with icon + one-line outcome. |
| **R7** | **Three SKUs only** | Trust Brief ($10k) · Copilot Governance Pack ($2k–10k) · Bank Pilot (custom) — featured cards, no SKU creep. |
| **R8** | **Mega CTA close** | Full-bleed gold-border band: Request Governance Brief + design partner. Every hub page ends here. |
| **R9** | **Lane hubs** | Federal and MSP get same www shell — hero, trust anchors, proof grid, CTA. No separate “compare” surface. |
| **R10** | **Metadata-only M365** | Copy always: complement Purview, not replace; invalid blocked, allowed receipted, tamper fails on export. |

---

## Implementation (repo)

| Asset | Role |
|-------|------|
| `body.nf-www` | Global www layout — wide wrap, hide legacy offerings strip |
| `assets/noetfield-www.css?v=9` | **Imports enterprise v5 (Veridra/Credo reference)** — no invented components |
| `assets/noetfield-enterprise.css` | Locked reference stylesheet (receipt mock, cinematic hero, stat bar, sections 01–06) |
| `assets/noetfield-tokens.css` | Design tokens — `--gold-bright`, `--max-wide: 1320px` |
| `scripts/rebuild-www-v6.py` | Regenerates all GTM hub pages from zero |
| `assets/partials/header.html` | Home · Enterprise · Trust Brief · Copilot · Federal · MSP · Demo |
| `index.html` | Canonical homepage — cinematic hero + sections 01–06 |

---

## Explicitly out of scope (www)

- Battlecards, competitor-named markdown, `/compare/` hubs  
- “Vs {vendor}” tables or links to third-party positioning docs  
- Category comparison matrices with competitor columns  
- Saving reference site screenshots or teardowns in `docs/strategy/`

References inform **design quality** only. The website is the artifact.

---

## Verify

- Homepage E2E: `audit trail your Copilot deployment`, `Become a design partner`, `5-minute demo`, `Procurement pack`  
- Visual: receipt mock + stat bar + numbered sections render (enterprise CSS loaded)  
- Nav: no Compare link; Federal + MSP present  

**Related:** [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) · [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](./strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md)
