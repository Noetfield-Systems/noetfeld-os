# Noetfield platform runbook

## Architecture

| Host | Deploy |
|------|--------|
| `www.noetfield.com` | Static HTML from repo root + CDN |
| `platform.noetfield.com` | Docker or `make api-v3` (port **8001**) |

## Local full stack

```bash
docker compose -f infrastructure/docker/docker-compose.yml \
  -f infrastructure/docker/docker-compose.platform.yml up -d --build

make apply-migrations
PYTHONPATH=... python3 scripts/sync_knowledge_chunks.py

curl -sS http://127.0.0.1:8001/api/ecosystem/health | python3 -m json.tool
./scripts/deploy_platform_smoke.sh
```

## Production deploy (platform)

1. Set secrets (never in git): `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, optional `INTAKE_OPS_WEBHOOK_URL`, Langfuse keys.
2. `RUNTIME_EVENT_STORE=postgres`, `INTAKE_PERSISTENCE=auto`, `DATABASE_URL=...`, `REDIS_URL=...`
3. Apply migrations: `python3 scripts/apply_postgres_migrations.py`
4. Start API (port 8001).
5. `POST /api/telegram/register-webhook` with `X-Admin-Secret` if configured.
6. `PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh`
7. Publish www: `TELEGRAM_BOT_USERNAME=... python3 scripts/publish_ecosystem_config.py`

## Health endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | API + storage mode |
| `GET /api/ecosystem/health` | Chat + Telegram + intake |
| `GET /api/ecosystem/public` | Safe config for www |
| `GET /api/intake/recent` | Ops queue (`X-Admin-Secret`) |

## Intake operations

- Public: `POST /api/intake` (Postgres when `INTAKE_PERSISTENCE=auto` + postgres runtime).
- Web form mirrors via `noetfield-intake-api.js`.
- Slack: set `INTAKE_OPS_WEBHOOK_URL`.
- Idempotent on `request_id` (`RID-…`).

## Assistant

- LLM: OpenRouter primary, Gemini fallback (`PUBLIC_CHAT_PROVIDER=auto`).
- Sessions: Redis when `REDIS_SESSIONS_ENABLED=true`.
- Knowledge: `scripts/sync_knowledge_chunks.py` for DB index; pinned `OFFERINGS_LOCKED.md` in prompts.

## Governance pilot (production)

Full procedure: [GOVERNANCE_PILOT_RUNBOOK.md](./GOVERNANCE_PILOT_RUNBOOK.md) · Wave 0 checklist: [WAVE0_SHIP_CHECKLIST.md](./WAVE0_SHIP_CHECKLIST.md).

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/governance/evaluate` | Pre-execution decision + RID |
| `GET /api/v1/governance/ledger` | Compliance log slice |
| `GET /api/v1/governance/audit-export` | Trust Brief export by RID |

Trust Brief export script: `./scripts/trust_brief_audit_export.sh --request-id RID-...`

See also: [GO_LIVE.md](./GO_LIVE.md), [PRACTICAL_PLAYBOOK.md](./PRACTICAL_PLAYBOOK.md), [STAGING.md](./STAGING.md), [POSTGRES_OPERATIONS.md](./POSTGRES_OPERATIONS.md), [INTAKE_BACKUP_RETENTION.md](./INTAKE_BACKUP_RETENTION.md), [INTAKE_OPS.md](./INTAKE_OPS.md), [TELEGRAM_BOT_SETUP.md](./TELEGRAM_BOT_SETUP.md), [CHATBOT_SETUP.md](./CHATBOT_SETUP.md).
