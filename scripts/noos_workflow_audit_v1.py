#!/usr/bin/env python3
"""Strict 24/7 workflow audit — finds hidden failures, drift, and fake-green paths."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github/workflows"
LOOP_REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
import autorun_status_v1 as dash  # noqa: E402
import noos_loop_heartbeat_v1 as hb  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def scan_continue_on_error() -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for path in sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml")):
        for lineno, line in enumerate(read_text(path).splitlines(), start=1):
            if re.search(r"^\s*continue-on-error:\s*true\s*$", line):
                findings.append(
                    {
                        "scope": str(path.relative_to(ROOT)),
                        "severity": "high",
                        "line": lineno,
                        "summary": "Workflow step masks failures with continue-on-error",
                        "detail": line.strip(),
                    }
                )

    loop_text = read_text(LOOP_REGISTRY)
    for lineno, line in enumerate(loop_text.splitlines(), start=1):
        if re.search(r'"continue_on_error"\s*:\s*true', line):
            findings.append(
                {
                    "scope": str(LOOP_REGISTRY.relative_to(ROOT)),
                    "severity": "high",
                    "line": lineno,
                    "summary": "Loop registry masks failures with continue_on_error",
                    "detail": line.strip(),
                }
            )

    return findings


def classify_finding(finding: dict[str, Any]) -> str:
    scope = str(finding.get("scope") or "")
    summary = str(finding.get("summary") or "")
    detail = str(finding.get("detail") or "")
    if scope == "trigger_registry":
        return "blocking"
    if "continue-on-error" in summary.lower():
        return "blocking"
    if summary == "Dirty workspace total exceeds triage threshold":
        return "blocking"
    if summary == "Workflow SLO miss" and scope in {"noos_schedule_canary", "noos_factory_autorun", "noos_factory_autorun_tick"}:
        return "blocking"
    if summary == "Workflow SLO miss":
        return "dependency" if any(tok in detail for tok in ("freshness_missing", "latency_missing")) else "blocking"
    if summary.startswith("Workflow is not healthy"):
        return "dependency" if any(tok in detail for tok in ("stale_supabase_row", "no_supabase_receipt", "supabase_not_configured")) else "blocking"
    if summary == "Workflow has no observed_at evidence":
        return "dependency"
    if "stale_supabase_row" in detail or "no_supabase_receipt" in detail or "supabase_not_configured" in detail:
        return "dependency"
    return "blocking"


def audit_report() -> dict[str, Any]:
    dashboard = dash.build_dashboard()
    heartbeat = hb.build_heartbeat()
    findings = scan_continue_on_error()

    dash_findings = dash.dashboard_findings(dashboard)
    hb_findings = hb.heartbeat_findings(heartbeat)

    findings.extend(dash_findings)
    findings.extend(hb_findings)
    classified = [(finding, classify_finding(finding)) for finding in findings]
    blocking = [finding for finding, kind in classified if kind == "blocking"]
    dependency = [finding for finding, kind in classified if kind == "dependency"]

    report = {
        "schema": "noos-workflow-audit-v1",
        "generated_at": utc_now(),
        "overall_ok": not blocking,
        "findings_count": len(findings),
        "blocking_count": len(blocking),
        "dependency_count": len(dependency),
        "findings": findings,
        "dashboard": {
            "schema": dashboard.get("schema"),
            "triage_required": dashboard.get("triage_required"),
            "dirty_total": dashboard.get("dirty_total"),
            "workflow_count": len(dashboard.get("workflows") or []),
        },
        "heartbeat": {
            "schema": heartbeat.get("schema"),
            "drift_count": len(heartbeat.get("drift", {}).get("mismatches") or []),
            "escalation_count": len(heartbeat.get("escalations") or []),
            "loop_count": len(heartbeat.get("loops") or []),
        },
    }
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    report = audit_report()
    if args.write_receipt:
        out_dir = ROOT / ".noos-runtime" / "workflow-audit"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"audit-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"workflow_audit findings={report['findings_count']} blocking={report['blocking_count']} "
            f"dashboard_workflows={report['dashboard']['workflow_count']} "
            f"heartbeat_loops={report['heartbeat']['loop_count']}"
        )
        for finding in report["findings"][:20]:
            print(f"  {finding['severity'].upper()} {finding['scope']}: {finding['summary']}")

    return 0 if report["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
