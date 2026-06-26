#!/usr/bin/env python3
"""NF receipt cascade — fold gate/stale/voyage/surfaces into node ids (SourceA pattern)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nf_factory_lib_v1 import iso_now, load_event, load_json, load_sina, repo_root, write_event, write_sina


def _check_source(root: Path, src: dict) -> dict | None:
    data = None
    if src.get("path"):
        data = load_event(src["path"], root)
    if not data and src.get("sina"):
        data = load_sina(src["sina"])
    if not data:
        return {"node_id": src["fail_node"], "reason": "missing receipt", "ok": False}

    ok = True
    reason = ""

    if src.get("stale_field"):
        if data.get(src["stale_field"]):
            ok = False
            reason = f"{src['stale_field']}=true"
    if src.get("ok_field") and ok:
        if not data.get(src["ok_field"]):
            ok = False
            reason = f"{src['ok_field']}=false"
    if src.get("required_line") and ok:
        if not data.get(src["required_line"]):
            ok = False
            reason = f"missing {src['required_line']}"
    if src.get("required_line_2") and ok:
        if not data.get(src["required_line_2"]):
            ok = False
            reason = f"missing {src['required_line_2']}"

    if not ok:
        return {"node_id": src["fail_node"], "reason": reason or "check failed", "ok": False}
    return None


def build_cascade(root: Path | None = None) -> dict:
    root = root or repo_root()
    ssot_path = root / "data/nf_orient_routing_v1.json"
    ssot = load_json(ssot_path) or {}
    sources = ssot.get("receipt_cascade_sources") or []

    failures: list[dict] = []
    for src in sources:
        hit = _check_source(root, src)
        if hit:
            failures.append(hit)

    nodes = [f["node_id"] for f in failures]
    report = {
        "schema_version": "nf-receipt-cascade-v1",
        "generated_at": iso_now(),
        "ok": len(failures) == 0,
        "failures": failures,
        "nodes": nodes,
        "ssot": str(ssot_path),
        "heal": "make nf-onboard" if failures else None,
        "orient_read_chain": ssot.get("orient_read_chain") or [],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_cascade()
    write_event("nf-receipt-cascade-v1.json", report)
    write_sina("nf-receipt-cascade-v1.json", report)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["ok"] else "FAIL"
        print(f"nf_receipt_cascade: {status}")
        for f in report["failures"]:
            print(f"  FAIL {f['node_id']}: {f['reason']}")
        if report.get("heal"):
            print(f"heal: {report['heal']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
