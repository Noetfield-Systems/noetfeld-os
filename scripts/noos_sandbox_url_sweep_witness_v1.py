#!/usr/bin/env python3
"""GHA witness — public URL sweep (www/api/platform) + trigger registry sweep."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from autorun_status_v1 import WORKFLOWS, probe_url_sweep_readonly  # noqa: E402
from sandbox_health_sweep_v1 import run_sweep  # noqa: E402

PROOF = ROOT / "receipts/proof/noos-sandbox-url-sweep-witness-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def witness(*, write_receipt: bool = False) -> dict[str, Any]:
    wf_doc = json.loads(WORKFLOWS.read_text(encoding="utf-8"))
    wf = next((w for w in wf_doc.get("workflows") or [] if w.get("id") == "sandbox_health_sweep"), None)
    url_probe = probe_url_sweep_readonly(wf) if wf else {"status": "BLOCKED_WITH_REASON", "reason": "missing_workflow"}
    trigger_sweep = run_sweep(repo_root=ROOT)

    url_ok = url_probe.get("status") == "COMPLETE"
    sweep_ok = bool(trigger_sweep.get("ok"))
    overall = "green" if url_ok and sweep_ok else ("yellow" if url_ok or sweep_ok else "red")

    row: dict[str, Any] = {
        "schema": "noos-sandbox-url-sweep-witness-v1",
        "at": utc_now(),
        "read_only": True,
        "witness_mode": True,
        "one_law": "URL + trigger drift observe only — no deploy or product edits.",
        "overall_status": overall,
        "closure_token": f"NOOS_SANDBOX_URL_SWEEP_WITNESS: {overall}",
        "url_sweep": {
            "status": url_probe.get("status"),
            "evidence": url_probe.get("evidence"),
            "urls_checked": (url_probe.get("evidence") or {}).get("checked"),
        },
        "trigger_sweep": {
            "ok": sweep_ok,
            "report_line": trigger_sweep.get("report_line"),
            "dead_or_mismatch": len(trigger_sweep.get("dead_or_mismatch") or []),
            "unregistered_live": len(trigger_sweep.get("unregistered_live") or []),
        },
        "sandbox_health_sweep_script": "scripts/sandbox_health_sweep_v1.py",
    }
    row["ok"] = True
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
