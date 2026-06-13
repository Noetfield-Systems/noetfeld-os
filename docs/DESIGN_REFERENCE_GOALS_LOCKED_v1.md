# Noetfield www design reference goals (LOCKED v1)

**Status:** LOCKED — visual and UX targets for public GTM surfaces.  
**Not for:** vendor comparison pages, “vs” pages, or saved third-party teardown docs.  
**Use for:** building and reviewing `www.noetfield.com` — pick these patterns and ship them in HTML/CSS.

---

## Locked reference patterns (follow, do not copy logos or copy)

| ID | Pattern | Goal on Noetfield |
|----|---------|-------------------|
| **R1** | **Receipt-first proof** | Hero includes a live **TLE receipt mock** — monospace fields, verified badge, `export_integrity: PASS`. Proof before pitch. |
| **R2** | **Institutional light + gold** | Bank-grade palette: `#f4f5f8` base, gold accent `#8a6b1f`, IBM Plex sans headlines, white sticky nav. |
| **R3** | **Honest scope strip** | **Shipped / Orientation / Roadmap / Out of scope** badges on every GTM hub — no certifier or custody claims. |
| **R4** | **Numbered narrative** | Sections **01–10**: loop → scope → buyers → lanes → proof → SKUs → pain → category → stack → FAQ. |
| **R5** | **Split premium hero** | Left: kicker + H1 + buyer line + CTAs. Right: artifact panel (receipt mock or governance loop). |
| **R6** | **Procurement-ready proof grid** | Demo · TLE samples · Procurement ZIP · Enterprise lane — cards with icon + one-line outcome. |
| **R7** | **Three SKUs only** | Trust Brief ($10k) · Copilot Governance Pack ($2k–10k) · Bank Pilot (custom) — featured cards, no SKU creep. |
| **R8** | **Mega CTA close** | Full-bleed gold-border band: Apply for pilot ($2k–10k) + Trust Brief secondary. Every hub page ends here. |
| **R9** | **Lane hubs** | Federal and MSP get same www shell — hero, trust anchors, proof grid, CTA. No separate “compare” surface. |
| **R10** | **Metadata-only M365** | Copy always: complement Purview, not replace; invalid blocked, allowed receipted, tamper fails on export. |
| **R11** | **Category orientation strip** | Public www zone grid — no vendor names; investor page may name zones. |
| **R12** | **Pain moment (§07)** | Copilot live → auditor asks — before registry/inventory pitch. |
| **R13** | **Trust hub** | `/trust/` — honest scope / cert table; linked from footer + procurement. |
| **R14** | **CCS complement diagram** | Stack ladder on homepage §09 and `/copilot/` — Phase 1 partner · Phase 2 Noetfield. |
| **R15** | **Procurement rail** | Strip on homepage + trust: Trust · Pack · Samples · Verify |
| **R16** | **Trust diligence theme** | Light `/trust/` sub-theme for procurement/legal readers |
| **R17** | **Dual artifact hero** | Receipt mock + workspace mock on product hubs |
| **R18** | **Institutional table density** | RACI, AIA, cert tables — compact, captioned |
| **R19** | **Board-ready stat bar** | Four factual metrics max — no vanity stats |
| **R20** | **Console parity** | Workspace UI matches www receipt field names |
| **R21** | **Self-serve rail** | Homepage + hubs: “Try without a sales call” strip → `/start/` · `/pricing/` · API |
| **R22** | **Pack grid (not 4th SKU)** | `nf-pack-card` on `/start/` + `/pricing/` — free · program · 2 contract SKUs in grid |
| **R23** | **Sandbox signup form** | Work email → instant tenant · 14d · 50 evaluates · redirect to console |
| **R24** | **Sandbox vs production table** | `/pricing/` mode toggle + honest limits column |
| **R25** | **Agentic workflow strip** | Investigate · triage · draft TLE · low-risk act — with human gate on high-risk |
| **R26** | **Live Proof Hero** | Evaluate embed in hero — receipt animates from real API, not static YAML |
| **R27** | **Trial OS stepper** | Sandbox wizard · quota chip · sandbox/production env toggle |
| **R28** | **Command Center shell** | Left rail · context bar · ⌘K palette · optional Proof rail |
| **R29** | **Receipt Studio** | TLE split view — inspector + live receipt + sticky export dock |
| **R30** | **Decision Timeline** | RID-threaded evaluate → approve → export graph |
| **R31** | **Agent Command Deck** | In-product agent columns with human approve/reject gates |
| **R32** | **Usage meter chip** | 50 eval / 14d visible in product chrome |
| **R33** | **Proof mode toggle** | Light institutional default · dark artifact for board demos |
| **R34** | **Four-act homepage** | Try · Prove · Package · Trust — compress scroll |
| **R35** | **Visual QA gate** | Playwright baselines + Lighthouse budgets in CI |

---

## v18 tier-1 masterplan

**Execution SSOT:** [WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md](./WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md) — 10 upgrades · TTFR &lt; 90s north star.

**Packaging baseline:** [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](./WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) — self-serve · tiers · sandbox (UI-02 Trial OS builds on this).

**Institutional baseline:** [WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md](./WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md) — 100 steps · bank / VC grade.

## Explicitly out of scope (www)

- Vendor comparison pages, third-party positioning docs, comparison hub routes
- “Vs {vendor}” tables or links to third-party positioning docs
- Category comparison matrices with vendor columns on public homepage  
- Saving reference site screenshots or teardowns in `docs/strategy/`

References inform **design quality** only. The website is the artifact.

---

## Implementation (repo)

| Asset | Role |
|-------|------|
| `body.nf-www` | Global www layout — wide wrap, hide legacy offerings strip |
| `assets/noetfield-www.css?v=18` | **Imports enterprise + v14 light + v15 ref + v16 packaging + v18 tier-1 UI** |
| `body.nf-site-v14` | Light-first institutional default (bank / procurement grade) |
| `assets/noetfield-enterprise.css` | Locked reference stylesheet (receipt mock, cinematic hero, stat bar, sections 01–10) |
| `assets/noetfield-tokens.css` | Design tokens — `--gold-bright`, `--max-wide: 1320px` |
| `scripts/rebuild-www-v6.py` | Regenerates all GTM hub pages · `WWW_VER=16` |
| `assets/partials/header.html` | Pilot · $2k–10k · Demo · Sandbox · Pricing |
| `start/index.html` | Developer sandbox signup + async demo flow |
| `pricing/index.html` | Published tiers · sandbox vs production |
| `index.html` | Canonical homepage — cinematic hero + sections 01–10 |
| `trust/index.html` | Trust center — honest cert posture |
| `trust-ledger/verify/index.html` | Export integrity walkthrough |

---

## Verify

- Homepage E2E: `audit trail your Copilot deployment`, `Start free sandbox`, `Published tiers`, `Fully agentic workflows`, `Become a design partner`, `5-minute demo`
- `/start/` sandbox signup · `/pricing/` tier table
- `/trust/` live with honest cert table
- `/trust-ledger/verify/` tamper walkthrough
- Federal: canada.ca AIA + TBS ADM links above fold
- MSP: `Readiness → Record · Phase 2 TLE attach`
- Copilot: Copilot Control System complement copy
- Nav: no Compare link; Federal + MSP present

**Related:** [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) · [WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md](./WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md) · [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](./strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md)
