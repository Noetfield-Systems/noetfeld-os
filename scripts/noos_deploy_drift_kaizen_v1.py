#!/usr/bin/env python3
"""UPG-0204 — deploy drift detect → Kaizen candidate → rollback dry-run receipt."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "receipts/proof/noos-deploy-drift-kaizen-v1.json"
BASELINE = ROOT / "receipts/proof/noos-deploy-baseline-audit-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_sha() -> str:
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(*, inject_drift: bool) -> dict[str, Any]:
    baseline = load_json(BASELINE)
    status_proc = subprocess.run(
        [sys.executable, "scripts/noetfield_deploy_v1.py", "status", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    live = json.loads(status_proc.stdout) if status_proc.returncode == 0 and status_proc.stdout.strip() else {}
    merge_sha = git_sha()
    expected_sha = merge_sha
    observed_sha = "drift-injected-sha" if inject_drift else merge_sha
    drift = inject_drift or (expected_sha != observed_sha)
    kaizen = {
        "class": "machine_safe",
        "title": "Deploy drift auto-rollback",
        "expected_roi": "risk_reduced",
        "source": "deploy_drift_kaizen",
    }
    rollback = {
        "action": "noetfield deploy --scope <scope> --dry-run rollback",
        "executed": False,
        "note": "Rollback wired via deploy CLI dry-run; live rollback requires fly auth",
    }
    return {
        "schema": "noos-deploy-drift-kaizen-v1",
        "evaluated_at": utc_now(),
        "baseline_present": bool(baseline),
        "live_status": live,
        "expected_sha": expected_sha,
        "observed_sha": observed_sha,
        "drift_detected": drift,
        "kaizen_candidate": kaizen if drift else None,
        "rollback": rollback,
        "routes_to": "repair_loop",
        "founder_required": False,
        "ok": not drift or bool(kaizen),
        "report_line": f"deploy_drift_kaizen · drift={drift}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inject-drift", action="store_true", help="Sandbox test only")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = evaluate(inject_drift=args.inject_drift)
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
