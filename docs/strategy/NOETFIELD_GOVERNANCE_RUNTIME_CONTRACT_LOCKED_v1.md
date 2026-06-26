# Noetfield Governance Runtime Contract (LOCKED v1)

**Status:** LOCKED  
**Date:** 2026-06-17  
**Runtime:** `services/governance` on `platform.noetfield.com`  
**Authority:** Supersedes ad-hoc evaluate path documentation

---

## Public pilot surface (locked)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/governance/evaluate` | Pre-execution policy check |
| GET | `/api/v1/governance/ledger` | Audit slice by tenant/RID |
| GET | `/api/v1/governance/audit-export` | Procurement audit pack |
| POST | `/api/v1/tle/draft` | Trust Ledger Entry draft |
| POST | `/api/v1/tle/{id}/approve` | Human approval chain |
| GET | `/api/v1/tle/{id}/export` | Board pack export |

Internal-only (excluded from public OpenAPI): `/v3/evaluate`, `/v3/agent-loop`, `/governance/execute`.

## Decision vocabulary (customer-facing)

| Platform | Meaning |
|----------|---------|
| `PROCEED` | Policy allowed; execution may proceed |
| `REQUIRE_HUMAN_REVIEW` | Allowed pending human approval |
| `REJECT` | Veto — no execution |

Never use SourceA terms with customers: runs, spine, gatekeeper, receipt (use audit record).

## GEL adapter (optional)

When `payload.use_gel_adapter=true` or `payload.lane=gel`, evaluate may consult `noetfeld-os` `POST /v1/decision`. Mapping:

- `APPROVE` → `PROCEED`
- `REVIEW` → `REQUIRE_HUMAN_REVIEW`
- `DECLINE` → `REJECT`

GEL is credit-lane adjacency only. Platform policy pack remains authoritative for Copilot governance.

## Governance-as-Code

Default config: `docs/spec/samples/governance-copilot-v1.yaml`  
Response includes `config_policy_version_hash` when config resolves.

## Control plane state machine

```
INITIATED → INTENT_PARSED → ROUTED → GOVERNANCE_CHECKED → EXECUTED → ARCHIVED
```

Invariant: no execution without `GOVERNANCE_CHECKED` + policy allow.

## Boundary (locked)

Noetfield does not execute payments, hold custody, or operate as a PSP/MSB.
