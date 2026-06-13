# WWW v13 — Institutional 100-Step Upgrade Plan (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED execution roadmap — bank / VC / procurement grade |
| **Scope** | Public www · trust center · lane hubs · workspace shell · intake |
| **Not for** | Vendor names, comparison pages, SKU #4, fake certs/logos/ARR |
| **Parent** | [DESIGN_REFERENCE_GOALS_LOCKED_v1.md](./DESIGN_REFERENCE_GOALS_LOCKED_v1.md) · [GTM_COPYBOOK.md](./GTM_COPYBOOK.md) |
| **Generator** | `scripts/rebuild-www-v6.py` · bump `?v=13` |
| **Verify** | `make verify-no-vendor-names` · `make verify-ui-e2e` · `make verify-gtm` |

---

## Executive summary — what institutional buyers actually buy

After mapping **six buyer committees** (CISO, GRC/compliance, procurement/vendor management, board/corporate secretary, MSP channel, federal GC/digital), the pattern is consistent:

1. **Proof before pitch** — a receipt, sample export, or verify walkthrough beats feature lists.
2. **Honest scope** — Shipped / Orientation / Roadmap / Out of scope beats cert theater.
3. **Procurement without a call** — trust center + samples + ZIP path + API orientation.
4. **One wedge sentence** — “We receipt Copilot execution decisions” — not “AI governance platform.”
5. **Three SKUs, fixed bands** — Trust Brief · Copilot Pack · Bank Pilot — no catalog creep.
6. **Microsoft complement** — factual CCS/Purview Learn links; never imply partnership.
7. **Board artifact** — PDF in a governance meeting unlocks budget (W3 bar).
8. **Channel attach** — MSP Phase 2 after Phase 1 readiness; not competitive with partner stack.

v13 turns these into **visual hierarchy, typography, and conversion rails** — not more copy.

---

## Phase I — Buyer truth & positioning lock (Steps 1–10)

| # | Step | Done when |
|---|------|-----------|
| 1 | Lock wedge one-liner across generator, copybook, Worker V3 — no conflicting heroes | Single string in `rebuild-www-v6.py` + `GTM_COPYBOOK.md` |
| 2 | Lock three verbs **Evaluate · Record · Export** on every P0 hub | E2E grep on homepage + copilot + enterprise |
| 3 | Lock primary CTA **Request Governance Brief** → intake with RID | All hubs end with same mega CTA variant |
| 4 | Lock honest scope badges on every GTM hub (§02 pattern) | Shipped/Orientation/Roadmap/N/A visible |
| 5 | Remove any residual “platform inventory” language from public HTML | No “govern AI everywhere” tone |
| 6 | Add procurement rail on homepage (trust · pack · samples · verify) | v13 `nf-procurement-rail` live |
| 7 | Ensure investor page uses zone labels only — no company names | `verify-no-vendor-names` PASS |
| 8 | Federal hub: official canada.ca / tbs-sct links above fold | E2E federal row green |
| 9 | MSP hub: Phase 1→2 ladder + W3-MSP criteria visible | E2E msp row green |
| 10 | Document buyer persona → page map in copybook (internal) | Table: CISO→demo, Procurement→trust, etc. |

---

## Phase II — Design system v13 tokens (Steps 11–20)

| # | Step | Done when |
|---|------|-----------|
| 11 | Bump design tokens to **v13** — spacing scale, motion, focus ring | `noetfield-tokens.css` |
| 12 | Add **trust diligence sub-theme** CSS vars (lighter panel for `/trust/`) | `body.nf-trust-diligence` |
| 13 | Standardize `--max-wide: 1320px` on all www pages | No orphan 1140px wraps |
| 14 | Serif headlines (IBM Plex Serif) on H1/H2 only; sans on UI chrome | Typography audit |
| 15 | Gold accent discipline — one primary CTA gold fill per viewport | Button hierarchy check |
| 16 | Monospace artifact fields on all receipt mocks (tle_id, rid, export_integrity) | Consistent `nf-receipt-mock` |
| 17 | Status colors: ok green, review amber, deny red — locked tokens | `--ok`, `--warn`, `--deny` |
| 18 | Print stylesheet for trust + procurement pages | `noetfield-print.css` linked on `/trust/` |
| 19 | Dark mode only for GTM; trust sub-theme optional light for PDF readers | Procurement persona test |
| 20 | Document v13 patterns R15–R20 in DESIGN_REFERENCE | SSOT updated |

---

## Phase III — Shell, nav, footer (Steps 21–30)

| # | Step | Done when |
|---|------|-----------|
| 21 | Sticky glass nav with blur — max-width aligned to content | `#nfHeader` v13 polish |
| 22 | Add **Trust** to primary nav (procurement entry) | `header.html` |
| 23 | Mobile panel: trust + procurement + workspace links | Mobile grid complete |
| 24 | Footer: Proof column links trust, verify, samples, status | `footer.html` |
| 25 | RID row in footer — copy button + intake deep link | Shell JS `data-rid` |
| 26 | Stack context footer links — CCS + Purview Learn only | No partner vendor links |
| 27 | Skip link + focus visible on all interactive elements | a11y spot check |
| 28 | Shell version bump `2026.06.02.v13` for cache bust | `noetfield-shell.js` |
| 29 | Remove legacy CSS classes from orphan pages via migrate script | No `nf-section__` on hubs |
| 30 | Nav active state for current hub (aria-current="page") | Shell JS enhancement |

---

## Phase IV — Homepage & core GTM (Steps 31–40)

| # | Step | Done when |
|---|------|-----------|
| 31 | Cinematic hero: receipt mock + buyer line + 3 CTAs | Homepage §hero |
| 32 | Stat bar: 4 · $10k · 90d · 3 SKUs — factual only | No analyst stats |
| 33 | §01 governance loop — four steps with institutional cards | Evaluate→Export |
| 34 | §02 honest scope grid | 6 rows minimum |
| 35 | §03 buyer personas — CISO, GRC, Procurement, CIO | Persona cards |
| 36 | §04–06 lanes + proof grid + three SKU cards | Offerings locked |
| 37 | §07 pain moment — “who approved this deployment?” | E2E heading |
| 38 | §08 category zones — no vendor names | Zone grid |
| 39 | §09 CCS stack ladder | Learn links |
| 40 | §10 FAQ — 6 buyer questions | `<details>` accessible |

---

## Phase V — Trust, procurement, diligence (Steps 41–50)

| # | Step | Done when |
|---|------|-----------|
| 41 | `/trust/` light diligence sub-theme body class | Readable long-form |
| 42 | Trust cert table — Shipped/Roadmap/N/A only | No fake SOC2 Shipped |
| 43 | Data handling section — metadata-only M365 explicit | Privacy cross-link |
| 44 | Export integrity section → verify walkthrough CTA | `/trust-ledger/verify/` |
| 45 | `/copilot/procurement/` links trust + NIST orientation | Procurement E2E |
| 46 | Sample TLE trio (go · conditional · rejected) downloadable | YAML paths live |
| 47 | Verify page: fail-closed explanation + steps | Tamper sample |
| 48 | Status page linked from trust footer | Uptime honest |
| 49 | Canada trust notes linked from trust/data section | `/docs/api/CANADA_TRUST.md` |
| 50 | Procurement rail duplicated on trust + procurement hubs | Consistent path |

---

## Phase VI — Lane hubs (Steps 51–60)

| # | Step | Done when |
|---|------|-----------|
| 51 | `/copilot/` — hero + workspace mock + CCS ladder | Product-in-hero |
| 52 | `/copilot/demo/` — 5-minute script steps 1–6 | Demo E2E |
| 53 | `/copilot/pilot/` — design partner band + timeline | W3 copy |
| 54 | `/trust-brief/` — $10,000 visible + 6-week table | Price E2E |
| 55 | `/enterprise/` — bank shadow mode honest | No custody claims |
| 56 | `/federal/` — ADM deadline chip + AIA preview table | June 2026 chip |
| 57 | `/msp/` — phase ladder + RACI table + mapping doc links | Two-tier visible |
| 58 | `/investors/` — thesis + scarcity + zone map | No ARR fiction |
| 59 | `/partners/` — gateway only; no payments lead | Boundary clean |
| 60 | `/faq/` aligned with homepage §10 themes | Single FAQ SSOT |

---

## Phase VII — Product & workspace UI (Steps 61–70)

| # | Step | Done when |
|---|------|-----------|
| 61 | Align governance console tokens with www gold/dark base | `globals.css` parity |
| 62 | Workspace list — institutional table density | Bank-grade rows |
| 63 | TLE detail — confidence badge + PDF + ZIP above fold | E2E export links |
| 64 | Evaluate → result flow — decision + confidence visible | E2E rid flow |
| 65 | Connectors page — mock M365 path labeled honestly | No fake OAuth brands |
| 66 | Cognitive dashboard — shadow simulation copy | Read-only explicit |
| 67 | Audit log — RID threading visible | Ops traceability |
| 68 | Receipt visual in workspace matches www mock fields | Field name parity |
| 69 | Empty states — CTA to demo or intake, not dead ends | UX review |
| 70 | 404 page — institutional tone + intake CTA | `not-found.tsx` |

---

## Phase VIII — Intake & conversion (Steps 71–80)

| # | Step | Done when |
|---|------|-----------|
| 71 | Single intake router `/trust-brief/intake/` covers all vectors | Query params documented |
| 72 | Interest params: copilot · federal · msp · bank-pilot · api | GTM_COPYBOOK table |
| 73 | RID generated on shell load + appended to intake links | `data-rid-link` |
| 74 | Intake form — institutional layout (`noetfield-intake.css`) | Mobile OK |
| 75 | Post-submit copy — operations@ + RID in confirmation | No fake automation |
| 76 | Design partner scarcity — honest count on investors + pilot | No fake logos |
| 77 | Email templates (Hub) — buyer proof oriented, no vendor refs | Internal only |
| 78 | Mega CTA on every hub — primary intake + secondary pilot | Visual audit |
| 79 | Console CTA routes to evaluate, not checkout | NF-04 gated |
| 80 | Gate `/gate/intake/` alias behavior documented | Redirect SSOT |

---

## Phase IX — Accessibility, motion, performance (Steps 81–90)

| # | Step | Done when |
|---|------|-----------|
| 81 | `prefers-reduced-motion` — disable hero fade / card lift | CSS media query |
| 82 | Color contrast AA on gold on dark — audit eyebrow + links | Lighthouse a11y |
| 83 | All images `alt` — decorative favicons empty alt | HTML audit |
| 84 | Table captions for AIA preview + RACI tables | `sr-only` captions |
| 85 | FAQ `<details>` keyboard operable | Manual test |
| 86 | Font subset — preload Plex weights used on www | LCP improvement |
| 87 | CSS single bundle path — tokens → shell → www | No duplicate imports |
| 88 | Static HTML cache headers documented for CDN | Deploy note |
| 89 | Hero receipt mock — no layout shift on mobile stack | CLS check |
| 90 | Print: hide nav, show RID + canonical URL in footer | Print preview |

---

## Phase X — Verify, W3 proof, ship gates (Steps 91–100)

| # | Step | Done when |
|---|------|-----------|
| 91 | `make verify-no-vendor-names` in CI / pre-demo bundle | Wired in verify-gtm |
| 92 | `verify-ui-e2e` — homepage §07–10 + no vendor names live | Script green |
| 93 | `rebuild-www-v6.py` sole SSOT — zero hand-edited GTM HTML | P-02 prompt done |
| 94 | Board PDF export E2E from workspace TLE | W3 critical path |
| 95 | Procurement ZIP export E2E | W3 critical path |
| 96 | 5-minute demo URL in SHIP_NOW | Founder outreach ready |
| 97 | Tier 1 prompt L-02/L-03 marked done after v13 ship | tier1-status.json |
| 98 | Design partner LOI template linked from MSP hub | Channel ready |
| 99 | First buyer debrief template on disk (sanitized) | Ops hygiene |
| 100 | W3 PASS: board PDF in meeting **or** deposit ≥ CAD 2K — celebrate, freeze v13 | Commercial proof |

---

## v13 pattern additions (DESIGN_REFERENCE R15–R20)

| ID | Pattern | Goal |
|----|---------|------|
| **R15** | **Procurement rail** | Persistent strip: Trust · Pack · Samples · Verify — procurement never hunts |
| **R16** | **Trust diligence theme** | Lighter `/trust/` reading surface for legal/procurement PDF export |
| **R17** | **Dual artifact hero** | Receipt mock + workspace mock on product hubs |
| **R18** | **Institutional table density** | RACI, AIA, cert tables — compact, captioned, printable |
| **R19** | **Board-ready stat bar** | Four facts max — no vanity metrics |
| **R20** | **Console parity** | Workspace UI matches www receipt field names and colors |

---

## Execution order (recommended sprints)

| Sprint | Steps | Outcome |
|--------|-------|---------|
| **S0** (now) | 11–13, 21–22, 28, 6, 41 | v13 tokens + nav + procurement rail + trust theme |
| **S1** | 31–40, 91–93 | Homepage complete + verify green |
| **S2** | 41–50, 51–53 | Trust + procurement + copilot hub |
| **S3** | 54–60 | All lane hubs institutional |
| **S4** | 61–70 | Workspace/console parity |
| **S5** | 71–80, 94–100 | Conversion + W3 proof |

---

## Anti-patterns (never ship)

- Vendor comparison grids, scorecards, or “vs” pages on public www  
- Fake SOC2/ISO Shipped badges without evidence  
- Fourth SKU or Trust Ledger SaaS checkout  
- Logo walls, ARR, analyst firm name-drops  
- Purple MSP-SaaS gradients on institutional pages  
- Hand-editing generated HTML outside `rebuild-www-v6.py`  

---

**Related:** [WWW_V12_MASTER_PLAN_LOCKED_v1.md](./WWW_V12_MASTER_PLAN_LOCKED_v1.md) · [NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md](./ops/NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md)
