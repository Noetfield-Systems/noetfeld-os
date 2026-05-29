# Noetfield Systems
Infrastructure for AI trust and stewardship

## Platform blueprint

See [PLATFORM_BLUEPRINT.md](PLATFORM_BLUEPRINT.md) for the architecture
constitution guiding Noetfield's transition from a static vision and branding
site into an enterprise AI governance operating system.

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

**Go live (roles):** [docs/PRACTICAL_PLAYBOOK.md](docs/PRACTICAL_PLAYBOOK.md) — visitor, Telegram, ops intake, DevOps.
