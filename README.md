# Noetfield Systems
Infrastructure for AI trust and stewardship

**This repository and Cursor chat are Noetfield only.** TrustField Technologies and VIRLUX are separate — see [PROJECT_BOUNDARIES_LOCKED.md](PROJECT_BOUNDARIES_LOCKED.md).

## Platform blueprint

See [PLATFORM_BLUEPRINT.md](PLATFORM_BLUEPRINT.md) for the architecture
constitution guiding Noetfield's transition from a static vision and branding
site into an enterprise AI governance operating system.

## Roadmap and tracking

| Doc | Audience |
|-----|----------|
| [docs/ROADMAP.md](docs/ROADMAP.md) | Public horizons + shipped summary |
| [docs/strategy/noetfield-future-path.md](docs/strategy/noetfield-future-path.md) | Product strategy (2026–2027) |
| [GitHub Issues](https://github.com/kazemnezhadsina144-dot/Noetfield/issues) | Team execution (`launch`, `legal`, `engineering`) |
| [ops/README.md](ops/README.md) | Private `ops/private/` (gitignored) for founder checklists |

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

**Go live:** [docs/GO_LIVE.md](docs/GO_LIVE.md) · [docs/RUNBOOK.md](docs/RUNBOOK.md) · [docs/PRACTICAL_PLAYBOOK.md](docs/PRACTICAL_PLAYBOOK.md)
