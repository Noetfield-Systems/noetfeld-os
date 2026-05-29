"""Optional Langfuse tracing for public chat LLM calls."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

logger = logging.getLogger("noetfield.governance.observability")


@contextmanager
def trace_public_chat(
    *,
    host: str | None,
    public_key: str | None,
    secret_key: str | None,
    name: str,
    metadata: dict[str, Any] | None = None,
) -> Iterator[None]:
    if not host or not public_key or not secret_key:
        yield
        return
    try:
        from langfuse import Langfuse

        client = Langfuse(
            host=host.rstrip("/"),
            public_key=public_key,
            secret_key=secret_key,
        )
        trace = client.trace(name=name, metadata=metadata or {})
        span = trace.span(name="llm_generate")
        try:
            yield
            span.end()
        except Exception as exc:
            span.end(level="ERROR", status_message=str(exc))
            raise
        finally:
            client.flush()
    except Exception as exc:
        logger.debug("langfuse_trace_skipped %s", exc)
        yield
