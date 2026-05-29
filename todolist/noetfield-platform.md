# Noetfield — platform API & assistant

Repo: this monolith · Host: `platform.noetfield.com` · Port: **8001**

## Launch blockers (founder / ops — not always code)

| ID | Item | Status | Owner | Type | Notes |
|----|------|--------|-------|------|-------|
| NF-DEPLOY-01 | Production API running with TLS on `platform.noetfield.com` | todo | ops | launch_blocker | `make platform-up` or container; see [docs/RUNBOOK.md](../docs/RUNBOOK.md) |
| NF-DEPLOY-02 | DNS for `platform.noetfield.com` resolves publicly | blocked | founder | launch_blocker | Was pending in PRODUCTION_READINESS_REPORT |
| NF-SECRET-01 | Rotate any API keys pasted in chat (OpenRouter, Telegram, Gemini) | todo | founder | launch_blocker | Server env only; never commit |
| NF-TG-01 | `TELEGRAM_BOT_TOKEN` on platform + `POST /api/telegram/register-webhook` | todo | ops | launch_blocker | Health: `ready: true` on `/api/telegram/health` |
| NF-TG-02 | Publish `TELEGRAM_BOT_USERNAME` → `scripts/publish_ecosystem_config.py` + deploy www | todo | ops | launch_blocker | Footer Telegram link |
| NF-LLM-01 | `OPENROUTER_API_KEY` and/or `GEMINI_API_KEY` on platform | todo | ops | launch_blocker | Gemini = fallback; see `PUBLIC_CHAT_PROVIDER=auto` |

## Engineering — shipped on `main` (verify in prod)

| ID | Item | Status | Notes |
|----|------|--------|-------|
| NF-ENG-01 | Public chat + OpenRouter/Gemini + fallback | done | `public_chat.py` |
| NF-ENG-02 | Telegram webhook + async processing + health diagnostics | done | PR #5 merged |
| NF-ENG-03 | Ecosystem JSON + footer assistant + RID unify | done | PR #6 merged |
| NF-ENG-04 | `POST /api/intake` + Postgres `public_intakes` | done | Migration `0005`; `INTAKE_PERSISTENCE=auto` |
| NF-ENG-05 | Redis sessions + rate limits | done | `REDIS_SESSIONS_ENABLED=true` |
| NF-ENG-06 | Ops Slack webhook `INTAKE_OPS_WEBHOOK_URL` | done | Optional |
| NF-ENG-07 | `scripts/verify_platform_health.py` + CI smoke | done | `make verify-platform-health` |
| NF-ENG-08 | Docker `docker-compose.platform.yml` port 8001 | done | `make platform-up` |

## Engineering — future (track here)

| ID | Item | Status | Owner | Type | Notes |
|----|------|--------|-------|------|-------|
| NF-ENG-10 | Postgres **persistent** intake + backup/retention policy | todo | engineering | code | In-memory fallback when not on postgres |
| NF-ENG-11 | CRM sync (HubSpot/Salesforce) from `/api/intake` | todo | engineering | nice_to_have | |
| NF-ENG-12 | pgvector RAG over `knowledge_chunks` + embeddings job | todo | engineering | code | `scripts/sync_knowledge_chunks.py` seeds table |
| NF-ENG-13 | Langfuse dashboards in prod | todo | ops | ops | Set `LANGFUSE_*` env |
| NF-ENG-14 | API service in default CI deploy pipeline | todo | engineering | ops | Not only manual `make api-v3` |
| NF-ENG-15 | Staging environment + `PUBLIC_CHAT_API_BASE` for preview www | todo | engineering | ops | |
| NF-ENG-16 | WAF / edge rate limit on `/api/public/chat` and webhook | todo | engineering | nice_to_have | |
| NF-ENG-17 | Telegram → `POST /api/intake` for structured leads | todo | engineering | code | Today: web form + commands |
| NF-ENG-18 | Formal **Supabase Auth** for pilot console only | todo | engineering | nice_to_have | Postgres remains SoR; Supabase optional |
| NF-ENG-19 | Email worker (Gmail monitor) for `operations@` — spec only today | todo | engineering | code | Mentioned in intake.js comments |

## Verify after deploy

```bash
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
curl -sS https://platform.noetfield.com/api/ecosystem/health | python3 -m json.tool
```
