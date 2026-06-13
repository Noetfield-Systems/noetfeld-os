# Noetfield Prompt Pack — v12 Redesign & Tiering (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | **SUPERSEDED** — historical archive only. Execution: [NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md](./NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md) · `make pick-wise` |
| **Scope** | Consolidate **1000 generated prompts** → **~500 catalogued / ~50 active** |
| **Success model SSOT** | [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](../strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md) · [WWW_V12_MASTER_PLAN_LOCKED_v1.md](../WWW_V12_MASTER_PLAN_LOCKED_v1.md) · W3 = deposit ≥ CAD 2K or signed LOI + **board PDF in meeting** |
| **Agent tag** | `NF-CLOUD-AGENT` / `nf-local-repo-agent` |
| **Do not** | Regenerate vendor comparison pages, full GRC platform scope, Prompt OS stage1/2/3 extraction chains for GTM |

---

## 1. Executive diagnosis (deep grade)

### What exists today

| Pack | Count | Generator | Grade | Verdict |
|------|-------|-----------|-------|---------|
| **NF-PLAN registry** | 1000 | `generate-prompt-pack-v2.py` | **C+** | Useful grid, **~85% duplicate intent** across phase×tier |
| **noetfield-1000 library** | 1000 (spec) | `generate-noetfield-1000-prompts.py` | **B−** | Better task specificity; overlaps NF-PLAN; prompts dir often empty |
| **GTM_PRIORITY_100 slice** | 100 | derived | **B** | Right fence (agentic vs cloud); repetitive rows |
| **Worker Blueprint V3** | 1 master | manual | **A** | Best single paste prompt — align all agents here |
| **Legacy Prompt OS** (v31/v37, stage1–3) | ~12 docs | archived | **D** | Superseded for Noetfield GTM — keep L0-law only for Prompt OS ingest |
| **WWW v12 implementation** | ~25 pages | `rebuild-www-v6.py` | **A−** | Receipt-first, honest scope — **now the visual SSOT for www-copy prompts** |

### Root problem

The 1000-pack is a **Cartesian product** (20 patterns × 10 phases × 5 tiers). It optimizes for *coverage*, not *W3 proof*. Result:

- Same “WWW copy block for {area}” **50 times**
- Same “demo rehearsal” **50 times**
- **350** rows flagged `gtm_priority=1` — everything feels P0
- Critics repeat: *“validation 2/10 until one contracted pilot uses board PDF”* — correct, but not actionable per row

**North star filter (one question):**  
*Does this prompt move us closer to **one org using board PDF in a governance meeting** or **W3 deposit/LOI** within 90 days?*

If no → Tier 3 archive or delete from active pickers.

---

## 2. Grading rubric (A–F)

| Grade | Meaning | Use in pack |
|-------|---------|-------------|
| **A** | Directly unblocks W3 / demo / procurement / Trust Brief conversion | **Tier 0–1 only** |
| **B** | Strengthens proof artifact (TLE, export, verify, trust center) | Tier 1–2 |
| **C** | Hardening (tests, openapi, runbooks) — after first pilot | Tier 2 |
| **D** | Research / drift / RAG / scale infra — gated | Tier 3 |
| **F** | Wrong lane (MSB lead, vendor comparisons, full GRC, TrustField scope) | **Frozen — never pick** |

### Buyer pattern weights → prompt focus

| Pattern | Copy into prompts | Weight |
|---------|-------------------|--------|
| **Receipt-first export** | Export in minutes, fail-closed tamper | **High** |
| **Trust center diligence** | Procurement ZIP, honest scope table | **High** |
| **Numbered GRC narrative** | Framework marquee — **not** “leader” claims | Medium |
| **Microsoft CCS + Purview Learn** | Complement stack, Phase 1 vs Phase 2 | **High** |
| **MSP two-tier attach** | “Readiness → Record · Phase 2 TLE” | **High** |
| **Fixed-fee readiness SKU** | Copilot Readiness Assessment naming, fixed fee | Medium |
| **Full estate GRC platform** | Ignore inventory/enforce scope | **Anti-pattern** |

---

## 3. Redesigned architecture — four tiers

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 0 — CONSTITUTION (12 meta-prompts, never duplicated)    │
│ Worker V3 paste · PLAN WITH NO ASF · www v12 regen · closeout│
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ TIER 1 — W3 ACTIVE (~50 prompts, max 3 per session)          │
│ Land → Expand → Channel · proof · demo · procurement         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ TIER 2 — PRODUCT BACKLOG (~150 prompts, pilot-gated)         │
│ TLE · connectors · workspace · API · federal/MSP lanes       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ TIER 3 — ARCHIVE (~800 prompts, deduped catalog)             │
│ Grid stubs · horizon · duplicate www-copy rows · drift research│
└─────────────────────────────────────────────────────────────┘
```

**Active catalog target:** **500 named prompts** in registry (Tier 0–2 + indexed Tier 3), with **only Tier 0–1** in `QUICK_PICK` / `pick-no-asf-plan`.

---

## 4. Pattern-level grades (20 NF-PLAN patterns)

| Pattern | Grade | Tier | Action |
|---------|-------|------|--------|
| `demo-rehearsal` | **A** | 1 | **Keep 5** (copilot, trust-ledger, federal, msp, investors) — merge duplicates |
| `www-copy` | **A** | 1 | **Keep 8** — one per hub + trust + verify; point at `rebuild-www-v6.py` |
| `diligence-doc` | **A** | 1 | **Keep 6** — procurement, trust, API, federal AIA, MSP RACI |
| `buyer-debrief` | **A** | 1 | **Keep 3** — template only; agentic execution |
| `customer-outreach` | **A** | 1 | **Agentic only** — 5 lanes max (Hub); never NF-CLOUD send |
| `smoke-script` | **B** | 2 | **Keep 10** — extend verify-ui-e2e per www v12 |
| `audit-export` | **B** | 2 | **Keep 8** — TLE manifest, board PDF, ZIP integrity |
| `openapi-sync` | **B** | 2 | **Keep 4** |
| `integration-test` | **B** | 2 | **Keep 12** — evaluate flow, tamper fail |
| `console-ui` | **B** | 2 | **Keep 6** |
| `schema-validate` | **B** | 2 | **Keep 4** |
| `examples-pack` | **B** | 2 | **Keep 4** — TLE YAML trio + tampered fail sample |
| `scope-gate-drill` | **B** | 2 | **Keep 4** |
| `registry-reconcile` | **C** | 3 | **Keep 2** — after each ship session only |
| `tier-gate-check` | **C** | 3 | **Keep 2** |
| `runbook` | **C** | 2 | **Keep 6** |
| `api-endpoint` | **C** | 2 | **Keep 8** — no new routes without pilot need |
| `drift-impl` | **D** | 3 | **Freeze 25** → single epic when customer asks |
| `verdict-review` | **D** | 3 | **Freeze** — postgres-first already locked |
| `performance` | **D** | 3 | **Freeze** — no load test before W3 |

**Dedup rule:** For each kept pattern × area, **one canonical NF-PLAN id**; mark siblings `status: superseded` in registry.

---

## 5. Phase remapping → success model (Land → Expand → Channel)

Replace abstract P0–P9 picking with **commercial phases**:

| Commercial phase | Old phases | Goal | Max active prompts |
|------------------|------------|------|-------------------|
| **LAND** | phase-7-pilot-gtm, P7, www-gtm | Trust Brief intake, homepage proof | 15 |
| **EXPAND** | phase-1-tle, phase-4-agents, P1/P4 | TLE + demo + board PDF path | 20 |
| **CHANNEL** | phase-2-connectors, msp, federal | MSP Phase 2, GC AIA attach | 10 |
| **PROVE** | phase-0-ship-ops, phase-8 | verify, trust center, staging smoke | 10 |
| **PLATFORM** | phase-3,5,6,9, P5–P9 | RBAC, RAG, drift — **gated** | 5 visible, rest archived |

---

## 6. Tier 0 — Constitution prompts (12)

Use these **instead of** random NF-PLAN rows.

| ID | Prompt name | Source |
|----|-------------|--------|
| **C-01** | PLAN WITH NO ASF (full sequence) | `NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md` |
| **C-02** | Noetfield Worker V3 paste block | `WORKER_BLUEPRINT_V3_NOETFIELD_COM_FULL_PROMPT.md` |
| **C-03** | WWW v12 regen + smoke | `python3 scripts/rebuild-www-v6.py` + `verify-ui-e2e.sh` |
| **C-04** | Agent reply YAML closeout | `EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md` |
| **C-05** | Scope gate — three SKUs only | `OFFERINGS_LOCKED.md` |
| **C-06** | Honest scope — no certifier fiction | `DESIGN_REFERENCE_GOALS R3, R13` |
| **C-07** | Copilot complement — never replace Purview | `GTM_COPYBOOK` wedge |
| **C-08** | MSP two-tier — Phase 2 attach | `MSP_GOVERNANCE_PACK_v1.md` |
| **C-09** | Federal — not a certifier | `FEDERAL_GOVERNANCE_PACK_v1.md` |
| **C-10** | Investor honesty — no fake ARR | `investors/index.html` callout |
| **C-11** | Agentic vs cloud fence | GTM_PRIORITY_100 R-011 |
| **C-12** | Pick max 3 tasks | `NOETFIELD_GTM_60_DAY_LOCKED_v1.md` |

---

## 7. Tier 1 — Top 50 active prompts (enriched templates)

Each template replaces **dozens** of grid duplicates. Copy **Agent prompt** block verbatim.

### LAND (15)

**L-01 · Trust Brief conversion copy audit**  
```
As NF-CLOUD-AGENT (Noetfield only): Audit /trust-brief/ against OFFERINGS_LOCKED ($10k, 6 weeks).
Ensure PRS block, no fourth SKU, CTA → /trust-brief/intake/. Run rebuild-www-v6 if HTML drift.
Verify: curl -s localhost:13081/trust-brief/ | grep -F '$10,000'
Sources: OFFERINGS_LOCKED.md, GTM_COPYBOOK.md, rebuild-www-v6.py
Success: Trust Brief page matches commercial SSOT.
```

**L-02 · Homepage §07–10 proof narrative**  
```
Implement or verify homepage sections 07–10 (pain, category zones, CCS stack, FAQ) per WWW_V12_MASTER_PLAN.
No vendor compare table on public www. Regenerate index via rebuild-www-v6.py.
Verify: grep -F 'The moment Copilot becomes auditable' index.html
```

**L-03 · Trust center (/trust/) diligence**  
```
Ensure /trust/ has honest cert table (Shipped/Roadmap/N/A), metadata-only M365, link from footer + procurement.
No SOC2 claim unless true. Match trust center *structure* only.
Verify: grep -F 'fail closed' trust/index.html
```

**L-04 · Procurement pack → trust link**  
```
/copilot/procurement/ must link /trust/ and sample TLE. ZIP orientation copy only — no fake buyer logos.
Verify: verify-ui-e2e procurement row.
```

**L-05 · Design partner scarcity copy**  
```
Add or verify "Accepting design partners" on /investors/ and /copilot/pilot/ — no fake logo wall.
Verify: grep -F 'Accepting design partners' investors/index.html
```

**L-06 · Investor 8-zone map**  
```
/investors/ category map: zones only, disclaimer "not a compare page". Align with WWW v12 master map.
```

**L-07 · QuickScan anchor (/copilot/#quickscan)**  
```
If missing, add Copilot QuickScan $2–3.5K strip on /copilot/ per Worker Blueprint V3 — sub-tier A only.
Do not add fourth SKU.
```

**L-08 · Intake RID threading**  
```
Verify all primary CTAs use data-rid-link; footer RID copy works. smoke: trust-brief intake.
```

**L-09 · Federal ADM deadline chip**  
```
/federal/ official canada.ca + TBS links above fold; AIA↔TLE preview table; "not a federal certifier".
```

**L-10 · MSP Phase 1→2 diagram**  
```
/msp/ hero "Readiness → Record"; phase ladder; W3-MSP PASS line.
```

**L-11 · Copilot CCS stack block**  
```
/copilot/ stack ladder references Learn.microsoft.com CCS — complement language only.
```

**L-12 · FAQ alignment**  
```
/faq/ answers: not Purview replacement, three SKUs, no certifier — sync with homepage §10.
```

**L-13 · Enterprise offerings grid**  
```
/enterprise/ uses nf-offerings-v5 three SKUs — no nf-sku legacy markup.
```

**L-14 · Gate intake vectors**  
```
/gate/intake/ routes Trust Brief, Copilot, Bank Pilot, Partner — RID in mailto.
```

**L-15 · Agentic: design partner outreach batch** *(Hub only)*  
```
Agentic Hub: Execute outreach batch per DESIGN_PARTNER_SOW_OUTLINE — max 5 contacts.
NF-CLOUD: prepare templates on disk only; do not send email.
```

### EXPAND (20)

**E-01 · 5-minute demo script lock**  
```
Lock copilot/demo narrative: evaluate → confidence → Purview/Entra/audit → TLE → export.
Workspace mock in hero. Demo completes in ≤5 min on dev stack.
Verify: verify-ui-e2e copilot demo row.
```

**E-02 · TLE verify walkthrough**  
```
/trust-ledger/verify/ documents tamper FAIL path. Link from /trust/ and samples.
Honest: no Ed25519 claim until shipped.
```

**E-03 · TLE YAML samples trio**  
```
samples: go, conditional, rejected + README for procurement. Optional tampered export fail example.
```

**E-04 · Export manifest JSON spec**  
```
Document sidecar manifest fields: tle_id, export_integrity, hashes — docs/api or trust-ledger.
```

**E-05 · Board PDF path E2E**  
```
Workspace TLE detail must expose Board pack (PDF) — dashboard chunk verify in verify-ui-e2e.
```

**E-06 · Procurement ZIP path E2E**  
```
Same for Procurement pack (ZIP) link on TLE detail.
```

**E-07 · Confidence score on result page**  
```
/evaluate → /result/{rid} shows Confidence score badge — already in e2e; fix if regressed.
```

**E-08 · M365 connector mock OAuth**  
```
/workspace/connectors mock flow → workspace banner — e2e green.
```

**E-09 · API decision semantics**  
```
docs/api/index.html: allow≈201, review≈202, deny≈403 orientation paragraph.
```

**E-10 · Governance console deep link**  
```
/console/ primary CTA resolves to pilot host; shadow mode copy correct.
```

**E-11 · Copilot pilot success signals**  
```
/copilot/pilot/ lists Wk 0–12 path aligned with commercial SSOT §90-day.
```

**E-12 · Trust Ledger hub**  
```
/trust-ledger/ links workspace + samples + verify.
```

**E-13 · Bank Pilot shadow scope**  
```
/bank-pilot/ read-only, no custody — OFFERINGS_LOCKED alignment.
```

**E-14 · SME pack lane**  
```
/copilot/sme/ same TLE spine, SME pricing orientation — no enterprise platform claims.
```

**E-15 · Receipt mock consistency**  
```
All GTM hubs: nf-receipt-mock with export_integrity PASS — generator receipt() helper.
```

**E-16 · Stat bar consistency**  
```
Homepage stat bar: 4 · $10k · 90d · 3 SKUs — no fake analyst stats.
```

**E-17 · Mega CTA every hub**  
```
Every hub ends nf-cta-mega — Request Governance Brief + secondary.
```

**E-18 · Shell v12 bump**  
```
SHELL_VERSION and ?v=12 on all regenerated pages after www changes.
```

**E-19 · Honest scope badges every hub**  
```
scope_block() on hubs: Shipped/Orientation/Roadmap/N/A — no certifier rows as Shipped.
```

**E-20 · Agentic: buyer debrief after call**  
```
Hub: After CIO call, capture debrief YAML — pain, Copilot timeline, next step Trust Brief vs pilot.
Cloud: store template under docs/copilot/debriefs/ only.
```

### CHANNEL (10)

**H-01 · MSP READINESS→RECORD mapping UX**  
```
/msp/ links READINESS_TO_RECORD_MAPPING_v1.md; partner intake CTA.
```

**H-02 · Federal AIA mapping doc link**  
```
Prominent link AIA_TLE_MAPPING_v1.md from federal proof grid.
```

**H-03 · Partner gateway**  
```
/partners/ API + MSP links; no MSB as primary hero.
```

**H-04 · GC Copilot PIN checklist**  
```
PIN checklist doc linked from federal; scope badges in hero.
```

**H-05 · NIST strip on procurement**  
```
Procurement ZIP citations mention NIST AI RMF — orientation only.
```

**H-06 · Partner LOI template**  
```
docs/msp/ or docs/partners/ LOI orientation — not legal advice.
```

**H-07 · Wholesale pricing orientation**  
```
MSP Governance Pack $2k–10k via partner — one paragraph on /msp/.
```

**H-08 · MSP Phase 1 complement copy**  
```
MSP page: Phase 1 examples generic — no third-party vendor names.
```

**H-09 · Federal intake query param**  
```
/trust-brief/intake/?interest=federal tested in links.
```

**H-10 · Agentic: MSP partner conversation**  
```
Hub: first MSP partner call script — Phase 2 attach after readiness vendor.
```

### PROVE (5)

**P-01 · verify-ui-e2e www v12**  
```
Extend and run verify-ui-e2e.sh for §07–10, /trust/, federal, msp, copilot CCS rows.
```

**P-02 · rebuild-www-v6 single source**  
```
Hand-edited GTM HTML forbidden — generator only.
```

**P-03 · plan-with-no-asf-verify**  
```
./scripts/plan-with-no-asf-verify.sh green after ship.
```

**P-04 · sync-prompt-pack-status**  
```
After done prompts: sync registry + QUICK_PICK.
```

**P-05 · Staging smoke / demo URL**  
```
Public demo URL documented in os/SHIP_NOW when staging live.
```

---

## 8. Consolidation: 1000 → 500 catalog

| Bucket | Count | Registry action |
|--------|-------|-----------------|
| Tier 0 constitution | 12 | New `docs/ops/plans/TIER0_CONSTITUTION.md` |
| Tier 1 active (L/E/H/P above) | 50 | New `docs/ops/plans/TIER1_W3_ACTIVE_50.md` |
| Tier 2 product backlog | ~150 | Filter registry: `tier_active: 2` |
| Tier 3 archive (deduped grid) | ~788 | `status: archived` + `superseded_by: L-xx` |
| **Total catalogued** | **~500** | Active + backlog + constitution |
| **Frozen grid remainder** | ~500 | Keep in JSON for history; exclude from pickers |

**Picker rule:** `pick-no-asf-plan.py --tier T0 --source tier1` only reads Tier 1 list.

---

## 9. Legacy Prompt OS — freeze list

**Do not use for Noetfield www/GTM:**

- `master-strategic-context-engine-v35/v37` — extraction theater
- `strategic-structuring-reasoning-engine-stage2` — pre-www v5
- `noetfield-gie-cursor-master-prompt-v31` — superseded by Worker V3
- `prompt-constitution-blueprint-directory-v10` — use Tier 0 table above
- `all-prompt-constitutions-comparison-fa` — archive

**Keep for SinaPromptOS ingest only:** L0-law stage3 execution output format.

---

## 10. Enriched universal agent prompt wrapper

Replace boilerplate `As NF-CLOUD-AGENT... implement: {pattern} for {area}` with:

```markdown
## Context (read first)
- Wedge: Copilot execution receipts — evaluate → TLE → export (metadata-only M365)
- W3 pass: board PDF in real meeting OR deposit ≥ CAD 2K
- Max scope: one artifact · one verify command · no SKU creep

## Task
{specific deliverable — one sentence}

## Forbidden
- Battlecards / compare pages / fourth SKU / fake certs / MSB lead on Noetfield www

## Sources (max 5)
{paths}

## Verify
{single command or e2e row}

## Done when
{observable outcome tied to W3 or www v12 metric}
```

---

## 11. Implementation checklist (ops)

- [ ] Add `TIER1_W3_ACTIVE_50.md` with full L/E/H/P prompts (copy from §7)
- [ ] Update `generate-prompt-pack-v2.py`: `tier_active` field + dedup `superseded_by`
- [ ] Update `pick-no-asf-plan.py`: default to Tier 1 only
- [ ] Point `QUICK_PICK.md` at Tier 1 list (replace empty 1000-done message)
- [ ] Add `BASE_SOURCES` in generator: `WWW_V12_MASTER_PLAN`, `GTM_COPYBOOK` v12 wedge
- [ ] Mark 800 registry rows `archived` via one-time script (do not delete JSON history)

---

## 12. Weekly pick order (founder default)

When unsure, pick **in this order** (max 3):

1. **E-01** demo script / workspace path  
2. **E-05/E-06** board PDF + ZIP e2e  
3. **L-02/L-03** www + trust center  
4. **L-10/L-09** MSP or federal lane  
5. **P-01** verify-ui-e2e green  
6. Only then Tier 2 API/connector work  

---

**Related:** [NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md](./NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md) · [NOETFIELD_1000_PROMPT_LIBRARY_LOCKED_v1.md](./NOETFIELD_1000_PROMPT_LIBRARY_LOCKED_v1.md) · [WWW_V12_MASTER_PLAN_LOCKED_v1.md](../WWW_V12_MASTER_PLAN_LOCKED_v1.md)
