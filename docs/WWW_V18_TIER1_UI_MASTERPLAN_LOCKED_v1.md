# WWW v18 — Tier-1 UI masterplan (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED — **supersedes** [WWW_V17_TIER1_UI_UPGRADES_LOCKED_v1.md](./WWW_V17_TIER1_UI_UPGRADES_LOCKED_v1.md) |
| **Updated** | 2026-06-13 |
| **Scope** | UI only — www · product console · sandbox · export surfaces |
| **Benchmark bar** | Sumsub trial UX · Stripe proof-in-hero · Linear shell · Vercel polish · institutional GRC density |
| **North star metric** | Time-to-first-receipt (TTFR) **&lt; 90 seconds** from cold landing → real RID + confidence + export orientation |

---

## What “tier-1 UI” means for Noetfield

Not prettier cards. Buyers must **feel** three things in the first minute:

1. **This is real** — live evaluate, not marketing fiction  
2. **This is defensible** — receipt fields match export/PDF semantics  
3. **This is buyable** — sandbox → tiers → upgrade without a sales call  

Today the repo is **copy-tier-1**, **interaction-tier-2**, **system-tier-3** (split CSS stacks, grep-only QA, scroll-heavy homepage).

---

## Gap map (repo evidence)

| Surface | Shipped | Blocks world tier-1 |
|---------|---------|---------------------|
| **www** | v16 packaging, receipt mock, 15+ homepage sections | Static proof; no live hero; IA bloat |
| **Product** | `ReceiptMock`, evaluate→result, workspace export | CRUD layout; no command center; no timeline |
| **Sandbox** | `/start/` + localStorage + banner | No wizard, no usage meter UI, no API drawer |
| **Tokens** | `noetfield-tokens.css` (dark) + Tailwind (light duplicate) | Two truths for gold, radius, status colors |
| **QA** | `verify-ui-e2e.sh` string grep | No layout/perf/visual regression |

---

## The 10 upgrades (rewritten — UI-first)

Each item: **Benchmark → Ship → UX spec → Done when → Primary files**

---

### 1. Live Proof Hero — product *is* the homepage

**Benchmark:** Sumsub dashboard preview · Stripe embedded checkout · Vercel deploy button in hero  

**Gap:** `nf-artifact-panel` shows frozen YAML; visitor must scroll 10 sections before touching product.

**Ship:**
- Replace static receipt in hero with **Live Evaluate Mini** (3 fields + Submit).
- On success: animate receipt rows from API response (RID, decision, confidence, export_integrity).
- Deep link: “Open full result” → `/result/{rid}`; “Continue in sandbox” → dashboard.
- Offline: honest degraded mock + “Start sandbox when API returns”.

**UX spec:**
- Desktop: 55/45 split — narrative left, live panel right (keep R5).
- Mobile: evaluate first, receipt below fold within one swipe.
- Loading: skeleton rows in monospace panel, not spinner-only.

**Done when:** Homepage POST `/evaluate` returns RID visible in hero without navigation; e2e needle `live-proof-hero`.

**Files:** `assets/noetfield-live-proof.js`, `scripts/rebuild-www-v6.py` `hero()`, `ReceiptMock.tsx` (shared animate API).

---

### 2. Trial OS — guided sandbox (Sumsub-class)

**Benchmark:** Sumsub 14-day · 50 checks · sandbox/production toggle · API keys in-app  

**Gap:** Single form on `/start/` → redirect; no stepper, no quota UI, no env switcher.

**Ship:**
- Full-screen **Trial OS** wizard (www + optional `/onboarding` in product):
  1. Account (email · org)  
  2. Environment (**Sandbox** active · Production locked)  
  3. Connect mock M365 (one-click OAuth success UI)  
  4. First evaluate (embedded form)  
  5. Receipt + “Download sample export orientation”  
- Persistent **usage chip**: `12/50 evaluates · 11 days left`.
- **API drawer**: key preview, copy, curl example, link to `/docs/api/`.

**UX spec:**
- Progress: horizontal stepper, completed steps green-check.
- Production tile: blur + lock icon → `/copilot/pilot/`.
- Never block sandbox on sales call.

**Done when:** S0→S2 completable without leaving wizard; counter updates on evaluate; e2e `trial-os-flow`.

**Files:** `assets/noetfield-sandbox.js` v2, `noetfield-v18-trial-os.css`, `app/onboarding/page.tsx` (product mirror).

---

### 3. Command Center Shell 2.0 — stop looking like admin CRUD

**Benchmark:** Linear app shell · Vercel dashboard · Datadog org context bar  

**Gap:** `Shell.tsx` = top links + page stack; no tenant context, no ⌘K, no persistent receipt slot.

**Ship:**
- **Layout:** collapsible left rail · top context bar · main · optional right **Proof rail** (receipt).
- **Context bar:** tenant slug · Sandbox/Production pill · usage meter · Upgrade CTA.
- **Command palette (`⌘K`):** jump to RID, TLE id, routes, docs.
- **Proof mode toggle:** light institutional default ↔ dark artifact panel for board demos.
- **Mobile:** bottom tab bar (Dashboard · Evaluate · Workspace · More).

**UX spec:**
- Active route: left rail indicator + serif page title below bar.
- Proof rail collapses on &lt;1024px; receipt accessible via floating “Receipt” chip.

**Done when:** All routes use shell v2; palette finds TLE-015DCFB8B953; sandbox meter on every page.

**Files:** `AppShell.tsx`, `CommandPalette.tsx`, `UsageMeter.tsx`, `ProofRail.tsx`, retire thin `Shell.tsx` wrapper.

---

### 4. One Design Language — tokens + primitives package

**Benchmark:** Stripe `@stripe/ui` discipline · single source of truth  

**Gap:** www imports 4 CSS layers; product duplicates colors in `tailwind.config.ts`; R20 parity manual.

**Ship:**
- **`packages/ui-tokens/`** — CSS `:root` light institutional + JSON export for Tailwind.
- **Primitives (React + HTML partials):** `Button`, `Badge`, `ReceiptPanel`, `StatBar`, `PackCard`, `SectionHead`, `ScopeBadge`.
- **Ladle/Storybook** — every primitive + receipt states (allow/deny/review/tamper FAIL).
- Kill dark default tokens on light pages; one `--gold: #8a6b1f`, one `--ok`, one radius scale.

**UX spec:**
- Primary button: gold fill, one per viewport.
- Status: allow green · review amber · deny red — same hex www + product + PDF.

**Done when:** `ReceiptMock` fields === www mock === board PDF labels; Storybook builds in CI.

**Files:** `packages/ui-tokens/`, `governance-console/frontend/tailwind.config.ts`, `assets/noetfield-tokens.css` (thin re-export).

---

### 5. Homepage compression — four acts, one screen story

**Benchmark:** Stripe homepage arc · Sumsub above-fold trial CTA  

**Gap:** ~15 sections (rails, CISO, §01–§10, packaging, agentic) — cognitive overload.

**Ship — four acts only on `/`:**
| Act | Content | Fold |
|-----|---------|------|
| **TRY** | Hero + Live Proof + Start sandbox | Above |
| **PROVE** | 5-min demo · TLE samples · verify export | Above/below |
| **PACKAGE** | Compact tier strip → “See all tiers” `/pricing/` | Below |
| **TRUST** | CISO strip (4 cards) + mega CTA | Close |

Move FAQ, stack ladder, category map, extended personas → `/copilot/` hub (already hub-capable).

**UX spec:**
- Max **2** horizontal rails on homepage (self-serve + procurement — merge if needed).
- Sticky mobile CTA: “Start free sandbox”.

**Done when:** Section count ≤ 8; all current e2e commercial strings preserved via act copy or hub links; LCP &lt; 2.5s local.

**Files:** `rebuild-www-v6.py` — refactor `homepage()` + trim `homepage_extended_sections()`.

---

### 6. Receipt Studio — TLE detail as flagship screen

**Benchmark:** GitHub checks UI · audit trail products · split diff + summary  

**Gap:** `workspace/[tle_id]/page.tsx` = stacked cards; board demo jumps across pages.

**Ship:**
- **Split studio:** left = structured inspector (YAML/JSON tabs); right = live `ReceiptMock` + export dock.
- **Approval timeline:** vertical stepper (pending · signed · rejected) with avatars/roles.
- **Evidence chips:** Purview · Entra · audit — click → connector status drawer.
- **Export dock (sticky):** Board PDF · Procurement ZIP · Verify integrity · Copy manifest.
- **Inline PDF preview** (iframe/blob) before download — “what the board sees”.

**UX spec:**
- Default view: receipt + export dock visible without scroll on 1440×900.
- Tamper demo button (sandbox): shows FAIL state on export_integrity row.

**Done when:** Full board demo from one URL; existing PDF/ZIP e2e green; visual baseline captured.

**Files:** `ReceiptStudio.tsx`, `ApprovalTimeline.tsx`, `ExportDock.tsx`, `workspace/[tle_id]/page.tsx`.

---

### 7. Decision Timeline — RID-threaded governance graph

**Benchmark:** Linear issue history · Stripe event timeline · unique to governance category  

**Gap:** Audit log is a flat searchable table — no narrative of evaluate → approve → export.

**Ship:**
- New **Timeline** view (dashboard tab or `/audit/timeline`):
  - Nodes: Evaluate · Decision · Connector ingest · TLE draft · Approval · Export.
  - Edges keyed by RID; zoom to single decision thread.
- Click node → side panel with receipt snippet + link to full record.
- Filter: sandbox vs production · date · decision type.

**UX spec:**
- Institutional density toggle: **Comfortable / Compact** (GRC power users).
- Empty state: CTA to first evaluate, not blank table.

**Done when:** Evaluate flow populates ≥4 node types; e2e opens timeline and finds RID from evaluate.

**Files:** `DecisionTimeline.tsx`, `app/audit/timeline/page.tsx`, API aggregate (or client-side from audit list initially).

---

### 8. Agent Command Deck — autonomous UI, human gates

**Benchmark:** Tier-1 “agentic” = visible runs + approvals, not chatbot chrome  

**Gap:** Agentic story lives on www marketing strip only.

**Ship:**
- **Command deck** on dashboard (below hero, above evaluate):
  - Columns: Investigate · Triage · Draft TLE · Await human · Recorded.
  - Cards: agent step status, confidence, linked RID/TLE, elapsed time.
- Sandbox: simulated runs with honest “sandbox simulation” badge.
- High-risk: **Approve / Reject** inline (respect RBAC); low-risk: auto-advance animation.
- Link to www agentic copy for procurement readers.

**UX spec:**
- No sci-fi gradients; same institutional light shell.
- Keyboard: `j/k` move between cards when deck focused.

**Done when:** Deck visible on dashboard; one card navigates to evaluate or TLE; grep “Investigate” in client chunk.

**Files:** `AgentCommandDeck.tsx`, `cognitive-dashboard/page.tsx`.

---

### 9. Motion, performance & accessibility — feel fast and trustworthy

**Benchmark:** Vercel.com restraint · WCAG AA · CLS discipline  

**Gap:** WWW v13 steps 81–90 open; `prefers-reduced-motion` partial; bank-grade responsive unchecked.

**Ship:**
- **`noetfield-v18-motion.css`:** enter transitions, receipt sign pulse, stepper slide — all gated by `prefers-reduced-motion`.
- **Perf:** preload only used Plex weights; hero receipt reserved height (zero CLS).
- **A11y pass:** gold-on-light contrast · focus rings · table captions · keyboard FAQ.
- **Responsive matrix:** 320 / 768 / 1280 / 1440 sign-off checklist.

**UX spec:**
- Motion duration ≤ 200ms for functional feedback; no parallax.
- Touch targets ≥ 44px on sandbox wizard + export dock.

**Done when:** Lighthouse a11y ≥ 95 on `/` and `/start/`; CLS ≤ 0.1; responsive checklist signed in BANK_GRADE.

**Files:** `noetfield-v18-motion.css`, `noetfield-www.css` import, product `globals.css` focus tokens.

---

### 10. Visual QA gate — never ship ugly regressions

**Benchmark:** Stripe/Percy · Vercel preview checks · Linear screenshot tests  

**Gap:** Only `curl | grep` — layout can break silently.

**Ship:**
- **Playwright visual suite:** `/`, `/start/`, `/pricing/`, evaluate→result, TLE Receipt Studio, shell v2.
- **Viewports:** 320 · 768 · 1280 baseline PNGs committed (or CI artifact).
- **Lighthouse CI:** LCP, CLS, a11y budgets on P0 URLs.
- **`make verify-ui-visual`** → wired into `verify-gtm` after `verify-ui-e2e`.
- PR rule: intentional visual change updates baselines in same PR as code.

**Done when:** CI fails on 10px+ receipt panel shift; documented in `BANK_GRADE_CHECKLIST.md` Pillar 5.

**Files:** `governance-console/playwright/`, `scripts/verify-ui-visual.sh`, `.github/workflows/ui-visual.yml`.

---

## Build waves (recommended)

```text
Wave A — Belief (week 1–2 UI):  #1 Live Proof Hero · #2 Trial OS · #5 Homepage compression
Wave B — Product (week 3–4):     #3 Shell 2.0 · #6 Receipt Studio · #7 Timeline
Wave C — System (week 5–6):      #4 Design Language · #8 Agent Deck · #9 Motion/a11y
Wave D — Stay tier-1 (ongoing):  #10 Visual QA gate
```

---

## Design patterns (add to DESIGN_REFERENCE — R26–R35)

| ID | Pattern |
|----|---------|
| **R26** | Live Proof Hero — evaluate embed, not screenshot |
| **R27** | Trial OS stepper — sandbox quota + env toggle |
| **R28** | Command Center shell — rail + context bar + ⌘K |
| **R29** | Receipt Studio — split inspector + receipt + export dock |
| **R30** | Decision Timeline — RID-threaded nodes |
| **R31** | Agent Command Deck — columns + human gate |
| **R32** | Usage meter chip — 50 eval / 14d always visible in product |
| **R33** | Proof mode — light default, dark artifact for demos |
| **R34** | Four-act homepage — Try · Prove · Package · Trust |
| **R35** | Visual QA gate — Playwright baselines in CI |

---

## WISE prompt IDs (Tier-1 UI lane)

| ID | Title | Wave |
|----|-------|------|
| UI-01 | Live Proof Hero embed | A |
| UI-02 | Trial OS wizard | A |
| UI-03 | Homepage four-act compression | A |
| UI-04 | Command Center Shell 2.0 | B |
| UI-05 | Receipt Studio split view | B |
| UI-06 | Decision Timeline | B |
| UI-07 | Design Language package + Ladle | C |
| UI-08 | Agent Command Deck | C |
| UI-09 | Motion + a11y + responsive matrix | C |
| UI-10 | Playwright visual QA gate | D |

**Pick:** extend `pick-wise.py --bottleneck ui` · preflight read this doc.

---

## Anti-patterns (instant disqualification from tier-1)

- Fake logo walls, ARR, “trusted by 500+ banks”
- Fourth homepage SKU card (`nf-offer-card`)
- Dark-mode SaaS pivot (stay light institutional R2)
- Agent UI implying unsupervised production Copilot
- Static receipt pretending to be live without offline label
- Shipping UI without updating visual baselines

---

## Verify stack (when waves land)

```bash
make verify-ui-e2e          # commercial strings + flows
make verify-ui-visual       # layout baselines (UI-10)
make verify-static-www      # v16+ needles
make verify-gtm             # full bundle
```

**Related:** [DESIGN_REFERENCE_GOALS_LOCKED_v1.md](./DESIGN_REFERENCE_GOALS_LOCKED_v1.md) · [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](./WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) · [BANK_GRADE_CHECKLIST.md](./BANK_GRADE_CHECKLIST.md)
