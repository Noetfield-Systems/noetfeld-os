# Noetfield Systems
Infrastructure for AI trust and stewardship

**This repository and Cursor chat are Noetfield only.** TrustField Technologies and VIRLUX are separate — see [PROJECT_BOUNDARIES_LOCKED.md](PROJECT_BOUNDARIES_LOCKED.md).

## Current law stack (read first)

**Visible entry:** [docs/LAWS/README.md](docs/LAWS/README.md) · **Latest stack:** [docs/LAWS/CURRENT_STACK_v2026.md](docs/LAWS/CURRENT_STACK_v2026.md) · **L0 pointer:** [L0-law/CURRENT.md](L0-law/CURRENT.md)

```bash
make verify-law-stack    # anti-fragmentation / anti-drift
make sync-derived-docs   # regenerate L2 + All-Documents mirrors
```

Old constitutional versions stay in batch folders — indexed in [docs/SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md](docs/SOURCE_OF_TRUTH/archive/SUPERSESSION_INDEX.md), not deleted (registry path integrity).

## Platform blueprint

See [PLATFORM_BLUEPRINT.md](PLATFORM_BLUEPRINT.md) for the architecture
constitution guiding Noetfield's transition from a static vision and branding
site into an enterprise AI governance operating system.

## Roadmap and tracking

| Doc | Audience |
|-----|----------|
| [docs/ROADMAP.md](docs/ROADMAP.md) | Public horizons + shipped summary |
| [docs/strategy/noetfield-future-path.md](docs/strategy/noetfield-future-path.md) | Product strategy (2026–2027) |
| [GitHub Issues](https://github.com/Noetfield-Systems/Noetfield/issues) | Team execution (`launch`, `legal`, `engineering`) |
| [.cursor/AGENT_TRACKING.md](.cursor/AGENT_TRACKING.md) | **Agents:** local `ops/private/` or Issues |
| [ops/README.md](ops/README.md) | Ops guide + gitignored `ops/private/` |

## Noetfield v3.1 executable foundation

The repository now includes the initial monorepo foundation for the Noetfield
Autonomous Governed Intelligence Nervous System:

- `apps/` contains Next.js app shells for public web, platform, and admin.
- `services/` contains modular FastAPI/Python service boundaries.
- `packages/` contains shared typed contracts, schemas, config, SDK, prompts,
  and shared utilities.
- `infrastructure/` contains Docker, Supabase/PostgreSQL, monitoring, and
  Terraform scaffolding.
- `docs/SOURCE_OF_TRUTH/` records the v3.1 constitutional source layer.

Start with [docs/DEVELOPER_BOOTSTRAP.md](docs/DEVELOPER_BOOTSTRAP.md).

## Ship now (canonical)

**Bounded founder `implement` + GTM_NEXT queue.** Direction: [os/SHIP_NOW.md](os/SHIP_NOW.md)

```bash
make ship-verify        # merge/deploy readiness (local stack + www smoke)
```

Wave 0 production: [docs/WAVE0_SHIP_CHECKLIST.md](docs/WAVE0_SHIP_CHECKLIST.md) · Trust Ledger blueprint: [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md)

## Local development

```bash
make dev-local          # start all services (website, console, dashboard)
make dev-local-status   # health + URLs
make verify-local-dev   # smoke checks only
```

**Cursor Cloud:** forward port **13080** in the **Ports** panel, then open the globe link. See [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md).

**Go live:** [docs/GO_LIVE.md](docs/GO_LIVE.md) · [docs/RUNBOOK.md](docs/RUNBOOK.md) · [docs/PRACTICAL_PLAYBOOK.md](docs/PRACTICAL_PLAYBOOK.md)
