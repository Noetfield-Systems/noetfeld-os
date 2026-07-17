#!/usr/bin/env python3
"""NOOS 24/7 loop heartbeat — governed-autorun L11/L12 daily rollup.

Emits autorun-heartbeat-v2: per-loop last state, cost window, spend-by-value_class,
throttle flag, L12 drift check (registry cron vs deployed workflow cron), and
founder_blocked total. Read-only; never mutates loop config or verifiers (L5).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
RUNTIME = ROOT / ".noos-runtime/loops"
WORKFLOWS = ROOT / ".github/workflows"

sys.path.insert(0, str(ROOT / "scripts"))
from sandbox_health_sweep_v1 import run_sweep  # noqa: E402
from noos_slo_v1 import autofile_kaizen_receipt, score_slo, slo_config, status_proxy_success_rate  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    text = str(ts).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def age_minutes(ts: str | None) -> float | None:
    dt = parse_iso(ts)
    if dt is None:
        return None
    return round((datetime.now(timezone.utc) - dt).total_seconds() / 60.0, 2)


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def deployed_cron(workflow_file: str) -> str | None:
    path = WORKFLOWS / workflow_file
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.search(r'cron:\s*["\']([^"\']+)["\']', line)
        if m:
            return m.group(1)
    return None


def committed_cron(interval_minutes: int) -> str:
    """Expected cron surface derived from the registry interval."""
    if interval_minutes >= 60:
        return "hourly"
    return f"every_{interval_minutes}m"


def cron_matches(deployed: str | None, interval_minutes: int) -> bool:
    """L12 — deployed cron must fire at least as often as the registry interval."""
    if not deployed:
        return False
    minute_field = deployed.split()[0]
    if minute_field.startswith("*/"):
        try:
            return int(minute_field[2:]) <= interval_minutes
        except ValueError:
            return False
    if minute_field == "*":
        return True
    if interval_minutes >= 60:
        return True
    # explicit comma list e.g. "0,10,20,30,40,50" — count slots per hour
    slots = [s for s in minute_field.split(",") if s.strip().isdigit()]
    if not slots:
        return False
    return (60 / len(slots)) <= interval_minutes + 0.001


def loop_state(loop_id: str) -> dict[str, Any]:
    path = RUNTIME / loop_id / "state-v1.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def recent_cycles(loop_id: str, limit: int = 20) -> list[dict[str, Any]]:
    d = RUNTIME / loop_id
    if not d.is_dir():
        return []
    files = sorted(d.glob("cycle-*.json"))[-limit:]
    out: list[dict[str, Any]] = []
    for f in files:
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def trigger_registry_sweep() -> dict[str, Any]:
    """L12 T-REG — diff live triggers vs data/trigger-registry-v1.json."""
    try:
        return run_sweep(repo_root=ROOT)
    except Exception as exc:
        return {
            "schema": "sandbox-health-sweep-v1",
            "ok": False,
            "drift": True,
            "report_line": f"trigger_sweep_error · {exc}",
            "errors": [str(exc)[:120]],
        }


def build_heartbeat() -> dict[str, Any]:
    registry = load_registry()
    slo_defaults = registry.get("slo_defaults") or {}
    loops_out: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    founder_blocked_total = 0
    founder_gated_improvements: list[dict[str, Any]] = []
    trigger_sweep = trigger_registry_sweep()
    if trigger_sweep.get("drift") or not trigger_sweep.get("ok"):
        mismatches.append(
            {
                "loop_id": "trigger_registry",
                "surface": "trigger_sweep",
                "committed_truth": trigger_sweep.get("registry_path"),
                "deployed_truth": trigger_sweep.get("report_line"),
                "dead_or_mismatch": trigger_sweep.get("dead_or_mismatch"),
                "unregistered_live": trigger_sweep.get("unregistered_live"),
            }
        )

    for loop in registry.get("loops") or []:
        loop_id = str(loop["id"])
        interval = int(loop.get("interval_minutes") or 60)
        state = loop_state(loop_id)
        cycles = recent_cycles(loop_id)

        cost_window = sum(float((c.get("cost") or {}).get("total_usd") or 0) for c in cycles)
        completes = [c for c in cycles if c.get("state_after") == "COMPLETE"]
        cost_per_complete = (cost_window / len(completes)) if completes else 0.0
        value_class = loop.get("value_class") or "hygiene"
        spend_by_value: dict[str, float] = {
            "revenue_path": 0.0, "proof_asset": 0.0, "risk_reduction": 0.0, "hygiene": 0.0, "none": 0.0
        }
        for c in cycles:
            vc = c.get("value_class") or value_class
            spend_by_value[vc] = spend_by_value.get(vc, 0.0) + float((c.get("cost") or {}).get("total_usd") or 0)

        # L11 throttle: >30% of window spend in value_class:none → THROTTLED_ROI
        total_spend = sum(spend_by_value.values())
        throttled = bool(total_spend > 0 and (spend_by_value["none"] / total_spend) > 0.30)

        fb = 0
        for c in reversed(cycles):
            fbv = (c.get("founder_blocked") or {}).get("count")
            if isinstance(fbv, int):
                fb = fbv
                break
        founder_blocked_total = max(founder_blocked_total, fb)

        dep_cron = deployed_cron(str(loop.get("github_workflow") or ""))
        if not cron_matches(dep_cron, interval):
            mismatches.append({
                "loop_id": loop_id,
                "surface": "cron_schedule",
                "committed_truth": committed_cron(interval),
                "deployed_truth": dep_cron or "MISSING",
            })

        freshness_minutes = age_minutes(state.get("last_finished_at") or state.get("last_status_at") or state.get("last_recorded_at"))
        success_rate = (
            sum(1 for c in cycles if str(c.get("state_after") or "").upper() == "COMPLETE") / len(cycles)
            if cycles
            else status_proxy_success_rate(str(state.get("last_state") or state.get("last_status") or ""))
        )
        latency_minutes = freshness_minutes
        slo_targets = slo_config(slo_defaults, loop)
        slo = score_slo(
            freshness_minutes=freshness_minutes,
            success_rate=success_rate,
            latency_minutes=latency_minutes,
            targets=slo_targets,
        )
        kaizen_receipt = None
        if not slo["ok"]:
            kaizen_receipt = autofile_kaizen_receipt(
                root=ROOT,
                source="loop-heartbeat",
                loop_id=loop_id,
                score_row=slo,
                evidence={
                    "workflow_id": str(loop.get("github_workflow") or loop_id),
                    "freshness_minutes": freshness_minutes,
                    "success_rate": round(success_rate, 4) if success_rate is not None else None,
                    "latency_minutes": latency_minutes,
                    "status": state.get("last_state") or state.get("last_status") or "UNKNOWN",
                },
            )
            founder_gated_improvements.append(
                {
                    "id": kaizen_receipt,
                    "expected_roi": {
                        "cost_saved_usd": 0,
                        "risk_reduced": "loop heartbeat SLO miss",
                        "revenue_unblocked": "",
                        "build_cost_usd": 0,
                    },
                    "age_days": 0,
                }
            )

        loops_out.append({
            "workflow_id": str(loop.get("github_workflow") or loop_id),
            "lane": loop.get("lane") or "noos",
            "last_run_at": state.get("last_finished_at") or "",
            "state": state.get("last_state") or state.get("last_status") or "UNKNOWN",
            "sink_invariant_ok": all(
                (c.get("sink_invariant") or {}).get("verdict") == "PASS" for c in cycles
            ) if cycles else None,
            "cost_window_usd": round(cost_window, 6),
            "cost_per_complete_usd": round(cost_per_complete, 6),
            "spend_by_value_class": {k: round(v, 6) for k, v in spend_by_value.items()},
            "throttled_roi": throttled,
            "cycles_observed": len(cycles),
            "slo": {
                "targets": slo_targets,
                "observed": {
                    "freshness_minutes": freshness_minutes,
                    "success_rate": round(success_rate, 4),
                    "latency_minutes": latency_minutes,
                },
                "score": slo["score"],
                "misses": slo["misses"],
                "ok": slo["ok"],
                "kaizen_receipt": kaizen_receipt,
            },
        })

    findings = heartbeat_findings(
        {
            "drift": {"mismatches": mismatches},
            "loops": loops_out,
        }
    )
    return {
        "schema": "autorun-heartbeat-v2",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "generated_at": utc_now(),
        "loops": loops_out,
        "drift": {
            "checked": True,
            "mismatches": mismatches,
            "trigger_sweep": trigger_sweep,
        },
        "founder_blocked_total": founder_blocked_total,
        "founder_gated_improvements": founder_gated_improvements,
        "escalations": [m["loop_id"] for m in mismatches]
        + [lp["workflow_id"] for lp in loops_out if lp["throttled_roi"] or not lp["slo"]["ok"]],
        "critique": {"overall_ok": not findings, "findings": findings},
    }


def heartbeat_findings(hb: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for mismatch in hb.get("drift", {}).get("mismatches") or []:
        findings.append(
            {
                "scope": mismatch.get("loop_id"),
                "severity": "high",
                "summary": f"Drift mismatch on {mismatch.get('surface')}",
                "detail": f"committed={mismatch.get('committed_truth')} deployed={mismatch.get('deployed_truth')}",
            }
        )
    for loop in hb.get("loops") or []:
        slo = loop.get("slo") or {}
        observed = loop.get("last_run_at")
        cycles = int(loop.get("cycles_observed") or 0)
        if not slo.get("ok") and (observed or cycles > 0):
            findings.append(
                {
                    "scope": loop.get("workflow_id"),
                    "severity": "high",
                    "summary": "Loop SLO miss",
                    "detail": ", ".join(slo.get("misses") or []) or "slo_miss",
                }
            )
        if loop.get("throttled_roi"):
            findings.append(
                {
                    "scope": loop.get("workflow_id"),
                    "severity": "medium",
                    "summary": "Loop ROI is throttled",
                    "detail": "More spend is going to low-value work than the allowed threshold",
                }
            )
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    hb = build_heartbeat()
    if args.write_receipt:
        out_dir = ROOT / ".noos-runtime/heartbeat"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"heartbeat-{hb['date']}.json").write_text(
            json.dumps(hb, indent=2) + "\n", encoding="utf-8"
        )

    if args.json:
        print(json.dumps(hb, indent=2))
    else:
        drift = hb["drift"]["mismatches"]
        print(
            f"heartbeat {hb['date']} loops={len(hb['loops'])} "
            f"drift_mismatches={len(drift)} founder_blocked={hb['founder_blocked_total']} "
            f"escalations={len(hb['escalations'])}"
        )
        for m in drift:
            print(f"  DRIFT {m['loop_id']}: committed={m['committed_truth']} deployed={m['deployed_truth']}")

    # Fail closed on drift and SLO misses so the heartbeat is a real critique, not a green wash.
    return 1 if heartbeat_findings(hb) else 0


if __name__ == "__main__":
    raise SystemExit(main())
