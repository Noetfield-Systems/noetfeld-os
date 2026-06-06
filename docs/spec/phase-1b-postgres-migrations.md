# Phase 1B — Postgres migrations (design + alembic skeleton)

**Status:** DESIGN — local dev may remain SQLite; staging uses Postgres via `DATABASE_URL`.  
**Related:** [phase-1b-activation-checklist.md](./phase-1b-activation-checklist.md)

## Tables (governance-console)

| Table | Purpose |
|-------|---------|
| `tenants` | Tenant isolation |
| `audit_logs` | Legacy audit (migrate → audit_events) |
| `audit_events` | Append-only tenant audit |
| `evidence_index` | M365 / manual evidence metadata |
| `connectors` | Connector registry + `oauth_json` |
| `tle_entries` | Trust Ledger v1 documents |

## Environment

```bash
# SQLite (default local)
DATABASE_URL=sqlite:///./governance-console/backend/noetfield.db

# Postgres (staging)
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/noetfield
```

Never commit production credentials. Use founder vault / Render env.

## Rollout order

1. `tenants` + pilot seed (`ensure_pilot_tenant`)
2. `audit_events` + one-time `migrate_audit_logs_to_events`
3. `evidence_index`, `connectors`, `tle_entries`
4. Require `X-Tenant-ID` on write APIs (already in dev)

## Alembic (skeleton)

From `governance-console/backend/`:

```bash
pip install alembic
export DATABASE_URL=sqlite:///./noetfield_dev.db
alembic -c alembic.ini upgrade head   # applies initial revision
alembic -c alembic.ini history
```

Initial revision uses SQLAlchemy `Base.metadata.create_all` for bootstrap parity with `db/bootstrap.py`. Production should move to explicit migrations per table before go-live.

## Verification

- Local: `make verify-local-dev` after `make dev-local`
- Staging: `make staging-smoke` with `NF_STAGING_URL`
