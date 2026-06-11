# Drift blueprints — cloud read order (LOCKED v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-DRIFT-READ-001` |
| **Not** | `NF-LOCAL-REPO-AGENT` · `noetfield_local` |
| **Merged** | `origin/cursor/bank-grade-fullstack-37f0` @ `f18925e` |
| **Updated** | 2026-06-06 |

Blueprint bodies: `[NF-LOCAL-REPO-AGENT]` on `docs/references/`. Cloud wires read order only.

---

## Authority split

| Topic | In charge | Tag |
|-------|-----------|-----|
| Drift taxonomy | [GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md) | LOCKED v1 (canonical) |
| Product mandate | [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) | LOCKED (cloud ff24d56 + local §8) |
| Architecture vision | [GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md) | `NF-LOCAL-REPO-AGENT` |
| Code truth | `ops/private/agent-reference/NOETFIELD_DRIFT_IMPLEMENTATION_MAP.md` | `NF-CLOUD-AGENT` (private) |

---

## Read order

1. [GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md) — taxonomy boss
2. [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) — product mandate
3. [GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md) — hub
4. Supplements: engine → TLE-for-drift → LLM → enterprise framework
5. [NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md](./NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md)
6. Private annex: `ops/private/agent-reference/blueprints/` (`NF-LOCAL-REPO-AGENT` only)

---

## GTM honesty

> Noetfield records governance drift decisions before external execution — against your signed Trust Ledger baseline, exported as audit evidence. Continuous ML/LLM monitoring stays in your environment or Trust Brief scope.

---

## Shipped vs roadmap (cloud verified)

| Capability | Status |
|------------|--------|
| TLE immutability, evidence hash, confidence factors | Shipped |
| `GET /events/replay` | Shipped |
| TLE hash chain (`prev_tle_digest`) | Roadmap (TLE v1.3) |
| Evaluate vs last TLE diff | **P0** |
| Drift Contract v0 | **P0** |
| `risk_summary` + drift class in factors | **P0** |

**Verify:** `make ship-verify` (merge readiness) · `make verify-gtm` (pre-demo GTM bundle)

---

| v1.1 | 2026-06-06 | NF-CLOUD-AGENT post-merge f18925e |
