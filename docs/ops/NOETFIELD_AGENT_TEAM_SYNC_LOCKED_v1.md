# Noetfield agent team sync (LOCKED v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-BRIDGE-001` |
| **Merged** | `origin/cursor/bank-grade-fullstack-37f0` @ `f18925e` |
| **Updated** | 2026-06-06 |

Cloud-safe bridge. Full private canon: `ops/private/agent-reference/` (gitignored).

---

## Verify targets (repo truth)

| Target | Use |
|--------|-----|
| **`make ship-verify`** | Merge/deploy readiness — **cloud canonical** (superset) |
| **`make verify-gtm`** | Pre-demo GTM bundle — **Mac waves 034–042** |

These are **not aliases** — different scripts, different scope.

---

## In charge (summary)

| Tier | Governs |
|------|---------|
| L0 | `NORTH_STAR.md`, `PRODUCT_TRUTH.md`, `OFFERINGS_LOCKED.md`, `PROJECT_BOUNDARIES_LOCKED.md` |
| L1 | `NOETFIELD_GTM_60_DAY_LOCKED_v1.md`, `NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md` |
| L2 taxonomy | `GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md` |
| L2 product | `TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md` |
| L2 vision | `GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md` + four supplements (`NF-LOCAL-REPO-AGENT`) |
| L3 | `os/plan.json`, `QUICK_PICK.md`, agent context LOCKED |
| L4 private | `ops/private/agent-reference/` + `blueprints/` annex |

---

## Drift blueprints (merged f18925e)

| Role | Path | Tag |
|------|------|-----|
| Hub | `docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md` | `NF-LOCAL-REPO-AGENT` |
| Cloud read order | `docs/ops/NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md` | `NF-CLOUD-AGENT` |
| Code truth | `ops/private/.../NOETFIELD_DRIFT_IMPLEMENTATION_MAP.md` | `NF-CLOUD-AGENT` |

Canonical path: **`docs/references/`** (plural). Redirect: `docs/reference/README.md`.

---

## Shipped waves (local summary)

| Wave | Highlights |
|------|------------|
| 028–033 | M365 ingest, PDF v2, RBAC, staging-smoke |
| 034–036 | Procurement ZIP, demo page, `make demo-url` |
| 037–039 | Buyer pack, workspace UX, `make verify-gtm` |
| 040–042 | Design partner SOW, copilot hub, homepage CTA |

---

## Self-healing

```
CLAIM → VERIFY ON DISK → CORRECT → UPDATE REGISTRY → LOG INTAKE
```

| Agent | After ship |
|-------|------------|
| **Local (Mac)** | `make verify-gtm` or `make ship-verify` · ingest · update private LOCKED_PLANS |
| **Cloud** | `make ship-verify` on PR · `founder_ingest_required: true` in TEAM_STATE |

**Tags:** `NF-CLOUD-AGENT` (cloud) · `NF-LOCAL-REPO-AGENT` (local blueprints) · grep before merge.

---

## P0 drift code (agreed)

- Drift Contract v0
- Evaluate vs last TLE diff
- `risk_summary` + drift class in `confidence_factors`

---

## Systems Operating Plan (Lane B — private L4)

Local ingested Desktop SOURCE. Cloud verified read-order; **do not duplicate L0–L3 prose**.

| Order | Private path (when `ops/private/` on disk) |
|-------|-------------------------------------------|
| 1 | `agent-reference/plans/SYSTEMS_OPERATING_PLAN_ANALYSIS_LOCKED_2026.md` |
| 2 | `agent-reference/plans/SYSTEMS_OPERATING_PLAN_LOCKED_2026.md` |
| 3 | `intake/systems-operating-plan-desktop-2026-06-06/SOURCE.md` — detail only |

**NKUE (local):** kept 6 · merged 4 · split 2 · deferred 4 · rejected 3  
**TrustField Phase 8:** `TRUSTFIELD_OPERATING_EXCERPT_POINTER.md` — separate entity  
**Verified sources (private):** `SOURCES_VERIFIED_OPERATING_PLAN_2026.md` — StatCan · CMHC · Vancouver · www (6 URLs checked)  
**Live 8-phase mirror:** https://www.noetfield.com/ai-automation/ (`ai-automation/index.html`)  
**Verdict:** two engines (Lane A product + Lane B Vancouver services), one discipline (RID + metrics + governance artifact per engagement).

---

| v1.2 | 2026-06-06 | NF-CLOUD-AGENT Systems Operating Plan read-order |
