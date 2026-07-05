#!/usr/bin/env python3
"""UPG-0205/0212 — registry-driven scaling evaluation (THROTTLED_ROI rules)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCALING = ROOT / "data/noos-runtime-scaling-v1.json"
PROOF = ROOT / "receipts/proof/noos-inbox-scaler-v1.json"
PROOF_ALL = ROOT / "receipts/proof/noos-runtime-scaling-eval-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def inbox_depth() -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "scripts/reenqueue_blocked_upg_inbox_v1.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    blocked = 0
    if proc.stdout.strip():
        try:
            blocked = int(json.loads(proc.stdout).get("blocked_seen") or 0)
        except json.JSONDecodeError:
            blocked = 0
    return {"pending": blocked, "source": "reenqueue_blocked_probe", "ok": True}


def metric_value(metric: str, *, simulate: dict[str, int | None]) -> int:
    if metric in simulate and simulate[metric] is not None:
        return int(simulate[metric])
    if metric == "pending_inbox_depth":
        return int(inbox_depth().get("pending") or 0)
    return 0


def evaluate_rule(rule: dict[str, Any], *, simulate: dict[str, int | None]) -> dict[str, Any]:
    metric = str(rule.get("metric") or "")
    threshold = int(rule.get("threshold") or 0)
    value = metric_value(metric, simulate=simulate)
    tripped = value > threshold
    return {
        "rule_id": rule.get("id"),
        "sandbox": rule.get("sandbox"),
        "metric": metric,
        "value": value,
        "threshold": threshold,
        "tripped": tripped,
        "action": rule.get("action"),
        "roi_class": rule.get("roi_class"),
        "scale_from": rule.get("from"),
        "scale_to": rule.get("to"),
    }


def evaluate(*, simulate_pending: int | None = None, evaluate_all: bool = False) -> dict[str, Any]:
    cfg = json.loads(SCALING.read_text(encoding="utf-8"))
    rules = cfg.get("rules") or []
    simulate = {"pending_inbox_depth": simulate_pending}

    if evaluate_all:
        evaluations = [evaluate_rule(r, simulate=simulate) for r in rules]
        tripped = [e for e in evaluations if e.get("tripped")]
        return {
            "schema": "noos-runtime-scaling-eval-v1",
            "evaluated_at": utc_now(),
            "authority": "UPG-0212",
            "rule_count": len(evaluations),
            "tripped_count": len(tripped),
            "evaluations": evaluations,
            "tripped_rules": tripped,
            "fly_apps": cfg.get("fly_apps"),
            "ok": True,
            "report_line": (
                f"runtime_scaling_eval · rules={len(evaluations)} tripped={len(tripped)}"
            ),
        }

    rule = next((r for r in rules if r.get("id") == "inbox-queue-depth"), {})
    ev = evaluate_rule(rule, simulate=simulate)
    depth_row = inbox_depth() if simulate_pending is None else {"pending": simulate_pending, "simulated": True}
    return {
        "schema": "noos-inbox-scaler-v1",
        "evaluated_at": utc_now(),
        "pending": ev["value"],
        "threshold": ev["threshold"],
        "should_scale": ev["tripped"],
        "action": ev.get("action"),
        "scale_from": ev.get("scale_from"),
        "scale_to": ev.get("scale_to"),
        "roi_class": ev.get("roi_class"),
        "depth_probe": depth_row,
        "ok": True,
        "report_line": f"inbox_scaler · pending={ev['value']} scale={ev['tripped']}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--simulate-pending", type=int, default=None)
    ap.add_argument("--evaluate-all", action="store_true", help="Evaluate all THROTTLED_ROI rules")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = evaluate(simulate_pending=args.simulate_pending, evaluate_all=args.evaluate_all)
    if args.write_receipt:
        path = PROOF_ALL if args.evaluate_all else PROOF
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(path.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
