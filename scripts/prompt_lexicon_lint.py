#!/usr/bin/env python3
"""
prompt_lexicon_lint.py — deterministic scanner for classifier-trigger vocabulary
in context-entering text (CLAUDE.md, AGENTS.md, copilot-instructions, manifests,
dispatch prompts, issue templates).

Usage:
    python3 prompt_lexicon_lint.py [--lexicon PROMPT_LEXICON_v1.json] FILE [FILE...]
    cat prompt.txt | python3 prompt_lexicon_lint.py -

Exit codes: 0 = clean or LOW-only · 1 = MEDIUM/HIGH findings present.
Output: one line per hit  SEVERITY  file:line  term -> replacement
Never edits anything. Pinned custody artifacts are out of scope by law.
"""
import argparse
import json
import os
import re
import sys

DEFAULT_LEXICON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "PROMPT_LEXICON_v1.json")


def scan(text, name, terms):
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        for t in terms:
            for m in re.finditer(t["pattern"], line, re.IGNORECASE):
                hits.append({
                    "severity": t["severity"], "file": name, "line": n,
                    "term": m.group(0), "replacement": t["replacement"],
                })
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lexicon", default=DEFAULT_LEXICON)
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    terms = json.load(open(args.lexicon))["terms"]
    all_hits = []
    for path in args.files:
        if path == "-":
            all_hits += scan(sys.stdin.read(), "<stdin>", terms)
        else:
            with open(path, errors="ignore") as fh:
                all_hits += scan(fh.read(), path, terms)

    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_hits.sort(key=lambda h: (order[h["severity"]], h["file"], h["line"]))

    if args.json:
        print(json.dumps(all_hits, indent=2))
    else:
        for h in all_hits:
            print(f'{h["severity"]:6} {h["file"]}:{h["line"]}  '
                  f'"{h["term"]}" -> {h["replacement"]}')
        counts = {}
        for h in all_hits:
            counts[h["severity"]] = counts.get(h["severity"], 0) + 1
        print(f'\nTOTAL: {len(all_hits)} '
              f'(HIGH {counts.get("HIGH",0)} / MEDIUM {counts.get("MEDIUM",0)} '
              f'/ LOW {counts.get("LOW",0)})')

    return 1 if any(h["severity"] in ("HIGH", "MEDIUM") for h in all_hits) else 0


if __name__ == "__main__":
    sys.exit(main())
