"""Public website chat — grounded answers via server-side Gemini or OpenRouter."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict, deque
from typing import Literal

from noetfield_config import CANONICAL_INTAKE_EMAIL, get_settings
from noetfield_governance.chat_errors import ChatAPIError, ChatConfigurationError
from noetfield_governance.chatbot_knowledge import select_relevant_excerpt
from noetfield_governance.observability import trace_public_chat
from noetfield_governance import redis_runtime
from noetfield_governance.gemini_client import generate_reply as gemini_generate_reply
from noetfield_governance.openrouter_client import generate_reply as openrouter_generate_reply

_MAX_MESSAGE_LEN = 2000
_RATE_LIMIT_WINDOW_SEC = 60
_RATE_LIMIT_MAX_PER_WINDOW = 30

ChatProvider = Literal["gemini", "openrouter", "auto"]

logger = logging.getLogger("noetfield.governance.public_chat")

_buckets: defaultdict[str, deque[float]] = defaultdict(deque)


def _check_rate_limit_memory(client_key: str) -> None:
    now = time.monotonic()
    bucket = _buckets[client_key]
    while bucket and now - bucket[0] > _RATE_LIMIT_WINDOW_SEC:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT_MAX_PER_WINDOW:
        raise PermissionError("Rate limit exceeded. Try again in a minute.")
    bucket.append(now)


async def _check_rate_limit(client_key: str) -> None:
    if redis_runtime.is_enabled():
        await redis_runtime.check_rate_limit(
            f"chat:{client_key}",
            max_calls=_RATE_LIMIT_MAX_PER_WINDOW,
            window_sec=_RATE_LIMIT_WINDOW_SEC,
        )
        return
    _check_rate_limit_memory(client_key)


def _system_instruction(context: str) -> str:
    return f"""You are the Noetfield institutional assistant on www.noetfield.com — for buyers, developers, partners, and investors.

Tone: professional, precise, calm, board-ready. No hype or startup slang.

Audience lanes (use the matching knowledge):
- **Buyer / SME:** Diagnostic Sprint from $2,500, Copilot Governance Pack $2k–10k, Trust Brief $10k, Bank Pilot shadow — see OFFERINGS_LOCKED and intelligence-lane.
- **Developer:** GEL = Governance Execution Layer (/gel/), api.noetfield.com, pip package noetfield-gate, noetfield gate / noetfield decide — see gel-runtime and developer-tools.
- **Investor:** /investors/ and /investors/diligence/ — see investor-public.
- **Trust / audit:** Trust Ledger (TLE infrastructure) vs Trust Brief (consulting SKU) — see trust-ledger-public.

Rules:
- Answer using the knowledge base below. Prefer pinned (core) sources for pricing and identity.
- **GEL is a public acronym** — Governance Execution Layer. Never say GEL is unused or unknown.
- **noetfield-gate exists on PyPI** when developer-tools says so — give install/command guidance and PyPI org form templates from that doc.
- If absent from knowledge, say so briefly and direct to the best public page or {CANONICAL_INTAKE_EMAIL} with RID — do not refuse answerable developer or GEL questions that are in the KB.
- Never invent pricing, legal terms, SLAs, or features not in the KB.
- Never claim payments, custody, or fund routing.
- Contract SKUs: Trust Brief ($10,000), Copilot Governance Pack ($2k–10k), Bank Pilot (read-only). Free sandbox at /start/ is not a fourth contract SKU.
- Include relevant paths (/gel/, /trust-brief/intake/, /investors/diligence/) when helpful.
- For buyer, investor, developer, or intake questions, end with one clean next step and a public link or {CANONICAL_INTAKE_EMAIL}.
- Keep replies compact: answer first, then next step. Avoid long lists unless the user asks for detail.
- Do not reveal API keys, secrets, or internal-only ops details.

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
) -> tuple[str, ChatProvider, list[str]]:
    text = (message or "").strip()
    if not text:
        raise ValueError("message is required")
    if len(text) > _MAX_MESSAGE_LEN:
        raise ValueError(f"message must be at most {_MAX_MESSAGE_LEN} characters")

    await _check_rate_limit(client_key or "anonymous")

    context = select_relevant_excerpt(text)
    if len(context.strip()) < 200:
        logger.warning("public_chat_thin_context chars=%s question=%r", len(context), text[:80])
    citations = _citations_from_context(context)
    system = _system_instruction(context)

    resolved, api_key = resolve_chat_provider(
        preference=provider,
        gemini_api_key=gemini_api_key,
        openrouter_api_key=openrouter_api_key,
    )

    settings = get_settings()
    lf_host = settings.langfuse_host
    lf_pub = (
        settings.langfuse_public_key.get_secret_value().strip()
        if settings.langfuse_public_key
        else None
    )
    lf_sec = (
        settings.langfuse_secret_key.get_secret_value().strip()
        if settings.langfuse_secret_key
        else None
    )

    with trace_public_chat(
        host=lf_host,
        public_key=lf_pub,
        secret_key=lf_sec,
        name="public_chat",
        metadata={"provider": resolved, "client_key": client_key[:64]},
    ):
        try:
            reply = await asyncio.to_thread(
                _generate_sync,
                provider=resolved,
                api_key=api_key,
                gemini_model=gemini_model,
                openrouter_model=openrouter_model,
                system_instruction=system,
                user_message=text,
            )
            return reply, resolved, citations
        except ChatAPIError as primary_exc:
            fallback = _fallback_provider(
                resolved,
                gemini_api_key=gemini_api_key,
                openrouter_api_key=openrouter_api_key,
            )
            if fallback is None:
                raise primary_exc
            fb_provider, fb_key = fallback
            try:
                reply = await asyncio.to_thread(
                    _generate_sync,
                    provider=fb_provider,
                    api_key=fb_key,
                    gemini_model=gemini_model,
                    openrouter_model=openrouter_model,
                    system_instruction=system,
                    user_message=text,
                )
                return reply, fb_provider, citations
            except ChatAPIError:
                raise primary_exc from None


def _citations_from_context(context: str) -> list[str]:
    """Surface knowledge doc labels used for the answer (institutional citations)."""
    labels: list[str] = []
    for line in context.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Source:"):
            labels.append(stripped.replace("## Source:", "", 1).strip())
    return labels[:6]


def _fallback_provider(
    current: ChatProvider,
    *,
    gemini_api_key: str | None,
    openrouter_api_key: str | None,
) -> tuple[ChatProvider, str] | None:
    """If primary LLM fails, try the other configured provider."""
    g = (gemini_api_key or "").strip()
    o = (openrouter_api_key or "").strip()
    if current == "openrouter" and g:
        return "gemini", g
    if current == "gemini" and o:
        return "openrouter", o
    if current == "auto":
        return None
    return None
