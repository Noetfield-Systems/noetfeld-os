# WP-01 - Context Graph Specification, Runtime Edition v2

Document key: `wp01-context-graph-runtime-edition-v2`

Version: Runtime Edition v2, Execution Hardened

Status in source: Implementation-Ready

Consumers: Memory Agent, Planning Agent, Orchestration Kernel, Security Agent

## Normalized purpose

This document defines the Context Graph as the canonical execution state model
for Noetfield agents.

All agent reasoning must derive from graph snapshots, not directly from raw
external systems.

## Core model

The Context Graph is:

- directed
- typed
- attributed
- versioned
- partially materialized
- policy-governed
- event-sourced

Formal model:

```text
G_t = (V_t, E_t, A_V, A_E, T)
```

## Node system

Core node groups:

- Code: Service, Module, File, API
- Infrastructure: Database, Table, Job, Pipeline, Deployment, Environment
- Data: EventStream, Dataset
- Operations: Incident, Runbook
- Business: BusinessProcess
- Capital abstraction: CapitalObject, Rail, ExposureBucket
- Governance: Policy, ContextContract
- Runtime: Agent, HumanActor, SystemActor
- Regulatory: Jurisdiction

## Edge system

Canonical edge types:

- depends_on
- part_of
- calls
- reads_from
- writes_to
- flows_to
- deployed_to
- hosted_on
- triggers
- relates_to
- governed_by
- authorized_by
- implements
- flows_over
- settled_via
- within

## Runtime rules

- Queries execute only on snapshots.
- Cross-snapshot mixing is forbidden in execution paths.
- Diff operations are allowed only in Planning Agent flows.
- Invalid edges are rejected or stored as shadow edges.
- All queries are policy-checked before execution.
- No silent mutation: graph changes create new versions.

## Identity and temporal semantics

Canonical identity:

```text
canonical_id = hash(namespace + normalized_name + type)
```

Temporal dimensions:

- event_time
- observed_time
- valid_time

## Active-rule relevance

This appears to be the latest and most execution-hardened WP-01 version in the
uploaded batch. It supersedes the earlier Draft-1 and should be treated as the
active Context Graph source-of-truth for runtime semantics.

