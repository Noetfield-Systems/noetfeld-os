---
id: governance-drift-blueprints-index
status: locked
version: 2
locked_at: 2026-06-06
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
agent_alias: nf-local-agent
---

# Governance Drift Blueprints — Index (LOCKED v1.2)

**Status:** LOCKED — L2 **design supplements** (not product mandate)  
**Canonical path:** `docs/references/` (plural) — committed for GitHub + Cursor Cloud  
**Processor:** `[NF-LOCAL-REPO-AGENT]` · Cloud review: `[NF-CLOUD-AGENT]`  
**Private annexes:** `ops/private/agent-reference/blueprints/` (gitignored)

---

## Router — read in this order

| Step | Document | Tier | Role |
|------|----------|------|------|
| 1 | [GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md](./GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md) | **L2 boss** | Taxonomy, primary citations, Noetfield mapping §F |
| 2 | [../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) | **L2 product** | Product mandate — evaluate → TLE → audit-export |
| 3 | **This index** | L2 vision | Architecture supplements below |
| 4a | [GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md](./GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md) | L2 supplement | Trust Brief / board narrative — temporal loop |
| 4b | [TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md](./TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md) | L2 supplement | **TLE v1.3 extension spec** — not a second ledger |
| 4c | [LLM_DRIFT_DETECTION_ARCHITECTURE_LOCKED_v1.md](./LLM_DRIFT_DETECTION_ARCHITECTURE_LOCKED_v1.md) | L2 supplement | Copilot/RAG buyer appendix — cite and record |
| 4d | [ENTERPRISE_GOVERNANCE_DRIFT_FRAMEWORK_LOCKED_v1.md](./ENTERPRISE_GOVERNANCE_DRIFT_FRAMEWORK_LOCKED_v1.md) | L2 supplement | GTM honesty — roles, cadence, compliance |
| 5 | Cloud read order | L3 ops | [../ops/NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md](../ops/NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md) |
| 6 | Code truth (private) | L4 | `ops/private/agent-reference/NOETFIELD_DRIFT_IMPLEMENTATION_MAP.md` |

**Rule:** Blueprints **cite and defer** to steps 1–2. They do **not** replace drift sources or TLE product mandate.

---

## GTM honesty line (use everywhere)

> Noetfield records **governance drift decisions before external execution**—detected against your signed Trust Ledger baseline, exported as audit evidence. Continuous ML/LLM monitoring remains your environment or Trust Brief scope; **we do not host your models**.

---

## Product kernel (what we ship vs surround)

| Kernel (Lane A — shipped) | Enterprise surround (blueprints — partial / roadmap) |
|---------------------------|--------------------------------------------------------|
| evaluate → TLE → audit-export | 8-layer runtime platform |
| `signature_hash` + `audit_digest` on approval | Full hash chain between TLE entries (P1: `prev_tle_digest`) |
| `compute_confidence_score()` + factors | `drift_class` + `risk_summary` in factors (P0) |
| `GET /events/replay` (event bus) | TLE replay narrative in audit-export (P2) |
| Evidence hash + immutability after approve | Second “drift DB” — **rejected**; one ledger |

**Core insight:** Noetfield wedge = **pre-execution governance drift** (policy intent, approval state, evidence lineage vs last signed TLE/RID). Blueprints describe the enterprise surround; the product kernel is still **evaluate → TLE → audit-export**.

---

## Blueprint library

| # | Doc | Buyer value |
|---|-----|-------------|
| 1 | Governance Drift Engine | Trajectory + response story: drift → RID → TLE → export |
| 2 | Trust Ledger for Drift | Drift terminates in TLE — extension spec, not parallel ledger |
| 3 | LLM Drift | Trust Brief methodology — shadow-evaluate, rate-limit, record RID |
| 4 | Enterprise Framework | Roles, cadence, compliance mapping without running customer MLOps |

---

## Shipped vs roadmap (code-verified)

| Capability | Shipped | Roadmap |
|------------|---------|---------|
| TLE immutability after approve | Yes (DB trigger / service) | — |
| `signature_hash` + evidence hash | Yes (`tle_service.py`) | — |
| Evaluate vs last TLE diff | Yes (`POST /tle/diff/evaluate`) | Drift Contract v0 extensions |
| `prev_hash` TLE chain | **No** (PLATFORM_BLUEPRINT mention only) | P1 `prev_tle_digest` migration |
| Event replay | Yes (`GET /events/replay`) | Link to audit-export narrative |
| Observability middleware → tables | **No** (schema may exist) | P1 wire NF-0104 |
| PSI / embedding monitors | **No** | Customer env + Trust Brief |

**Code truth authority:** `[NF-CLOUD-AGENT]` maintains `NOETFIELD_DRIFT_IMPLEMENTATION_MAP.md` after verify.

---

## Agent tags

| Tag | Agent |
|-----|-------|
| `[NF-LOCAL-REPO-AGENT]` / `nf-local-agent` | Local Mac repo chat (alias registered) |
| `[NF-CLOUD-AGENT]` | Cloud VM — read-order + path fixes only; no annex overwrite |

Spec: `ops/private/agent-reference/NOETFIELD_AGENT_TAGGING_LOCKED.md`

---

## Authority registry rows (single owner per topic)

| Topic | In charge |
|-------|-----------|
| Taxonomy | `GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md` |
| Product mandate | `TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md` |
| Architecture vision | This index + docs 1–4 |
| Code truth | `NOETFIELD_DRIFT_IMPLEMENTATION_MAP.md` |
