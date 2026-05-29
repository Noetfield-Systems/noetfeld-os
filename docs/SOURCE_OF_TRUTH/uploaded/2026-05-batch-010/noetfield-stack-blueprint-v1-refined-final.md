# Noetfield Stack Blueprint v1 — Refined Final

Document key: `noetfield-stack-blueprint-v1-refined-final`

**Active execution-kernel architecture SOT.**

PostgreSQL is the only system of truth. All other stores are projection, optimization,
cache, or derived intelligence layers.

## Layer roles

| Layer | Role | Technology |
| Truth | immutable facts | PostgreSQL |
| Temporal opt | partitioning (extension only) | TimescaleDB in PG |
| Semantic | advisory similarity | pgvector in PG |
| Execution | state machine | LangGraph (checkpoints in PG) |
| Ephemeral | speed, locks | Redis |
| Archive | cold artifacts | S3 |

## Production rules

1. Postgres only source of truth
2. Every action emits an event
3. No probabilistic system mutates state directly
4. Replay from ledger + snapshots
5. Semantic advisory only
6. Timescale must not be a parallel logical model

## MVP minimum

PostgreSQL + Redis + S3 (Kafka/vector external DB deferred).
