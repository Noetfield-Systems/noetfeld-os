# Noetfield v2.0 — Temporal Governance OS (Bank-Grade)

Document key: `noetfield-v2-temporal-governance-os-bank-grade`

**Active v2 product architecture SOT** (distinct from v3.1 ambient intelligence nervous system).

Time-first: every change is an immutable event; state reconstructed via replay + snapshots.

## Logical layers

Input → Event Core → State Reconstruction → Evidence Snapshots → Drift Trajectory →
Temporal Conflict → Temporal Risk → Decision Agents → Audit/Replay → Human Gatekeeper

## Core APIs

POST /events | GET /state?time=T | GET /diff | GET /drift | POST /replay |
POST /evidence-pack | POST /agent/action-request

## Safety (non-negotiable)

No autonomous production execution. HSM-signed immutable evidence. Least-privilege agents.
Separation of duties. Fork governance with TTL. Tamper detection via rehash reconciliation.

## SLAs (pilot)

Critical drift ≥0.7 → triage ≤4h | Evidence Pack ≤30min | Replay ≤15min (≤1M events)

Aligns with `governed-execution-system-mvp-blueprint-v1` commercial wedge; extends to full Temporal OS.
