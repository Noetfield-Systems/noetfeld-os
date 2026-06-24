#!/usr/bin/env python3
"""NF founder reply loop — translate + language gate before founder sees reply."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from nf_factory_lib_v1 import iso_now, load_json, repo_root, write_sina

ROOT = repo_root()
GLOSSARY = ROOT / "data/nf-founder-reply-glossary-v1.json"
GATE = ROOT / "scripts/nf_agent_report_language_gate_v1.py"


def translate(text: str) -> tuple[str, list[str]]:
    data = load_json(GLOSSARY) or {}
    notes: list[str] = []
    out = text or ""
    for pat in data.get("strip_patterns") or []:
        out = re.sub(re.escape(pat) + r"[^\n]*", "", out, flags=re.I)
    for key in sorted((data.get("translations") or {}).keys(), key=len, reverse=True):
        val = data["translations"][key]
        if re.search(re.escape(key), out, re.I):
            out = re.sub(re.escape(key), val, out, flags=re.I)
    if out.count("·") >= 3:
        notes.append("internal label chain — rewrite as sentences")
        out = re.sub(r"\s*·\s*", "; ", out)
    return out.strip(), notes


def run_gate(text: str, *, why: bool = False) -> dict:
    cmd = [sys.executable, str(GATE), "--scan-text", text, "--json"]
    if why:
        cmd.insert(-1, "--why")
    out = subprocess.check_output(cmd, cwd=ROOT, text=True)
    return json.loads(out)


def evaluate(*, draft: str, founder_message: str = "") -> dict:
    why = bool(re.search(r"\b(why|understand|meaning|stupid|wasted)\b", founder_message, re.I))
    translated, notes = translate(draft)
    gate_draft = run_gate(draft, why=why)
    gate_plain = run_gate(translated, why=why) if translated != draft else gate_draft
    ok = gate_plain.get("ok") or (not gate_draft.get("ok") and gate_plain.get("ok"))
    verdict = "SHIP" if ok and translated == draft else "SHIP_TRANSLATED" if ok else "REJECT"
    hints = [h.get("label", "") for h in (gate_draft.get("hits") or []) if h.get("label")]
    return {
        "schema": "nf-founder-reply-loop-v1",
        "at": iso_now(),
        "ok": ok,
        "verdict": verdict,
        "founder_text": translated if ok else "",
        "rewrite_hints": hints or ["Explain in normal English what changed for the founder"],
        "translate_notes": notes,
        "gate": gate_draft,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="")
    ap.add_argument("--file", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8", errors="replace")
    if not body and not sys.stdin.isatty():
        body = sys.stdin.read()
    row = evaluate(draft=body, founder_message=args.founder_message)
    if args.write_receipt:
        write_sina("nf-founder-reply-loop-v1.json", row)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(f"verdict={row['verdict']} ok={row['ok']}")
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
