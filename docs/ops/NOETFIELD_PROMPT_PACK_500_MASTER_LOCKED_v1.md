# Noetfield Prompt Pack — 500 Master Catalog (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED — canonical consolidation of 1000 NF-PLAN grid |
| **Machine SSOT** | [catalog-500.json](./plans/catalog-500.json) |
| **Active picker** | [catalog-500.json](./plans/catalog-500.json) · **`make pick-wise`** ([V14 WISE](./NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md)) |
| **North star** | Board PDF in governance meeting OR deposit ≥ CAD 2K / signed LOI |
| **Generated** | 2026-06-13T08:32:34Z |

---

## 1. Executive grade (whole pack)

| Pack source | Raw count | Grade | After consolidation |
|-------------|-----------|-------|---------------------|
| NF-PLAN registry grid | 1000 | **C+** | → 300 archived (Tier 3 index) |
| Tier 1 SMART (W3 active) | 50 | **A** | Pick now |
| Tier 2 product backlog | 138 | **B+** | After first pilot SOW |
| Tier 0 constitution | 12 | **A** | Every cold-start session |
| Legacy Prompt OS | ~12 docs | **D** | Frozen |
| Worker Blueprint V3 | 1 | **A+** | Paste before any agent work |
| **Catalog total** | **500** | **B+ → A path** | |

**Root diagnosis:** The 1000 grid is 20×10×5 Cartesian coverage — **~85% duplicate intent**. v13 SMART + this catalog dedupes to **500 named entries** with grades, success lanes, and pick rules.

**One filter:** Does this move us toward **board PDF in a real meeting** or **W3 deposit/LOI** in 90 days? If no → Tier 3.

---

## 2. Tier architecture (500)

| Tier | Count | Pick? | Gate |
|------|-------|-------|------|
| **T0** Constitution | 12 | Manual | Always read C-02 Worker V3 |
| **T1** W3 SMART | 50 | **Yes — max 3/session** | None |
| **T2** Product backlog | 138 | After W3 signal | First pilot SOW or deposit |
| **T3** Archive index | 300 | **Never** | Superseded by T1/T2 id |

---

## 3. Pattern grades (all 20 NF-PLAN patterns)

| Pattern | Grade | Tier | Success lane | Action |
|---------|-------|------|--------------|--------|
| **Self-serve sandbox** | **A+** | 1 | Product-led try · no sales call | **Active T1 — S-01** |
| `demo-rehearsal` | **A** | 1 | Receipt-first export | **Active T1** |
| `www-copy` | **A** | 1 | Receipt-first export | **Active T1** |
| `diligence-doc` | **A** | 1 | Trust center diligence | **Active T1** |
| `buyer-debrief` | **A** | 1 | Fixed-fee readiness SKU | **Active T1** |
| `customer-outreach` | **A** | 1 | Fixed-fee readiness SKU | **Active T1** |
| `smoke-script` | **B** | 2 | Trust center diligence | T2 backlog |
| `audit-export` | **B** | 2 | Receipt-first export | T2 backlog |
| `openapi-sync` | **B** | 2 | Microsoft CCS + Purview | T2 backlog |
| `integration-test` | **B** | 2 | Receipt-first export | T2 backlog |
| `console-ui` | **B** | 2 | Microsoft CCS + Purview | T2 backlog |
| `schema-validate` | **B** | 2 | Trust center diligence | T2 backlog |
| `examples-pack` | **B** | 2 | Receipt-first export | T2 backlog |
| `scope-gate-drill` | **B** | 2 | Trust center diligence | T2 backlog |
| `runbook` | **C** | 2 | Trust center diligence | Archive/freeze |
| `api-endpoint` | **C** | 2 | Microsoft CCS + Purview | Archive/freeze |
| `registry-reconcile` | **C** | 3 | Trust center diligence | Archive/freeze |
| `tier-gate-check` | **C** | 3 | Trust center diligence | Archive/freeze |
| `drift-impl` | **D** | 3 | Anti-pattern: full GRC platform breadth | Archive/freeze |
| `verdict-review` | **D** | 3 | Anti-pattern: full GRC platform breadth | Archive/freeze |
| `performance` | **D** | 3 | Anti-pattern: full GRC platform breadth | Archive/freeze |

---

## 4. Success model lanes (copy weight)

| Lane | Weight | Copy into prompts |
|------|--------|---------------------|
| **Product-led sandbox** | +12 | Self-serve · 14d · 50 evaluates · /start/ → console |
| **Receipt-first export** | +10 | Receipt-first · export in minutes · fail-closed tamper |
| **Trust center diligence** | +10 | Trust center · procurement ZIP · honest cert table |
| **Microsoft CCS + Purview** | +9 | Complement stack · Phase 1 readiness → Phase 2 TLE receipts |
| **MSP two-tier RACI** | +9 | Two-tier RACI · Readiness → Record · Phase 2 attach |
| **Numbered buyer narrative** | +6 | Numbered narrative · framework marquee · no leader claims |
| **Fixed-fee readiness SKU** | +6 | Copilot Readiness Assessment · fixed fee · reduced scope |
| **Platform breadth** | **−10** | Anti-pattern — never prompt full GRC estate |

---

## 5. W3 critical path (pick order)

```
S-01 sandbox → C-02 Worker V3 → E-01 demo → E-04 manifest → E-05 board PDF → E-06 ZIP → L-03 trust → P-01 e2e
```

**Dispatcher:** `python3 scripts/pick-wise.py --bottleneck sandbox|export|demo|www|pipeline|channel|ship`

---

## 6. Top 25 active prompts (Tier 1 — always prefer these)

| Rank | ID | Title | Lane |
|------|-----|-------|------|
| 0 | S-01 | Self-serve sandbox `/start/` + e2e | Product-led sandbox |
| 1 | E-05 | Board PDF path E2E | Receipt-first |
| 2 | E-06 | Procurement ZIP E2E | Trust center |
| 3 | E-01 | 5-minute demo script | Receipt-first |
| 4 | L-02 | Homepage §07–10 | Numbered narrative |
| 5 | L-03 | Trust center | Trust center |
| 6 | E-04 | Export manifest spec | Receipt-first |
| 7 | L-01 | Trust Brief $10k audit | Readiness SKU |
| 8 | P-01 | verify-ui-e2e v12 | Trust center |
| 9 | L-10 | MSP Phase 1→2 | MSP two-tier |
| 10 | L-09 | Federal ADM chip | Numbered narrative |
| 11 | E-02 | TLE verify walkthrough | Receipt-first |
| 12 | E-03 | TLE YAML trio | Receipt-first |
| 13 | L-11 | Copilot CCS stack | Microsoft CCS |
| 14 | L-08 | Intake RID threading | Ops |
| 15 | H-01 | MSP mapping UX | MSP two-tier |
| 16 | H-02 | Federal AIA mapping | Numbered narrative |
| 17 | E-07 | Confidence on result | Receipt-first |
| 18 | L-04 | Procurement → trust | Trust center |
| 19 | P-02 | rebuild-www-v6 SSOT | Ops |
| 20 | E-19 | Honest scope badges | Trust center |
| 21 | L-05 | Design partner scarcity | Honest investor |
| 22 | E-11 | Pilot Wk 0–12 | Readiness SKU |
| 23 | P-05 | Staging demo URL | Commercial SSOT |
| 24 | L-07 | QuickScan anchor | Readiness SKU |
| 25 | E-15 | Receipt mock consistency | Receipt-first |

Full SMART blocks: [TIER1_SMART_PROMPTS.md](./plans/TIER1_SMART_PROMPTS.md)

---

## 7. Brainstorm enrichments (10 new — folded into T1/T2)

| ID | Idea | Why | Lane |
|----|------|-----|------|
| **N-01** | "Receipt in 5 minutes" timer on demo page | Buyer proof moment | Receipt-first |
| **N-02** | Trust center downloadable sample manifest JSON | Diligence self-serve | Trust center |
| **N-03** | Copilot hub "What Purview already did" vs "What we receipt" table | Microsoft complement | CCS |
| **N-04** | MSP partner one-pager PDF (generated, not hand) | Channel enablement | MSP two-tier |
| **N-05** | Federal AIA level ↔ TLE verdict mapping interactive preview | GC attach | Numbered narrative |
| **N-06** | Investor "proof milestones" checklist (no ARR) | Honest scarcity | Numbered narrative |
| **N-07** | Workspace "export integrity FAIL" demo button | Tamper story | Receipt-first |
| **N-08** | Procurement ZIP contents manifest page (orientation) | Pack index | Trust center |
| **N-09** | Design partner debrief YAML template auto-created post-call | Pipeline intelligence | Readiness SKU |
| **N-10** | verify-ui-e2e "honest scope badge" row per hub | Regression guard | Trust center |

---

## 8. What we dropped (500 vs 1000)

- **500 removed from active pick:** duplicate phase×tier rows for same pattern×area
- **Frozen F-grade:** drift-impl, verdict-review, performance at scale, Prompt OS stage1–3 chains
- **Agentic fence:** customer-outreach never NF-CLOUD send (Hub only)
- **Anti-patterns:** vendor comparisons, fourth SKU, fake certs, MSB lead, full GRC platform breadth

---

## 9. Commands

```bash
make generate-tier1-smart          # 50 W3 prompts
python3 scripts/generate-prompt-catalog-500.py  # full 500 catalog
make pick-wise                       # pick next WISE prompt
python3 scripts/pick-wise.py --bottleneck export --prompt
python3 scripts/sync-tier1-status.py --done E-01
```

---

## 10. Related docs

- [NOETFIELD_PROMPT_PACK_V13_SMART_LOCKED_v1.md](./NOETFIELD_PROMPT_PACK_V13_SMART_LOCKED_v1.md)
- [CATALOG_500_INDEX.md](./plans/CATALOG_500_INDEX.md)
- [PRIORITY_MATRIX_500.md](./plans/PRIORITY_MATRIX_500.md)
- [WWW_V12_MASTER_PLAN_LOCKED_v1.md](../WWW_V12_MASTER_PLAN_LOCKED_v1.md)
- [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](../strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md)
