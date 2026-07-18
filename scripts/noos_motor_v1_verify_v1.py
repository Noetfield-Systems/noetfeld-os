#!/usr/bin/env python3
"""NOOS Motor v1 — canonical verification command.

NF-NOOS-MOTOR-V1-FULL-RUNWAY, Phase 7/8. This is what `noos verify` runs. It
exercises the OFFLINE organic path end-to-end and the masking regression, and
exits non-zero on any failure. It NEVER uses a repair-generated receipt as proof
of organic execution, and it does not fabricate the cloud http_loop cycles.

Checks:
  1. Three consecutive LOCAL reference organic cycles, each producing a real,
     retrievable, integrity-checked output artifact with a valid lifecycle.
  2. Masking regression: a fresh repair receipt must classify as
     DEGRADED_REPAIR_SUSTAINED (never RUNNING_CONFIRMED); restoring organic
     evidence returns RUNNING_CONFIRMED.
  3. Deliberate invalid input fails truthfully (no artifact).

Writes receipts under receipts/runway/ when --emit-receipts is passed.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_motor_local_executor_v1 as lx  # noqa: E402
import noos_motor_state_machine_v1 as fsm  # noqa: E402
import noos_observability_semantics_v1 as sem  # noqa: E402

RUNWAY = ROOT / "receipts" / "runway"
COMPLETION_THRESH = 30.0
DISPATCH_THRESH = 10.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _cycle(i: int, art: Path, rcp: Path) -> dict[str, Any]:
    """Run one real local organic cycle and return its captured evidence."""
    job = {
        "task_kind": "digest",
        "title": f"verify cycle {i}",
        "records": [{"cycle": i, "value": i * 10}, {"cycle": i, "value": i * 5, "note": "n"}],
    }
    res = lx.run_job(job, **{"artifact_dir": art, "receipt_dir": rcp})
    got = lx.retrieve(res["execution_id"], receipt_dir=rcp, artifact_dir=art)
    ok = (
        res["ok"]
        and res["status"] == fsm.COMPLETED
        and got["output_integrity_ok"] is True
        and res["record"]["execution_origin"] == fsm.ORIGIN_ORGANIC
        and res["record"]["producer"] == lx.PRODUCER
    )
    return {
        "cycle": i,
        "execution_id": res["execution_id"],
        "attempt_id": res["record"]["attempt_id"],
        "correlation_id": res["record"]["correlation_id"],
        "dispatch_id": res["record"]["dispatch_id"],
        "producer": res["record"]["producer"],
        "receipt_origin": "organic",
        "execution_plane": "local_reference",
        "final_state": res["status"],
        "output_hash": res["output_hash"],
        "artifact_uri": res["artifact_uri"],
        "integrity_ok": got["output_integrity_ok"],
        "ok": bool(ok),
    }


def run_local_organic_cycles(n: int, art: Path, rcp: Path) -> dict[str, Any]:
    cycles = [_cycle(i, art, rcp) for i in range(1, n + 1)]
    unique_ids = {c["execution_id"] for c in cycles}
    return {
        "check": "local_organic_cycles",
        "requested": n,
        "cycles": cycles,
        "all_ok": all(c["ok"] for c in cycles),
        "all_unique_execution_ids": len(unique_ids) == n,
        "consecutive_pass": all(c["ok"] for c in cycles) and len(unique_ids) == n,
    }


def run_masking_regression() -> dict[str, Any]:
    """Repair-fresh must NOT be RUNNING_CONFIRMED; organic-fresh must be."""
    repair = sem.classify_loop_state(
        dispatch_age_minutes=1.0, dispatch_stale_threshold_minutes=DISPATCH_THRESH,
        completion_age_minutes=2.0, completion_stale_threshold_minutes=COMPLETION_THRESH,
        completion_origin="noos_integrator_repair",
    )
    restored = sem.classify_loop_state(
        dispatch_age_minutes=1.0, dispatch_stale_threshold_minutes=DISPATCH_THRESH,
        completion_age_minutes=2.0, completion_stale_threshold_minutes=COMPLETION_THRESH,
        completion_origin="http_loop",
    )
    masked_blocked = (
        repair["execution_state"] == sem.DEGRADED_REPAIR_SUSTAINED
        and repair["execution_state"] != sem.RUNNING_CONFIRMED
        and repair["route_permits_execution_mutation"] is False
    )
    restored_ok = restored["execution_state"] == sem.RUNNING_CONFIRMED
    return {
        "check": "masking_regression",
        "repair_state": repair["execution_state"],
        "restored_state": restored["execution_state"],
        "repair_not_running_confirmed": masked_blocked,
        "organic_returns_running_confirmed": restored_ok,
        "ok": masked_blocked and restored_ok,
    }


def run_truthful_failure(art: Path, rcp: Path) -> dict[str, Any]:
    res = lx.run_job({"task_kind": "digest", "records": []}, artifact_dir=art, receipt_dir=rcp)
    ok = res["status"] == fsm.FAILED and res["json_artifact"] is None
    return {"check": "truthful_failure", "state": res["status"], "no_artifact": res["json_artifact"] is None, "ok": ok}


def verify(*, cycles: int = 3, emit_receipts: bool = False, workdir: Path | None = None) -> dict[str, Any]:
    tmp = workdir or Path(tempfile.mkdtemp(prefix="noos-motor-verify-"))
    art, rcp = tmp / "art", tmp / "rcp"
    results = {
        "schema": "noos-motor-v1-verify-v1",
        "not_a_verdict": "Deterministic self-verification of the OFFLINE organic path. Cloud http_loop 3-cycle is EXTERNAL_ACTIVATION_REQUIRED and is NOT covered here. SUBMITTED for independent verification.",
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
        "verified_at": utc_now(),
        "checks": [
            run_local_organic_cycles(cycles, art, rcp),
            run_masking_regression(),
            run_truthful_failure(art, rcp),
        ],
    }
    results["all_ok"] = all(c.get("ok") or c.get("consecutive_pass") for c in results["checks"])
    if emit_receipts:
        RUNWAY.mkdir(parents=True, exist_ok=True)
        cyc = results["checks"][0]["cycles"]
        for c in cyc:
            (RUNWAY / f"noos-motor-v1-organic-cycle-{c['cycle']}.json").write_text(
                json.dumps({
                    "schema": "noos-motor-v1-organic-cycle-v1",
                    "not_a_verdict": "LOCAL reference organic cycle (execution_plane=local_reference). This is NOT a cloud http_loop cycle; the cloud 3-cycle is EXTERNAL_ACTIVATION_REQUIRED. SUBMITTED for independent verification.",
                    "verified_at": results["verified_at"],
                    **c,
                }, indent=2) + "\n", encoding="utf-8"
            )
        (RUNWAY / "noos-motor-v1-masking-regression.json").write_text(
            json.dumps({"schema": "noos-motor-v1-masking-regression-v1", "verified_at": results["verified_at"], **results["checks"][1]}, indent=2) + "\n",
            encoding="utf-8",
        )
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cycles", type=int, default=3)
    ap.add_argument("--emit-receipts", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    res = verify(cycles=args.cycles, emit_receipts=args.emit_receipts)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        for c in res["checks"]:
            verdict = "OK" if (c.get("ok") or c.get("consecutive_pass")) else "FAIL"
            print(f"[{verdict}] {c['check']}")
        print(f"OVERALL: {'ALL_OK' if res['all_ok'] else 'FAIL'}")
    return 0 if res["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
