# Intake persistence — backup and retention (NF-ENG-10)

## System of record

When `INTAKE_PERSISTENCE=auto` and PostgreSQL runtime is available, public intakes are stored in **`public_intakes`** (migration `infrastructure/supabase/migrations/0005_public_ecosystem_platform.sql`).

## Backup (production)

| Item | Recommendation |
|------|----------------|
| **Frequency** | Daily automated backup of PostgreSQL (managed provider snapshot or `pg_dump`) |
| **Retention** | Minimum 90 days for sales/audit; align with customer contracts |
| **Scope** | Include `public_intakes` and governance event tables |
| **Restore test** | Quarterly restore drill to staging |

## Retention and deletion

| Data | Policy |
|------|--------|
| Intake rows | Retain while engagement active + 24 months unless legal hold |
| PII minimization | Public form is non-confidential by design; no credentials in `message` |
| Export | Ops: `GET /api/intake/recent` with `X-Admin-Secret` |
| Erasure | Process GDPR/PIPEDA requests via ops; delete by `intake_id` in Postgres |

## Fallback mode

If Postgres is unavailable, intake may fall back to in-memory store (non-durable). **Production must use Postgres** for launch.

## Related

- [RUNBOOK.md](./RUNBOOK.md) · [PRACTICAL_PLAYBOOK.md](./PRACTICAL_PLAYBOOK.md)
