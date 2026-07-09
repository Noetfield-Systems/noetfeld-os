#!/usr/bin/env python3
"""L12 schedule gate — registry is schedule home; GHA workflow crons must match or be absent.

Fail closed before cloud worker deploy (same class as config-hash drift gates).
Primary dispatch is CF/Railway repository_dispatch; schedule crons are backup only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "noos-24-7-loops-v1.json"
WORKFLOWS = ROOT / ".github" / "workflows"

sys.path.insert(0, str(ROOT / "scripts"))
import noos_loop_heartbeat_v1 as hb  # noqa: E402


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def verify(*, skip_missing: bool = False) -> dict[str, Any]:
    registry = load_registry()
    mismatches: list[dict[str, Any]] = []
    checked = 0
    for loop in registry.get("loops") or []:
        workflow_file = str(loop.get("github_workflow") or "")
        if not workflow_file:
            continue
        interval = int(loop.get("interval_minutes") or 0)
        if interval <= 0:
            continue
        deployed = hb.deployed_cron(workflow_file)
        if deployed is None:
            if skip_missing:
                continue
            mismatches.append(
                {
                    "loop_id": loop.get("id"),
                    "workflow": workflow_file,
                    "committed_truth": hb.committed_cron(interval),
                    "deployed_truth": "MISSING",
                    "reason": "no_schedule_cron_in_workflow",
                }
            )
            continue
        checked += 1
        if not hb.cron_matches(deployed, interval):
            mismatches.append(
                {
                    "loop_id": loop.get("id"),
                    "workflow": workflow_file,
                    "committed_truth": hb.committed_cron(interval),
                    "deployed_truth": deployed,
                    "reason": "schedule_mismatch",
                }
            )
    return {
        "schema": "noos-loop-schedule-registry-verify-v1",
        "registry_path": str(REGISTRY.relative_to(ROOT)),
        "checked": checked,
        "ok": not mismatches,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skip-missing", action="store_true", help="Only verify workflows that declare a cron")
    args = ap.parse_args()
    report = verify(skip_missing=args.skip_missing)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"schedule_registry_verify ok={report['ok']} checked={report['checked']} "
            f"mismatches={report['mismatch_count']}"
        )
        for row in report["mismatches"]:
            print(
                f"  DRIFT {row['loop_id']}: committed={row['committed_truth']} "
                f"deployed={row['deployed_truth']} ({row['reason']})"
            )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
