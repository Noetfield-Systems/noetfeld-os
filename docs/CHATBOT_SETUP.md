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
| `var/public_chat_telemetry.jsonl` | First-party prompt/reply/error telemetry for behavior review |

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

The health payload also includes `telemetry`:

- `enabled` — whether public chat telemetry is on.
- `path` — configured JSONL path.
- `events` — number of recorded chat turns if the file is readable.
- `last_status` — latest recorded turn status.

## Telemetry and behavior review

The platform API records each public chat turn to JSONL by default:

```bash
PUBLIC_CHAT_TELEMETRY_ENABLED=true
PUBLIC_CHAT_TELEMETRY_PATH=var/public_chat_telemetry.jsonl
PUBLIC_CHAT_TELEMETRY_MAX_CHARS=4000
```

Use a durable mounted path in production if the host filesystem is ephemeral.

Each event stores prompt, reply, provider, citations, status, duration, and error class. Session/client/user-agent identifiers are hashed, and obvious API-key/token patterns are redacted before storage.

Each event also stores:

- `conversation_state` — turn index and recent prior turns for the same session.
- `intent` — deterministic classification such as `pricing`, `privacy_history`, `developer_gel`, or `investor`.
- `decision_path` — whether the answer used deterministic policy, retrieval, LLM provider, citations, or error handling.
- `alignment` — whether the reply satisfied required intent terms and citation expectations.

Generate an operator report:

```bash
python3 scripts/report_public_chat_telemetry.py \
  --path var/public_chat_telemetry.jsonl \
  --recent 20
```

Use the report to find:

- questions that route to thin or wrong knowledge,
- LLM/provider failures,
- repeated pricing or product-boundary confusion,
- places where the assistant gives unsupported or unclear answers.

## Enterprise interaction polish

The public widget renders Noetfield-owned links and `operations@noetfield.com` as safe clickable anchors. It also shows public citation chips returned by the API, so users can move from answer to action without copying paths manually.

The backend prompt asks for compact, board-ready answers: answer first, then one clean next step such as `/trust-brief/intake/`, `/gel/`, `/investors/diligence/`, or `operations@noetfield.com`.

Production chat history is retained only after deploying the telemetry-enabled platform API with a durable `PUBLIC_CHAT_TELEMETRY_PATH`. Without that deploy, `www.noetfield.com` can answer users but cannot yet retain first-party operator history.

## Vercel alternative

You may proxy Gemini from a Vercel Serverless Function instead of FastAPI; keep the same rule: key in env, browser calls your `/api/chat` only.
