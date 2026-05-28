# Phase 3 Runtime Activation

Phase 3 turns the v3.1 foundation into a live governed intelligence runtime.
It remains a modular monolith and avoids premature microservices, Kubernetes,
blockchain, or autonomous swarm complexity.

## Runtime capabilities

- Async in-process event bus
- Publisher/subscriber dispatch
- Replayable retained events
- Dead-letter capture for subscriber failures
- Signal ingestion with raw payload hashing
- Live graph relationship mutation
- Relationship confidence evolution
- Temporal graph reflection cycles
- Governance policy evaluation
- Governance veto boundaries
- Human approval queue
- Inspector collaboration runtime
- Realtime operational console API

## Runtime endpoints

Start the API:

```bash
make api
```

Key endpoints:

- `GET /health`
- `GET /events/catalog`
- `GET /events/replay?after_sequence=0&event_type=*`
- `POST /signals/ingest`
- `POST /graph/relationships/mutate`
- `POST /graph/reflections/run`
- `POST /governance/execute`
- `GET /approvals`
- `POST /approvals/decide`
- `POST /inspectors/collaborate`
- `GET /runtime/console`

## Governance guarantees

Phase 3 preserves the platform rules:

- Events are typed and versioned.
- Runtime events are replayable.
- Failed subscriber execution is dead-lettered.
- Confidence thresholds can force human review.
- Governance boundaries can veto execution.
- Consequential runtime actions emit audit events.
- Inspectors coordinate through bounded collaboration, not uncontrolled
  autonomy.

## Current durability posture

The runtime bus and stores are in-process for the first activation step. The
database migrations define durable projections for event traces, dead letters,
graph reflections, approval queues, and the existing append-only governance
ledger. Future adapters should persist through those tables without changing
the runtime contracts.

## Operational console

Backend console:

```bash
curl http://localhost:8000/runtime/console
```

Frontend shell:

```bash
npm run dev:platform
```

Then open `/console` in the platform app.
