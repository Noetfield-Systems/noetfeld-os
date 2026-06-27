#!/usr/bin/env python3
"""Distill public www HTML pages into data/chatbot/knowledge/*.md (Phase 3 plan 021)."""

from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "data" / "chatbot" / "knowledge"
MANIFEST_PATH = ROOT / "data" / "chatbot" / "MANIFEST.json"

WWW_SOURCES: tuple[tuple[str, str, str, str], ...] = (
    (
        "pricing/index.html",
        "pricing-matrix.md",
        "buyer",
        "https://www.noetfield.com/pricing/",
    ),
    (
        "faq/index.html",
        "faq-live.md",
        "buyer",
        "https://www.noetfield.com/faq/",
    ),
)

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def _clean(text: str) -> str:
    text = html.unescape(_TAG.sub(" ", text))
    return _WS.sub(" ", text).strip()


def _extract_faq_sections(html_text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    for match in re.finditer(
        r"<section>\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>\s*</section>",
        html_text,
        flags=re.I | re.S,
    ):
        title = _clean(match.group(1))
        body = _clean(match.group(2))
        if title and body:
            sections.append((title, body))
    return sections


def _extract_offer_cards(html_text: str) -> list[tuple[str, str, str]]:
    cards: list[tuple[str, str, str]] = []
    for match in re.finditer(
        r'<article class="nf-offer-card[^"]*">\s*'
        r'<p class="meta">(.*?)</p>\s*'
        r'<p class="price">(.*?)</p>\s*'
        r"<p>(.*?)</p>",
        html_text,
        flags=re.I | re.S,
    ):
        cards.append((_clean(match.group(1)), _clean(match.group(2)), _clean(match.group(3))))
    return cards


def _extract_pack_cards(html_text: str) -> list[tuple[str, str, str]]:
    cards: list[tuple[str, str, str]] = []
    for match in re.finditer(
        r'<article class="nf-pack-card[^"]*"[^>]*>\s*'
        r'<p class="nf-pack-card__tag">(.*?)</p>\s*'
        r'<p class="nf-pack-card__price">(.*?)</p>\s*'
        r"<p>(.*?)</p>",
        html_text,
        flags=re.I | re.S,
    ):
        cards.append((_clean(match.group(1)), _clean(match.group(2)), _clean(match.group(3))))
    return cards


def _extract_table_rows(html_text: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for match in re.finditer(
        r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>",
        html_text,
        flags=re.I | re.S,
    ):
        rows.append((_clean(match.group(1)), _clean(match.group(2)), _clean(match.group(3))))
    return rows


def _frontmatter(
    *,
    lane: str,
    source_path: str,
    source_url: str,
    content_hash: str,
) -> str:
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        "---\n"
        f"lane: {lane}\n"
        "public: true\n"
        f"source_path: {source_path}\n"
        f"source_url: {source_url}\n"
        f"updated: {updated}\n"
        f"content_hash: {content_hash}\n"
        "---\n\n"
    )


def distill_pricing(html_text: str) -> str:
    lines = ["# Noetfield pricing matrix (distilled from www)", ""]
    lead = re.search(r'<p class="nf-lead">(.*?)</p>', html_text, flags=re.I | re.S)
    if lead:
        lines += ["## Summary", _clean(lead.group(1)), ""]

    cards = _extract_offer_cards(html_text)
    if cards:
        lines += ["## Noetfield Intelligence (SME)", ""]
        for meta, price, desc in cards:
            lines += [f"### {meta}", f"**Price:** {price}", desc, ""]

    pack_cards = _extract_pack_cards(html_text)
    if pack_cards:
        lines += ["## Access paths and contract programs", ""]
        for tag, price, desc in pack_cards:
            lines += [f"### {tag}", f"**Price:** {price}", desc, ""]

    rows = _extract_table_rows(html_text)
    if rows:
        lines += ["## Sandbox vs production", "", "| Capability | Sandbox | Production |", "|---|---|---|"]
        for cap, sandbox, prod in rows:
            lines.append(f"| {cap} | {sandbox} | {prod} |")
        lines.append("")

    milestone = re.findall(
        r'<a class="nf-milestone-step[^"]*"[^>]*>.*?<strong>(.*?)</strong><span>(.*?)</span></a>',
        html_text,
        flags=re.I | re.S,
    )
    if milestone:
        lines += ["## Milestone ladder", ""]
        for price, label in milestone:
            lines.append(f"- **{_clean(price)}** — {_clean(label)}")
        lines.append("")

    lines += [
        "## Contract SKUs (locked)",
        "",
        "Three contract SKUs only: Copilot Governance Pack ($2k–10k), Trust Brief ($10k), Bank Pilot (custom).",
        "Free sandbox is developer access — not a fourth retail SKU.",
        "",
    ]
    return "\n".join(lines).strip() + "\n"


def distill_faq(html_text: str) -> str:
    lines = ["# Noetfield FAQ (live www distill)", ""]
    for title, body in _extract_faq_sections(html_text):
        lines += [f"## {title}", body, ""]
    return "\n".join(lines).strip() + "\n"


def _hash_body(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def distill_one(source_rel: str, out_name: str, lane: str, source_url: str) -> Path:
    src = ROOT / source_rel
    if not src.is_file():
        raise FileNotFoundError(src)
    html_text = src.read_text(encoding="utf-8")
    if "faq/" in source_rel:
        body = distill_faq(html_text)
    else:
        body = distill_pricing(html_text)
    content_hash = _hash_body(body)
    doc = _frontmatter(
        lane=lane,
        source_path=source_rel,
        source_url=source_url,
        content_hash=content_hash,
    ) + body
    out = KNOWLEDGE_DIR / out_name
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


def update_manifest(outputs: list[str]) -> None:
    if not MANIFEST_PATH.is_file():
        return
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = list(data.get("knowledge_files", []))
    for name in outputs:
        if name not in files:
            files.append(name)
    data["knowledge_files"] = sorted(files)
    data["distilled_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    MANIFEST_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    written: list[str] = []
    for source_rel, out_name, lane, source_url in WWW_SOURCES:
        out = distill_one(source_rel, out_name, lane, source_url)
        written.append(out_name)
        print(f"OK {source_rel} → {out.relative_to(ROOT)}")
    update_manifest(written)
    print(f"OK manifest → {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
