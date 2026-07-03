#!/usr/bin/env python3
"""Cost policy scanner for CI.

Checks for:
- forbidden model/provider identifiers in code/config/workflows
- scheduled workflows that require cost receipts
- missing required receipt fields in loop runner

Exits 0 if clean, 1 if violations found. Emits JSON summary to stdout.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data/cost_policy_machine.json"


def load_policy(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_files(globs: list[str], root: Path) -> list[Path]:
    out = []
    for g in globs:
        matches = list(root.glob(g))
        out.extend(matches)
    # dedupe preserving order
    seen = set()
    dedup = []
    for p in out:
        s = str(p)
        if s not in seen:
            seen.add(s)
            dedup.append(p)
    return dedup


def scan_forbidden_strings(files: list[Path], forbidden: list[str]) -> dict:
    hits = []
    patterns = [re.compile(re.escape(s), re.IGNORECASE) for s in forbidden]
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for s, pat in zip(forbidden, patterns):
            if pat.search(text):
                hits.append({"file": str(p), "forbidden": s})
    return {"hits": hits}


def find_scheduled_workflows(workflows_dir: Path) -> list[Path]:
    out = []
    for p in workflows_dir.glob("**/*.yml"):
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "schedule:" in txt or "cron:" in txt:
            out.append(p)
    return out


def check_receipt_fields(loop_runner_path: Path, required_fields: list[str]) -> dict:
    try:
        txt = loop_runner_path.read_text(encoding="utf-8")
    except Exception:
        return {"ok": False, "reason": "cannot_read_loop_runner"}
    missing = []
    for f in required_fields:
        if f not in txt:
            missing.append(f)
    return {"ok": len(missing) == 0, "missing": missing}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(POLICY_PATH))
    args = ap.parse_args()

    policy = load_policy(Path(args.policy))

    globs = policy.get("scan_file_globs") or ["**/*"]
    files = iter_files(globs, ROOT)

    forbidden_models = policy.get("forbidden_models", [])
    forbidden_providers = policy.get("forbidden_providers", [])
    forbidden = list(set(forbidden_models + forbidden_providers))

    forbidden_hits = scan_forbidden_strings(files, forbidden)

    # scheduled workflows
    sched = find_scheduled_workflows(ROOT / ".github/workflows")
    sched_files = [str(p) for p in sched]

    # check loop runner for receipt fields
    loop_runner = ROOT / "scripts/noos_loop_runner_v1.py"
    receipt_check = check_receipt_fields(loop_runner, policy.get("receipt_requirements", []))

    violations = []
    if forbidden_hits["hits"]:
        violations.append({"type": "forbidden_strings", "detail": forbidden_hits["hits"]})

    if sched_files and not receipt_check.get("ok"):
        violations.append({"type": "missing_receipt_fields", "detail": receipt_check})

    # Also fail on unknown model/provider patterns (simple heuristic: look for "model": "gpt-" or provider: openrouter)
    unknown_hits = []
    unknown_pattern = re.compile(r"model\W*:\W*\"?([a-zA-Z0-9_\-/\.]+)\"?", re.IGNORECASE)
    provider_pattern = re.compile(r"provider\W*:\W*\"?([a-zA-Z0-9_\-/\.]+)\"?", re.IGNORECASE)
    for p in files:
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in unknown_pattern.findall(txt):
            # skip allowed
            if m in policy.get("allowed_default_models", []):
                continue
            # skip none/placeholder
            if m.lower() in ("none", "null", "0"):
                continue
            # if it's in forbidden, it's already reported
            if any(f.lower() in m.lower() for f in forbidden):
                continue
            # heuristically flag unknown long model ids
            if m.startswith("gpt-") or "/" in m or m.count("."):
                unknown_hits.append({"file": str(p), "model_mention": m})
        for prov in provider_pattern.findall(txt):
            if prov in policy.get("allowed_providers", []) or prov in policy.get("forbidden_providers", []):
                continue
            if prov.strip():
                unknown_hits.append({"file": str(p), "provider_mention": prov})

    if unknown_hits:
        violations.append({"type": "unknown_model_provider_mentions", "detail": unknown_hits[:25]})

    summary = {
        "policy_path": str(Path(args.policy)),
        "forbidden_hits_count": len(forbidden_hits.get("hits", [])),
        "scheduled_workflow_count": len(sched_files),
        "scheduled_workflow_files": sched_files,
        "loop_runner_receipt_check": receipt_check,
        "unknown_mentions_count": len(unknown_hits),
        "violations_found": len(violations) > 0,
        "violations": violations,
    }

    print(json.dumps(summary, indent=2))

    return 1 if summary["violations_found"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
