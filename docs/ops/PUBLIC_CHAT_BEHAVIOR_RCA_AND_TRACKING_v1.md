# Public Chat Behavior RCA and Tracking — v1

**Date:** 2026-06-27  
**Scope:** `www.noetfield.com` assistant, `POST /api/public/chat`, platform FastAPI backend

## Live Audit

- The public widget is live and calls `POST /api/public/chat`.
- Production health reports chat enabled and configured with `active_provider: openrouter`.
- Production health does not yet expose `telemetry`; deploy is required before live transcript capture starts.
- Browser testing confirmed chat answers are returned, but the previous behavior did not clearly answer whether chat history is stored.

## Root Cause

1. **No first-party durable transcript store.** The platform had optional Langfuse span tracing and normal logs, but no durable prompt/reply/error history available to operators.
2. **No conversation state.** The browser sent `session_id`, but the backend did not reconstruct prior turns or store turn indexes.
3. **No decision-path logging.** Operators could not see whether an answer came from deterministic policy, retrieval, provider selection, fallback, or error handling.
4. **No intent-alignment scoring.** There was no record of whether the reply satisfied the user's likely intent, included required facts, or missed required citations.
5. **Privacy/history questions were not deterministic.** Questions like "do you store my chat history?" could flow through the LLM or broad FAQ rules instead of a precise compliance answer.

## Fix Implemented

- Added `public_chat_telemetry.py` for JSONL chat telemetry with hashed session/client/user-agent identifiers and secret redaction.
- Added `public_chat_intelligence.py` for deterministic intent classification, privacy/history policy replies, off-topic redirects, decision paths, and alignment checks.
- Updated `api.py` so every chat request records:
  - full prompt/reply/error state,
  - provider and citations,
  - session turn index and recent prior turns,
  - intent classification and outcome goal,
  - decision path,
  - alignment result.
- Updated the Vercel/www fallback chat route with a deterministic privacy/history answer.
- Added `report_public_chat_telemetry.py` for operator reporting.
- Updated `CHATBOT_SETUP.md` with telemetry env vars and reporting instructions.
- Added tests for telemetry persistence, redaction, conversation-state continuity, and deterministic privacy/history behavior.

## Operator Commands

```bash
python3 scripts/report_public_chat_telemetry.py \
  --path var/public_chat_telemetry.jsonl \
  --recent 20
```

Production should set a durable path:

```bash
PUBLIC_CHAT_TELEMETRY_ENABLED=true
PUBLIC_CHAT_TELEMETRY_PATH=/data/public_chat_telemetry.jsonl
PUBLIC_CHAT_TELEMETRY_MAX_CHARS=4000
```

## Remaining Deployment Requirement

Deploy the platform API and static www fallback route. After deploy, verify:

```bash
curl -sS https://www.noetfield.com/api/public/chat/health | python3 -m json.tool
```

Expected: `telemetry.enabled=true` and event counts increasing after test chats.
