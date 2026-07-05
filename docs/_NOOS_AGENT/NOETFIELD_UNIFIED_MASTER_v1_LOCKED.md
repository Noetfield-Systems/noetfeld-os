# NOETFIELD UNIFIED MASTER — v1 LOCKED
**Status:** LOCKED — single entry point for all Noetfield agents and founders
**Date:** 2026-06-15
**Parent SSOT:** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md`
**Product SSOT:** `NOETFIELD_OS_SSOT_v1_LOCKED.md`
**Authority:** On conflict → parent SSOT wins on portfolio/identity. Product SSOT wins on build/GTM.
**Tag:** NOOS-AGENT-DOC · NOETFIELD-MASTER

---

## PART 0 — WHY THIS FILE EXISTS

Noetfield content was built across 4 separate locations over multiple sessions. Each location has real value. No single agent has seen all of it. This document is the unification layer — it maps everything, assigns status verdicts, and gives agents a clear reading order so they never start from scratch again.

**Four content locations found:**
```
Location 1: ~/Desktop/SourceA/                           ← commercial + governance (most current)
Location 2: ~/SinaaiMonoRepo/SinaaiDataBase/noetfield/  ← deep product specs + market research
Location 3: ~/Projects/noetfeld-os/                     ← live prototype (GEL runtime)
Location 4: ~/SinaPromptOS/projects/noetfield/          ← thin project stub
```

---

## PART 1 — WHAT NOETFIELD IS (UNIFIED DEFINITION)

**Three-layer view:**

```
noetfield.com (brand)
  → Story, evidence narrative, Copilot governance pitch
  → Trust Brief $10K · Copilot Governance Pack · Bank Pilot · Design Partner $2–10K CAD

Noetfield OS / GEL (product runtime)
  → POST /v1/decision → APPROVE / REVIEW / DECLINE
  → TLE v1 (Trust Ledger Entry) — signed, timestamped, policy-versioned
  → Append-only audit trail → board PDF export
  → ~/Projects/noetfeld-os/ (FastAPI + SQLite, Phase 4 chain tools + CI; GEL runtime live)

SourceA (engine underneath)
  → Pre-LLM governance execution runtime — never mentioned to customers
  → Every TLE v1 = SourceA receipt. Every audit trail = SourceA spine pattern.
```

**One strategic sentence:**
> "Noetfield sells the story and the evidence. Noetfield OS sells the gate and the log."

**External pitch line:**
> "Noetfield OS evaluates policy, scores risk, and produces audit-ready evidence before your systems execute."

**Category:** Governance Execution Layer (GEL) — pre-execution, non-custodial, board-defensible. NOT chat, NOT LOS, NOT payments.

---

## PART 2 — COMPLETE CONTENT MAP (ALL 4 LOCATIONS)

### Location 1 — ~/Desktop/SourceA/ (COMMERCIAL + GOVERNANCE)

| File | Status | Contains |
|------|--------|----------|
| `NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md` | ✅ ACTIVE — THIS FILE | Single entry point |
| `NOETFIELD_OS_SSOT_v1_LOCKED.md` | ✅ ACTIVE | Product SSOT — build order, GTM, golden rules |
| `NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md` | ✅ ACTIVE | Competitive analysis, SKUs, pricing, win/lose lines |
| `NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md` | ✅ ACTIVE | Full 5-min demo script, vocabulary rules, SKU ladder |
| `NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md` | ✅ ACTIVE | Git/agent workspace entry rules |
| `founder/NOETFIELD_CLOUD_FINAL_ACKNOWLEDGE_PROMPT_v1.md` | ✅ ACTIVE | Founder acknowledgement prompt |
| `agent-skills/noetfield_cloud/` | ✅ ACTIVE | Cloud agent skills |
| `agent-skills/noetfield_local/` | ✅ ACTIVE | Local agent skills |
| `scripts/run_noetfield_compliance_demo_v1.sh` | ✅ ACTIVE | Demo runner script |
| `scripts/noetfield_unified_guide.py` | ✅ ACTIVE | Unified guide script |
| `REPO_STATUS_REPORTS/noetfield.yaml` | 🟡 REFERENCE | Repo health snapshot |
| `RESEARCH/ROUTING_NOETFIELD.yaml` | 🟡 REFERENCE | Routing config |

---

### Location 2 — ~/SinaaiMonoRepo/SinaaiDataBase/noetfield/ (DEEP PRODUCT SPECS)

#### /docs/ — Governance & Market Research

| File | Status | Key Content |
|------|--------|-------------|
| `NOETFIELD_GOVERNANCE_PLANE_LOCKED_v1.md` | ✅ ACTIVE — MERGE | Noetfield = govern (before execution), TrustField = deliver (after). "Should this run? Under what rules? With what proof?" Canada AI for All fit. |
| `CONSIDERATION_MARKET_ANALYSIS_PRODUCTS_2026-06_v1.md` | ✅ ACTIVE — KEY | Canada market: AI for All ($2.3B June 2026), Bill C-12 FINTRAC penalties, ~1,500 RPAA PSP applicants. Buyer segments ranked. Assessments win first. |
| `CONSIDERATION_ENTITY_MONEY_FLOW_SAFE_REVENUE_v1.md` | ✅ ACTIVE — READ | Revenue/entity structure — how to invoice safely |
| `NOETFIELD_TRUSTFIELD_CONFLICT_PASS_v1.md` | ✅ ACTIVE | Explicit TrustField/Noetfield boundary — no overlap |
| `CONSIDERATIONS_INDEX.md` | 🟡 REFERENCE | Index of all considerations |
| `TRACE_REGISTRY_GOVERNANCE_GOAL_20260608.md` | 🟡 REFERENCE | Trace registry for governance goal session |

#### /os/ — Strategy & Plan

| File | Status | Key Content |
|------|--------|-------------|
| `strategy.md` | ✅ ACTIVE — MERGE | Plane: [DESIGN]. SourceA SSOT is authority. Cursor work = documentation + schema. |
| `plan.json` | ✅ ACTIVE | MVP criteria (top 5). Phase gating. |
| `task_definition.json` | 🟡 REFERENCE | Task definitions |
| `VERIFY.md` | 🟡 REFERENCE | Verification checklist |

#### /product/ — 23 Deep Technical Specs

**Status key:** FUTURE (don't build now), REFERENCE (read when building that phase), ACTIVE (current phase)

| File | Status | Phase | Key Content |
|------|--------|-------|-------------|
| `noetfield_gcip_document_hierarchy__noetfield-master-document-directory-l0-l5-v1.md` | ✅ READ FIRST | All | L0-L5 hierarchy: Constitution → Product Kernel → MECR Kernel → EGS Runtime → SoT Registry → NF-CHAIN-LOCK |
| `noetfield_mvp_spec__noetfield-mvp-system-spec-v3-0-hardened.md` | ✅ ACTIVE | Phase 1-2 | MVP: CDO output, no financial instructions, Copilot governance wedge |
| `noetfield_product_kernel_l1__noetfield-constitutional-annex-product-kernel-v4-en.md` | ✅ ACTIVE | Phase 1-2 | L1: CDA, PHO, corridors, intent structure |
| `noetfield_mecr_l2__noetfield-mecr-governance-kernel-l2-v1.md` | ✅ ACTIVE | Phase 2 | L2: APPROVE/REJECT/REWRITE/FLAG kernel |
| `noetfield_l3_egs_runtime__noetfield-l3-egs-runtime-v3-2.md` | 🔵 FUTURE | Phase 3 | L3: External governance service runtime |
| `noetfield_evidence_pack_schema__noetfield-evidence-pack-json-schema-v1.md` | ✅ ACTIVE | Phase 1 | Evidence pack JSON — maps to TLE v1 + board PDF |
| `noetfield_sot_registry_l4__noetfield-sot-registry-l4-v3-2.md` | 🔵 FUTURE | Phase 4 | L4: SoT Registry — observability only |
| `noetfield_operating_discipline__noetfield-directory-enforced-consistency-spec-fa.md` | ✅ ACTIVE | All | Directory + consistency enforcement rules |
| `noetfield_documentation_standard__noetfield-dual-layer-documentation-standard-v1.md` | ✅ ACTIVE | All | Dual-layer doc standard |
| `noetfield_rfc_governance__noetfield-rfc-standard-v1-github-ci.md` | 🟡 REFERENCE | Phase 2+ | RFC governance standard for CI |
| `noetfield_unified_system_graph__noetfield-unified-system-graph-v1.md` | 🟡 REFERENCE | Phase 3 | Full system topology |
| `noetfield_gie__noetfield-gie-specification-supplement-v31.md` | 🔵 FUTURE | Phase 3+ | GIE specification |
| `noetfield_execution_kernel_spec__noetfield-execution-kernel-temporal-v1-canonical.md` | 🔵 FUTURE | Phase 4 | Temporal-based execution kernel |
| `noetfield_langgraph_integration__noetfield-langgraph-rfc-execution-integration-v1.md` | 🔵 FUTURE | Phase 4 | LangGraph RFC |
| `noetfield_bank_governance_integration__noetfield-bank-integration-pack-v2.md` | 🔵 FUTURE | Phase 5 | Bank-grade integration pack v2 |
| `noetfield_bank_production_architecture__noetfield-bank-grade-implementation-design-v1.md` | 🔵 FUTURE | Phase 5 | Bank production architecture |
| `noetfield_agent_catalog__noetfield-agent-catalog-bank-grade-v1.md` | 🔵 FUTURE | Phase 5 | Bank-grade agent catalog |
| `noetfield_temporal_governance_v2__noetfield-v2-temporal-governance-os-bank-grade.md` | 🔵 FUTURE | Phase 5 | Temporal governance OS v2 |
| `noetfield_execution_vm__noetfield-execution-consensus-vm-v40-blueprint.md` | 🔵 FUTURE | Phase 5 | Consensus VM v4.0 |
| `noetfield_sme_visibility_pilot__noetfield-master-blueprint-sme-visibility-readonly-v1.md` | 🔵 FUTURE | Phase 6 | SME visibility pilot |
| `noetfield_v3_ai_orchestration_product__noetfield-v3-mvp-production-spec-final.md` | 🔵 FUTURE | Phase 6 | v3 AI orchestration product |
| `noetfield_product_vision__noetfield-ambient-intelligence-nervous-system-sot-v31.md` | 🔵 VISION ONLY | Long-term | Ambient Intelligence Nervous System — 5-year north star, not current build |
| `noetfield_execution_roadmap__noetfield-5-year-vision-enterprise-ai-os.md` | 🔵 VISION ONLY | Long-term | P1-P5 enterprise AI OS phases |

---

### Location 3 — ~/Projects/noetfeld-os/ (LIVE GEL RUNTIME)

| Item | Status | Notes |
|------|--------|-------|
| FastAPI app | RUNNING | `POST /v1/decision` |
| SQLite audit | ACTIVE | Local dev persistence |
| Agent vault | ACTIVE | `docs/_NOOS_AGENT/` + MANIFEST.json |
| Phase | Phase 4 | Chain tools + CI hardening (PRODUCT_TRUTH live); Phase 3 evidence/TLE in build order |
| Hosted API | LIVE | `https://api.noetfield.com` on Railway `gel-api` |
| Local port | ACTIVE | `:8001`; never mono `:8000` |
| Tests | PASS | 143 pytest checks passing in noetfeld-os |

---

### Location 4 — ~/SinaPromptOS/projects/noetfield/ (THIN STUB)

| Item | Status | Notes |
|------|--------|-------|
| README.md | 🟡 REFERENCE | Thin project pointer |
| project.json | 🟡 REFERENCE | Project metadata |
| **Verdict** | Low priority | Content thin — no unique value beyond pointers |

---

## PART 3 — CANADA MARKET INTELLIGENCE (ACTIVE, JUNE 2026)

From `CONSIDERATION_MARKET_ANALYSIS_PRODUCTS_2026-06_v1.md` — key facts:

**Regulatory forcing functions (why buyers pay now):**
- **AI for All** — launched June 4, 2026 · $2.3B+ · target 60% SME AI adoption by 2034
- **Bill C-12 / FINTRAC** — Royal assent March 26, 2026 · penalties up to $20M or 3% global revenue
- **RPAA supervision live** — ~1,500 PSP applicants supervised (Sept 2025+)
- **PacifiCan RAII** — $500K–$3M repayable per project for AI adoption

**Buyer segments (ranked by near-term pay probability):**

| Rank | Segment | Pays for | Budget | Lead |
|------|---------|----------|--------|------|
| 1 | MSB / PSP / fintech (RPAA+FINTRAC) | Dual compliance, readiness evidence | $15K–150K | TrustField |
| 2 | Credit unions / small FI | Copilot + data governance | $12K–40K | **Noetfield** |
| 3 | Professional services SMB | Copilot readiness, PIPEDA | $5K–15K | **Noetfield** |
| 4 | MSP / Microsoft partner | White-label governance assessment | $3K–12K/client | **Noetfield** |
| 5 | Healthcare / legal SMB | Vertical governance | $8K–25K | Defer |

**Global success models to learn from:**
- Model A (fastest cash): Assessment-first services → fixed-fee diagnostic → roadmap → retainer
- Model B (recurring): Compliance automation SaaS → evidence vault + audit export
- Model C (enterprise): AI governance platform → policy packs, agent registry

**Noetfield path:** Model A first (NF-QS QuickScan) → Model B (GEL Starter SaaS) → Model C (long-term)

---

## PART 4 — SKU LADDER (CANONICAL)

| SKU | Price (CAD) | Deliverable | Phase |
|-----|-------------|-------------|-------|
| **NF-QS** Copilot QuickScan | $2,000–$3,500 | 3–5 day gap scan · exec summary | **NOW** |
| **NF-RD** Copilot Readiness Pilot | $5,000–$10,000 | 4–6 wk · signed TLE v1 · board PDF · procurement ZIP | **NOW (NW1)** |
| **NF-TB** Trust Brief | $10,000 USD · 6 wk | Governance audit · policy mapping · risk exposure | After NW1 |
| **NF-BP** Bank Pilot | Scoped | Read-only shadow governance | Institutional (Phase 5+) |
| GEL Starter | ~$10K | Sandbox, 1 policy pack, audit portal | Phase 2 |
| GEL Standard | ~$50K | Multi-tenant, Postgres, SLA | Phase 3 |
| GEL + Trust Ledger | ~$120K | Quarterly export, drift scoring, board pack | Phase 4 |

**NW1 target:** first NF-RD design partner at $2K+ CAD deposit.
**Invoicing law:** All deposits via TrustField bank until Noetfield entity is split and structured.

---

## PART 5 — NOETFIELD vs TRUSTFIELD BOUNDARY (LOCKED)

From `NOETFIELD_TRUSTFIELD_CONFLICT_PASS_v1.md` and `NOETFIELD_GOVERNANCE_PLANE_LOCKED_v1.md`:

```
NOETFIELD (govern — BEFORE)       TRUSTFIELD (deliver — AFTER)
──────────────────────────────    ────────────────────────────
Policy & control plane         →  RPAA readiness pilots
AI oversight & evidence        →  MSP / licensed partner ops
Pre-implementation gate        →  Payment program execution
Board / supervisor view        →  Canadian commercial delivery
```

**Noetfield answers:** Should this run? Under what rules? With what proof?
**TrustField answers:** How does this program go live in Canada under RPAA with partners?

**Explicit handoff rule:** When both appear in one deal — explicit handoff, separate proposals, do not blend.

---

## PART 6 — L0–L5 DOCUMENT HIERARCHY (PRODUCT ARCHITECTURE)

From `noetfield-master-document-directory-l0-l5-v1`:

| Layer | Role | Primary Artifact | Phase |
|-------|------|-----------------|-------|
| L0 | Constitution — identity, boundaries, axioms | Constitutional Annex v3.2 | Active |
| L1 | Product Kernel — CDA, PHO, corridors, intent | Product Kernel v4.0 | Active |
| L2 | MECR Governance Kernel — APPROVE/REJECT/REWRITE/FLAG | MECR v1 | Phase 2 |
| L3 | EGS Runtime — enforce L2 only; external trigger | EGS v3.2 | Phase 3 |
| L4 | SoT Registry — reference index, no decisions | SoT Registry v3.2 | Phase 4 |
| L5 | NF-CHAIN-LOCK — integrity binding | NF-CHAIN-LOCK | Phase 5 |

**Pipeline:** L0 → L1 → L2 → L3, with L4 as observability. L4 answers "where defined" not "what to do."

**Current build focus:** keep GEL runtime live, harden deterministic replay, publish developer tools, and keep `PRODUCT_TRUTH.md` current.

---

## PART 7 — AGENT READING ORDER (SESSION START)

Every Noetfield agent must read in this exact order:

```
1. SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md   (parent — portfolio truth)
2. NOETFIELD_OS_SSOT_v1_LOCKED.md                             (product SSOT — build/GTM)
3. THIS FILE (NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md)           (content map + market intel)
4. NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md                     (commercial — before any call)
5. NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md              (demo — before any demo)
6. ~/Projects/noetfeld-os/docs/_NOOS_AGENT/PRODUCT_TRUTH.md   (live product state)
```

**Only after reading all 6:** begin work.

**Never trust:** Hub, chat history, or any file outside this reading list for strategic decisions.

---

## PART 8 — UNIFIED FOLDER LAW

All Noetfield OS agent documents must live in:
```
~/Projects/noetfeld-os/docs/_NOOS_AGENT/
```

A copy of this file AND `NOETFIELD_OS_SSOT_v1_LOCKED.md` must be synced there every time either is updated.

**Sync command (canonical: Noetfield-All-Documents):**
```bash
bash ~/Projects/noetfeld-os/scripts/sync-noos-ssot.sh
```

---

## PART 9 — COMPETITIVE POSITION (FROM BATTLE CARD)

**One-sentence moat:**
> "Noetfield gives your board what Microsoft Copilot alone cannot: every AI action evaluated, signed, and logged. When policy changes, your agents re-brief in the same session — not next quarter."

**Win table:**

| Competitor | Noetfield angle |
|-----------|----------------|
| Microsoft Purview | Purview shows *activity*. Noetfield proves what was *permitted*, under which policy version, with board-defensible export. |
| Securiti | Securiti gets data ready for Copilot. Noetfield keeps governance current *after* Copilot is live. |
| Zenity | Zenity secures how agents are *built*. Noetfield kills *governance latency* — stale policy cannot execute. |
| Credo AI / Holistic | Full GRC suite. Noetfield is narrow Vanta for Copilot governance — faster, cheaper, Canada-first. |

**When to win:** Board/regulator asking for Copilot evidence · Copilot live but "we don't know what's allowed" · Policy docs change monthly.

**When to lose:** Buyer needs full data estate discovery (Securiti) · Copilot Studio agent inventory at scale (Zenity AISPM) · Zero Copilot deployment (sell NF-QS only).

---

## PART 10 — GOLDEN RULES (NON-NEGOTIABLE)

1. Non-custodial — never initiate payment or settlement
2. Pre-execution only — evaluate before the action, not after
3. Fail closed — uncertain = DECLINE
4. Append-only audit — no deletes, no edits
5. Version everything — every decision references a policy version hash
6. Canada first — regulatory framing is Canadian
7. Evidence over dashboards — ship the log before the chart
8. GEL narrow scope — do not expand into LOS, payments, or agent proxy
9. Noetfield vocabulary only with customers — never SourceA internal terms
10. ASF owns ecosystem structure — no registry or SSOT changes without ASF

---

## PART 11 — WHAT TO DO NOW

**ASF (this week):**
- Send NW1 outreach email (template in `NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md`)
- Target: Canadian credit union, lending fintech, or enterprise with active Copilot rollout
- Do not wait for Phase 1 exit. NF-QS QuickScan can be sold TODAY against noetfield.com

**Noetfield OS agent (noetfeld-os workspace):**
- Sync this file and `NOETFIELD_OS_SSOT_v1_LOCKED.md` to `docs/_NOOS_AGENT/`
- Keep `docs/_NOOS_AGENT/PRODUCT_TRUTH.md` current after every runtime change
- Harden P0 live items: deterministic replay, PyPI publish, npm SDK, chatbot distill/RAG
- Update MANIFEST.json

**SourceA engine (Maintainer 2):**
- K1: Receipt validator on read — makes TLE v1 cryptographically defensible
- critic_boot_v1.py — Layer 1 local boot gate

---

*NOETFIELD UNIFIED MASTER v1 LOCKED — live-state refresh 2026-06-28*
*Supersedes: scattered content across 4 locations*
*Next version: when NW1 closes or GEL runtime state changes materially*
*Must be synced to ~/Projects/noetfeld-os/docs/_NOOS_AGENT/ on every update*
