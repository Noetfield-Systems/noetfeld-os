# Noetfield Production Governance API

FastAPI production runtime for intake, trust ledger, public chat, and webhooks.

**Entry point:** `noetfield_governance/api.py`

**Architecture:** [PLATFORM_BLUEPRINT.md](../../PLATFORM_BLUEPRINT.md) §8.3 (Governance Service) and §8.4 (Trust Ledger Service).

## Dual-stack note

| Stack | Path | Role |
|-------|------|------|
| Dev / Golden Edge | `governance-console/` | Local E2E, TLE flow, workspace UI |
| Production API | `services/governance/` | Deployed runtime (intake, trust ledger, Telegram, public OpenAPI) |

Schema convergence between dev and prod stacks is a future engineering wave — not required for GTM www ship.

## Public API

- OpenAPI schema: `/openapi.json` (filtered public surface for institutional buyers)
- Status: `GET /api/status` includes `openapi` path

## Key modules

- `noetfield_governance/api.py` — FastAPI app
- `noetfield_governance/trust_ledger.py` — TLE operations
- `noetfield_governance/public_intake.py` — trust-brief intake
- `noetfield_governance/governance_rid.py` — evaluate / RID flow

See [governance-console/README.md](../../governance-console/README.md) for dev-stack smoke (`make governance-console-e2e`).
