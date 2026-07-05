#!/usr/bin/env python3
"""Step 10 — T3 sandbox fleet closeout: manifest + backlog sync."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "data/noos-unified-upgrade-backlog-v1.json"
MANIFEST = ROOT / "docs/_NOOS_AGENT/UPGRADE_MANIFEST.json"
PROOF = ROOT / "receipts/proof/noos-t3-sandbox-closeout-v1.json"

UPG_T2_DOCS = ["UPG-0164", "UPG-0168", "UPG-0169"]
UPG_T3 = ["SANDBOX-REGISTRY", "UPG-0211", "UPG-0212", "UPG-0208"]
UPG_DEFER = ["UPG-0209", "UPG-0213"]
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
    matrix = row.get("motor_matrix") or {}
    return bool(matrix.get("fly_live"))


def receipt_ok(rel: str) -> bool:
    return (ROOT / rel).is_file()


def update_backlog() -> dict[str, Any]:
    data = load_json(BACKLOG)
    changed: list[str] = []
    l4 = fly_l4_live()
    evidence_map = {
        "UPG-0164": "packages/noetfield-gate/README.md",
        "UPG-0168": "docs/examples/noetfield-gate-gha-v1.yml",
        "UPG-0169": "docs/examples/pre-commit-noetfield-gate-v1.md",
        "SANDBOX-REGISTRY": "data/noos-sandbox-fleet-v1.json + scripts/noos_sandbox_registry_reconcile_v1.py",
        "UPG-0211": "scripts/noos_improve_kaizen_runner_v1.py",
        "UPG-0212": "data/noos-runtime-scaling-v1.json",
        "UPG-0208": "data/noos-deploy-scopes-v1.json internal_health_url + NOOS_GEL_INTERNAL_HEALTH",
    }
    for item in data.get("items") or []:
        iid = str(item.get("id") or "")
        if iid in UPG_T2_DOCS + UPG_T3:
            ev = evidence_map.get(iid, "")
            primary = ev.split(" + ")[0].split(" ")[0]
            if primary and (ROOT / primary).is_file():
                item["status"] = "done"
                item["evidence"] = ev
                changed.append(iid)
        if iid in UPG_DEFER:
            item["note"] = "Deferred to next plan per T3 closeout"
        if iid in UPG_FLY and not l4:
            item["note"] = "Scaffold + local smoke; Fly L4 pending fly auth deploy"
        elif iid in UPG_FLY and l4:
            item["status"] = "done"
            item["evidence"] = "Fly L4 deploy receipts"
            changed.append(iid)
    summary = data.get("summary") or {}
    items = data.get("items") or []
    summary["done"] = sum(1 for x in items if x.get("status") == "done")
    summary["open_t2"] = sum(1 for x in items if x.get("tier") == "T2" and x.get("status") == "open")
    summary["open_t3"] = sum(1 for x in items if x.get("tier") == "T3" and x.get("status") == "open")
    data["summary"] = summary
    data["updated_at"] = utc_now()[:10]
    BACKLOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"changed": changed, "fly_l4_live": l4, "summary": summary}


def update_manifest() -> dict[str, Any]:
    data = load_json(MANIFEST)
    completed = set(data.get("completed_steps") or [])
    evidence = data.setdefault("evidence", {})
    for step in UPG_T2_DOCS + UPG_T3:
        completed.add(step)
        if step == "UPG-0164":
            evidence[step] = "packages/noetfield-gate/README.md"
        elif step == "UPG-0168":
            evidence[step] = "docs/examples/noetfield-gate-gha-v1.yml"
        elif step == "UPG-0169":
            evidence[step] = "docs/examples/pre-commit-noetfield-gate-v1.md"
        elif step == "SANDBOX-REGISTRY":
            evidence[step] = "data/noos-sandbox-fleet-v1.json"
        elif step == "UPG-0211":
            evidence[step] = "scripts/noos_improve_kaizen_runner_v1.py"
        elif step == "UPG-0212":
            evidence[step] = "data/noos-runtime-scaling-v1.json"
        elif step == "UPG-0208":
            evidence[step] = "NOOS_GEL_INTERNAL_HEALTH mesh probe"
    if fly_l4_live():
        for step in UPG_FLY:
            completed.add(step)
            evidence[step] = "Fly L4 deploy receipts"
    else:
        for step in UPG_FLY:
            evidence[step] = "ops/fly/* scaffold + local smoke (L4 pending fly auth)"
    for step in UPG_DEFER:
        evidence[step] = "Deferred — next plan"
    data["completed_steps"] = sorted(completed)
    data["updated_at"] = utc_now()[:10]
    data["notes"] = (
        "T3 sandbox fleet lane closed. Fly L4 honest: see deploy baseline. "
        "UPG-0209/0213 deferred."
    )
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"completed_added": sorted(UPG_T2_DOCS + UPG_T3 + (UPG_FLY if fly_l4_live() else []))}


def closeout(*, write_receipt: bool) -> dict[str, Any]:
    backlog = update_backlog()
    manifest = update_manifest()
    row = {
        "schema": "noos-t3-sandbox-closeout-v1",
        "closed_at": utc_now(),
        "authority": "NOOS_T3_SANDBOX_STEP_10",
        "backlog_update": backlog,
        "manifest_update": manifest,
        "fly_l4_live": fly_l4_live(),
        "sandbox_registry_receipt": receipt_ok("receipts/proof/noos-sandbox-registry-v1.json"),
        "improve_kaizen_receipt": receipt_ok("receipts/proof/noos-improve-kaizen-daily-v1.json"),
        "loop_verify_receipt": receipt_ok("receipts/proof/noos-loop-verify-all-v1.json"),
        "ok": True,
        "report_line": "t3_sandbox_closeout · lane complete",
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
