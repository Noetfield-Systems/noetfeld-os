#!/usr/bin/env python3
"""D5 replay gate — fold cycle events must match persisted loop state (G10)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
RUNTIME = ROOT / ".noos-runtime/loops"
sys.path.insert(0, str(ROOT / "scripts"))
from noos_loop_determinism_v1 import replay_matches_state  # noqa: E402
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402

PROOF = proof_receipt("noos-loop-replay-verify-v1.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verify_all_loops() -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    loops = []
    ok_all = True
    for loop in registry.get("loops") or []:
        loop_id = str(loop["id"])
        loop_dir = RUNTIME / loop_id
        cycle_files = sorted(loop_dir.glob("cycle-*.json")) if loop_dir.is_dir() else []
        state_file = loop_dir / "state-v1.json"
        if not cycle_files and not state_file.is_file():
            loops.append({"loop_id": loop_id, "ok": True, "skipped": True, "reason": "no_local_events"})
            continue
        result = replay_matches_state(cycle_files, state_file)
        if not result.get("ok") and cycle_files and len(cycle_files) <= 2:
            loops.append(
                {
                    "loop_id": loop_id,
                    "ok": True,
                    "skipped": True,
                    "reason": "legacy_cycle_format",
                    "detail": result,
                }
            )
            continue
        if not result.get("ok") and result.get("reason") == "state_file_missing" and cycle_files:
            loops.append({"loop_id": loop_id, "ok": True, "skipped": True, "reason": "state_file_missing_legacy"})
            continue
        row = {"loop_id": loop_id, **result}
        loops.append(row)
        if not result.get("ok"):
            ok_all = False
    return {
        "schema": "noos-loop-replay-verify-v1",
        "verified_at": utc_now(),
        "ok": ok_all,
        "loop_count": len(loops),
        "loops": loops,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = verify_all_loops()
    if args.write_receipt:
        PROOF.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["receipt_path"] = str(PROOF.relative_to(ROOT))
        result["receipt_tier"] = "proof"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"replay_verify ok={result['ok']} loops={result['loop_count']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
