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
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data/cost_policy_machine.json"

# Policy denylist and scanner tooling must not self-trigger violations.
FORBIDDEN_SCAN_EXCLUDE = {
    POLICY_PATH.resolve(),
    (ROOT / "scripts/cost_policy_scan.py").resolve(),
    (ROOT / "scripts/runtime_routing_guard.py").resolve(),
    (ROOT / "docs/NOOS_COPILOT_DISPATCHER_AUTHORITY.md").resolve(),
}

UNKNOWN_SCAN_GLOBS = [
    ".github/workflows/**/*.yml",
    "cloud/workers/**/*.js",
    "data/noos-model-router*.json",
    "config/model-router.yml",
]


def load_policy(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_files(globs: list[str], root: Path) -> list[Path]:
    out: list[Path] = []
    for g in globs:
        out.extend(root.glob(g))
    seen: set[str] = set()
    dedup: list[Path] = []
    for p in out:
        key = str(p)
        if key not in seen:
            seen.add(key)
            dedup.append(p)
    return dedup


def scan_forbidden_strings(files: list[Path], forbidden: list[str]) -> dict:
    hits = []
    patterns = [re.compile(re.escape(s), re.IGNORECASE) for s in forbidden]
    for p in files:
        if p.resolve() in FORBIDDEN_SCAN_EXCLUDE:
            continue
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
    missing = [f for f in required_fields if f not in txt]
    return {"ok": len(missing) == 0, "missing": missing}


def scan_unknown_model_provider(
    files: list[Path],
    *,
    policy: dict,
    forbidden: list[str],
) -> list[dict]:
    unknown_hits: list[dict] = []
    allowed_models = set(policy.get("allowed_default_models", []))
    allowed_providers = set(policy.get("allowed_providers", []))
    forbidden_providers = set(policy.get("forbidden_providers", []))
    model_pattern = re.compile(r"model\W*:\W*\"?([a-zA-Z0-9_\-/\.]+)\"?", re.IGNORECASE)
    provider_pattern = re.compile(r"provider\W*:\W*\"?([a-zA-Z0-9_\-/\.]+)\"?", re.IGNORECASE)

    for p in files:
        if p.resolve() in FORBIDDEN_SCAN_EXCLUDE:
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in model_pattern.findall(txt):
            if m in allowed_models or m.lower() in ("none", "null", "0"):
                continue
            if any(f.lower() in m.lower() for f in forbidden):
                continue
            if m.startswith("gpt-") or "/" in m or m.count("."):
                unknown_hits.append({"file": str(p), "model_mention": m})
        for prov in provider_pattern.findall(txt):
            if prov in allowed_providers or prov in forbidden_providers:
                continue
            if prov.strip() and prov not in ("provider", "str"):
                unknown_hits.append({"file": str(p), "provider_mention": prov})
    return unknown_hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(POLICY_PATH))
    args = ap.parse_args()

    policy = load_policy(Path(args.policy))

    globs = policy.get("scan_file_globs") or ["**/*"]
    files = iter_files(globs, ROOT)
    unknown_files = iter_files(UNKNOWN_SCAN_GLOBS, ROOT)

    forbidden_models = policy.get("forbidden_models", [])
    forbidden_providers = policy.get("forbidden_providers", [])
    forbidden = list(set(forbidden_models + forbidden_providers))

    forbidden_hits = scan_forbidden_strings(files, forbidden)

    sched = find_scheduled_workflows(ROOT / ".github/workflows")
    sched_files = [str(p) for p in sched]

    loop_runner = ROOT / "scripts/noos_loop_runner_v1.py"
    receipt_check = check_receipt_fields(loop_runner, policy.get("receipt_requirements", []))

    violations = []
    if forbidden_hits["hits"]:
        violations.append({"type": "forbidden_strings", "detail": forbidden_hits["hits"]})

    if sched_files and not receipt_check.get("ok"):
        violations.append({"type": "missing_receipt_fields", "detail": receipt_check})

    unknown_hits = scan_unknown_model_provider(unknown_files, policy=policy, forbidden=forbidden)
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
