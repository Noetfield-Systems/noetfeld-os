"""Load public knowledge sources for the website chatbot (no secrets)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_KNOWLEDGE_DIR = _REPO_ROOT / "data" / "chatbot" / "knowledge"
_EXTRA_MD = (
    _REPO_ROOT / "PRODUCT_BRIEF.md",
    _REPO_ROOT / "OFFERINGS_LOCKED.md",
    _REPO_ROOT / "docs" / "FINAL_PUBLIC_SITE.md",
)


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


@lru_cache(maxsize=1)
def build_knowledge_context() -> str:
    """Single context block injected into the model system instruction."""
    chunks: list[str] = []
    if _KNOWLEDGE_DIR.is_dir():
        for path in sorted(_KNOWLEDGE_DIR.glob("*.md")):
            body = _read(path)
            if body:
                chunks.append(f"## Source: {path.name}\n{body}")
    for path in _EXTRA_MD:
        body = _read(path)
        if body:
            chunks.append(f"## Source: {path.name}\n{body}")
    return "\n\n---\n\n".join(chunks)


def _pinned_offerings() -> str:
    body = _read(_REPO_ROOT / "OFFERINGS_LOCKED.md")
    if not body:
        return ""
    return f"## Source: OFFERINGS_LOCKED.md (authoritative)\n{body}"


def select_relevant_excerpt(question: str, *, max_chars: int = 24_000) -> str:
    """Keyword-ranked excerpts with pinned offerings (RAG-lite)."""
    pinned = _pinned_offerings()
    full = build_knowledge_context()
    if pinned and pinned not in full:
        full = pinned + "\n\n---\n\n" + full
    if len(full) <= max_chars:
        return full
    tokens = {t.lower() for t in question.split() if len(t) > 2}
    if not tokens:
        return full[:max_chars]
    sections = full.split("\n## ")
    scored: list[tuple[int, str]] = []
    for i, section in enumerate(sections):
        text = section if i == 0 else "## " + section
        score = sum(1 for t in tokens if t in text.lower())
        scored.append((score, text))
    scored.sort(key=lambda x: (-x[0], x[1]))
    out: list[str] = []
    size = 0
    for _, text in scored:
        if size + len(text) > max_chars:
            break
        out.append(text)
        size += len(text)
    return "\n\n".join(out) if out else full[:max_chars]
