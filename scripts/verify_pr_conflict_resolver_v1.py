#!/usr/bin/env python3
"""Machine gate: PR conflict resolver skill wiring + hygiene (fail-closed)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ok(msg: str) -> None:
    print(f"OK   verify-pr-conflict-resolver: {msg}")


def fail(msg: str) -> None:
    print(f"FAIL verify-pr-conflict-resolver: {msg}", file=sys.stderr)


def main() -> int:
    errors = 0
    ssot_path = ROOT / "data" / "nf-pr-conflict-resolver-v1.json"
    if not ssot_path.is_file():
        fail(f"missing {ssot_path.relative_to(ROOT)}")
        return 1
    ssot = json.loads(ssot_path.read_text(encoding="utf-8"))
    ok("data SSOT present")

    required = [
        "docs/ops/NF_PR_CONFLICT_RESOLVER_LOCKED_v1.md",
        ".cursor/skills/SKILL-011-pr-conflict-resolver.md",
        ".cursor/rules/nf-pr-conflict-resolver-mandatory.mdc",
        "scripts/nf_pr_conflict_classify_v1.py",
        "tools/pr-conflict-resolver-report/report.html",
        "tools/pr-conflict-resolver-report/open-report.sh",
    ]
    for rel in required:
        p = ROOT / rel
        if not p.is_file():
            fail(f"missing {rel}")
            errors += 1
        else:
            ok(rel)

    rule = (ROOT / ".cursor/rules/nf-pr-conflict-resolver-mandatory.mdc").read_text(encoding="utf-8")
    if "alwaysApply: true" not in rule:
        fail("nf-pr-conflict-resolver-mandatory.mdc not alwaysApply")
        errors += 1
    else:
        ok("cursor rule alwaysApply")

    open_prs = ROOT / "docs/ops/plans/no-asf/OPEN_PRS.md"
    if open_prs.is_file():
        text = open_prs.read_text(encoding="utf-8")
        if "PR conflict resolver" not in text and "SKILL-011" not in text:
            fail("OPEN_PRS.md missing PR conflict resolver policy")
            errors += 1
        else:
            ok("OPEN_PRS policy wired")

    memory = ROOT / ".cursor/agent-memory/MEMORY_LOCKED.yaml"
    if memory.is_file() and "R-013" not in memory.read_text(encoding="utf-8"):
        fail("MEMORY_LOCKED.yaml missing R-013")
        errors += 1
    else:
        ok("R-013 in memory")

    # No conflict markers in tracked tree (exclude vendored report embed strings)
    grep = subprocess.run(
        [
            "git",
            "grep",
            "-l",
            "^<<<<<<< ",
            "--",
            ".",
            ":(exclude)tools/pr-conflict-resolver-report/report.html",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if grep.stdout.strip():
        fail(f"unresolved conflict markers in: {grep.stdout.strip()}")
        errors += 1
    else:
        ok("no conflict markers in tracked files")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    if "verify-pr-conflict-resolver" not in makefile:
        fail("Makefile missing verify-pr-conflict-resolver target")
        errors += 1
    else:
        ok("Makefile target wired")

    plan_verify = (ROOT / "scripts/plan-with-no-asf-verify.sh").read_text(encoding="utf-8")
    if "verify_pr_conflict_resolver_v1.py" not in plan_verify:
        fail("plan-with-no-asf-verify.sh missing pr conflict gate")
        errors += 1
    else:
        ok("plan-with-no-asf-verify wired")

    if errors:
        print(f"\nverify-pr-conflict-resolver: FAIL ({errors} checks)", file=sys.stderr)
        return 1
    print("\nverify-pr-conflict-resolver: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
