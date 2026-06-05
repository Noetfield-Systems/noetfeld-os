# SHIP NOW — Noetfield

**Ship rule:** `os/plan.json` `next_tasks` — agent-owned (no ASF). Ingest required after VERIFY.

## Active queue (`next_tasks`)

Empty — Wave 028–033 shipped. Pick next work from `os/plans/REGISTRY.json` (T0→T1) or founder order.

## Shipped waves

| Wave | IDs | Highlights |
|------|-----|------------|
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
