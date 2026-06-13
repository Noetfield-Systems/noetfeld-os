# WWW v12 Master Plan — Combined Redesign & Refactor (LOCKED v1)

> **Superseded for execution by** [WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md](./WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md) — keep for historical lane mapping only.

| Field | Value |
|-------|--------|
| **Status** | LOCKED planning SSOT — execution roadmap for public www + lanes |
| **Scope** | Positioning, Copilot complement, MSP two-tier, institutional UI, federal credibility, TLE differentiation |
| **Not for** | Vendor names, comparisons, comparison hub routes, oversharing internal systems |
| **Policy** | Buyer-facing copy only — patterns (receipt-first, trust center, Phase 1/2 MSP), never third-party company names |
| **Parent** | [DESIGN_REFERENCE_GOALS_LOCKED_v1.md](./DESIGN_REFERENCE_GOALS_LOCKED_v1.md) · [GTM_COPYBOOK.md](./GTM_COPYBOOK.md) |
| **Generator** | `scripts/rebuild-www-v6.py` → v12 bump · `scripts/migrate-all-public-www.py` |
| **Target shell** | `body.nf-www nf-site-v5` · `noetfield-www.css?v=12` |

---

## Executive summary

Noetfield is **not** rebuilding a full AI governance platform. The www program combines six reference lanes into one wedge:

> **Phase 1: Microsoft and partners deliver Copilot readiness. Phase 2: Noetfield records operational go/no-go decisions — evaluate → Trust Ledger Entry → board PDF / procurement ZIP — metadata-only M365, fail-closed on tamper.**

Ten execution steps below map each lane to repo deliverables, in dependency order.

---

## How to use this list (quick index)

| If you want… | Buyer pattern | Plan step |
|--------------|---------------|-----------|
| Positioning / copy | Numbered narrative · receipt-first export | **Step 1–2** |
| Copilot complement | Microsoft CCS + Purview Learn · Phase 2 attach | **Step 5** |
| MSP two-tier model | Partner Phase 1 configure · Noetfield Phase 2 receipt | **Step 6** |
| www / institutional UI | Trust center · honest scope · procurement ZIP | **Step 2–3, 8** |
| Federal lane credibility | Canada.ca AIA · TBS ADM · NIST AI RMF | **Step 7** |
| TLE differentiation | Signed TLE · fail-closed export · verify walkthrough | **Step 4** |

---

# Part A — Six lanes, one by one

---

## Lane 1 — Positioning / copy

**Buyer patterns:** Numbered narrative · receipt-first hero · honest scope badges · export-in-minutes proof

### What each pattern teaches

| Pattern | Copy shape | Borrow | Do not copy |
|---------|------------|--------|-------------|
| **Enterprise GRC narrative** | Pain → platform → proof; framework marquee | Numbered sections 01–10; outcome language without leader claims | Logo walls, full-estate scope, analyst stats |
| **Three-verb governance** | Identify · Protect · Enforce (industry) | Adapt to **Evaluate · Record · Export**; quantified gap (sourced) | Shadow-AI discovery breadth, enforce-at-scale claims |
| **Receipt-first www** | Pain moment → category orientation → CLI verify | Receipt hero; IN PROGRESS / MAPPED trust signals | Crypto/court claims until shipped |
| **Audit export SaaS** | Evidence before the question; PDF+JSON fast | Export-in-minutes; regulator-ready pack | Region-specific cert claims unless lane opens |

### Noetfield locked copy

| Element | Text |
|---------|------|
| **Wedge (one sentence)** | Noetfield is the governance execution layer for M365 Copilot: invalid changes blocked, allowed decisions receipted, export bundles fail closed on tamper. |
| **Three verbs** | Evaluate · Record · Export (not Identify · Protect · Enforce) |
| **Complement line** | Complement Purview and the Copilot Control System — not replace. Metadata-only M365. |
| **Primary CTA** | Request Governance Brief → `/trust-brief/intake/` |
| **Secondary CTA** | 5-minute demo · Become a design partner |

### New homepage sections (from Lane 1)

| Section | Title | Source pattern |
|---------|-------|----------------|
| **07** | The moment Copilot becomes auditable | Pain moment pattern |
| **08** | Where Noetfield sits (category orientation) | Zone labels only — **no vendor names on public www** |
| **10** | What buyers ask | FAQ block — 5–6 questions |

---

## Lane 2 — Copilot complement story

**Microsoft docs:** [Copilot Control System (Learn)](https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-control-system/overview) · [Purview / M365 compliance Learn](https://learn.microsoft.com/en-us/purview/)

### Stack map (complement, not compete)

```
┌─────────────────────────────────────────────────────────────┐
│ Microsoft Copilot Control System (CCS)                       │
│  Pillar 1: Security & governance (Purview, Entra, audit)   │
│  Pillar 2: Management (licensing, agent lifecycle)         │
│  Pillar 3: Measurement (Copilot Analytics, adoption, ROI)   │
└──────────────────────────┬──────────────────────────────────┘
                           │ baselines + labels + DLP
┌──────────────────────────▼──────────────────────────────────┐
│ Partner Phase 1 (MSP + Microsoft stack)                      │
│  Tenant readiness · policy standardization · Copilot enable  │
└──────────────────────────┬──────────────────────────────────┘
                           │ operational go/no-go
┌──────────────────────────▼──────────────────────────────────┐
│ Noetfield Phase 2                                            │
│  Evaluate → TLE v1 → board PDF · procurement ZIP             │
│  evidence_index: purview · entra · audit                     │
└─────────────────────────────────────────────────────────────┘
```

### Copy locks (Lane 2)

- **Say:** “We produce the signed governance record when your team decides Copilot may execute in production.”
- **Say:** “M365 metadata evidence index on every TLE.”
- **Never say:** Replace Purview, replace CCS, replace Agent 365, Microsoft partnership implied.

### Deliverables

- `/copilot/` hero + diagram block
- External links: CCS Learn overview (footer “Stack context”)
- Demo script mentions Purview + Entra + audit index

---

## Lane 3 — MSP two-tier model

**Buyer pattern:** Partner Phase 1 configure · Noetfield Phase 2 receipt

### Two-tier RACI (locked — see `docs/msp/MSP_GOVERNANCE_PACK_v1.md`)

| Tier | Owner | Work | Buyer-visible outcome |
|------|-------|------|------------------------|
| **Phase 1** | MSP + Microsoft stack | Readiness assessment · Purview · labels · DLP · CA · Copilot enable | CAF/readiness score · secure tenant |
| **Phase 2** | Noetfield | Evaluate intent · TLE v1 · board PDF · procurement ZIP | Governance decision receipt per tenant |

### Phase 1 → Noetfield attach (generic)

| Phase 1 work (examples) | What MSP delivers | Noetfield attach |
|---------------------------|-------------------|------------------|
| Multi-tenant policy baseline | Standardized tenant posture | TLE after baselines |
| Readiness assessment report | Executive readiness summary | Trust Brief / CSV → TLE |
| Workspace governance prep | Copilot-ready workspaces | Governance Monitor MRR (roadmap) |
| Secure score / GDAP baseline | Readiness signal | Evaluate API trigger |

### MSP www blocks

1. Phase 1 → Phase 2 diagram (generic icons — no vendor names)
2. W3-MSP PASS: LOI + 1 live tenant
3. Link: `READINESS_TO_RECORD_MAPPING_v1.md`
4. Partner CTA: `/trust-brief/intake/?interest=msp`

---

## Lane 4 — www / institutional UI

**Buyer patterns:** Trust center · procurement ZIP · receipt-first hero · honest scope table

### UI pattern library → Noetfield components

| Pattern | Buyer shape | Noetfield component | Status |
|---------|-------------|---------------------|--------|
| Receipt-first hero | Receipt mock beside headline | `nf-hero-cinematic` + `nf-receipt-mock` | Shipped |
| Product-in-hero | Workspace screenshot beside receipt | Workspace screenshot beside receipt | **v12** |
| Trust Center | Honest cert / scope table | `/trust/` hub | **v12** |
| Stats bar | Fixed commercial facts | `nf-stat-bar` (4 · $10k · 90d · 3 SKUs) | Shipped |
| Numbered narrative | 01–10 section blocks | `nf-section-block` + `nf-section-num` 01–10 | Extend to 10 |
| Honest scope badges | SHIPPED / ORIENTATION / ROADMAP | `nf-signal-badge--shipped/orientation/roadmap/na` | Shipped |
| Mega CTA | Single conversion spine | `nf-cta-mega` | Shipped |
| Single markup dialect | — | Kill `nf-section__`, `nf-sku`, `nf-card` on hubs | **v12 refactor** |

### Visual rules (unchanged)

- Dark `#07070b` + gold accent on GTM (R2)
- Optional lighter sub-theme on `/trust/` only (procurement readers)
- No purple MSP-SaaS gradients on institutional pages

---

## Lane 5 — Federal lane credibility

**References:** [Canada.ca AIA](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/algorithmic-impact-assessment.html) · [TBS Directive on ADM](https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592) · [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

### Policy anchor table

| Instrument | Buyer fear | Noetfield artifact | Doc |
|------------|------------|-------------------|-----|
| **ADM** | Legacy ADS by **2026-06-24** | Trust Brief + TLE refresh export | `FEDERAL_GOVERNANCE_PACK_v1.md` |
| **AIA** | Questionnaire + open-data publication | TLE ↔ AIA field crosswalk | `AIA_TLE_MAPPING_v1.md` |
| **Copilot PIN** | Unclassified M365 constraints | PIN checklist scope badges | `GC_COPILOT_PIN_CHECKLIST_v1.md` |
| **GC AI Register** | Inventory without governance depth | TLE as supplementary evidence | Federal pack §2 |
| **NIST AI RMF** | Procurement / US alignment | Procurement ZIP citations | `/copilot/procurement/` |

### Federal www checklist

- [x] Official canada.ca / tbs-sct links above fold
- [x] “Not a federal certifier” callout prominent
- [x] “Unclassified information only” hero badge
- [x] AIA ↔ TLE preview table (5 rows HTML — not full doc dump)
- [x] ADM deadline countdown or date chip
- [x] CTA: `/trust-brief/intake/?interest=federal`

---

## Lane 6 — TLE differentiation

**Buyer pattern:** Signed TLE · fail-closed export · verify walkthrough · M365 metadata index

### Capability honesty matrix

| Capability | Shipped | Orientation | Out of scope |
|------------|---------|-------------|--------------|
| TLE v1 + workspace UI | ✓ | | |
| `confidence_score` on decision | ✓ | | |
| `export_integrity` fail-closed | ✓ | | |
| M365 evidence index (purview · entra · audit) | ✓ | | |
| Board PDF + procurement ZIP | ✓ | | |
| YAML / JSON export manifest | ✓ | | |
| HTTP-style decision codes (201/202/403) | | Document in API | |
| Offline verify walkthrough page | ✓ | `/trust-ledger/verify/` | |
| Ed25519 / Merkle / transparency log | | Roadmap | |
| Court / Daubert / full agent proxy | | | Full agent-runtime scope |

### Differentiation one-liners (category zones — not vendors)

| Category zone | Typical optimize-for | Noetfield optimizes for |
|---------------|----------------------|-------------------------|
| Crypto evidence platforms | Any-model signed decisions, CLI verify | **Copilot operational decisions** + M365 metadata index |
| Agent runtime governance | Every agent tool call, hash chain | **Governance evaluate** before Copilot execution scope |
| Audit trail SaaS | Integration event capture | **TLE + board PDF** from evaluate path |
| Estate GRC platforms | Registry + policy packs | **Receipt export** after readiness |

---

## Master category map (all lanes — investor / internal)

```
                    BREADTH (estate · compliance · tenants)
                              ↑
    Compliance automation    │        AI estate GRC platforms
    (company SOC posture)    │        (registry · policy · enforce)
                              │
    Vertical MRM tools       │        Decision evidence · agent audit
                              │
    MSP Phase 1 + Microsoft  │                    ★ NOETFIELD
    CCS / Purview stack      │              (Copilot execute + TLE)
                              │
                              └──────────────────────────→
                                    DEPTH (M365 / Copilot)
```

Public www uses **zone labels only** (no third-party company names). Category orientation on `/investors/` with honest scope disclaimer.

---

# Part B — Ten-step combined program

Execute in order; steps 6 and 7 can parallel after step 3.

---

## Step 1 — Lock narrative SSOT (Lane 1)

**Goal:** One story across www, docs, investors.

**Actions:**
1. Update `docs/GTM_COPYBOOK.md` — wedge sentence, three verbs, forbidden claims.
2. Extend `DESIGN_REFERENCE_GOALS_LOCKED_v1.md` with **R11–R14**:
   - R11: Category orientation strip (public, no vendor names)
   - R12: Pain moment section (§07)
   - R13: Trust hub link in nav/footer
   - R14: CCS complement diagram on Copilot hub
3. Add honest claim matrix to `PRODUCT_TRUTH.md` or commercial SSOT cross-link.

**Files:** `docs/GTM_COPYBOOK.md`, `docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md`

**Done when:** Generator hero strings pull from copybook table; no conflicting one-liners on P0 pages.

---

## Step 2 — Homepage extension 01 → 10 (Lane 1 + 4)

**Goal:** Numbered homepage scroll depth without SKU creep.

**New sections in `rebuild-www-v6.py` homepage template:**

| # | ID | Heading |
|---|-----|---------|
| 07 | `s07` | The moment Copilot becomes auditable |
| 08 | `s08` | What you get — execution receipts for Copilot decisions |
| 09 | `s09` | Microsoft stack complement (CCS + Purview + Phase 2) |
| 10 | `s10` | What buyers ask (FAQ) |

**Files:** `scripts/rebuild-www-v6.py`, `index.html`, `assets/noetfield-enterprise.css`

**Done when:** E2E finds §07–§10 headings + existing CTAs.

---

## Step 3 — Trust Center `/trust/` (Lane 4)

**Goal:** Trust center procurement surface without fake certs.

**Page sections:**
1. Metadata-only M365 processing
2. Export integrity (fail-closed)
3. Retention defaults
4. Subprocessors list (honest)
5. Cert / framework table: Shipped · Orientation · Roadmap · N/A
6. Link: demo · TLE samples · procurement ZIP · status

**Files:** new `trust/index.html`, `assets/partials/header.html`, `footer.html`, generator registry

**Done when:** `/copilot/procurement/` links to `/trust/`.

---

## Step 4 — TLE differentiation hardening (Lane 6)

**Goal:** Provable export path in &lt;5 minutes.

**Actions:**
1. Spec export manifest JSON (sidecar to board PDF).
2. Static `/trust-ledger/verify/` — tamper fail walkthrough.
3. API docs: decision semantics + optional 201/202/403 mapping.
4. TLE samples: go · conditional · rejected · **tampered export fails**.

**Files:** `docs/api/`, `trust-ledger/`, `trust-ledger/sample-report/`, `trust-ledger/verify/index.html`

**Done when:** Demo script: evaluate → TLE → export → verify fail on tamper.

---

## Step 5 — Copilot hub = CCS complement (Lane 2)

**Goal:** IT buyer understands complement in 10 seconds.

**Actions:**
1. Rewrite `/copilot/` hero with three-pillar CCS map + Noetfield overlay.
2. Update `/copilot/demo/` script copy (Purview · Entra · audit).
3. Footer “Stack context” external links (Learn.microsoft.com — no endorsement).

**Files:** `copilot/index.html`, `copilot/demo/index.html`, `docs/copilot/`, generator

**Done when:** Zero “replace Purview” language in copilot subtree.

---

## Step 6 — MSP two-tier redesign (Lane 3)

**Goal:** Phase 1 partner stack → Phase 2 Noetfield receipts.

**Actions:**
1. `/msp/` visual diagram Phase 1 → Phase 2.
2. Surface W3-MSP PASS + partner LOI.
3. Readiness CSV handoff callout → `READINESS_TO_RECORD_MAPPING_v1.md`.
4. Confirm no vendor comparison pages in repo.

**Files:** `msp/index.html`, `docs/msp/*`, generator

**Done when:** MSP hero says “Readiness → Record · Phase 2 TLE attach.”

---

## Step 7 — Federal lane upgrade (Lane 5)

**Goal:** Canada.ca-grade credibility.

**Actions:**
1. ADM **2026-06-24** date chip + official links bar.
2. AIA ↔ TLE preview table (5 rows).
3. Copilot PIN checklist as scope badges.
4. GC AI Register gap paragraph + link.

**Files:** `federal/index.html`, `docs/federal/*`, generator

**Done when:** Federal page links to canada.ca AIA + TBS ADM above fold.

---

## Step 8 — UI system refactor (Lane 4)

**Goal:** One markup dialect; product-in-hero.

**Actions:**
1. Bump `SHELL_VERSION` / `?v=12`.
2. Add workspace screenshot or loop beside receipt mock.
3. Migrate all hubs to `nf-section-block`, `nf-offerings-v5`, `nf-proof-grid`.
4. Remove compat CSS for `nf-section__`, `nf-sku`, legacy cards.
5. Run `migrate-all-public-www.py` on remaining shell pages.

**Files:** `assets/noetfield-www.css`, `noetfield-enterprise.css`, `noetfield-shell.js`, `rebuild-www-v6.py`, `migrate-all-public-www.py`

**Done when:** `rg 'nf-section__' index.html enterprise/ copilot/ msp/ federal/` → 0.

---

## Step 9 — Investor alignment (all lanes)

**Goal:** VC diligence without public compare page.

**Actions:**
1. Expand `/investors/` category map to 8 zones (see Master map above).
2. Design partner scarcity line (“Accepting N design partners”).
3. Link investor page from footer only (not primary nav).
4. Keep honesty callout (no fake ARR, certs, logos).

**Files:** `investors/index.html`, `gate/investors/index.html`

**Done when:** Investor page answers “feature vs company” and capital use.

---

## Step 10 — Verify, regenerate, ship (ops)

**Goal:** Repeatable www factory.

**Actions:**
1. `python3 scripts/rebuild-www-v6.py`
2. `python3 scripts/migrate-all-public-www.py`
3. Extend `scripts/verify-ui-e2e.sh`: homepage §07–10, `/trust/`, federal ADM, msp Phase diagram, copilot CCS copy.
4. Update `docs/DESIGN_SYSTEM.md` component list for v12.
5. Preview: `python3 -m http.server 13081` → `/?v=12`

**Done when:** E2E green; branch ready for review.

---

# Part C — Execution timeline

| Week | Steps | Primary lanes |
|------|-------|---------------|
| 1 | 1, 8 (base) | Copy SSOT + UI unify |
| 2 | 2, 3, 5 | Homepage + Trust + Copilot |
| 3 | 4, 6, 7 | TLE proof + MSP + Federal |
| 4 | 9, 10 | Investor + verify + ship |

Steps 6 ∥ 7 after step 3. Step 4 can start after step 5.

---

# Part D — Brainstorming guardrails

1. **No public comparison hubs** — category zones only; no third-party company names on www.
2. **Three SKUs locked** — Trust Brief · Copilot Pack · Bank Pilot. Federal/MSP are lanes.
3. **Microsoft complement is factual** — cite CCS/Purview Learn; never imply partnership.
4. **Honest scope &gt; cert theater** — trust center *structure*, not fake SOC2 claims.
5. **TLE moat = M365 depth + fail-closed export** — not Merkle/Daubert until shipped.
6. **MSP = Phase 2 attach** — complement Phase 1 partners; never name vendors in copy.
7. **Generator is source of truth** — hand-edit HTML only via `rebuild-www-v6.py` templates.

---

# Part E — Success metrics (www v12)

| Metric | Target |
|--------|--------|
| Homepage sections | 10 numbered blocks + mega CTA |
| GTM hubs on unified CSS classes | 100% |
| Trust hub live | `/trust/` with honest cert table |
| TLE verify path | Static walkthrough + tamper fail demo |
| Federal official links | AIA + ADM above fold |
| MSP Phase diagram | Visible on `/msp/` hero area |
| Copilot CCS complement | Diagram on `/copilot/` |
| E2E script coverage | All above routes |
| Vendor comparison pages | 0 |

---

## Related docs

| Doc | Role |
|-----|------|
| [DESIGN_REFERENCE_GOALS_LOCKED_v1.md](./DESIGN_REFERENCE_GOALS_LOCKED_v1.md) | Visual patterns R1–R10 (+ R11–R14 after Step 1) |
| [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) | Component reference |
| [MSP_GOVERNANCE_PACK_v1.md](./msp/MSP_GOVERNANCE_PACK_v1.md) | Two-tier RACI |
| [FEDERAL_GOVERNANCE_PACK_v1.md](./federal/FEDERAL_GOVERNANCE_PACK_v1.md) | GC policy anchors |
| [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](./strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md) | SKUs + pricing |

---

**Status:** Steps 1–10 implemented (www **v12**). Regenerate: `python3 scripts/rebuild-www-v6.py` · Preview: `http://127.0.0.1:13081/?v=12`
