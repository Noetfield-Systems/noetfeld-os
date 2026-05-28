# Phase 3 Runtime Activation

Phase 3 turns the v3.1 foundation into a live governed intelligence runtime.
Phase 3.1 narrows the work to backend durability and runtime integrity.

## Backend-first runtime capabilities

- Async event bus
- Publisher/subscriber dispatch
- Replayable events
- Dead-letter capture for subscriber failures
- PostgreSQL-backed event, trace, and dead-letter adapters
- Manual and webhook signal ingestion
- Live graph relationship mutation
- Relationship confidence evolution
- Temporal graph reflection cycles
- Governance policy evaluation
- Governance veto boundaries
- Human approval queue
- Deterministic workflow state machine
- Inspector execution loop
- Copilot Governance demo use-case layer

## PostgreSQL authority

PostgreSQL is the system of record for governance memory. Supabase may be used
as tooling around PostgreSQL, but it is not the governance authority.

Use:

```env
RUNTIME_EVENT_STORE=postgres
```

Use `memory` only for local tests and smoke validation.

## Runtime endpoints

Start the API:

```bash
make api
```

Key endpoints:

- `GET /health`
- `GET /events/catalog`
- `GET /events/replay?after_sequence=0&event_type=*`
- `POST /ingestion/manual`
- `POST /ingestion/webhook/{source_name}`
- `POST /graph/relationships/mutate`
- `POST /graph/reflections/run`
- `POST /workflows/start`
- `POST /workflows/transition`
- `POST /governance/execute`
- `GET /approvals`
- `POST /approvals/decide`
- `POST /inspectors/execute`
- `POST /use-cases/copilot-governance/demo`

## Deferred

- Realtime console UI
- RSS/news connectors
- Kubernetes
- microservice extraction
- autonomous swarms
- blockchain systems
