#!/usr/bin/env python3
"""Step 2 — reconcile loop registry vs GitHub workflow files."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
DISPATCH_TABLE = ROOT / "data/noos-cf-dispatch-table-v1.json"
WORKFLOW_DIR = ROOT / ".github/workflows"
RECEIPT = ROOT / "receipts/proof/noos-loop-registry-reconcile-v1.json"

CORE_LOOP_IDS = frozenset(
    {
        "inbox",
        "runtime",
        "surface",
        "chain",
        "self_heal",
        "sourcea_observe",
        "agent_nerve",
    }
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_dispatch_types(text: str) -> list[str]:
    block = re.search(r"repository_dispatch:\s*\n(?:[^\n]+\n)*?\s*types:\s*\[(.*?)\]", text, re.DOTALL)
    if not block:
        return []
    return re.findall(r"[\w_]+", block.group(1))


def workflow_triggers(text: str) -> dict[str, Any]:
    return {
        "schedule": bool(re.search(r"\n\s*schedule:", text)),
        "workflow_dispatch": bool(re.search(r"\n\s*workflow_dispatch:", text)),
        "repository_dispatch_types": parse_dispatch_types(text),
    }


def cf_dispatch_event_types() -> set[str]:
    if not DISPATCH_TABLE.is_file():
        return set()
    doc = json.loads(DISPATCH_TABLE.read_text(encoding="utf-8"))
    return {str(t.get("event_type") or "") for t in doc.get("targets") or []}


def event_matches_loop(*, loop_id: str, event_type: str, triggers: dict[str, Any]) -> bool:
    if event_type in cf_dispatch_event_types():
        return True
    dispatch_types = triggers.get("repository_dispatch_types") or []
    if event_type in dispatch_types:
        return True
    if loop_id in CORE_LOOP_IDS:
        return False
    return bool(triggers.get("schedule") or triggers.get("workflow_dispatch"))


def reconcile() -> dict[str, Any]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    workflow_files = {p.name for p in WORKFLOW_DIR.glob("noos-*.yml")}
    rows: list[dict[str, Any]] = []
    issues: list[str] = []
    orphan_workflows: list[str] = []

    registered_workflows = set()
    for loop in registry.get("loops") or []:
        loop_id = str(loop.get("id") or "")
        wf_name = str(loop.get("github_workflow") or "")
        event_type = str(loop.get("event_type") or "")
        factory_id = str(loop.get("factory_id") or f"loop-{loop_id}")
        wf_path = WORKFLOW_DIR / wf_name
        row: dict[str, Any] = {
            "loop_id": loop_id,
            "github_workflow": wf_name,
            "event_type": event_type,
            "factory_id": factory_id,
            "core_domain_loop": loop_id in CORE_LOOP_IDS,
            "workflow_exists": wf_path.is_file(),
            "event_match": None,
            "factory_id_ok": factory_id.startswith("loop-"),
        }
        if not wf_path.is_file():
            issues.append(f"missing_workflow:{loop_id}:{wf_name}")
        else:
            registered_workflows.add(wf_name)
            text = wf_path.read_text(encoding="utf-8")
            triggers = workflow_triggers(text)
            row["triggers"] = triggers
            row["event_match"] = event_matches_loop(
                loop_id=loop_id,
                event_type=event_type,
                triggers=triggers,
            )
            if not row["event_match"]:
                issues.append(f"event_mismatch:{loop_id}:{event_type}")
        rows.append(row)

    for wf in sorted(workflow_files):
        if wf.startswith("noos-") and wf.endswith("-loop.yml") and wf not in registered_workflows:
            orphan_workflows.append(wf)

    core_issues = [issue for issue in issues if not issue.startswith("event_mismatch:")] + [
        issue
        for issue in issues
        if issue.startswith("event_mismatch:")
        and issue.split(":", 2)[1] in CORE_LOOP_IDS
    ]

    ok = not core_issues
    return {
        "schema": "noos-loop-registry-reconcile-v1",
        "reconciled_at": utc_now(),
        "authority": "NOOS_MACHINE_LOOPS_UPGRADE_STEP_2",
        "loop_count": len(rows),
        "core_loop_count": len(CORE_LOOP_IDS),
        "loops": rows,
        "orphan_loop_workflows": orphan_workflows,
        "issues": issues,
        "core_issues": core_issues,
        "ok": ok,
        "report_line": f"loop_registry_reconcile · loops={len(rows)} core_issues={len(core_issues)}",
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
