# PostgreSQL operations (Wave 3)

**Scope:** Production platform (`RUNTIME_EVENT_STORE=postgres`) — governance events, public intakes, audit store.

---

## Backup

| Item | Recommendation |
|------|----------------|
| Frequency | Daily automated snapshot or `pg_dump` |
| Retention | 90 days minimum (align with contracts) |
| Tables | `public_intakes`, governance/audit tables, migrations schema |
| Drill | Quarterly restore to [staging](./STAGING.md) |

```bash
pg_dump "$DATABASE_URL" -Fc -f "noetfield-$(date +%Y%m%d).dump"
```

---

## Migrations

```bash
make platform-migrate
# or
PYTHONPATH=packages/types:packages/config:packages/sdk:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance \
  python3 scripts/apply_postgres_migrations.py
```

---

## Pilot auth and rate limits

| Setting | Purpose |
|---------|---------|
| `GOVERNANCE_PILOT_AUTH_REQUIRED` | Require API key on `/api/v1/governance/*` |
| `GOVERNANCE_PILOT_API_KEYS` | `tenant-uuid:secret` or `secret` comma-separated |
| `GOVERNANCE_PILOT_RATE_LIMIT_PER_MIN` | Per-key evaluate/ledger/export cap (default 120) |
| `REDIS_URL` | Enables distributed rate limits when set |

---

## Intake retention

See [INTAKE_BACKUP_RETENTION.md](./INTAKE_BACKUP_RETENTION.md).

---

## Related

[GOVERNANCE_PILOT_RUNBOOK.md](./GOVERNANCE_PILOT_RUNBOOK.md) · [RUNBOOK.md](./RUNBOOK.md) · [GO_LIVE.md](./GO_LIVE.md)
