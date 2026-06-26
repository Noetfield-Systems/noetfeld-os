"""Public site content rendering for Noetfield institutional pages."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent
CONTENT_ROOT = SITE_ROOT / "content"


@dataclass(frozen=True)
class PageContent:
    title: str
    description: str
    page_type: str
    layout: str
    version: str
    hero_headline: str
    hero_subheadline: str
    body_html: str


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, raw[match.end() :]


def _markdown_to_html(markdown: str) -> str:
    try:
        import markdown as md
    except ImportError:
        escaped = (
            markdown.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return f"<pre>{escaped}</pre>"

    return md.markdown(
        markdown,
        extensions=["tables", "fenced_code", "sane_lists"],
    )


def load_page(relative_path: str) -> PageContent:
    path = CONTENT_ROOT / relative_path
    if not path.is_file():
        raise FileNotFoundError(relative_path)

    raw = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)
    body_html = _markdown_to_html(body.strip())

    return PageContent(
        title=meta.get("title", "Noetfield Systems"),
        description=meta.get("description", ""),
        page_type=meta.get("type", "page"),
        layout=meta.get("layout", "page"),
        version=meta.get("version", ""),
        hero_headline=meta.get("hero_headline", meta.get("title", "")),
        hero_subheadline=meta.get("hero_subheadline", meta.get("description", "")),
        body_html=body_html,
    )


__all__ = ["PageContent", "load_page", "SITE_ROOT", "CONTENT_ROOT"]
