"""SSOT governance demo — policy change → invalidate → re-brief → evaluate → TLE.

Runs entirely on fixtures; no external services required.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT_DIR = ROOT / "demos" / "copilot-governance" / "ssot"


def _load(name: str) -> dict[str, Any]:
    return json.loads((SSOT_DIR / name).read_text(encoding="utf-8"))


def _parse_version(raw: str | float) -> float:
    text = str(raw).strip().lower().lstrip("v")
    try:
        return float(text)
    except ValueError:
        return 3.1


def apply_ssot_change(
    *,
    from_version: str,
    to_version: str,
    pending: list[dict[str, Any]],
) -> dict[str, Any]:
    from_v = _parse_version(from_version)
    to_v = _parse_version(to_version)
    invalidated: list[dict[str, Any]] = []
    re_brief_queue: list[dict[str, Any]] = []

    for item in pending:
        pv = _parse_version(item.get("policy_version", "3.1"))
        if pv < to_v:
            invalidated.append(
                {
                    "rid": item["rid"],
                    "action": item.get("action"),
                    "prior_policy_version": str(pv),
                    "status": "invalidated",
                    "reason": f"SSOT_CHANGED — policy v{to_v} supersedes v{from_v}",
                }
            )
            re_brief_queue.append(
                {
                    "rid": item["rid"],
                    "action": item.get("action"),
                    "required_policy_version": str(to_v),
                    "briefing_status": "queued",
                    "reason": f"Re-brief required against Copilot Acceptable Use v{to_v}",
                }
            )

    return {
        "event": "SSOT_CHANGED",
        "from_version": str(from_v),
        "to_version": str(to_v),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "policy_id": "copilot-acceptable-use",
        "invalidated_count": len(invalidated),
        "invalidated": invalidated,
        "re_brief_queue": re_brief_queue,
    }


def evaluate_copilot_rollout(*, policy_version: str) -> dict[str, Any]:
    """Deterministic evaluate aligned with api/_lib/governance-evaluate.js v3.2 rules."""
    pv = _parse_version(policy_version)
    context = (
        "Copilot rollout to production M365 tenant — re-briefed after policy v3.2 publish"
    )
    score = 10
    reasons: list[str] = []
    conditions: list[str] = []

    if pv >= 3.2:
        score += 10
        reasons.append("Production Copilot rollout requires v3.2 evidence index and approver chain.")

    score = min(100, max(0, score))
    if score >= 70:
        decision = "deny"
    elif score >= 40:
        decision = "review"
        conditions.append("Route to compliance owner with RID attached.")
    else:
        decision = "allow"
        reasons.append("Intent within default policy tolerance for shadow evaluation.")
        conditions.append(
            "External systems may proceed only under your institution's execution authority."
        )

    rid_suffix = datetime.now(timezone.utc).strftime("%H%M")
    return {
        "decision": decision,
        "risk_score": score,
        "reason": reasons or ["Re-brief completed against current SSOT."],
        "conditions": conditions,
        "rid": f"RID-SSOT-DEMO-{rid_suffix}",
        "policy_version": str(pv),
        "context": context,
        "confidence_score": round((100 - score) / 100, 2),
    }


def build_demo_package() -> dict[str, Any]:
    policy_old = _load("policy_v3.1.json")
    policy_new = _load("policy_v3.2.json")
    pending_doc = _load("pending_evaluations.json")
    pending = pending_doc["pending_evaluations"]

    ssot_event = apply_ssot_change(
        from_version=policy_old["version"],
        to_version=policy_new["version"],
        pending=pending,
    )
    eval_result = evaluate_copilot_rollout(policy_version=policy_new["version"])

    board_snippet = {
        "title": "Copilot Governance — board digest (demo excerpt)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executive_summary": (
            f"Policy v{policy_new['version']} published; "
            f"{ssot_event['invalidated_count']} stale evaluations invalidated; "
            f"fresh evaluate → {eval_result['decision']} with signed receipt."
        ),
        "bullets": [
            "SSOT change triggers automatic context invalidation (governance latency fix).",
            "Re-brief queue routes agency agents through middleware evaluate API.",
            "Board PDF exports TLE + evidence index — no payment rails or execution.",
        ],
        "decision": eval_result["decision"],
        "confidence_score": eval_result["confidence_score"],
    }

    tle_receipt = {
        "tle_id": f"TLE-{eval_result['rid'][-12:].upper()}",
        "decision": eval_result["decision"],
        "confidence_score": str(eval_result["confidence_score"]),
        "rid": eval_result["rid"],
        "evidence_index": "purview · entra · audit",
        "export_integrity": "PASS · fail closed on tamper",
        "policy_version": policy_new["version"],
    }

    return {
        "demo": "noetfield-ssot-governance-vertical",
        "status": "ready_for_demo",
        "policy_before": policy_old,
        "policy_after": policy_new,
        "ssot_event": ssot_event,
        "re_brief_queue": ssot_event["re_brief_queue"],
        "evaluate_result": eval_result,
        "tle_receipt": tle_receipt,
        "board_snippet": board_snippet,
        "middleware": {
            "ssot_endpoint": "POST /api/demo/ssot-change",
            "evaluate_endpoint": "POST /api/demo/evaluate",
            "note": "Agency agents call Noetfield as gate + ledger — not the execution layer.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(SSOT_DIR / "generated" / "demo_output.json"),
        help="Write JSON demo output to this path.",
    )
    args = parser.parse_args()
    payload = build_demo_package()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    print(
        f"SSOT v{payload['policy_after']['version']}: "
        f"{payload['ssot_event']['invalidated_count']} invalidated → "
        f"evaluate {payload['evaluate_result']['decision']}"
    )


if __name__ == "__main__":
    main()
