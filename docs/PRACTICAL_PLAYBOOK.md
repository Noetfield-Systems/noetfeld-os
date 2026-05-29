# Practical playbook — use Noetfield end to end

Role-based guide for making the public site, assistant, Telegram bot, and intake work together in production.

---

## Visitor (www.noetfield.com)

| Goal | Action |
|------|--------|
| Learn offerings | Home → Enterprise / Trust Brief / Copilot pages |
| Quick Q&A | **Assistant** (bottom-right) — same knowledge as Telegram |
| Start engagement | [Request Governance Brief](/trust-brief/intake/) — copy **Request ID** from footer |
| Human contact | `operations@noetfield.com` (all SKUs) |

**Request ID** is `RID-…` everywhere (footer, intake, email subject). Include it in every ops email.

---

## Telegram user

| Goal | Action |
|------|--------|
| Open bot | Link on [FAQ](/faq/) when `TELEGRAM_BOT_USERNAME` is published to `assets/noetfield-ecosystem.json` |
| Menu / offerings | `/start` then inline buttons |
| Free-text questions | Needs `OPENROUTER_API_KEY` or `GEMINI_API_KEY` on platform |
| Intake | `/intake` or **Request Brief** button → web form (no payment in bot) |

Setup: [TELEGRAM_BOT_SETUP.md](./TELEGRAM_BOT_SETUP.md)

---

## Operations (intake inbox)

| Source | What you receive |
|--------|------------------|
| Web intake | **`POST /api/intake`** primary (`noetfield-intake-api.js`) + `mailto:` fallback with `RID-…` |
| Ops API view | `GET /api/intake/recent` with `X-Admin-Secret`; optional `INTAKE_OPS_WEBHOOK_URL` (Slack) |
| Idempotency | Same `RID-…` returns existing intake row |
| Email | `operations@noetfield.com` — subject should include vector + RID |
| Chat / Telegram | Users directed to intake or email; no auto-ticket yet |

**Correlate** using Request ID (`RID-…`) in subject/body.

---

## DevOps (platform.noetfield.com)

```bash
# 1. Secrets on API host only (never in git)
OPENROUTER_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBHOOK_BASE_URL=https://platform.noetfield.com
PUBLIC_CHAT_PROVIDER=auto
RUNTIME_EVENT_STORE=postgres   # or memory for smoke tests

# 2. Run API
make api-v3   # port 8001

# 3. Register Telegram webhook
curl -X POST https://platform.noetfield.com/api/telegram/register-webhook \
  -H "X-Admin-Secret: $TELEGRAM_WEBHOOK_SECRET"

# 4. Health
curl -sS https://platform.noetfield.com/api/ecosystem/health | python3 -m json.tool

# 5. Publish www ecosystem links (optional Telegram @username)
TELEGRAM_BOT_USERNAME=YourBotName PUBLIC_CHAT_API_BASE=https://platform.noetfield.com \
  python3 scripts/publish_ecosystem_config.py
# commit + deploy assets/noetfield-ecosystem.json with static site
```

| Check | Endpoint |
|-------|----------|
| Chat + LLM | `GET /api/public/chat/health` |
| Intake API | `GET /api/intake/health` · `POST /api/intake` |
| Telegram | `GET /api/telegram/health` → `ready: true` |
| Combined | `GET /api/ecosystem/health` |
| Verify all | `make verify-platform-health` or `PLATFORM_HEALTH_BASE=https://platform.noetfield.com python3 scripts/verify_platform_health.py` |

Chat widget reads `assets/noetfield-ecosystem.json` → `chat_api_base` (override via `PUBLIC_CHAT_API_BASE` at publish time).

---

## Product / GTM

- **Three SKUs only** — see `OFFERINGS_LOCKED.md`
- **Trust Brief** — **$10,000** fixed (intake estimator is scope planning, not list price)
- **No** custody, payments, or trading on public surfaces

---

## Common failures

| Symptom | Fix |
|---------|-----|
| Chat spinner then error | Platform down, CORS, or missing LLM key |
| Telegram silent | Webhook not registered or token revoked |
| Wrong API host on staging | Set `PUBLIC_CHAT_API_BASE` and re-run `publish_ecosystem_config.py` |
| Ops can't match leads | Ask for footer **Request ID** (`RID-…`) |

See also: [CHATBOT_SETUP.md](./CHATBOT_SETUP.md), [TELEGRAM_BOT_SETUP.md](./TELEGRAM_BOT_SETUP.md), [DEPLOYMENT_ARCHITECTURE.md](../DEPLOYMENT_ARCHITECTURE.md).
