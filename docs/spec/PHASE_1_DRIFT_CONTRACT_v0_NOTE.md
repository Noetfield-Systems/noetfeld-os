---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-10"
doc_id: phase-1-drift-contract-v0-note
---

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-06-10

# Phase 1 — Drift Contract v0 (shipped note)

Phase `phase-1-tle-core` T0 ships **Drift Contract v0** on the Noetfield Trust Ledger path.

## Shipped surfaces

| Surface | Fields |
|---------|--------|
| `POST /tle/draft` | `drift_class`, `baseline_tle_id`, `delta_summary`, `severity` |
| `POST /tle/diff/evaluate` | diff helper vs last TLE + `delta_summary`, `severity` |
| `POST /evaluate` | `risk_summary`, `confidence_factors` |
| `GET /tle/{id}/export` | `drift_contract`, `audit_digest_link`, `signature_block.digest_version=v2` |
| Workspace UI | drift badge when `drift_class` present and not `initial` |

## P0 blueprint alignment

See [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](./TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) §8.

| P0 item | Status |
|---------|--------|
| Drift Contract v0 fields | Shipped |
| Evaluate vs last TLE diff | Shipped (`POST /tle/diff/evaluate`) |
| `risk_summary` in confidence factors | Shipped on evaluate |
| `delta_summary`, `severity` on export | Shipped |

**Deferred:** `prev_tle_digest` (P1), event replay narrative (P2).

### TLE v1 field map (nf-0116)

| Blueprint field | Shipped | Surface |
|-----------------|---------|---------|
| `drift_class` | Yes | draft, export |
| `baseline_tle_id` | Yes | draft, diff |
| `delta_summary` | Yes | draft, export |
| `severity` | Yes | draft, export |
| `prev_tle_digest` | No | P1 defer |


Noetfield records governance drift **decisions** against signed TLE baseline — not a hosted ML observability platform.
