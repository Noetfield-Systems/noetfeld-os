# NOETFIELD OS — PRODUCT SSOT v1 LOCKED
**Status:** LOCKED
**Date:** 2026-06-15
**Parent SSOT:** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` (wins on all portfolio, identity, and architecture conflicts)
**Repo:** `~/Projects/noetfeld-os`
**Index ID:** `NOETFIELD_OS_SSOT`
**Tag:** NOOS-AGENT-DOC

---

## PART 0 — SSOT HIERARCHY LAW

```
SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md   ← PARENT (portfolio truth)
        ↓ inherits into
NOETFIELD_OS_SSOT_v1_LOCKED.md                             ← THIS FILE (product truth)
        ↓ governs
docs/_NOOS_AGENT/                                          ← unified agent vault
```

**Rules:**
- This SSOT governs noetfield-os product decisions, build order, GTM, and agent briefings
- Parent SSOT governs portfolio identity, SourceA engine architecture, and cross-layer rules
- If conflict: parent wins on identity/architecture. This file wins on product/build/GTM specifics.
- This file CAN be updated as implementation progresses and new decisions are locked
- Every update must increment the version and note what changed
- noetfield-os agents must read THIS file AND the parent SSOT at session start

---

## PART 1 — WHAT NOETFIELD OS IS

**Noetfield OS is the Governance Execution Layer (GEL) runtime that powers noetfield.com.**

```
noetfield.com         → brand, story, evidence, sales surface
Noetfield OS (GEL)   → the runtime: evaluate() → APPROVE / REVIEW / DECLINE + immutable audit
SourceA engine        → durable execution infra underneath — DO NOT merge into this repo
TrustField            → regulated program delivery peer — hand off execution, keep governance design
```

**One strategic sentence:**
> "Noetfield sells the story and evidence. Noetfield OS sells the gate and the log."

**External line (use in all customer-facing materials):**
> "Noetfield OS evaluates policy, scores risk, and produces audit-ready evidence before your systems execute."

**Category:** Governance Execution Layer (GEL) for structured operational decisions — credit, eligibility, fraud triage, Copilot action governance. NOT chat, NOT LOS, NOT payments, NOT custody.

---

## PART 2 — SOURCEA AS FOUNDATION (ENGINE LAW)

SourceA is the foundation. Noetfield OS is the application built on top of it.

**What this means in practice:**

| Noetfield OS component | SourceA foundation |
|------------------------|-------------------|
| `decide()` audit row | SourceA governance receipt (same schema) |
| TLE v1 output | SourceA signed receipt surfaced for enterprise buyer |
| Board PDF export | SourceA spine → human-readable export |
| Policy version hash | SourceA SSOT version reference |
| Append-only audit trail | SourceA governance event spine pattern |
| Fail-closed gate | SourceA gatekeeper 10-check invariant pattern |

**Law:** When SourceA engine patterns are updated (spine schema, receipt format, gatekeeper logic), Noetfield OS must align. SourceA is the source of truth for engine patterns. Noetfield OS applies them to the GEL product.

**What NOT to do:**
- Do not merge SourceA engine code into this repo
- Do not override SourceA receipt schema with a custom format
- Do not run on `:8000` (that is the SinaaiMonoRepo spine port)
- Do not read SourceA internal governance vocab (runs, SDK, replay) in customer-facing docs

---

## PART 3 — IDENTITY AND VOCABULARY

**Noetfield vocabulary (use with customers):**
TLE · Trust Ledger Entry · board pack · governance · audit trail · pre-execution · evidence · compliance · APPROVE / REVIEW / DECLINE · policy version · drift · non-custodial

**SourceA vocabulary (NEVER use with customers):**
runs · SDK · replay · spine · gatekeeper · brain-os · worker · receipt (use "audit record" instead)

---

## PART 4 — UNIFIED AGENT VAULT (CANONICAL FOLDER)

All Noetfield OS agent documents, strategy, roadmap, and governance live in ONE place:

```
~/Projects/noetfeld-os/docs/_NOOS_AGENT/
```

**This is the single source of truth for noetfield-os agents.**

**Required contents (consolidate everything here):**

```
docs/_NOOS_AGENT/
├── MANIFEST.json                          ← index of all agent docs
├── NOETFIELD_OS_SSOT_v1_LOCKED.md        ← copy of this file (synced from SourceA)
├── 001_governance_drift_essay.md          ← already exists
├── 002_business_and_icp.md               ← already exists
├── 003_10_market_success_models.md       ← already exists
├── 004_1000_step_roadmap.md              ← already exists
├── 005_orientation.md                    ← already exists
├── 006_noetfield_os_strategy_v1.md       ← Brain's strategy output (consolidate here)
├── 007_build_order_phase1_exit.md        ← Phase 1 exit criteria and P0 build items
├── 008_tle_v1_schema.md                  ← TLE v1 output format (aligned to SourceA receipt)
└── PRODUCT_TRUTH.md                      ← live product state (phase, steps done, what's built)
```

**Law:** If information about Noetfield OS exists outside `docs/_NOOS_AGENT/` — move it in or delete it. No scattered docs. No two places for the same truth.

**MANIFEST.json must be updated every time a file is added.**

---

## PART 5 — CURRENT STATE (PHASE 1)

| Field | Value |
|-------|-------|
| Phase | 1 — Declare & baseline |
| Steps done | 0 / 1000 |
| Phase 1 exit | NOT MET |
| Runtime | FastAPI + SQLite + `.venv` |
| Port | `:8000` (local dev only — NOT the mono spine port) |
| DB | `noetfeld.db` — 2 audit rows |
| Decision endpoint | `POST /v1/decision` → score 49.69 → DECLINE |
| Audit portal | `GET /portal/audits` |

**What's built:**
- Policy JSON + loader
- Scoring + corridors
- SQLite audit trail
- FastAPI routes
- Agent vault (7 docs)
- 1000-step roadmap

**What's missing (gaps):**
- Postgres
- Tenant isolation
- API auth
- `/drift` endpoint
- `api.noetfield.com` deployment
- `rule_set_version` on every decision
- `request_id` + deterministic replay
- Board PDF export
- Paying pilot

---

## PART 6 — BUILD ORDER (WHAT TO BUILD AND WHEN)

**Design Partner Ready = 4 things. Not 1000 steps.**

A $2K–10K Design Partner needs to see:
1. `POST /v1/decision` → evaluates intent → APPROVE / REVIEW / DECLINE
2. TLE v1 output → signed, timestamped, audit_id, rule_set_version
3. Board PDF export → one page, decision + evidence trail
4. API key → they can test themselves before signing

**P0 — Phase 1 exit (weeks 1–2):**
| Item | Why |
|------|-----|
| `rule_set_version` + policy hash on every decision | Auditors ask "which policy?" |
| `request_id` + deterministic replay | "Prove same input → same outcome" |
| API key auth (one key is fine for first DP) | Can't demo without isolation story |
| `PRODUCT_TRUTH.md` updated | Phase 1 exit gate |

**P0 — Design Partner demo (weeks 3–4):**
| Item | Why |
|------|-----|
| Board-ready export (JSON + PDF from audit) | Boards buy proof, not dashboards |
| Credit / Copilot scenario policy pack | Vertical depth beats generic gate |
| Deploy to `api.noetfield.com` | Sandbox link in outreach email |

**P1 — After first DP signs (weeks 5–8):**
- Postgres migration
- Real tenant isolation
- `/drift` endpoint
- Multi-policy support

**P2 — After Trust Brief ($10K):**
- Full Copilot connector
- Compliance exports (SOC 2 evidence pack)
- Quarterly TLE export to Trust Ledger register
- Production-grade `api.noetfield.com`

**Do NOT build before first DP:**
- Multi-tenant architecture
- Full GRC suite
- LLM observability layer
- Custody or payment initiation (never)

---

## PART 7 — GTM STRATEGY (THREE TRACKS, PARALLEL)

**Track A — Revenue (30% energy)**
- Target: 1 Design Partner ($2K–10K) or Trust Brief ($10K)
- ICP: Canadian CU / lending fintech / enterprise with AI-in-production compliance pressure
- Motion: noetfield.com → 5-min demo → 6-week pilot SOW
- Win code: NW1 (first DP signed)

**Track B — Product (25% energy)**
- Target: GEL gate credible enough to demo in a compliance meeting
- Motion: `POST /v1/decision` + audit portal + policy version on every row
- Win code: working 5-min demo filmed

**Track C — Developer seeds (15% energy, plant now, harvest Phase 7)**
- Target: `api.noetfield.com` sandbox + API key + credit-decision example
- Motion: 3-line integration, compliance team buys later
- Win code: first external API key issued

**First money path:** NW1 Design Partner OR GEL Starter sandbox (~$10K) — whichever closes first. Do not wait for Postgres, drift, or full tenant isolation.

---

## PART 8 — ICP AND OFFER LADDER

**Primary buyer:** Regulated Decision Operator — 50–5,000 employees, Canada, board/compliance asking "show the log before the system acted."

| Persona | Cares about |
|---------|-------------|
| CRO / VP Risk | Audit defensibility |
| Platform engineer | API, isolation, determinism |
| AI governance lead | Policy versioning, drift |

**SKU ladder:**
| SKU | Price | What they get |
|-----|-------|---------------|
| GEL Starter | ~$10K | Sandbox, 1 policy pack, audit portal |
| GEL Standard | ~$50K | Multi-tenant, Postgres, SLA |
| GEL + Trust Ledger | ~$120K | Quarterly export, drift scoring, board pack |

**Anti-ICP (never sell to):**
- Crypto lending
- Full LOS in 30 days
- Custody or payment initiation
- "Build us ChatGPT"

---

## PART 9 — COMPETITIVE POSITION

**Own:** GEL for structured operational decisions in Canada — pre-execution, non-custodial, board-defensible.

**Moat:** Pre-execution + non-custodial + versioned policy + append-only audit + Canadian regulatory framing + Trust Ledger export path + SourceA engine underneath.

| Archetype | Learn | Don't become |
|-----------|-------|--------------|
| Exogram / Execlave | One API, three outcomes, fail-closed | Generic agent tool proxy |
| Credo / FairNow | Evidence packs boards buy | Full GRC suite |
| Fiddler / Holistic | In-VPC, FS depth, audit language | ML observability only |
| Galileo | Drift as differentiator | LLM eval platform |

---

## PART 10 — GOLDEN RULES (NON-NEGOTIABLE)

1. Non-custodial — never initiate payment or settlement
2. Pre-execution only — evaluate before the action, not after
3. Fail closed — uncertain = DECLINE, not APPROVE
4. Append-only audit — no deletes, no edits, ever
5. Version everything — every decision references a policy version hash
6. Tag all agent docs with NOOS-AGENT-DOC
7. Canada first — regulatory framing is Canadian
8. Evidence over dashboards — ship the log before the chart
9. GEL narrow scope — do not expand into LOS, payments, or agent proxy
10. ASF owns ecosystem structure — no registry changes without ASF

---

## PART 11 — ECOSYSTEM RULES

| Do | Don't |
|----|-------|
| Stay on separate port from `:8000` mono runtime | Merge into SinaaiRuntime |
| Export audit to Trust Ledger narrative | Become TrustField delivery |
| Read SourceA SSOT for DESIGN truth | Override SourceA SSOT from this repo |
| Ship narrow GEL API | Expand into full GRC or agent proxy |
| Use Noetfield vocabulary with customers | Use SourceA vocabulary (runs, SDK, replay) |

---

## PART 12 — SUCCESS METRICS (12 MONTHS)

| Metric | Target |
|--------|--------|
| Paying pilots | 3+ regulated orgs |
| Decisions logged | 100K+ with full audit trail |
| Replay determinism | 100% on regression suite |
| Time to board export | < 30 minutes from audit query |
| First NW1 | Design Partner signed |

---

## PART 13 — AGENT SESSION BOOT SEQUENCE

Every noetfield-os agent session must:

```
1. Read: SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md (parent)
2. Read: THIS FILE (NOETFIELD_OS_SSOT_v1_LOCKED.md)
3. Read: docs/_NOOS_AGENT/MANIFEST.json
4. Read: docs/_NOOS_AGENT/PRODUCT_TRUTH.md (current phase/state)
5. Confirm: active phase, steps done, what's built, what's next
6. Confirm: running on correct port (NOT :8000)
7. Report: ORIENTATION COMPLETE or list gaps
```

**Never start work without completing this boot sequence.**
**Never trust Hub or chat for product state — read PRODUCT_TRUTH.md on disk.**

---

## PART 14 — WHAT TO DO NEXT (IMMEDIATE)

**For the noetfield-os agent (Brain in noetfeld-os workspace):**

```
Immediate actions:
1. Create docs/_NOOS_AGENT/PRODUCT_TRUTH.md with current state
2. Copy this SSOT into docs/_NOOS_AGENT/NOETFIELD_OS_SSOT_v1_LOCKED.md
3. Update MANIFEST.json to include new files
4. Implement P0 items: rule_set_version + request_id + API auth
5. Report Phase 1 exit gate status
```

**For ASF:**
- Send NW1 outreach email (noetfield.com Design Partner link)
- Do NOT wait for Phase 1 exit before starting outreach

---

*NOETFIELD OS SSOT v1 LOCKED — 2026-06-15*
*Parent: SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md*
*Next version: when Phase 1 exits or first DP signs*
*All updates must be reflected in docs/_NOOS_AGENT/ copy within same session*
