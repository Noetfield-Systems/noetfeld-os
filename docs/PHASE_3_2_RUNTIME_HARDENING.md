# Phase 3.2 Runtime Hardening

Phase 3.2 closes the first backend durability gaps after Phase 3.1.

## Completed hardening goals

- Durable approval queue store for PostgreSQL.
- Durable graph reflection cycle store for PostgreSQL.
- Durable Copilot Governance demo run store.
- Durable dead-letter hydration from PostgreSQL rows.
- PostgreSQL migration runner.
- Backend smoke harness for memory and PostgreSQL modes.

## Commands

Run fast in-memory smoke validation:

```bash
make phase32-smoke
```

Apply migrations to PostgreSQL:

```bash
make apply-migrations
```

Run PostgreSQL-backed backend smoke validation:

```bash
make phase32-postgres-smoke
```

## PostgreSQL smoke coverage

The Phase 3.2 smoke harness exercises:

- event persistence and replay
- audit-ledger subscription
- manual signal ingestion
- graph relationship mutation
- graph reflection persistence
- workflow state transition
- governance approval queueing
- inspector execution-loop persistence
- Copilot Governance use-case run persistence
- dead-letter store hydration path

## Remaining hardening work

- Add automated test containers in CI.
- Add dead-letter replay/resolution commands.
- Add richer policy pack validation.
- Add exportable audit package generation.
