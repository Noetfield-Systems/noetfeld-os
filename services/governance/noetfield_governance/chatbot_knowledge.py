"""Load public knowledge sources for the website chatbot (no secrets)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

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
    "sme": ("intelligence-lane.md", "faq.md", "pricing-matrix.md"),
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

_BUILTIN_CORE = """## Source: Public site context (core)
Noetfield is governance execution infrastructure. Three contract SKUs: Trust Brief, Copilot Governance Pack, Bank Pilot.
GEL = Governance Execution Layer — see /gel/ and gel-runtime.md.
Developer tools: pip install noetfield-gate · api.noetfield.com
Intake: operations@noetfield.com with RID in subject.
"""

_ENTITY_ALIASES: dict[str, tuple[str, ...]] = {
    "AI Factories": ("ai factories", "ai factory", "factory layer", "factory"),
    "Bank Pilot": ("bank pilot", "shadow mode"),
    "Copilot Governance Pack": ("copilot governance pack", "governance pack", "copilot pack"),
    "Developer Sandbox": ("developer sandbox", "free sandbox", "sandbox"),
    "Federal": ("federal", "government"),
    "GEL": ("gel", "governance execution layer", "api.noetfield.com", "noetfield-gate"),
    "Governance": ("governance", "governance evaluation"),
    "Intelligence": ("intelligence", "intelligence tab", "intelligence page"),
    "MSP": ("msp", "partner"),
    "Noetfield OS": ("noetfield os", "noetfeld-os", "noos"),
    "Pricing": ("pricing", "price", "cost"),
    "Templates": ("templates", "template"),
    "Trust Brief": ("trust brief", "governance brief"),
    "Trust Ledger": ("trust ledger", "tle"),
}

_FOLLOW_UP_RE = re.compile(
    r"^\s*(why|what about|how about|and|so|then|it|that|this|they|them|those|"
    r"why retired|why remove|why rename|should we|is it|does it|can it)\b",
    re.I,
)

_LIFECYCLE_TERMS = {
    "changed",
    "deprecated",
    "old",
    "outdated",
    "removed",
    "renamed",
    "retired",
}

_GENERIC_SUBJECT_RE = re.compile(
    r"\b(?:retired|deprecated|renamed|removed|outdated|changed|old)\s+"
    r"([a-z][a-z0-9 /-]{2,80}?)(?:[?.!,;:]|$)",
    re.I,
)
_OBJECT_SUBJECT_RE = re.compile(
    r"\b(?:about|for|to|the|this|that)\s+"
    r"([a-z][a-z0-9 /-]{0,60}?"
    r"(?:tab|page|route|offer|sku|program|path|pricing|alias|aliases|intake))\b",
    re.I,
)

_PUBLIC_SOURCE_LABELS: dict[str, str] = {
    "PRODUCT_BRIEF.md": "Public product brief",
    "OFFERINGS_LOCKED.md": "Public offerings",
    "ai-factory.md": "AI Factory public page",
    "canada-regulatory-2026.md": "Canada regulatory context",
    "developer-tools.md": "Developer tools",
    "faq-live.md": "Public site context",
    "faq.md": "Public site context",
    "gel-runtime.md": "GEL runtime public context",
    "intelligence-lane.md": "Intelligence lane public context",
    "investor-public.md": "Investor public context",
    "partner-control-layer.md": "Partner control layer",
    "pricing-matrix.md": "Pricing public context",
    "site-surfaces.md": "Public site map",
    "trust-ledger-public.md": "Trust Ledger public context",
}


def detect_question_lanes(question: str) -> list[str]:
    text = (question or "").strip()
    lanes: list[str] = []
    for lane, pattern in _LANE_PATTERNS.items():
        if pattern.search(text):
            lanes.append(lane)
    return lanes


def detect_entities(text: str) -> list[str]:
    """Return canonical public entities mentioned in text."""

    haystack = (text or "").lower()
    found: list[str] = []
    for canonical, aliases in _ENTITY_ALIASES.items():
        if any(alias in haystack for alias in aliases):
            found.append(canonical)
    return found


def _clean_subject_phrase(value: str) -> str | None:
    text = re.sub(r"\s+", " ", value or "").strip(" -_.,;:?!/").lower()
    if not text:
        return None
    text = re.sub(r"^(the|this|that|a|an)\s+", "", text)
    text = re.sub(r"\b(still|used|stay|stays|changed|retired|removed|renamed)\b.*$", "", text).strip()
    if not text or text in {"it", "this", "that", "why", "what"}:
        return None
    if len(text.split()) > 6:
        text = " ".join(text.split()[:6])
    return text.title() if len(text) <= 4 else text


def infer_subject_phrase(text: str) -> str | None:
    """Infer a subject phrase when the prior turn names an entity outside the alias map."""

    source = (text or "").strip()
    for pattern in (_GENERIC_SUBJECT_RE, _OBJECT_SUBJECT_RE):
        match = pattern.search(source)
        if match:
            cleaned = _clean_subject_phrase(match.group(1))
            if cleaned:
                return cleaned
    return None


def active_subject_from_conversation(conversation_state: dict[str, Any] | None) -> str | None:
    """Infer the current subject from recent turns, newest first."""

    if not conversation_state:
        return None
    recent = conversation_state.get("recent") or []
    if not isinstance(recent, list):
        return None
    for event in reversed(recent):
        if not isinstance(event, dict):
            continue
        text = " ".join(
            str(event.get(key) or "") for key in ("message", "reply_preview", "active_subject")
        )
        entities = detect_entities(text)
        if entities:
            return entities[0]
        inferred = infer_subject_phrase(text)
        if inferred:
            return inferred
    return None


def is_follow_up_question(question: str) -> bool:
    text = (question or "").strip()
    if not text:
        return False
    if detect_entities(text):
        return False
    return bool(_FOLLOW_UP_RE.search(text)) or len(text.split()) <= 4


def _word_tokens(text: str) -> set[str]:
    return {t.lower() for t in re.split(r"\W+", text or "") if len(t) > 2}


def _aliases_for(entity: str | None) -> tuple[str, ...]:
    if not entity:
        return ()
    return _ENTITY_ALIASES.get(entity, ()) + ((entity or "").lower(),)


def _mentions_entity(text: str, entity: str | None) -> bool:
    lower = (text or "").lower()
    return any(alias and alias in lower for alias in _aliases_for(entity))


def _mentions_other_entity(text: str, active_subject: str | None) -> bool:
    lower = (text or "").lower()
    for canonical, aliases in _ENTITY_ALIASES.items():
        if canonical == active_subject:
            continue
        if any(alias in lower for alias in aliases):
            return True
    return False


def _has_lifecycle_term(text: str) -> bool:
    return bool(_word_tokens(text) & _LIFECYCLE_TERMS)


def build_query_with_subject(
    question: str,
    *,
    conversation_state: dict[str, Any] | None = None,
) -> tuple[str, str | None, bool]:
    """Resolve elliptical follow-ups for retrieval without hardcoding an answer."""

    text = (question or "").strip()
    mentioned = detect_entities(text)
    if mentioned:
        return text, mentioned[0], False
    subject = active_subject_from_conversation(conversation_state)
    follow_up = bool(subject and is_follow_up_question(text))
    if follow_up:
        return f"{subject}: {text}", subject, True
    return text, subject, False


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _source_block(path: Path, *, core: bool = False) -> str:
    body = _read(path)
    if not body:
        return ""
    label = _PUBLIC_SOURCE_LABELS.get(path.name, path.stem.replace("-", " ").title())
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


def knowledge_bundle_version() -> str:
    manifest = _REPO_ROOT / "data" / "chatbot" / "MANIFEST.json"
    if not manifest.is_file():
        return "NOETFIELD-CHATBOT-UNKNOWN"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "NOETFIELD-CHATBOT-INVALID"
    trace = data.get("trace_id", "NOETFIELD-CHATBOT")
    done = data.get("plans_done", 0)
    distilled = data.get("distilled_at", "")
    suffix = distilled[:10] if distilled else str(len(data.get("knowledge_files", [])))
    return f"{trace}-p{done}-{suffix}"


def knowledge_context_stats() -> dict[str, int | bool | str]:
    """Lightweight health signal for deploy verification."""
    pinned = _pinned_sections()
    full = build_knowledge_context()
    return {
        "loaded": bool(full.strip()),
        "chars": len(full),
        "pinned_chars": len(pinned),
        "knowledge_files": len(list(_KNOWLEDGE_DIR.glob("*.md"))) if _KNOWLEDGE_DIR.is_dir() else 0,
        "knowledge_bundle_version": knowledge_bundle_version(),
    }


def select_relevant_excerpt(
    question: str,
    *,
    max_chars: int = 32_000,
    conversation_state: dict[str, Any] | None = None,
) -> str:
    """Keyword-ranked excerpts with pinned core + lane-forced sources."""
    query, active_subject, is_follow_up = build_query_with_subject(
        question,
        conversation_state=conversation_state,
    )
    lanes = detect_question_lanes(query)
    pinned = _pinned_sections()
    forced = _forced_lane_sections(lanes)
    full = build_knowledge_context()

    parts: list[str] = [pinned]
    if forced and forced not in pinned:
        parts.append(forced)
    if full and full not in "\n\n".join(parts):
        parts.append(full)
    combined = "\n\n---\n\n".join(p for p in parts if p.strip())

    if len(combined) <= max_chars and not active_subject:
        return combined

    tokens = _word_tokens(query)
    subject_tokens = _word_tokens(active_subject or "")
    lifecycle_follow_up = is_follow_up and bool(tokens & _LIFECYCLE_TERMS)
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
        lower = text.lower()
        subject_match = _mentions_entity(lower, active_subject)
        score = sum(1 for t in tokens if t in lower)
        score += 4 * sum(1 for t in subject_tokens if t in lower)
        if subject_match:
            score += 8
        if active_subject and _mentions_other_entity(lower, active_subject) and not subject_match:
            score -= 12
        if lifecycle_follow_up and _has_lifecycle_term(lower) and not subject_match:
            score -= 30
        for lane in lanes:
            if lane in lower:
                score += 2
        scored.append((score, text))
    scored.sort(key=lambda x: (-x[0], x[1]))

    out: list[str] = []
    size = 0
    for score, text in scored:
        if active_subject and score <= 0:
            continue
        if size + len(text) > budget:
            break
        out.append(text)
        size += len(text)
    ranked = "\n\n".join(out) if out else remainder[:budget]

    head = _BUILTIN_CORE if active_subject and is_follow_up else pinned
    if forced:
        head = head + "\n\n---\n\n" + forced
    if active_subject:
        marker = (
            "## Conversation Kernel\n"
            f"Active subject: {active_subject}\n"
            f"Follow-up resolved: {'yes' if is_follow_up else 'no'}\n"
            f"Retrieval query: {query}\n"
            "Entity boundary: do not borrow lifecycle facts from another entity.\n"
            "Missing detail rule: if sources do not give the reason/detail for the active subject, say the detail is not in the public knowledge.\n"
        )
        head = marker + "\n---\n\n" + head
    return head + "\n\n---\n\n" + ranked


def clear_knowledge_cache() -> None:
    build_knowledge_context.cache_clear()
