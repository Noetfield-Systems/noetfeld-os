# Noetfield Services

The v3.1 backend is a modular monolith with explicit service boundaries.

Current service boundaries:

- `identity`: SSO, RBAC, ABAC, tenant membership, and access decisions.
- `events`: canonical event contracts, async event bus, PostgreSQL event store,
  tracing store, replay, and dead-letter persistence.
- `ledger`: append-only Trust Ledger boundary and audit ledger runtime.
- `signals`: manual/webhook signal ingestion pipeline and PostgreSQL raw signal
  store.
- `graph`: living knowledge graph inference, mutation, confidence evolution,
  temporal reflection cycles, and PostgreSQL graph store.
- `governance`: FastAPI entrypoint, policy evaluation, veto boundaries, and
  human approval runtime.
- `workflow`: deterministic workflow state machine with durable workflow
  instances and history.
- `ai-runtime`: governed model provider abstraction.
- `inspectors`: bounded ambient inspector framework, collaboration runtime, and
  inspector execution loop.
- `copilot-governance`: first use-case module built on top of the core runtime.

PostgreSQL is the governance system of record. Supabase is optional tooling
around the database and must not be treated as the authority layer.
