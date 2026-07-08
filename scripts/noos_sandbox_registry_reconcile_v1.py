#!/usr/bin/env python3
"""Step 4 — reconcile sandbox fleet registry vs loops + deploy scopes."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FLEET = ROOT / "data/noos-sandbox-fleet-v1.json"
LOOPS = ROOT / "data/noos-24-7-loops-v1.json"
DEPLOY = ROOT / "data/noos-deploy-scopes-v1.json"
WORKFLOW_DIR = ROOT / ".github/workflows"
RECEIPT = ROOT / "receipts/proof/noos-sandbox-registry-v1.json"

EXPECTED_SANDBOX_IDS = frozenset(
    {"inbox", "chain", "surface", "sourcea_observe", "improve", "gel-api", "www", "cf"}
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def reconcile() -> dict[str, Any]:
    fleet = load_json(FLEET)
    loops = load_json(LOOPS)
    deploy = load_json(DEPLOY)
    loop_ids = {str(x.get("id")) for x in loops.get("loops") or []}
    loop_workflows = {str(x.get("id")): str(x.get("github_workflow") or "") for x in loops.get("loops") or []}
    deploy_scopes = deploy.get("scopes") or {}

    rows: list[dict[str, Any]] = []
    issues: list[str] = []
    seen_ids: set[str] = set()

    for sb in fleet.get("sandboxes") or []:
        sid = str(sb.get("sandbox_id") or "")
        seen_ids.add(sid)
        row: dict[str, Any] = {
            "sandbox_id": sid,
            "motor": sb.get("motor"),
            "loop_id": sb.get("loop_id"),
            "workflow_id": sb.get("workflow_id"),
            "deploy_scope": sb.get("deploy_scope"),
            "loop_registered": True,
            "workflow_exists": None,
            "deploy_scope_ok": None,
        }
        loop_id = sb.get("loop_id")
        if loop_id and str(loop_id) not in loop_ids:
            row["loop_registered"] = False
            issues.append(f"missing_loop:{sid}:{loop_id}")
        wf = sb.get("workflow_id")
        if wf:
            wf_path = WORKFLOW_DIR / str(wf)
            row["workflow_exists"] = wf_path.is_file()
            if not wf_path.is_file():
                issues.append(f"missing_workflow:{sid}:{wf}")
            elif loop_id and loop_workflows.get(str(loop_id)) != str(wf):
                issues.append(f"workflow_mismatch:{sid}:{wf}")
        scope = sb.get("deploy_scope")
        if scope:
            row["deploy_scope_ok"] = str(scope) in deploy_scopes
            if str(scope) not in deploy_scopes:
                issues.append(f"missing_deploy_scope:{sid}:{scope}")
        rows.append(row)

    for missing in sorted(EXPECTED_SANDBOX_IDS - seen_ids):
        issues.append(f"missing_sandbox_row:{missing}")

    ok = not issues
    return {
        "schema": "noos-sandbox-registry-reconcile-v1",
        "reconciled_at": utc_now(),
        "authority": "NOOS_T3_SANDBOX_FLEET_STEP_4",
        "sandbox_count": len(rows),
        "expected_count": len(EXPECTED_SANDBOX_IDS),
        "sandboxes": rows,
        "issues": issues,
        "ok": ok,
        "report_line": f"sandbox_registry_reconcile · sandboxes={len(rows)} issues={len(issues)}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = reconcile()
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
