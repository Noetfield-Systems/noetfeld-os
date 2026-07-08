#!/usr/bin/env python3
"""NOOS machine gate — PR conflict resolver skill lock + hygiene."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "data/noos-pr-conflict-skill-lock-v1.json"
STUB_SKILL = ROOT / ".cursor/skills/pr-conflict-resolver/SKILL.md"
LOCK_DOC = ROOT / "docs/_NOOS_AGENT/[NOOS-AGENT-20260708-001]_PR_CONFLICT_RESOLVER_MANDATORY_v1_LOCKED.md"
CURSOR_RULE = ROOT / ".cursor/rules/noos-pr-conflict-resolver-mandatory.mdc"
HOOK = ROOT / ".cursor/hooks/noos-pr-conflict-guard.py"

CONFLICT_MARKERS = ("<<<<<<<", ">>>>>>>")


def sha_prefix(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def sg_root() -> Path | None:
    env = os.environ.get("SG_SSOT_ROOT", "").strip()
    if env:
        p = Path(os.path.expanduser(env))
        return p if p.is_dir() else None
    default = Path.home() / "Desktop/Noetfield-Systems/sina-governance-SSOT"
    return default if default.is_dir() else None


def tracked_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def files_with_conflict_markers() -> list[str]:
    hits: list[str] = []
    for rel in tracked_files():
        path = ROOT / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(m in text for m in CONFLICT_MARKERS):
            hits.append(rel)
    return hits


def merge_in_progress() -> bool:
    return (ROOT / ".git/MERGE_HEAD").is_file()


def unmerged_paths() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def matches_governance_glob(path: str, globs: list[str]) -> bool:
    for pattern in globs:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern.rstrip("/") + "/*"):
            return True
    return False


def verify(*, require_sg: bool = False, mac_desktop: bool = False) -> dict[str, Any]:
    issues: list[str] = []
    checks: dict[str, Any] = {}

    if not LOCK.is_file():
        issues.append("missing:noos_lock_manifest")
        lock: dict[str, Any] = {}
    else:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))

    for label, path in [
        ("lock_manifest", LOCK),
        ("skill_stub", STUB_SKILL),
        ("lock_doc", LOCK_DOC),
        ("cursor_rule", CURSOR_RULE),
        ("hook", HOOK),
    ]:
        checks[f"{label}_exists"] = path.is_file()
        if not path.is_file():
            issues.append(f"missing:{path.relative_to(ROOT)}")

    sg = lock.get("sg_canonical") or {}
    sg_base = sg_root()
    checks["sg_root_found"] = sg_base is not None
    if sg_base and isinstance(sg, dict):
        sg_skill = sg_base / str(sg.get("skill") or "")
        sg_lock = sg_base / str(sg.get("lock_manifest") or "")
        checks["sg_skill_exists"] = sg_skill.is_file()
        checks["sg_lock_exists"] = sg_lock.is_file()
        if sg_skill.is_file():
            got = sha_prefix(sg_skill)
            want = str(sg.get("skill_sha256_prefix") or "")
            checks["sg_skill_hash_ok"] = not want or got == want
            if want and got != want:
                issues.append(f"sg_skill_hash_drift:{got}!={want}")
        if not checks.get("sg_skill_exists"):
            if require_sg:
                issues.append("missing:sg_canonical_skill")
        if mac_desktop:
            app = sg_base / "desktop-app/PR-Conflict-Resolver-Report.app"
            shortcut = Path.home() / "Desktop/PR-Conflict-Resolver-Report.app"
            checks["sg_desktop_app"] = app.is_dir()
            checks["desktop_shortcut"] = shortcut.is_dir()
            if not checks["sg_desktop_app"]:
                issues.append("missing:sg_desktop_app")
            if not checks["desktop_shortcut"]:
                issues.append("missing:desktop_shortcut")
    elif require_sg or mac_desktop:
        issues.append("missing:sg_ssot_root")

    marker_hits = files_with_conflict_markers()
    checks["conflict_markers_in_tree"] = marker_hits
    if marker_hits:
        issues.append(f"conflict_markers:{','.join(marker_hits[:5])}")

    unmerged = unmerged_paths()
    checks["unmerged_paths"] = unmerged
    checks["merge_in_progress"] = merge_in_progress()
    if unmerged:
        issues.append(f"unmerged:{','.join(unmerged[:5])}")

    globs = list(lock.get("governance_sensitive_globs") or [])
    gov_unmerged = [p for p in unmerged if matches_governance_glob(p, globs)]
    checks["governance_unmerged"] = gov_unmerged
    if gov_unmerged:
        issues.append(
            "governance_conflict_requires_skill:"
            + ",".join(gov_unmerged[:5])
            + " · load .cursor/skills/pr-conflict-resolver/SKILL.md"
        )

    ok = not issues
    return {
        "schema": "noos-pr-conflict-resolution-verify-v1",
        "ok": ok,
        "issues": issues,
        "checks": checks,
        "lock_status": lock.get("status"),
        "report_line": (
            "noos_pr_conflict_resolution · ALL PASS"
            if ok
            else f"noos_pr_conflict_resolution · FAIL ({len(issues)})"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--require-sg", action="store_true", help="Fail if SG SSOT root or canonical skill missing")
    ap.add_argument("--mac-desktop", action="store_true", help="Require desktop eval apps on Mac")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = verify(require_sg=args.require_sg, mac_desktop=args.mac_desktop)
    if args.write_receipt:
        out = ROOT / "receipts/proof/noos-pr-conflict-skill-lock-v1.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(out.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
        for issue in row.get("issues") or []:
            print(f"  {issue}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
