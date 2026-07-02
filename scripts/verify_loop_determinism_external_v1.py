#!/usr/bin/env python3
"""External-verify determinism gate — D1/D2/D4/D5 + illegal transitions (UPG-0214)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402

PROOF = proof_receipt("noos-loop-determinism-external-verify-v1.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_gate() -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_loop_determinism_ci.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    checks = [
        {"id": "D1", "name": "idempotency_op_key", "test": "test_d1_idempotency_op_key_stable"},
        {"id": "D2", "name": "cas_stale_reject", "test": "test_d2_cas_rejects_stale_advance"},
        {"id": "D4", "name": "advance_requires_sink_ack", "test": "test_d4_advance_requires_sink_ack"},
        {"id": "D5", "name": "replay_fold_matches_state", "test": "test_d5_replay_fold_matches_state"},
        {"id": "T", "name": "illegal_transition_fuzz", "test": "test_illegal_transition_fuzz"},
    ]
    return {
        "schema": "external-verify-receipt-v1",
        "runner": "github-action",
        "verified_at": utc_now(),
        "gate": "loop-determinism-v1",
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "checks": checks,
        "stdout_tail": (proc.stdout or "")[-800:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = run_gate()
    if args.write_receipt:
        PROOF.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["receipt_path"] = str(PROOF.relative_to(ROOT))
        result["receipt_tier"] = "proof"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"determinism_gate ok={result['ok']} exit={result['exit_code']}")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
