# Public website chatbot (Gemini via OpenRouter or Google)

## Security (required)

- **Never** put `OPENROUTER_API_KEY` or `GEMINI_API_KEY` in frontend JavaScript, HTML, or git.
- Configure keys only on the server: `.env`, Vercel env vars, or your secrets manager.
- If a key was pasted into chat, email, or a repo, **revoke it immediately** (OpenRouter dashboard or Google AI Studio) and create a new key.

## Architecture

| Layer | Role |
|-------|------|
| `assets/noetfield-chat.js` | Floating widget on www — calls API only |
| `POST /api/public/chat` | FastAPI on `platform.noetfield.com` (or `:8001` locally) |
| `data/chatbot/knowledge/*.md` | FAQ, GEL, developer tools, site map, investor, trust ledger |
| `OFFERINGS_LOCKED.md` | Pinned contract SKUs + sandbox caps |
| `PRODUCT_BRIEF.md` | Trust Ledger positioning |
| `OPENROUTER_API_KEY` or `GEMINI_API_KEY` | Server environment variables (never in the browser) |

## Providers

| Provider | Env | Default model |
|----------|-----|----------------|
| **OpenRouter** (recommended) | `OPENROUTER_API_KEY` | `OPENROUTER_MODEL=google/gemini-2.5-flash` |
| **Google Gemini** (direct) | `GEMINI_API_KEY` | `GEMINI_MODEL=gemini-2.0-flash` |

`PUBLIC_CHAT_PROVIDER`:

- `auto` — use OpenRouter if `OPENROUTER_API_KEY` is set, else Gemini
- `openrouter` — force OpenRouter
- `gemini` — force Google API

## Run locally

```bash
export OPENROUTER_API_KEY="your-key-from-openrouter.ai"
export OPENROUTER_MODEL="google/gemini-2.5-flash"
export PUBLIC_CHAT_PROVIDER=openrouter
export RUNTIME_EVENT_STORE=memory
make api-v3
```

Or with direct Gemini:

```bash
export GEMINI_API_KEY="your-new-key-from-google-ai-studio"
export GEMINI_MODEL="gemini-2.0-flash"
export PUBLIC_CHAT_PROVIDER=gemini
export RUNTIME_EVENT_STORE=memory
make api-v3
```

Serve static site (e.g. `python3 -m http.server 8080` in repo root) and open `http://localhost:8080/faq/`.

## Production

1. Set `OPENROUTER_API_KEY` and/or `GEMINI_API_KEY` on the platform host (not on static www).
2. Ensure `PUBLIC_CHAT_CORS_ORIGINS` includes `https://www.noetfield.com`.
3. Widget resolves API to `https://platform.noetfield.com`.

## Health check

`GET /api/public/chat/health` → `enabled`, `configured`, `active_provider`, `gemini`, `openrouter`

## Vercel alternative

You may proxy Gemini from a Vercel Serverless Function instead of FastAPI; keep the same rule: key in env, browser calls your `/api/chat` only.
