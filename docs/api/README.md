# Noetfield institutional API

Public and **pilot governance** endpoints for regulated buyers (OSFI E-23, CDB policy adjacency, enterprise Copilot).

## Boundary (non-negotiable)

Noetfield is a **pre-execution governance layer**. These APIs do **not** execute payments, hold custody, or operate as a PSP/MSB. Partner execution remains outside Noetfield.

## Tiers

| Tier | Routes | Auth |
|------|--------|------|
| **1 — GTM** | `POST /api/public/chat`, `POST /api/intake`, `GET /api/ecosystem/health` | Rate-limited anonymous |
| **2 — Pilot** | `POST /api/v1/governance/evaluate`, `GET …/ledger`, `GET …/audit-export`, `GET …/vendor-evidence` | Pilot API key when `GOVERNANCE_PILOT_AUTH_REQUIRED=true` |
| **3 — Enterprise** | Webhooks, mTLS (design) | Per-engagement |

## OpenAPI

- Machine-readable: [`openapi.json`](./openapi.json) (regenerate with `make generate-openapi`)
- Live schema (filtered): `GET https://platform.noetfield.com/openapi.json`

## Evaluate response fields

| Field | Meaning |
|-------|---------|
| `request_id` | RID lineage (`RID-…`) |
| `correlation_id` | Bank orchestration id (optional) |
| `mode` | `shadow` (Bank Pilot) or `enforce` |
| `decision` | `PROCEED`, `REJECT`, `REQUIRE_HUMAN_REVIEW` |
| `allowed` | Policy allow flag |
| `reason_code` | Stable machine code |
| `policy_refs` | Policy pack references |

## Canada trust

See [CANADA_TRUST.md](./CANADA_TRUST.md).

## Partner pre-execution

See [PARTNER_PRE_EXECUTION.md](./PARTNER_PRE_EXECUTION.md).

## Status

- API summary: `GET /api/status`
- www: [https://www.noetfield.com/status/](https://www.noetfield.com/status/)
