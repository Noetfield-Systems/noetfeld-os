#!/usr/bin/env python3
"""Write optional T2 local-boot receipt (noos-local-boot-v1)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_agent_conflict_check_v1 as conflict  # noqa: E402
import noos_integrator_mirror_check_v1 as mirror  # noqa: E402
import verify_living_system_governance_v1 as gov  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def git_line(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def dirty_count() -> int:
    try:
        out = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0
    return sum(1 for line in out.splitlines() if line.strip())


def integrator_summary() -> dict[str, Any]:
    try:
        out = subprocess.check_output(
            [sys.executable, "scripts/noos_integrator_sync_v1.py", "summary", "--json"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return {}


def build_receipt(*, write_file: bool = True) -> dict[str, Any]:
    registry = conflict.load_json(conflict.REGISTRY_PATH)
    integrator = conflict.load_json(conflict.INTEGRATOR_STATE)
    conflict_row = conflict.check_conflicts(registry=registry, integrator=integrator)
    gov_row = gov.run_verify(write_receipt=False)
    summary = integrator_summary()
    mirror_row = mirror.check_mirror_drift()

    row: dict[str, Any] = {
        "schema": "noos-local-boot-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "branch": git_line(["branch", "--show-current"]),
        "head": git_line(["rev-parse", "--short", "HEAD"]),
        "dirty_count": dirty_count(),
        "parallel_conflict_ok": conflict_row.get("ok"),
        "governance_ok": gov_row.get("ok"),
        "governance_checks": gov_row.get("checks"),
        "mirror_drift": mirror_row,
        "integrator_summary": summary.get("summary") if isinstance(summary, dict) else {},
        "active_agents": summary.get("agents") if isinstance(summary.get("agents"), list) else [],
        "ok": bool(conflict_row.get("ok")) and bool(gov_row.get("ok")) and bool(mirror_row.get("ok")),
        "report_line": (
            "local_boot_clean · T2 session ready"
            if conflict_row.get("ok") and gov_row.get("ok")
            else "local_boot_drift · see receipt"
        ),
    }

    if write_file:
        out_dir = ROOT / "receipts/proof"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = out_dir / f"noos-local-boot-{ts}.json"
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(path.relative_to(ROOT))

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true", help="Build receipt dict without writing file")
    args = ap.parse_args()
    row = build_receipt(write_file=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
