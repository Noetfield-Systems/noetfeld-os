# Drift blueprints — cloud read order (LOCKED v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-DRIFT-READ-001` |
| **Not** | `NF-LOCAL-REPO-AGENT` · `noetfield_local` |
| **Updated** | 2026-06-06 |

**Prerequisite:** Local agent blueprints on `docs/references/` — merge branch `cursor/bank-grade-fullstack-37f0` after local **push** (commit `fef0126+`). Verify: `test -f docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md`

---

## Authority split (do not mix)

| Topic | In charge | Agent tag |
|-------|-----------|-----------|
| Drift **taxonomy** | [GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md) | ASF / existing LOCKED |
| Product **mandate** | [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) | ASF / existing LOCKED |
| Architecture **vision** | [GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md) | `NF-LOCAL-REPO-AGENT` |
| **Code truth** | `ops/private/agent-reference/NOETFIELD_DRIFT_IMPLEMENTATION_MAP.md` | `NF-CLOUD-AGENT` (private) |

Cloud agents **wire read order only** — do not overwrite `NF-LOCAL-REPO-AGENT` private annexes without UKE intake.

---

## Read order (cloud — every drift session)

1. [GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md) — taxonomy (boss)
2. [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) — product mandate
3. [GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md) — hub / router
4. Supplements (index order):
   - [GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_ENGINE_BLUEPRINT_LOCKED_v1.md)
   - [TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md](../references/TRUST_LEDGER_FOR_DRIFT_BLUEPRINT_LOCKED_v1.md)
   - [LLM_DRIFT_DETECTION_ARCHITECTURE_LOCKED_v1.md](../references/LLM_DRIFT_DETECTION_ARCHITECTURE_LOCKED_v1.md)
   - [ENTERPRISE_GOVERNANCE_DRIFT_FRAMEWORK_LOCKED_v1.md](../references/ENTERPRISE_GOVERNANCE_DRIFT_FRAMEWORK_LOCKED_v1.md)
5. [NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md](./NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md) — team + repo truth
6. Private (if on disk): `ops/private/agent-reference/blueprints/` — implementation annex (`NF-LOCAL-REPO-AGENT` only)

---

## GTM honesty (one line — all drift docs)

> Noetfield records **governance drift decisions** before external execution — against your signed Trust Ledger baseline, exported as audit evidence. Continuous ML/LLM monitoring stays in **your environment** or **Trust Brief** scope.

---

## Shipped vs roadmap (repo truth — cloud verified)

| Capability | Status |
|------------|--------|
| TLE immutability, evidence hash, confidence factors | **Shipped** |
| `GET /events/replay` | **Shipped** |
| TLE hash chain (`prev_tle_digest`) | **Roadmap** (TLE v1.3) |
| Evaluate vs last TLE diff | **P0 roadmap** |
| Drift Contract v0 on API | **P0 roadmap** |
| `risk_summary` + drift class in factors | **P0 roadmap** |
| Observability middleware → tables | **P1 roadmap** |

**Verify gate:** `make ship-verify`

---

## P0 ship queue (agreed local + cloud)

| Priority | Work |
|----------|------|
| P0 | Drift Contract v0 on evaluate/TLE paths |
| P0 | Evaluate vs last TLE diff helper |
| P0 | `risk_summary` + drift class in `confidence_factors` |

---

| v1 | 2026-06-06 | NF-CLOUD-AGENT read-order pass |
