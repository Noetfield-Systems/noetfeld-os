#!/usr/bin/env python3
"""NOOS control layer — 11-layer TrustField parallel autorun health (Studio IDE model)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/noos-trustfield-parallel-layers-v1.json"
PROOF = ROOT / "receipts/proof/noos-trustfield-parallel-layers-observe-v1.json"
RUNTIME = ROOT / ".noos-runtime/observe/trustfield"
PLAN_WORKER_HEALTH = "https://trustfield-plan-worker-production.up.railway.app/health"

# Railway plan_matrix lane id → layer id
RAILWAY_LANE_MAP = {
    "plan_matrix": "TF-L03",
    "critic_circle": "TF-L05",
    "deep_research": "TF-L06",
    "self_heal": "TF-L08",
    "www_upgrade_queue": "TF-L09",
    "autorun_stack": "TF-L11",
    "partner_access": "TF-L10",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def fetch_plan_worker() -> dict:
    try:
        with urllib.request.urlopen(PLAN_WORKER_HEALTH, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"status": "unreachable", "error": str(exc)[:200]}


def fetch_registry_observe() -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/observe_trustfield_loop_registry_v1.py"), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode not in (0, 1) and not proc.stdout.strip():
        return {"ok": False, "error": proc.stderr[:300] or "observe failed"}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid json from registry observe"}


def registry_row_status(observe: dict, loop_id: str | None) -> tuple[str, str | None]:
    if not loop_id:
        return "unknown", None
    for row in observe.get("rows") or []:
        if row.get("loop_id") == loop_id:
            return str(row.get("status") or "unknown"), row.get("reason")
    if loop_id == "tf_cf_lane_partner_access_v1":
        # May not exist as separate row yet — infer from partner_access lane health
        return "yellow", "cf_loop_id not registered in registry yet"
    return "yellow", "loop_id not in registry sample"


def layer_status(
    layer: dict,
    *,
    plan_worker: dict,
    registry_observe: dict,
) -> dict:
    lid = layer["id"]
    lane = (layer.get("motor") or {}).get("railway_lane")
    cf_loop = layer.get("cf_loop_id")
    reasons: list[str] = []
    status = "green"

    reg_status, reg_reason = registry_row_status(registry_observe, cf_loop)
    if reg_status == "red":
        status = "red"
        if reg_reason:
            reasons.append(reg_reason)
    elif reg_status == "yellow" and status == "green":
        status = "yellow"
        if reg_reason:
            reasons.append(reg_reason)

    if lid == "TF-L01":
        overall = registry_observe.get("overall_status") or "unknown"
        if overall == "red":
            status = "red"
        elif overall == "yellow" and status == "green":
            status = "yellow"
        reasons.append(f"registry_overall={overall}")
    elif lid == "TF-L02":
        # Shares critic_circle motor + staleness state file
        staleness = (layer.get("motor") or {}).get("state")
        reasons.append(f"staleness_state={staleness}")
    elif lid == "TF-L04":
        # ROI layer — autorun_stack partial + recipe runs
        if plan_worker.get("status") == "degraded":
            status = "yellow" if status != "red" else status
            reasons.append("plan_worker_degraded")
    elif lane:
        lane_ok = (plan_worker.get("lane_ok") or {}).get(lane)
        if lane_ok is False:
            status = "red"
            failures = plan_worker.get("self_heal_failures") or []
            if lane == "self_heal" and failures:
                reasons.append(f"self_heal_failures={failures[:3]}")
            else:
                reasons.append(f"railway_lane_{lane}=false")
        elif lane_ok is True and status == "green":
            reasons.append(f"railway_lane_{lane}=true")

    if plan_worker.get("status") == "unreachable":
        status = "red"
        reasons.append("plan_worker_unreachable")

    motor_state = "RUNNING" if status == "green" else "FAILED_WITH_RECEIPT" if status == "red" else "DEGRADED"
    if status == "green" and lane is None and lid not in ("TF-L01", "TF-L07"):
        motor_state = "IDLE_NO_WORK"

    return {
        "layer_id": lid,
        "name": layer.get("name"),
        "value_class": layer.get("value_class"),
        "tier": layer.get("tier"),
        "status": status,
        "motor_state": motor_state,
        "cf_loop_id": cf_loop,
        "railway_lane": lane,
        "reasons": reasons,
    }


def observe(*, write_receipt: bool = False) -> dict:
    manifest = load_manifest()
    layers = manifest.get("layers") or []
    plan_worker = fetch_plan_worker()
    registry_observe = fetch_registry_observe()

    layer_rows = [
        layer_status(layer, plan_worker=plan_worker, registry_observe=registry_observe) for layer in layers
    ]

    counts = {"green": 0, "yellow": 0, "red": 0, "unknown": 0}
    for row in layer_rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    overall = "green"
    if counts.get("red", 0) > 0:
        overall = "red"
    elif counts.get("yellow", 0) > 0:
        overall = "yellow"

    roi_layers = [r for r in layer_rows if r.get("value_class") == "revenue_path"]
    hygiene_layers = [r for r in layer_rows if r.get("value_class") == "hygiene"]

    result = {
        "schema": "noos-trustfield-parallel-layers-observe-v1",
        "at": utc_now(),
        "read_only": True,
        "one_law": manifest.get("one_law"),
        "layer_count": len(layer_rows),
        "overall_status": overall,
        "summary": counts,
        "roi_intelligence": {
            "revenue_path_layers": len(roi_layers),
            "revenue_path_green": sum(1 for r in roi_layers if r["status"] == "green"),
            "hygiene_layers": len(hygiene_layers),
            "plan_worker_status": plan_worker.get("status"),
            "plan_worker_last_cycle_ok": plan_worker.get("last_cycle_ok"),
            "cycles_completed": plan_worker.get("cycles_completed"),
        },
        "fleet": manifest.get("fleet_dispatcher"),
        "plan_worker": {
            "url": PLAN_WORKER_HEALTH,
            "status": plan_worker.get("status"),
            "last_cycle_ok": plan_worker.get("last_cycle_ok"),
            "lane_ok": plan_worker.get("lane_ok"),
            "lanes_run": plan_worker.get("lanes_run"),
        },
        "registry_observe": {
            "overall_status": registry_observe.get("overall_status"),
            "row_count": registry_observe.get("row_count"),
            "probe_present": (registry_observe.get("summary") or {}).get("probe_present"),
            "deadman_status": (registry_observe.get("summary") or {}).get("deadman_status"),
        },
        "layers": layer_rows,
        "trustfield_worker_deliverables": manifest.get("trustfield_worker_deliverables"),
        "closure_token": f"NOOS_TF_11_LAYERS: {overall}",
    }

    if write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        RUNTIME.mkdir(parents=True, exist_ok=True)
        (RUNTIME / "parallel-layers-observe-v1.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["receipt_path"] = str(PROOF)

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = observe(write_receipt=args.write_receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        s = row.get("summary") or {}
        print(
            f"tf_11_layers overall={row.get('overall_status')} "
            f"green={s.get('green')} yellow={s.get('yellow')} red={s.get('red')} "
            f"plan_worker={row.get('plan_worker', {}).get('status')}"
        )
        print(row.get("closure_token"))

    return 0 if row.get("overall_status") == "green" else 1


if __name__ == "__main__":
    raise SystemExit(main())
