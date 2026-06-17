"""Request-scoped context for RID and correlation threading."""

from __future__ import annotations

from contextvars import ContextVar, Token
from uuid import UUID

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_correlation_id: ContextVar[UUID | None] = ContextVar("correlation_id", default=None)


def get_request_id() -> str | None:
    return _request_id.get()


def get_correlation_id() -> UUID | None:
    return _correlation_id.get()


def set_request_context(
    *,
    source_request_id: str | None = None,
    correlation_id: UUID | None = None,
) -> tuple[Token[str | None], Token[UUID | None]]:
    rid_token = _request_id.set(source_request_id)
    corr_token = _correlation_id.set(correlation_id)
    return rid_token, corr_token


def reset_request_context(
    rid_token: Token[str | None],
    corr_token: Token[UUID | None],
) -> None:
    _request_id.reset(rid_token)
    _correlation_id.reset(corr_token)
