# Noetfield Execution Kernel v1.0 — Temporal Canonical

Document key: `noetfield-execution-kernel-temporal-v1-canonical`

Canonical execution kernel: deterministic structure, probabilistic cognition, fully replayable governance.

## Core principle

All intelligence is probabilistic. All truth is event-sourced. LLMs never mutate state — only propose transitions;
kernel commits, rejects, or compensates.

## Three layers

1. LLM probabilistic layer (proposal engine)
2. Arbitration + governance (policy, validator, decision gate)
3. Event-sourced state kernel (append-only log, replay, temporal DAG)

## State model

`STATE(t) = REDUCE(EVENT_LOG[0..t])` — state is derived, not persisted as authoritative truth.

## Node types

LLM_NODE, TOOL_NODE, POLICY_NODE, SAGA_NODE, MERGE_NODE → COMMIT_EVENT

## LLM arbitration

Outputs: COMMIT | REJECT | ESCALATE_TO_FRONTIER | COMPENSATE | REQUEST_CLARIFICATION.
Policy engine is pure functions — no LLM in policy gate.

## Replay

Exact replay: cached LLM tokens, not regenerated. Semantic replay for debugging only.

## Semantic integrity

Raw events only as truth; no LLM regeneration on replay; embedding versioning required.

## MVP phases

P1: event log + graph executor | P2: policy + saga | P3: LLM arbitration + cache replay | P4: drift + audit export
