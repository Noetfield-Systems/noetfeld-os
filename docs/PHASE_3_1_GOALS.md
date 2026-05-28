# Phase 3.1 Goals: Backend Durability and Runtime Integrity

Phase 3.1 is backend-only. Its purpose is to stabilize Noetfield's operational
cognition before investing in live console UI polish.

## Binding priorities

- PostgreSQL is the system of record.
- Supabase is optional tooling, not governance authority.
- Runtime integrity comes before frontend experience.
- Webhook and manual ingestion come first.
- RSS/news connectors are deferred.
- Copilot Governance is the first demo module, but it remains a use-case layer.
- The platform foundation remains event-centric, workflow-first, and
  audit-centric.

## Goal 1: Durable Runtime Persistence

Persist operational memory in PostgreSQL-backed runtime stores:

- governance events
- event traces
- dead-letter records
- raw/manual/webhook signals
- graph relationship mutations
- relationship confidence evolution
- workflow state transitions
- inspector execution runs
- audit ledger records

## Goal 2: Event Bus Integrity

The event bus must support:

- typed event contracts
- append-only publish flow
- replay from PostgreSQL
- dead-letter capture
- subscriber dispatch isolation
- tracing metadata
- local in-memory mode for tests only

## Goal 3: Webhook and Manual Ingestion

Implement only:

- generic webhook ingestion
- manual JSON signal ingestion
- payload hashing
- provenance capture
- governance event emission

RSS/news connectors are explicitly deferred.

## Goal 4: Durable Graph Mutation Engine

Persist graph runtime behavior:

- relationship upserts
- confidence changes
- evidence links
- temporal reflection summaries
- low-confidence detection

## Goal 5: Audit Ledger Runtime

Every consequential runtime action must be:

- attributable
- timestamped
- traceable
- replayable
- exportable later

The audit ledger runtime should write append-only audit records and preserve
event integrity boundaries.

## Goal 6: Workflow State Machine

Implement a backend workflow state machine for governed runtime execution:

- deterministic state transitions
- transition validation
- workflow history
- approval/waiting states
- terminal states
- event emission

## Goal 7: Inspector Execution Loop

Inspectors should run through a bounded execution loop:

- objective input
- inspector selection
- execution state
- findings persistence
- confidence thresholds
- human review boundary
- audit events

This is not an autonomous swarm.

## Goal 8: Copilot Governance Demo Module

Build Copilot Governance on top of the core runtime as the first use case:

1. A Copilot governance signal is manually or webhook-ingested.
2. Graph relationships mutate from the signal.
3. Confidence evolves.
4. Reflection runs.
5. Governance workflow requires approval.
6. Audit trail is replayable.

The Copilot module must not become the platform foundation.

## Deferred

- Realtime console UI
- RSS/news connectors
- Kubernetes
- microservice extraction
- autonomous agent swarms
- blockchain systems
