# Noetfield Execution Kernel — Full Stack Blueprint v1.0

Document key: `noetfield-execution-kernel-full-stack-blueprint-v1`

Postgres-centered deterministic kernel: immutable events, LLM advisory-only,
policy-governed execution, full replay.

## Stack (initial draft)

PostgreSQL (truth), pgvector (semantic advisory), Timescale (extension-only optimization),
Redis (ephemeral), S3 (archive), LangGraph (runtime).

## Pipeline

Input → LLM proposal → schema gate → policy → risk (advisory) → LangGraph → PG commit → snapshot → S3.

**Superseded by** `noetfield-stack-blueprint-v1-refined-final` for canonical architecture SOT.
