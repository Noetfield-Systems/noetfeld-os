# Noetfield Services

The v3.1 backend is a modular monolith with explicit service boundaries.

Current service boundaries:

- `identity`: SSO, RBAC, ABAC, tenant membership, and access decisions.
- `events`: canonical event contracts and Phase 3 async event bus runtime.
- `ledger`: append-only Trust Ledger boundary.
- `signals`: raw signal ingestion pipeline.
- `graph`: living knowledge graph inference, mutation, confidence evolution,
  and temporal reflection cycles.
- `governance`: FastAPI entrypoint, policy evaluation, veto boundaries, and
  human approval runtime.
- `workflow`: Temporal-ready workflow orchestration boundary.
- `ai-runtime`: governed model provider abstraction.
- `inspectors`: bounded ambient inspector framework and collaboration runtime.

The boundary structure is designed for future extraction, but services should
remain deployable together until operational scale requires separation.
