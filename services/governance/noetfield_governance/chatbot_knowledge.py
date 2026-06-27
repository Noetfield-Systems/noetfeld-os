"""Load public knowledge sources for the website chatbot (no secrets)."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_KNOWLEDGE_DIR = _REPO_ROOT / "data" / "chatbot" / "knowledge"
_EXTRA_MD = (
    _REPO_ROOT / "PRODUCT_BRIEF.md",
    _REPO_ROOT / "OFFERINGS_LOCKED.md",
)

# Always inject these knowledge files when question lane matches (even when trimming).
_LANE_FILES: dict[str, tuple[str, ...]] = {
    "developer": (
        "gel-runtime.md",
        "developer-tools.md",
        "site-surfaces.md",
    ),
    "investor": ("investor-public.md", "site-surfaces.md"),
    "gel": ("gel-runtime.md", "site-surfaces.md"),
    "sme": ("intelligence-lane.md", "faq.md"),
    "trust": ("trust-ledger-public.md", "PRODUCT_BRIEF.md"),
}

_LANE_PATTERNS: dict[str, re.Pattern[str]] = {
    "developer": re.compile(
        r"\b(pypi|pip install|noetfield[- ]gate|noetfield decide|cli|npm|package|"
        r"python|developer|api\.noetfield|chain tool)\b",
        re.I,
    ),
    "gel": re.compile(
        r"\b(gel|governance execution layer|/gel/|api\.noetfield|pre-execution|"
        r"approve|decline|review)\b",
        re.I,
    ),
    "investor": re.compile(
        r"\b(investor|vc|diligence|fund|cap table|shadow governance brief)\b",
        re.I,
    ),
    "sme": re.compile(
        r"\b(mortgage|broker|immigration|sme|diagnostic sprint|spreadsheet|"
        r"toronto|canadian)\b",
        re.I,
    ),
    "trust": re.compile(
        r"\b(trust ledger|tle|trust brief|audit trail|tamper)\b",
        re.I,
    ),
}

_BUILTIN_CORE = """## Source: faq.md (core)
Noetfield is governance execution infrastructure. Three contract SKUs: Trust Brief, Copilot Governance Pack, Bank Pilot.
GEL = Governance Execution Layer — see /gel/ and gel-runtime.md.
Developer tools: pip install noetfield-gate · api.noetfield.com
Intake: operations@noetfield.com with RID in subject.
"""


def detect_question_lanes(question: str) -> list[str]:
    text = (question or "").strip()
    lanes: list[str] = []
    for lane, pattern in _LANE_PATTERNS.items():
        if pattern.search(text):
            lanes.append(lane)
    return lanes


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _source_block(path: Path, *, core: bool = False) -> str:
    body = _read(path)
    if not body:
        return ""
    if path.parent.name == "knowledge":
        label = f"knowledge/{path.name}"
    else:
        label = path.name
    if core:
        label = f"{label} (core)"
    return f"## Source: {label}\n{body}"


@lru_cache(maxsize=1)
def build_knowledge_context() -> str:
    """Single context block injected into the model system instruction."""
    chunks: list[str] = []
    if _KNOWLEDGE_DIR.is_dir():
        for path in sorted(_KNOWLEDGE_DIR.glob("*.md")):
            block = _source_block(path)
            if block:
                chunks.append(block)
    for path in _EXTRA_MD:
        block = _source_block(path)
        if block:
            chunks.append(block)
    if not chunks:
        return _BUILTIN_CORE
    return "\n\n---\n\n".join(chunks)


_PINNED_PATHS: tuple[Path, ...] = (
    _REPO_ROOT / "OFFERINGS_LOCKED.md",
    _REPO_ROOT / "data" / "chatbot" / "knowledge" / "faq.md",
    _REPO_ROOT / "data" / "chatbot" / "knowledge" / "gel-runtime.md",
    _REPO_ROOT / "data" / "chatbot" / "knowledge" / "site-surfaces.md",
)


def _pinned_sections() -> str:
    chunks: list[str] = []
    for path in _PINNED_PATHS:
        block = _source_block(path, core=True)
        if block:
            chunks.append(block)
    if not chunks:
        return _BUILTIN_CORE
    return "\n\n---\n\n".join(chunks)


def _forced_lane_sections(lanes: list[str]) -> str:
    if not lanes:
        return ""
    names: list[str] = []
    seen: set[str] = set()
    for lane in lanes:
        for name in _LANE_FILES.get(lane, ()):
            if name in seen:
                continue
            seen.add(name)
            names.append(name)
    chunks: list[str] = []
    for name in names:
        path = _KNOWLEDGE_DIR / name
        if not path.is_file():
            path = _REPO_ROOT / name
        block = _source_block(path)
        if block:
            chunks.append(block)
    return "\n\n---\n\n".join(chunks)


def knowledge_context_stats() -> dict[str, int | bool]:
    """Lightweight health signal for deploy verification."""
    pinned = _pinned_sections()
    full = build_knowledge_context()
    return {
        "loaded": bool(full.strip()),
        "chars": len(full),
        "pinned_chars": len(pinned),
        "knowledge_files": len(list(_KNOWLEDGE_DIR.glob("*.md"))) if _KNOWLEDGE_DIR.is_dir() else 0,
    }


def select_relevant_excerpt(question: str, *, max_chars: int = 32_000) -> str:
    """Keyword-ranked excerpts with pinned core + lane-forced sources."""
    lanes = detect_question_lanes(question)
    pinned = _pinned_sections()
    forced = _forced_lane_sections(lanes)
    full = build_knowledge_context()

    parts: list[str] = [pinned]
    if forced and forced not in pinned:
        parts.append(forced)
    if full and full not in "\n\n".join(parts):
        parts.append(full)
    combined = "\n\n---\n\n".join(p for p in parts if p.strip())

    if len(combined) <= max_chars:
        return combined

    tokens = {t.lower() for t in question.split() if len(t) > 2}
    remainder = full
    if pinned and full.startswith(pinned):
        remainder = full[len(pinned) :].lstrip("\n-")
    budget = max(6000, max_chars - len(pinned) - len(forced) - 16) if pinned else max_chars

    if not tokens or not remainder.strip():
        return combined[:max_chars]

    sections = remainder.split("\n## ")
    scored: list[tuple[int, str]] = []
    for i, section in enumerate(sections):
        text = section if i == 0 else "## " + section
        score = sum(1 for t in tokens if t in text.lower())
        for lane in lanes:
            if lane in text.lower():
                score += 2
        scored.append((score, text))
    scored.sort(key=lambda x: (-x[0], x[1]))

    out: list[str] = []
    size = 0
    for _, text in scored:
        if size + len(text) > budget:
            break
        out.append(text)
        size += len(text)
    ranked = "\n\n".join(out) if out else remainder[:budget]

    head = pinned
    if forced:
        head = head + "\n\n---\n\n" + forced
    return head + "\n\n---\n\n" + ranked


def clear_knowledge_cache() -> None:
    build_knowledge_context.cache_clear()
