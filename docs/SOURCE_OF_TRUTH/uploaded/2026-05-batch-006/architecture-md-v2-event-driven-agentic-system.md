# ARCHITECTURE.md v2.0 — Event-Driven Agentic System

Document key: `architecture-md-v2-event-driven-agentic-system`

## System law

**No action occurs without an event. No state changes without traceability.**

## Paradigm

Event → Plan → Execute → Transition → Persist

## Canonical event schema

`event_id`, `event_type`, `timestamp`, `source`, `context_id`, `payload`, `state_before`, `state_after`, `retry_count`

## HALT protocol

Max retry per task: **2**. On `RETRY_LIMIT_REACHED_EVENT`: stop autonomous execution, emit diagnostics, return to human layer.

## Memory

Event-sourced only. No memory write without `STATE_VALIDATION_EVENT`.

## Registry

**Active bank-grade event architecture reference** aligned with Noetfield Phase 3 runtime posture.
