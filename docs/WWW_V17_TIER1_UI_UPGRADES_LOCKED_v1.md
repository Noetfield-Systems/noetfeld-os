# WWW v17 — Top tier-1 UI upgrades (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | **Superseded** by [WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md](./WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md) |
| **Updated** | 2026-06-13 |
| **Benchmark class** | Sumsub · Stripe · Vercel · Linear · institutional GRC consoles |
| **Parent** | [DESIGN_REFERENCE_GOALS_LOCKED_v1.md](./DESIGN_REFERENCE_GOALS_LOCKED_v1.md) · [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](./WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) |
| **Not for** | Backend rewrites, fourth SKU, fake logos, vendor comparison pages |

---

## Executive diagnosis (from repo search)

| Area | Today | Tier-1 gap |
|------|-------|------------|
| **Design system** | Split stack: `noetfield-tokens.css` (dark defaults) + `v14-light` + `v15-ref` + `v16-packaging` on www; Tailwind duplicate in `governance-console/frontend` | No single token source · no shared React/HTML component SSOT |
| **Homepage** | Hero + stat bar + 2 rails + CISO strip + §01–§10 + packaging + agentic + mega CTA (~15 sections) | Conversion sites compress to **one story arc**; proof is interactive, not scroll marathon |
| **Product console** | Functional CRUD: forms, cards, lists (`Shell`, `EvaluateForm`, workspace table) | Tier-1 governance UIs feel like **command centers** — timeline, graph, agent rail, density modes |
| **Proof artifacts** | Static `ReceiptMock` / `nf-artifact-panel` — same YAML everywhere | Live data-bound receipt that updates as user evaluates (www + product parity) |
| **Self-serve** | `/start/` form → localStorage → banner on dashboard | Sumsub-class **onboarding wizard** with stepper, env toggle, API key drawer, usage meter |
| **Motion / a11y** | WWW v13 steps 81–90 largely open; `prefers-reduced-motion` partial | Micro-interactions, CLS-safe hero, AA contrast audit, keyboard paths |
| **Quality gates** | `verify-ui-e2e.sh` = curl + grep strings | No visual regression · no Lighthouse budgets · no responsive matrix in CI |
| **Agentic story** | Marketing strip on www | **In-product** agent workflow UI with human-gate affordances |

**W3 UI north star:** A CISO completes **sign up → evaluate → live receipt → export sample** in under 5 minutes **without scrolling a 10-section homepage**.

---

## The 10 next big UI upgrades

### U1 — Unified Design System v17 (single token + component SSOT)

**Why tier-1:** World-class products have one design language from marketing site through app. Today www and console diverge (`noetfield-tokens.css` dark vs Tailwind light in `tailwind.config.ts`).

**Ship:**
- Extract `@noetfield/ui-tokens` (CSS variables + JSON for Tailwind) — one source for gold `#8a6b1f`, serif/sans, radius, shadows, status colors.
- Shared primitives: `Button`, `Badge`, `ReceiptPanel`, `StatBar`, `SectionHead`, `PackCard` — implemented once in React, mirrored in `rebuild-www-v6.py` HTML partials or MDX.
- Deprecate orphan imports (`noetfield-components.css`, dark `:root` defaults on light pages).

**Files:** `assets/noetfield-tokens.css`, `governance-console/frontend/tailwind.config.ts`, new `packages/ui/` or `components/design-system/`.

**Done when:** Field names on `ReceiptMock` === www `tle-receipt.yaml` mock === PDF export labels; one token file referenced everywhere.

**Verify:** Storybook or Ladle page; `make verify-ui-e2e` unchanged.

---

### U2 — Interactive product-led hero (live evaluate, not static mock)

**Why tier-1:** Sumsub/Stripe heroes **are** the product — a sandbox evaluate inline, not a screenshot.

**Ship:**
- Homepage + `/start/` hero right panel: mini **Evaluate** widget (actor · action · context) → calls real `/evaluate` → animates `ReceiptMock` with returned RID + confidence.
- Fallback: static mock when API offline (honest banner).
- CTA chain: result RID link → full console.

**Files:** `index.html` via generator, new `assets/noetfield-live-demo.js`, `governance-console` API proxy (already on :13080).

**Done when:** First-time visitor gets a **real RID** from homepage without leaving hero viewport (desktop); mobile stacks with same flow.

**Verify:** New e2e — POST evaluate from homepage embed; RID appears in receipt panel.

---

### U3 — Governance Command Center shell (replace “admin app” chrome)

**Why tier-1:** Current `Shell.tsx` is a thin nav bar + page stack. Tier-1 consoles use **persistent context**: tenant, mode (sandbox/production), usage quota, RID thread, upgrade path.

**Ship:**
- App shell v2: left rail (Dashboard · Evaluate · Workspace · Audit · Connectors · Settings), top bar (tenant · sandbox badge · 14d/50-eval meter · Start free / Upgrade), **command palette** (`⌘K` → jump to RID/TLE/evaluate).
- Unified page template: hero slot + primary workspace + optional receipt side panel (same grid as cognitive dashboard).
- Dark artifact panel option for “proof mode” presentations (board demo view).

**Files:** `governance-console/frontend/components/Shell.tsx`, new `AppShell.tsx`, `CommandPalette.tsx`, `UsageMeter.tsx`.

**Done when:** Every product route uses shell v2; sandbox session visible on all pages; mobile collapses to bottom nav.

**Verify:** Playwright smoke — palette opens, navigate to workspace by TLE id.

---

### U4 — Sandbox onboarding wizard (Sumsub-class self-serve)

**Why tier-1:** `/start/` is a single form + redirect. Tier-1 trials use **guided steps** with progress and immediate value.

**Ship:**
- 4-step wizard UI: **Sign up** → **Connect mock M365** (one-click) → **First evaluate** → **Export sample TLE**.
- Progress bar + checkmarks; persist step in session; skip/resume.
- Environment pill: **Sandbox** (active) | Production (locked → `/copilot/pilot/`).
- API key drawer with copy + curl snippet (orientation key from session).

**Files:** new `app/onboarding/page.tsx` or enhance `/start/` with React island; `noetfield-sandbox.js` v2; `noetfield-v16-packaging.css` stepper styles.

**Done when:** `verify-ui-e2e` walks wizard steps; 50-eval counter decrements visually on evaluate.

**Verify:** E2E sandbox funnel S0→S2 in one scripted path.

---

### U5 — Homepage IA compression (4-act narrative, not §01–§16 scroll)

**Why tier-1:** Institutional ≠ infinite scroll. Top GTM sites: **Try · Prove · Package · Trust** above the fold; depth below fold or on subpages.

**Ship:**
- Collapse homepage to **4 acts** (keep e2e needles as subsections or linked hubs):
  1. **Try** — hero + live evaluate + Start free sandbox
  2. **Prove** — receipt + 5-min demo + TLE samples (proof grid)
  3. **Package** — tier grid (move full §06–§07 depth to `/pricing/`)
  4. **Trust** — CISO strip + procurement rail + mega CTA
- Move extended FAQ, category map, stack ladder to `/copilot/` hub (already partially there).
- Sticky sub-nav on long pages only (pricing, trust).

**Files:** `scripts/rebuild-www-v6.py` `homepage()`, `homepage_extended_sections()` — refactor IA, not just copy.

**Done when:** Homepage `<main>` section count ≤ 8; LCP element is hero H1 + receipt; median scroll depth to CTA ↓ in analytics (when wired).

**Verify:** Update `verify-ui-e2e` section needles; keep commercial strings grep-green.

---

### U6 — TLE Workspace premium (split-pane receipt + approval stepper)

**Why tier-1:** `workspace/[tle_id]/page.tsx` is card stacks. Tier-1 audit products use **split view**: structured record left, human-readable receipt + export actions right.

**Ship:**
- Split layout: YAML/JSON inspector (read-only) | `ReceiptMock` live-bound to TLE document.
- **Approval chain stepper** — vertical timeline with signed/pending states, not flat list.
- Export dock: Board PDF · Procurement ZIP · Verify integrity — sticky on scroll.
- Evidence index as chips (Purview · Entra · audit) linking to connector status.

**Files:** `workspace/[tle_id]/page.tsx`, new `ApprovalStepper.tsx`, `ExportDock.tsx`, `YamlInspector.tsx`.

**Done when:** Board demo can run entirely from TLE detail without jumping pages; matches www receipt field order (R20).

**Verify:** Existing tle detail PDF/ZIP e2e + visual snapshot of stepper states.

---

### U7 — In-product agentic workflow UI (not marketing-only)

**Why tier-1:** v16 agentic strip is www copy only. Tier-1 “autonomous” products show **agent runs** in the UI with human gates.

**Ship:**
- **Agent activity rail** on dashboard: Investigate → Triage → Draft TLE → Awaiting approver → Recorded.
- Cards show status, confidence, linked RID/TLE; high-risk steps show **Approve / Reject** (RBAC-aware).
- Sandbox: simulated agent steps with sample timings; production: wire to `agent-manifest` / workflow service when ready — UI ships first with honest “sandbox simulation” label.

**Files:** `cognitive-dashboard/page.tsx`, new `AgentWorkflowRail.tsx`, `docs/WWW_V16` agentic section linked from UI.

**Done when:** Dashboard shows 4-step rail; at least one step clickable → evaluate or TLE draft; no overclaim on production autonomy.

**Verify:** E2e grep “Investigate” on dashboard client chunk; a11y on approve buttons.

---

### U8 — Motion system + institutional micro-interactions

**Why tier-1:** Static pages feel dated. Tier-1 uses **restrained motion**: receipt verify pulse, step transitions, card lift — all `prefers-reduced-motion` safe.

**Ship:**
- Motion tokens in v17: `--motion-fast`, `--motion-enter`, easing curves.
- Receipt **sign** animation on evaluate success (export_integrity line highlights).
- Sandbox wizard step transitions; pack card hover (already partial — unify).
- Hero receipt panel: subtle entrance, zero CLS (v13 step 89).

**Files:** `noetfield-v17-motion.css`, `ReceiptMock.tsx` CSS transitions, www generator class hooks.

**Done when:** WWW v13 steps 81, 89 marked done; Lighthouse CLS ≤ 0.1 on homepage.

**Verify:** `prefers-reduced-motion: reduce` disables animations (unit test or Playwright emulation).

---

### U9 — Mobile-first responsive + touch-grade polish

**Why tier-1:** `BANK_GRADE_CHECKLIST.md` P0 responsive check is **unchecked**. Tier-1 means flawless 320px → 1440px.

**Ship:**
- Breakpoint audit: nav burger, hero stack, pack grid, sandbox form, workspace tables → horizontal scroll or card collapse.
- Touch targets ≥ 44px; sticky CTAs on mobile (`Start free sandbox`).
- Table alternatives on mobile (RACI, pricing, AIA → accordion cards).

**Files:** `noetfield-v14-light.css`, `noetfield-shell.css`, product Tailwind responsive classes, all `nf-table` usages in generator.

**Done when:** Founder device lab sign-off; Playwright viewports 320/768/1280 screenshot baselines.

**Verify:** New `scripts/verify-responsive-screenshots.sh` or Playwright project in `governance-console/`.

---

### U10 — Visual quality gates in CI (world-class release bar)

**Why tier-1:** String-grep e2e catches regressions, not **ugly** or **broken layout**. Tier-1 teams ship with visual + performance budgets.

**Ship:**
- Playwright suite: homepage, `/start/`, `/pricing/`, evaluate→result, TLE detail export dock.
- Lighthouse CI budgets: LCP, CLS, a11y score ≥ 95 on P0 URLs.
- Optional: Percy/Chromatic baselines for receipt panel + shell (fork-safe).
- `make verify-ui-visual` wired into `verify-gtm` after `verify-ui-e2e`.

**Files:** `governance-console/playwright.config.ts`, `.github/workflows/ui-visual.yml`, `scripts/verify-ui-visual.sh`.

**Done when:** CI fails on unintended receipt layout shift or missing primary CTA; documented in `BANK_GRADE_CHECKLIST.md`.

**Verify:** Intentional UI change requires baseline update — same discipline as e2e needles.

---

## Recommended build order (UI impact × effort)

| Priority | ID | Effort | W3 impact |
|----------|-----|--------|-----------|
| 1 | **U2** Interactive hero | M | Sandbox starts without scroll |
| 2 | **U4** Onboarding wizard | M | Sumsub parity |
| 3 | **U3** Command Center shell | L | Product feels “real” |
| 4 | **U6** TLE split-pane workspace | M | Board demo quality |
| 5 | **U5** Homepage compression | S | Conversion clarity |
| 6 | **U1** Design system v17 | L | Long-term velocity |
| 7 | **U7** Agentic workflow rail | M | Differentiation |
| 8 | **U8** Motion system | S | Polish |
| 9 | **U9** Responsive pass | M | Mobile buyers |
| 10 | **U10** Visual CI gates | M | Stay tier-1 |

---

## Agent picker integration

Add to WISE catalog as **Tier 1 UI lane** (`ui-tier1`):

| Prompt ID | Title |
|-----------|-------|
| U-01 | Design tokens v17 single SSOT |
| U-02 | Live evaluate hero embed |
| U-03 | App shell v2 command center |
| U-04 | Sandbox onboarding wizard |
| U-05 | Homepage 4-act compression |
| U-06 | TLE split-pane + approval stepper |
| U-07 | Agent workflow rail (dashboard) |
| U-08 | Motion tokens + receipt animation |
| U-09 | Responsive 320–1280 audit |
| U-10 | Playwright visual regression gate |

**Pick:** `make pick-wise` with bottleneck `sandbox` or new `--bottleneck ui`.

---

## Explicit anti-patterns (stay tier-1 honest)

- Fake customer logo walls, ARR counters, or “500+ enterprises”
- Fourth `nf-offer-card` on homepage
- Dark SaaS rebrand — stay **light institutional** (R2)
- Agentic UI that implies unsupervised production Copilot rollout
- Chasing pixel-perfect copies of reference sites — **patterns only**

---

## Related

- [WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md](./WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md) — Phases VII–IX (steps 61–90) feed U6–U9
- [BANK_GRADE_CHECKLIST.md](./BANK_GRADE_CHECKLIST.md) — Pillar 1 experience
- [docs/BANK_GRADE_CHECKLIST.md](./BANK_GRADE_CHECKLIST.md) — responsive checkbox → U9
