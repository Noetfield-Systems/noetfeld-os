#!/usr/bin/env python3
"""Shared SLO scoring and Kaizen autofile helpers for NOOS autorun surfaces."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slo_config(defaults: dict[str, Any], row: dict[str, Any]) -> dict[str, float]:
    slo = dict(defaults or {})
    if isinstance(row.get("slo"), dict):
        slo.update(row["slo"])
    return {
        "freshness_target_minutes": float(slo.get("freshness_target_minutes") or 30),
        "success_rate_target": float(slo.get("success_rate_target") or 0.98),
        "latency_target_minutes": float(slo.get("latency_target_minutes") or 60),
    }


def status_proxy_success_rate(status: str) -> float:
    normalized = str(status or "").upper()
    if normalized == "COMPLETE":
        return 1.0
    if normalized in {"RUNNING", "IDLE_NO_WORK"}:
        return 0.95
    if normalized == "TRIAGE_REQUIRED":
        return 0.5
    if normalized in {"BLOCKED_WITH_REASON", "FAILED_WITH_RECEIPT"}:
        return 0.0
    return 0.6


def score_slo(*, freshness_minutes: float | None, success_rate: float | None, latency_minutes: float | None, targets: dict[str, float]) -> dict[str, Any]:
    score = 100.0
    misses: list[str] = []

    freshness_target = float(targets["freshness_target_minutes"])
    success_target = float(targets["success_rate_target"])
    latency_target = float(targets["latency_target_minutes"])

    if freshness_minutes is None:
        score -= 20.0
        misses.append("freshness_missing")
    elif freshness_minutes > freshness_target:
        score -= min(45.0, ((freshness_minutes - freshness_target) / max(freshness_target, 1.0)) * 45.0)
        misses.append("freshness_miss")

    if success_rate is None:
        score -= 20.0
        misses.append("success_rate_missing")
    elif success_rate < success_target:
        score -= min(35.0, ((success_target - success_rate) / max(success_target, 0.01)) * 35.0)
        misses.append("success_rate_miss")

    if latency_minutes is None:
        score -= 15.0
        misses.append("latency_missing")
    elif latency_minutes > latency_target:
        score -= min(25.0, ((latency_minutes - latency_target) / max(latency_target, 1.0)) * 25.0)
        misses.append("latency_miss")

    score = max(0.0, round(score, 2))
    return {
        "score": score,
        "misses": misses,
        "ok": score >= 80.0 and not misses,
    }


def autofile_kaizen_receipt(
    *,
    root: Path,
    source: str,
    loop_id: str,
    score_row: dict[str, Any],
    evidence: dict[str, Any],
) -> str:
    out_dir = root / "receipts" / "proof"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_loop = loop_id.replace("/", "_")
    path = out_dir / f"noos-kaizen-{source}-{safe_loop}-{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    doc = {
        "schema": "improvement-receipt-v2",
        "class": "machine_safe",
        "source": "failed_check",
        "diff_summary": f"{source} SLO miss for {loop_id}: score {score_row['score']} < 80",
        "expected_effect": "Restore freshness, success rate, and latency SLO compliance for the loop",
        "expected_roi": {
            "cost_saved_usd": 0,
            "risk_reduced": "workflow heartbeat drift / SLO miss",
            "revenue_unblocked": "",
            "build_cost_usd": 0,
        },
        "rollback_command": "revert the SLO target change or fix the underlying loop/runtime issue",
        "external_verify_before": "",
        "external_verify_after": "",
        "auto_rolled_back": False,
        "source_ref": source,
        "loop_id": loop_id,
        "score": score_row,
        "evidence": evidence,
        "generated_at": utc_now(),
    }
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(root))
