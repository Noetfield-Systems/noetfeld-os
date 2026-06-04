# SHIP NOW — Noetfield

**Ship rule:** `os/plan.json` `next_tasks` — agent-owned (no ASF). Ingest required after VERIFY.

## Active queue (`next_tasks`)

Empty — Wave 028–033 shipped. Pick next work from `os/plans/REGISTRY.json` (T0→T1) or founder order.

## Shipped waves

| Wave | IDs | Highlights |
|------|-----|------------|
| 023–027 | pilot, PDF, OAuth mock, RBAC, staging doc | Next Wave |
| 028–033 | M365 E2E ingest, PDF v2, chain RBAC, KMS export, staging make, alembic | Latest |

## Verify

```bash
make dev-local && make verify-local-dev && make tle-smoke && make copilot-pilot-e2e
pytest governance-console/backend/tests/test_tle_flow.py -q
cd governance-console/backend && alembic -c alembic.ini history
```

## NO ASF closeout

1. Pick from `os/plans/` or repopulate `next_tasks`.
2. `reports/cursor-reply-latest.txt` + ingest + sync + commit.
