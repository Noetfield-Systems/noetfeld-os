# Telegram bot (Noetfield assistant)

## Security (required)

- **Never** commit `TELEGRAM_BOT_TOKEN` to git or put it in frontend JavaScript.
- If the token was shared in chat or email, **revoke it** via [@BotFather](https://t.me/BotFather) (`/revoke`) and issue a new token.
- Store only in server environment variables or your secrets manager.

## Architecture

| Component | Role |
|-----------|------|
| Telegram user | Messages your bot |
| `POST /api/telegram/webhook` | FastAPI receives updates (HTTPS required) |
| `handle_telegram_update` | Same FAQ knowledge + OpenRouter/Gemini as website chat |
| `TELEGRAM_BOT_TOKEN` | Server env only |

## Environment

```bash
TELEGRAM_BOT_TOKEN=          # from @BotFather — server only
TELEGRAM_WEBHOOK_BASE_URL=https://platform.noetfield.com
TELEGRAM_WEBHOOK_SECRET=     # random string; sent as X-Telegram-Bot-Api-Secret-Token
TELEGRAM_BOT_ENABLED=true

# LLM (same as website chat)
OPENROUTER_API_KEY=
PUBLIC_CHAT_PROVIDER=auto
```

## Register webhook (production)

After the API is reachable on HTTPS:

```bash
export TELEGRAM_WEBHOOK_SECRET="your-random-secret"
curl -X POST "https://platform.noetfield.com/api/telegram/register-webhook" \
  -H "X-Admin-Secret: your-random-secret"
```

Or use the script:

```bash
TELEGRAM_BOT_TOKEN=... TELEGRAM_WEBHOOK_BASE_URL=https://platform.noetfield.com \
  TELEGRAM_WEBHOOK_SECRET=... python3 scripts/register_telegram_webhook.py
```

## Health checks

- `GET /api/telegram/health`
- `GET /api/ecosystem/health` — website chat + Telegram + providers

## Commands

- `/start` — welcome + intake links
- `/help` — same as start
- Any other text — grounded assistant reply
