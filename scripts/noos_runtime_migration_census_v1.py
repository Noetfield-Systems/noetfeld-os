#!/usr/bin/env python3
"""Census NOOS loops/dispatch for Runtime Value Contract migration."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOPS = ROOT / "data" / "noos-24-7-loops-v1.json"
DISPATCH = ROOT / "data" / "noos-cf-dispatch-table-v1.json"
OUT = ROOT / "receipts" / "proof" / "noos-runtime-migration-census-v1.json"


def main() -> int:
    loops_doc = json.loads(LOOPS.read_text(encoding="utf-8"))
    dispatch_doc = json.loads(DISPATCH.read_text(encoding="utf-8"))
    errors: list[str] = []

    quarantined_loops = []
    active_loops = []
    for loop in loops_doc.get("loops") or []:
        status = loop.get("schedule_status", "active")
        row = {
            "id": loop.get("id"),
            "value_class": loop.get("value_class"),
            "interval_minutes": loop.get("interval_minutes"),
            "schedule_status": status,
            "enabled": loop.get("enabled", True),
        }
        if status == "quarantined" or loop.get("enabled") is False:
            quarantined_loops.append(row)
        else:
            nw = loop.get("no_work_behavior") or {}
            if not all(nw.get(k) is True for k in ("no_write", "no_llm", "no_notification")):
                errors.append(f"loop {loop.get('id')}: missing idle no-work behavior")
            active_loops.append(row)

    quarantined_targets = []
    active_targets = []
    for t in dispatch_doc.get("targets") or []:
        row = {
            "dispatch_id": t.get("dispatch_id"),
            "event_type": t.get("event_type"),
            "interval_minutes": t.get("interval_minutes"),
            "enabled": t.get("enabled", True),
            "schedule_status": t.get("schedule_status", "active"),
        }
        if t.get("enabled") is False or t.get("schedule_status") == "quarantined":
            quarantined_targets.append(row)
        else:
            active_targets.append(row)

    required_quarantine = {"orchestrator", "factory_autorun"}
    found = {t["dispatch_id"] for t in quarantined_targets}
    missing = sorted(required_quarantine - found)
    for mid in missing:
        errors.append(f"expected quarantined dispatch_id missing: {mid}")

    receipt = {
        "schema": "noos_runtime_migration_census_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "active_loops": active_loops,
        "quarantined_loops": quarantined_loops,
        "active_targets": active_targets,
        "quarantined_targets": quarantined_targets,
        "idle_law": "queue empty => no write, no LLM, no notification",
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": receipt["verdict"], "receipt": str(OUT.relative_to(ROOT))}, indent=2))
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
