# WP-01 - Context Graph Specification, Hardened Edition

Document key: `wp01-context-graph-hardened-2026-05-hardening-1`

Version: `2026-05-Hardening-1`

Status in source: Implementation-Ready

Consumers: Memory Agent, Planning Agent, Orchestration Kernel, Security Agent,
Policy Engine

## Normalized purpose

This document hardens the Context Graph into a distributed, multi-agent,
regulated runtime contract.

It adds runtime-critical components to the original graph specification:

- Graph State Model
- Identity Resolution Layer
- Temporal Semantics
- Ingestion Normalization Pipeline
- Graph Compute Primitives
- Policy Evaluation Binding Layer

## Important additions

State layers:

- Live Graph
- Historical Graph
- Staging Layer
- Shadow Graph

Write pipeline:

1. Agent proposes mutation.
2. Mutation enters staging.
3. NPL policies evaluate.
4. Execution Token is issued.
5. Mutation commits to live graph.
6. Historical version is archived.

Conflict priority:

1. Manual override
2. Runtime telemetry
3. Static analysis
4. Import sources

## Registry classification

This is a strong implementation source, but the batch also includes a later
Runtime Edition v2. Keep this as supporting source material and provenance.

