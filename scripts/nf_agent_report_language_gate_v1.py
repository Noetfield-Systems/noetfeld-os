#!/usr/bin/env python3
"""NF agent report language gate — machine-enforced anti-parrot law."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data/nf-agent-report-language-standard-v1.json"

MACHINE_LINE = re.compile(
    r"(email-defer\s*·|sites=RED|main=\d+/\d+|defer flag ON|lift=NO)",
    re.I,
)
LABEL_SOUP = re.compile(r"(\w+\s*=\s*\w+[\s;·]{0,3}){2,}")
DOT_SOUP = re.compile(r"[^.\n]{0,120}·[^.\n]{0,80}·[^.\n]{0,80}·")
THEATER = re.compile(
    r"\b(completed successfully|all green|shipped successfully|validator snapshot)\b",
    re.I,
)
WHY_QUESTION = re.compile(r"\b(why|why\?|why!!|understand|meaning|benefit)\b", re.I)
VERB_HINT = re.compile(
    r"\b(is|are|was|were|has|have|still|because|means|blocks|serves|shows|failed|passes|continues|changed|defers|helps|explains|you|your|for you)\b",
    re.I,
)
JARGON_TOKEN = re.compile(
    r"\b(SSOT|probe|pulse|wired|receipt|validator|defer_active|witness note|parrot|WBC-P\d|TF-P\d|nf-gaos)\b",
    re.I,
)
PARROT_CLAIM = re.compile(
    r"\b(wired|PASS|STOP|shipped|updated SSOT|gate PASS|verify-doc-ssot passed)\b",
    re.I,
)
BENEFIT_HINT = re.compile(
    r"\b(you|your|for you|means|because|so |which means|helps|blocked|ready|unlock|understand|explain|can see|cannot see)\b",
    re.I,
)


def scan_text(text: str, *, founder_asked_why: bool = False) -> dict:
    t = (text or "").strip()
    hits: list[dict] = []
    if not t:
        return {"ok": True, "hits": [], "score": 100}

    if MACHINE_LINE.search(t) and not VERB_HINT.search(t[:400]):
        hits.append({"id": "machine_line_as_answer", "label": "Receipt line without human explanation"})
    if LABEL_SOUP.search(t) and t.count("·") >= 3 and not VERB_HINT.search(t[:300]):
        hits.append({"id": "label_soup", "label": "Label chain without meaning"})
    if DOT_SOUP.search(t) and not VERB_HINT.search(t[:350]):
        hits.append({"id": "dot_soup", "label": "Middle-dot token chain — parrot"})
    if THEATER.search(t) and "because" not in t.lower() and "which means" not in t.lower():
        hits.append({"id": "green_theater", "label": "Success claim without explaining what changed"})

    if len(JARGON_TOKEN.findall(t)) >= 4 and not BENEFIT_HINT.search(t[:500]):
        hits.append({"id": "jargon_wall", "label": "Jargon without plain-English benefit"})
    if PARROT_CLAIM.search(t) and len(t) < 280 and not BENEFIT_HINT.search(t):
        hits.append({"id": "parrot_claim_only", "label": "PASS/wired alone — no meaning"})

    if founder_asked_why or WHY_QUESTION.search(t[:200]):
        first = t.split("\n\n")[0][:500]
        if not VERB_HINT.search(first):
            hits.append({"id": "why_without_cause", "label": "Why question but no human causal language"})
        if "because" not in t.lower() and "so " not in t.lower() and "which means" not in t.lower():
            hits.append({"id": "missing_causal_link", "label": "No because/so/which means"})

    score = max(0, 100 - 20 * len(hits))
    return {"ok": len(hits) == 0, "hits": hits, "score": score}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-text", default="")
    ap.add_argument("--scan-file", default="")
    ap.add_argument("--why", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = args.scan_text
    if args.scan_file:
        text = Path(args.scan_file).read_text(encoding="utf-8", errors="replace")
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read()

    row = scan_text(text, founder_asked_why=args.why)
    row["schema"] = "nf-agent-report-language-gate-v1"
    row["ssot"] = str(SSOT.relative_to(ROOT))
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(f"LANGUAGE ok={row['ok']} score={row['score']} hits={len(row['hits'])}")
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
