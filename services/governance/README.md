# Noetfield Production Governance API

FastAPI production runtime for intake, trust ledger, public chat, and webhooks.

**Entry point:** `noetfield_governance/api.py`

**Contract (locked):** [NOETFIELD_GOVERNANCE_RUNTIME_CONTRACT_LOCKED_v1.md](../../docs/strategy/NOETFIELD_GOVERNANCE_RUNTIME_CONTRACT_LOCKED_v1.md)

**Architecture:** [PLATFORM_BLUEPRINT.md](../../PLATFORM_BLUEPRINT.md) §8.3 (Governance Service) and §8.4 (Trust Ledger Service).

## Public pilot API (locked)

| Method | Path |
|--------|------|
| POST | `/api/v1/governance/evaluate` |
| GET | `/api/v1/governance/ledger` |
| GET | `/api/v1/governance/audit-export` |
| POST | `/api/v1/tle/draft`, `/approve`, `/export` |

Decisions: `PROCEED` / `REQUIRE_HUMAN_REVIEW` / `REJECT`.

## Dual-stack note

| Stack | Path | Role |
|-------|------|------|
| Dev / Golden Edge | `governance-console/` | Local E2E, TLE flow, workspace UI |
| Production API | `services/governance/` | Deployed runtime (intake, trust ledger, Telegram, public OpenAPI) |
| GEL adapter | `noetfeld-os` via `gel_adapter.py` | Optional credit lane — no merge |

## Policy packs

Loaded from `packages/policy-packs/` via `policy_loader.py`:

- `copilot-governance-v1` (default)
- `bank-pilot-v1`

Governance-as-Code: `governance_config.py` + `docs/spec/samples/governance-copilot-v1.yaml`

## Key modules

- `noetfield_governance/api.py` — FastAPI app
- `noetfield_governance/governance_v1.py` — public evaluate surface
- `noetfield_governance/golden_edge_v3.py` — evaluate pipeline
- `noetfield_governance/control_plane.py` — state machine
- `noetfield_governance/trust_ledger.py` — TLE operations
- `noetfield_governance/tle_signer.py` — HMAC signatures
- `noetfield_governance/gel_adapter.py` — optional GEL bridge

See [governance-console/README.md](../../governance-console/README.md) for dev-stack smoke (`make governance-console-e2e`).
