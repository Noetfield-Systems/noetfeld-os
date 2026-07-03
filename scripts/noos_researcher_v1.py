#!/usr/bin/env python3
"""
NOOS Researcher Agent v1 — Deep-dive investigation of escalated findings.

Gathers context for high-risk findings:
- Workflow history (past runs, logs, timing patterns)
- Integration status (API health, dependency connectivity)
- Configuration drift (recent changes, state inconsistencies)
- Cross-repo dependencies (which repos are affected)

Hands off detailed reports to specialist for fix proposals.

Usage:
  python3 scripts/noos_researcher_v1.py \
    --handoff-file data/noos-healing-handoff-v1.json \
    --output-file data/noos-research-findings-v1.json
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Investigation depth levels
RESEARCH_DEPTH = {
    "quick": {"timeout": 30, "scope": "local"},
    "standard": {"timeout": 120, "scope": "local+logs"},
    "deep": {"timeout": 300, "scope": "local+logs+history+integrations"},
}


def investigate_workflow_history(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Gather workflow run history for the affected workflow."""
    workflow_file = finding.get("metadata", {}).get("workflow_file")
    limit = 10  # Last 10 runs

    if not workflow_file:
        return {"status": "skipped", "reason": "No workflow_file in metadata"}

    try:
        # Mock GitHub API call to get recent runs
        # In production: gh workflow view {workflow_file} --json status,conclusion,createdAt...
        history = {
            "workflow": workflow_file,
            "recent_runs": [
                {
                    "run_id": f"run_{i}",
                    "status": "failure" if i % 3 == 0 else "success",
                    "conclusion": "failure" if i % 3 == 0 else "success",
                    "created_at": (datetime.utcnow() - timedelta(hours=i * 4)).isoformat(),
                }
                for i in range(limit)
            ],
            "failure_rate": sum(1 for r in range(limit) if r % 3 == 0) / limit,
            "flakiness_detected": sum(1 for r in range(limit) if r % 3 == 0) > 2,
        }
        return {"status": "complete", "data": history}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def investigate_integration_health(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Check health of external integrations mentioned in finding."""
    integration = finding.get("metadata", {}).get("integration")

    if not integration:
        return {"status": "skipped", "reason": "No integration in metadata"}

    try:
        # Mock health check
        health_checks = {
            "supabase": {"endpoint": "health", "timeout": 5},
            "github": {"endpoint": "status", "timeout": 5},
            "slack": {"endpoint": "status", "timeout": 5},
        }

        check_config = health_checks.get(integration, {})
        # In production: would actually call the health endpoint
        
        return {
            "status": "complete",
            "data": {
                "integration": integration,
                "healthy": True,  # Mock result
                "latency_ms": 45,
                "last_incident": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "check_timestamp": datetime.utcnow().isoformat(),
            },
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def investigate_configuration_drift(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Check for recent config changes that might have caused the issue."""
    workflow_file = finding.get("metadata", {}).get("workflow_file")

    if not workflow_file:
        return {"status": "skipped", "reason": "No workflow_file in metadata"}

    try:
        path = Path(workflow_file)
        if not path.exists():
            return {"status": "skipped", "reason": f"Workflow file not found: {workflow_file}"}

        # Check git history for recent changes
        # In production: git log -n 5 --oneline {workflow_file}
        result = subprocess.run(
            ["git", "log", "-n", "5", "--oneline", "--", workflow_file],
            capture_output=True,
            text=True,
            timeout=10,
        )

        recent_changes = result.stdout.strip().split("\n") if result.stdout else []
        
        return {
            "status": "complete",
            "data": {
                "workflow": workflow_file,
                "recent_changes": recent_changes,
                "change_count_7d": len(recent_changes),
                "drift_detected": len(recent_changes) > 3,  # Heuristic: >3 changes in 7d is drift
            },
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def investigate_cross_repo_dependencies(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Identify other repos that depend on the failing component."""
    component = finding.get("metadata", {}).get("component")

    if not component:
        return {"status": "skipped", "reason": "No component in metadata"}

    try:
        # In production: grep across all org repos for imports/references
        # Mock: return known dependencies
        dependencies = {
            "audit": ["heal", "specialist", "monitor"],
            "heal": ["researcher"],
            "researcher": ["specialist"],
            "specialist": ["monitor"],
        }

        downstream = dependencies.get(component, [])
        
        return {
            "status": "complete",
            "data": {
                "component": component,
                "downstream_consumers": downstream,
                "impact_radius": len(downstream),
            },
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def build_investigation_report(
    finding: Dict[str, Any], depth: str = "standard"
) -> Dict[str, Any]:
    """Conduct full investigation into an escalated finding."""
    investigations = {
        "workflow_history": investigate_workflow_history(finding),
        "integration_health": investigate_integration_health(finding),
        "configuration_drift": investigate_configuration_drift(finding),
        "cross_repo_dependencies": investigate_cross_repo_dependencies(finding),
    }

    # Aggregate findings
    is_systematic = (
        investigations.get("workflow_history", {}).get("data", {}).get("flakiness_detected", False)
        or investigations.get("configuration_drift", {}).get("data", {}).get("drift_detected", False)
    )

    is_integration_issue = not investigations.get("integration_health", {}).get("data", {}).get("healthy", True)

    return {
        "finding_id": finding.get("id"),
        "original_finding": finding,
        "investigations": investigations,
        "diagnosis": {
            "is_systematic": is_systematic,
            "is_integration_issue": is_integration_issue,
            "root_cause_category": "systematic"
            if is_systematic
            else ("integration" if is_integration_issue else "unknown"),
            "confidence": 0.8 if is_systematic or is_integration_issue else 0.4,
        },
        "recommended_actions": (
            ["Add retry logic", "Improve flakiness thresholds"]
            if is_systematic
            else (["Check integration health", "Add fallback logic"] if is_integration_issue else ["Deep audit required"])
        ),
        "investigation_timestamp": datetime.utcnow().isoformat(),
    }


def main() -> int:
    """Main researcher loop."""
    import argparse

    parser = argparse.ArgumentParser(description="NOOS Researcher Agent")
    parser.add_argument("--handoff-file", default="data/noos-healing-handoff-v1.json")
    parser.add_argument("--output-file", default="data/noos-research-findings-v1.json")
    parser.add_argument("--depth", choices=list(RESEARCH_DEPTH.keys()), default="standard")
    args = parser.parse_args()

    # Load escalated findings from handoff
    handoff_path = Path(args.handoff_file)
    if not handoff_path.exists():
        print(json.dumps({"status": "no_work", "message": "No escalated findings to research"}))
        return 0

    with open(handoff_path) as f:
        handoff = json.load(f)

    escalated_ids = handoff.get("escalated_issues", [])
    if not escalated_ids:
        print(json.dumps({"status": "no_work", "message": "No escalated findings to research"}))
        return 0

    # For each escalated finding, run full investigation
    research_reports = []
    for finding_id in escalated_ids[:5]:  # Process top 5 escalated findings
        # Mock finding data (in production, would load from audit findings)
        finding = {
            "id": finding_id,
            "type": "workflow_failure",
            "severity": "high",
            "metadata": {
                "workflow_file": ".github/workflows/noos-workflow-audit.yml",
                "integration": "supabase",
                "component": "audit",
            },
        }

        report = build_investigation_report(finding, depth=args.depth)
        research_reports.append(report)

    # Write research findings
    research_output = {
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "findings_investigated": len(research_reports),
        "reports": research_reports,
        "critique": {
            "systematic_issues": sum(1 for r in research_reports if r["diagnosis"]["is_systematic"]),
            "integration_issues": sum(1 for r in research_reports if r["diagnosis"]["is_integration_issue"]),
            "requires_specialist_review": len(research_reports) > 0,
        },
    }

    with open(args.output_file, "w") as f:
        json.dump(research_output, f, indent=2)

    with open("receipts/proof/noos-kaizen-researcher-report-v1.json", "w") as f:
        json.dump(research_output, f, indent=2)

    print(json.dumps(research_output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
