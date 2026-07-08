#!/usr/bin/env python3
"""Write cloud motor ops hardening receipt (UPG-LS-02)."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "receipts/proof/noos-cloud-motor-ops-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    e2e = subprocess.run(["bash", "scripts/verify_noos_cloud_motor_e2e_v1.sh"], cwd=ROOT, capture_output=True, text=True)
    dispatch = subprocess.run(
        [ "python3", "scripts/verify_noos_cf_railway_dispatch_v1.py", "--write-receipt"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    dispatch_row = {}
    if dispatch.stdout.strip():
        try:
            dispatch_row = json.loads(dispatch.stdout)
        except json.JSONDecodeError:
            dispatch_row = {"raw": dispatch.stdout[-500:]}

    row = {
        "schema": "noos-cloud-motor-ops-v1",
        "verified_at": utc_now(),
        "authority": "UPG-LS-02",
        "e2e_ok": e2e.returncode == 0,
        "e2e_tail": (e2e.stdout or "")[-600:],
        "dispatch_verify": dispatch_row,
        "runbook": "scripts/phase_a_wire_cloud_motor_v1.sh",
        "resync_target": "make cloud-motor-resync",
        "external_monitors": "data/noos-external-monitors-v1.json",
        "ok": e2e.returncode == 0 and dispatch_row.get("ok", dispatch.returncode == 0),
    }
    PROOF.parent.mkdir(parents=True, exist_ok=True)
    PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
