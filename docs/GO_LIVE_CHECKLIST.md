# Noetfield go-live checklist (Tier 0)

Founder/ops steps to complete **before** calling production live. Engineering artifacts are on `main`; this list is the critical path ([NEXT_MOVES.md](../todolist/NEXT_MOVES.md)).

## NF-SECRET-01 — Secrets

- [ ] Rotate **OpenRouter**, **Gemini**, and **Telegram** tokens if they were ever pasted in chat or committed
- [ ] Set secrets **only** on the platform host (or secrets manager) — never in git
- [ ] Confirm `.env` is gitignored locally

## NF-DEPLOY-02 — DNS and TLS

- [ ] `platform.noetfield.com` → API load balancer / VM (port **8001**)
- [ ] `www.noetfield.com` and `noetfield.com` → static CDN or Pages
- [ ] Valid TLS certificates on both hosts

## NF-DEPLOY-01 — Platform API

```bash
make platform-migrate
make platform-up   # or production container per docs/RUNBOOK.md
```

- [ ] `RUNTIME_EVENT_STORE=postgres`, `INTAKE_PERSISTENCE=auto`
- [ ] `DATABASE_URL`, `REDIS_URL` set
- [ ] Migrations applied

## NF-LLM-01 — Assistant

- [ ] `OPENROUTER_API_KEY` and/or `GEMINI_API_KEY`
- [ ] `PUBLIC_CHAT_PROVIDER=auto`
- [ ] `PUBLIC_CHAT_ENABLED=true`

## NF-WWW-01 — Public site

- [ ] Deploy repo root static HTML + `assets/`
- [ ] `TELEGRAM_BOT_USERNAME=... python3 scripts/publish_ecosystem_config.py` (if using Telegram)
- [ ] `assets/noetfield-ecosystem.json` points `publicChatApiBase` to production platform

## Verify (required)

```bash
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
```

Exit code **0** = Tier 0 complete.

## Optional (after Tier 0)

- [ ] NF-TG-01 / NF-TG-02 — Telegram webhook and footer link ([TELEGRAM_BOT_SETUP.md](./TELEGRAM_BOT_SETUP.md))
