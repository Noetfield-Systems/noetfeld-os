# Architecture Verdict — Postgres-First (Persian)

Document key: `noetfield-architecture-verdict-postgres-first-fa`

Reference analysis (FA): Postgres-first + pgvector inside PG aligns with Stripe/Temporal-style
single source of truth. Timescale must remain extension-only, not split truth path.
