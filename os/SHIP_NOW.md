# SHIP NOW — Noetfield

**Ship rule:** `os/plan.json` `next_tasks` — agent-owned (no ASF). Ingest required after VERIFY.

## Active queue (`next_tasks`)

**Shipped iter 8 (2026-06-06):** GTM_NEXT queue + QUICK_PICK fallback, staging demo www wire, security-buyer TLE copy.

**Prior iter 7:** registry pattern propagation + QUICK_PICK dedup, diligence procurement wire, design-partner BC AI channel.

**Prior iter 6:** registry sync + QUICK_PICK refresh, BC AI www wire, dual-brand boundary matrix.

**Prior:** iter 5 GTM ops wire, buyer debrief, tier-gate verify, BC AI outreach doc, incidents + SKILL-007.

**Queue:** Registry is fully synced — pick from [GTM_NEXT.md](docs/ops/plans/no-asf/GTM_NEXT.md) or `next_tasks` below. [QUICK_PICK.md](docs/ops/plans/no-asf/QUICK_PICK.md) inlines GTM_NEXT when registry backlog is empty.

## Shipped waves

| Wave | IDs | Highlights |
|------|-----|------------|
| 040–042 | Customer acquisition | design partner SOW, copilot hub, homepage CTA |
| 037–039 | GTM demo polish | buyer pack, workspace confidence UX, `make verify-gtm` |
| 034–036 | GTM Tier A | procurement zip, 5-min demo page, `make demo-url` |
| 023–033 | pilot → alembic | Trust Ledger product waves |
| **Locks** | GTM + sources book | `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md`, `docs/reference/GOVERNANCE_SOURCES_BOOK_v1.md` |

## Agent references

| Doc | Path |
|-----|------|
| Governance Sources Book | `docs/reference/GOVERNANCE_SOURCES_BOOK_v1.md` |
| Governance Drift Detection | `docs/reference/GOVERNANCE_DRIFT_DETECTION_SOURCES_v1.md` |
| GTM 60-day (CEO) | `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md` |

## Verify

```bash
make verify-gtm
```

Or step-by-step:

```bash
make verify-local-dev && make verify-ui-e2e && make copilot-pilot-e2e
```

```bash
make dev-local && make verify-local-dev && make tle-smoke && make copilot-pilot-e2e
pytest governance-console/backend/tests/test_tle_flow.py -q
cd governance-console/backend && alembic -c alembic.ini history
```

## NO ASF closeout

1. Pick from `os/plans/` or repopulate `next_tasks`.
2. `reports/cursor-reply-latest.txt` + ingest + sync + commit.
