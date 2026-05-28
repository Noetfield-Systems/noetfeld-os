# Developer Bootstrap

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker
- Make

## Local environment

Copy the environment template:

```bash
cp .env.example .env
```

Start local PostgreSQL and supporting services:

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

Install Python and frontend dependencies:

```bash
make bootstrap
```

Run backend API:

```bash
make api
```

## Phase 3.1 backend core

Phase 3.1 prioritizes backend durability and runtime integrity. PostgreSQL is
the system of record. Supabase is optional tooling only.

Use `RUNTIME_EVENT_STORE=postgres` for operational runtime. Use `memory` only
for test smoke flows that do not require a database.

See:

- [PHASE_3_1_GOALS.md](PHASE_3_1_GOALS.md)
- [PHASE_3_RUNTIME_ACTIVATION.md](PHASE_3_RUNTIME_ACTIVATION.md)

## Optional app shells

The Next.js app shells remain available, but live console UI work is deferred
until backend runtime stability is proven.

```bash
npm run dev:web
npm run dev:platform
npm run dev:admin
```

## Validation

```bash
make validate
```

## Governance development rules

- Do not add silent autonomous execution.
- Emit canonical governance events for consequential actions.
- Preserve raw signals and governance events as append-only records.
- Treat AI outputs as governed artifacts with citations, confidence, and review
  state.
- Add tenant boundaries to new data models from the beginning.
- Use confidence thresholds and human approval queues for consequential runtime
  actions.
