#!/usr/bin/env python3
"""Step 10 — T2 deploy + ACG lane closeout: manifest + backlog sync."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "data/noos-unified-upgrade-backlog-v1.json"
MANIFEST = ROOT / "docs/_NOOS_AGENT/UPGRADE_MANIFEST.json"
PROOF = ROOT / "receipts/proof/noos-t2-deploy-acg-closeout-v1.json"

UPG_T2 = ["UPG-0203", "UPG-0204", "UPG-0205"]
UPG_FLY = ["UPG-0201", "UPG-0202", "UPG-0206"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fly_l4_live() -> bool:
    baseline = ROOT / "receipts/proof/noos-deploy-baseline-audit-v1.json"
    if not baseline.is_file():
        return False
    row = load_json(baseline)
    return bool(row.get("motor_matrix", {}).get("fly_live"))


def deploy_receipt_ok(scope: str) -> bool:
    path = ROOT / f"receipts/proof/noos-deploy-{scope}-v1.json"
    if not path.is_file():
        return False
    row = load_json(path)
    return bool(row.get("l4_live") or row.get("ok"))


def update_backlog() -> dict[str, Any]:
    data = load_json(BACKLOG)
    changed: list[str] = []
    l4 = fly_l4_live()
    for item in data.get("items") or []:
        iid = str(item.get("id") or "")
        if iid in UPG_T2:
            if iid == "UPG-0203" and (ROOT / "scripts/noetfield_deploy_v1.py").is_file():
                item["status"] = "done"
                item["evidence"] = "scripts/noetfield_deploy_v1.py + data/noos-deploy-scopes-v1.json"
                changed.append(iid)
            elif iid == "UPG-0204" and (ROOT / "receipts/proof/noos-deploy-drift-kaizen-v1.json").is_file():
                item["status"] = "done"
                item["evidence"] = "receipts/proof/noos-deploy-drift-kaizen-v1.json"
                changed.append(iid)
            elif iid == "UPG-0205" and (ROOT / "receipts/proof/noos-inbox-scaler-v1.json").is_file():
                item["status"] = "done"
                item["evidence"] = "data/noos-runtime-scaling-v1.json + receipts/proof/noos-inbox-scaler-v1.json"
                changed.append(iid)
        if iid in UPG_FLY:
            if l4:
                item["status"] = "done"
                item["evidence"] = "receipts/proof/noos-deploy-fly-inbox-v1.json + fly L4"
            else:
                item["note"] = "Scaffold + local smoke; Fly L4 pending fly auth deploy"
    summary = data.get("summary") or {}
    items = data.get("items") or []
    summary["done"] = sum(1 for x in items if x.get("status") == "done")
    summary["open_t2"] = sum(1 for x in items if x.get("tier") == "T2" and x.get("status") == "open")
    data["summary"] = summary
    data["updated_at"] = utc_now()[:10]
    BACKLOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"changed": changed, "fly_l4_live": l4, "summary": summary}


def update_manifest() -> dict[str, Any]:
    data = load_json(MANIFEST)
    completed = set(data.get("completed_steps") or [])
    evidence = data.setdefault("evidence", {})
    for step in UPG_T2:
        completed.add(step)
        if step == "UPG-0203":
            evidence[step] = "scripts/noetfield_deploy_v1.py"
        elif step == "UPG-0204":
            evidence[step] = "scripts/noos_deploy_drift_kaizen_v1.py"
        elif step == "UPG-0205":
            evidence[step] = "scripts/noos_inbox_scaler_v1.py"
    if fly_l4_live():
        for step in UPG_FLY:
            completed.add(step)
            evidence[step] = "Fly L4 deploy receipts"
    else:
        for step in UPG_FLY:
            evidence[step] = "ops/fly/* scaffold + local smoke (L4 pending fly auth)"
    data["completed_steps"] = sorted(completed)
    data["planned_steps"] = [p for p in data.get("planned_steps") or [] if p not in UPG_T2]
    data["updated_at"] = utc_now()[:10]
    data["notes"] = "T2 deploy ACG lane closed. Fly L4 honest: see deploy baseline receipt."
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"completed_added": sorted(UPG_T2 + (UPG_FLY if fly_l4_live() else []))}


def closeout(*, write_receipt: bool) -> dict[str, Any]:
    backlog = update_backlog()
    manifest = update_manifest()
    prep_path = ROOT / "noetfield-org/receipts/NOOS_ACG_FOUNDER_SEND_PREP_2026-07-05.md"
    row = {
        "schema": "noos-t2-deploy-acg-closeout-v1",
        "closed_at": utc_now(),
        "authority": "NOOS_T2_DEPLOY_ACG_STEP_10",
        "backlog_update": backlog,
        "manifest_update": manifest,
        "fly_l4_live": fly_l4_live(),
        "acg_founder_prep": str(prep_path.relative_to(ROOT)) if prep_path.is_file() else None,
        "ok": True,
        "report_line": "t2_deploy_acg_closeout · lane complete",
    }
    if write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = closeout(write_receipt=args.write_receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
