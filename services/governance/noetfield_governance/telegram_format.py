"""Telegram HTML formatting and message chunking."""

from __future__ import annotations

import html
import re

_MAX_CHUNK = 3900


def escape_html(text: str) -> str:
    return html.escape(text, quote=False)


def bold(text: str) -> str:
    return f"<b>{escape_html(text)}</b>"


def link(url: str, label: str | None = None) -> str:
    safe_url = escape_html(url)
    safe_label = escape_html(label or url)
    return f'<a href="{safe_url}">{safe_label}</a>'


def split_telegram_chunks(text: str, *, max_len: int = _MAX_CHUNK) -> list[str]:
    text = text.strip()
    if len(text) <= max_len:
        return [text] if text else []
    chunks: list[str] = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        cut = text.rfind("\n\n", 0, max_len)
        if cut < max_len // 3:
            cut = text.rfind("\n", 0, max_len)
        if cut < max_len // 3:
            cut = max_len
        chunks.append(text[:cut].strip())
        text = text[cut:].strip()
    return chunks
