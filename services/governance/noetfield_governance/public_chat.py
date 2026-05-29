"""Public website chat — grounded answers via server-side Gemini or OpenRouter."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Literal

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.chat_errors import ChatAPIError, ChatConfigurationError
from noetfield_governance.chatbot_knowledge import select_relevant_excerpt
from noetfield_governance.gemini_client import generate_reply as gemini_generate_reply
from noetfield_governance.openrouter_client import generate_reply as openrouter_generate_reply

_MAX_MESSAGE_LEN = 2000
_RATE_LIMIT_WINDOW_SEC = 60
_RATE_LIMIT_MAX_PER_WINDOW = 30

ChatProvider = Literal["gemini", "openrouter", "auto"]

_buckets: defaultdict[str, deque[float]] = defaultdict(deque)


def _check_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    bucket = _buckets[client_key]
    while bucket and now - bucket[0] > _RATE_LIMIT_WINDOW_SEC:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT_MAX_PER_WINDOW:
        raise PermissionError("Rate limit exceeded. Try again in a minute.")
    bucket.append(now)


def _system_instruction(context: str) -> str:
    return f"""You are the Noetfield institutional assistant for banks, regulated enterprises, and institutional buyers.

Tone: professional, precise, calm, board-ready. No hype or startup slang.

Rules:
- Answer ONLY using the knowledge base below. If the answer is not in the knowledge base, say clearly that you do not have that information.
- Never invent pricing, legal terms, SLAs, or product features.
- Do not claim Noetfield executes payments, holds custody, or routes funds.
- Three offerings only: Trust Brief ($10,000), Copilot Governance Pack, Bank Pilot (read-only simulation).
- For engagement, procurement, or pilot access: direct to Request Governance Brief (/trust-brief/intake/) or {CANONICAL_INTAKE_EMAIL}.
- Prefer short paragraphs and bullets when listing multiple points.
- Do not reveal API keys, internal architecture names, or stack details.

Knowledge base:
{context}
"""


def resolve_chat_provider(
    *,
    preference: ChatProvider,
    gemini_api_key: str | None,
    openrouter_api_key: str | None,
) -> tuple[ChatProvider, str]:
    g = (gemini_api_key or "").strip()
    o = (openrouter_api_key or "").strip()

    if preference == "openrouter":
        if not o:
            raise ChatConfigurationError("OPENROUTER_API_KEY is not configured.")
        return "openrouter", o

    if preference == "gemini":
        if not g:
            raise ChatConfigurationError("GEMINI_API_KEY is not configured.")
        return "gemini", g

    # auto: prefer OpenRouter when both exist (single env for ops), else Gemini
    if o:
        return "openrouter", o
    if g:
        return "gemini", g
    raise ChatConfigurationError(
        "Chat is not configured. Set OPENROUTER_API_KEY or GEMINI_API_KEY on the server. "
        f"Email {CANONICAL_INTAKE_EMAIL} or use /trust-brief/intake/."
    )


def _generate_sync(
    *,
    provider: ChatProvider,
    api_key: str,
    gemini_model: str,
    openrouter_model: str,
    system_instruction: str,
    user_message: str,
) -> str:
    if provider == "openrouter":
        return openrouter_generate_reply(
            api_key=api_key,
            model=openrouter_model,
            system_instruction=system_instruction,
            user_message=user_message,
        )
    return gemini_generate_reply(
        api_key=api_key,
        model=gemini_model,
        system_instruction=system_instruction,
        user_message=user_message,
    )


async def answer_public_question(
    *,
    message: str,
    provider: ChatProvider,
    gemini_api_key: str | None,
    gemini_model: str,
    openrouter_api_key: str | None,
    openrouter_model: str,
    client_key: str,
) -> tuple[str, ChatProvider]:
    text = (message or "").strip()
    if not text:
        raise ValueError("message is required")
    if len(text) > _MAX_MESSAGE_LEN:
        raise ValueError(f"message must be at most {_MAX_MESSAGE_LEN} characters")

    _check_rate_limit(client_key or "anonymous")

    context = select_relevant_excerpt(text)
    system = _system_instruction(context)

    resolved, api_key = resolve_chat_provider(
        preference=provider,
        gemini_api_key=gemini_api_key,
        openrouter_api_key=openrouter_api_key,
    )

    reply = await asyncio.to_thread(
        _generate_sync,
        provider=resolved,
        api_key=api_key,
        gemini_model=gemini_model,
        openrouter_model=openrouter_model,
        system_instruction=system,
        user_message=text,
    )
    return reply, resolved
