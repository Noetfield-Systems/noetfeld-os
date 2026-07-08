#!/usr/bin/env python3
"""GHA witness — TrustField 11 layers + loop registry (ICL-D06/D07, handoff-only)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "receipts/proof/noos-trustfield-observe-witness-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_observe(script: str, *, write_receipt: bool) -> dict[str, Any]:
    cmd = [sys.executable, str(ROOT / "scripts" / script), "--json"]
    if write_receipt:
        cmd.append("--write-receipt")
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120, check=False)
    if not proc.stdout.strip():
        return {"ok": False, "exit_code": proc.returncode, "stderr": (proc.stderr or "")[-400:]}
    try:
        doc = json.loads(proc.stdout)
        if isinstance(doc, dict):
            doc.setdefault("exit_code", proc.returncode)
        return doc
    except json.JSONDecodeError:
        return {"ok": False, "exit_code": proc.returncode, "raw": proc.stdout[-600:]}


def witness(*, write_receipt: bool = False) -> dict[str, Any]:
    layers = run_observe("observe_trustfield_parallel_layers_v1.py", write_receipt=write_receipt)
    registry = run_observe("observe_trustfield_loop_registry_v1.py", write_receipt=write_receipt)

    layer_summary = layers.get("summary") or {}
    reg_summary = registry.get("summary") or {}
    reg_red = int(reg_summary.get("red") or 0)
    deadman_red = reg_summary.get("deadman_watched_red") or []

    d06_ok = layers.get("overall_status") in ("green", "yellow") and not layer_summary.get("red")
    d07_ok = reg_red == 0 and not deadman_red
    if not d07_ok:
        d07_ok = not deadman_red and reg_summary.get("deadman_status") == "green"

    checks = {
        "ICL-D06": {
            "title": "TrustField 11 layers (no red)",
            "ok": d06_ok,
            "overall": layers.get("overall_status"),
            "summary": layer_summary,
            "closure": layers.get("closure_token"),
        },
        "ICL-D07": {
            "title": "TrustField loop registry (deadman motors green)",
            "ok": d07_ok,
            "overall": registry.get("overall_status"),
            "summary": reg_summary,
            "closure": registry.get("closure_token"),
            "witness_relaxed": True,
        },
    }
    read_ok = layers.get("overall_status") is not None and registry.get("registry_read_ok") is not False
    fails = [k for k, v in checks.items() if not v.get("ok")]
    overall = "green" if not fails else ("yellow" if len(fails) == 1 else "red")

    row: dict[str, Any] = {
        "schema": "noos-trustfield-observe-witness-v1",
        "at": utc_now(),
        "read_only": True,
        "witness_mode": True,
        "one_law": "Observe + receipt only — TrustField worker owns product/registry writes.",
        "overall_status": overall,
        "closure_token": f"NOOS_TF_OBSERVE_WITNESS: {overall}",
        "checks": checks,
        "layers": layers,
        "registry": registry,
        "handoff_owner": "trustfield_worker",
        "fix_queue": [
            {
                "id": k,
                "fix": "Route to TrustField worker — NOOS does not edit TrustField product/www",
            }
            for k in fails
        ],
    }
    row["ok"] = read_ok
    if write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = witness(write_receipt=args.write_receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["closure_token"])

    if not row.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
