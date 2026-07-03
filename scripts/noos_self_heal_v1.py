#!/usr/bin/env python3
"""NOOS Self-Heal Engine v1 — Policy-gated with PR-based output."""

import fnmatch
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def read_policy(policy_file: str) -> Dict[str, Any]:
    """Load self-heal policy."""
    path = Path(policy_file)
    if not path.exists():
        return {"policy": {"auto": {}, "proposal": {}, "founder_gated": {}}}
    with open(path) as f:
        return json.load(f)


def classify_path(file_path: str, policy: Dict[str, Any]) -> Tuple[str, str]:
    """Classify file path against policy. Returns: (classification, reason)."""
    patterns_by_class = {
        "founder_gated": policy.get("policy", {}).get("founder_gated", {}).get("paths", []),
        "proposal": policy.get("policy", {}).get("proposal", {}).get("paths", []),
        "auto": policy.get("policy", {}).get("auto", {}).get("paths", []),
    }

    for classification, patterns in patterns_by_class.items():
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return classification, f"Policy: {classification}"

    default = policy.get("defaults", {}).get("unmatched_path", "proposal")
    return default, "Policy: default (unmatched)"


def classify_finding(finding: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    """Classify finding using path + severity."""
    file_path = finding.get("metadata", {}).get("workflow_file", "unknown")
    severity = finding.get("severity", "info")

    if severity in ("critical", "high"):
        return {
            "classification": "founder_gated",
            "reason": f"Severity: {severity}",
        }

    path_class, path_reason = classify_path(file_path, policy)
    return {
        "classification": path_class,
        "reason": path_reason,
    }


def execute_fix(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Generate fix as PR (never direct commit)."""
    classification = finding.get("classification", "proposal")
    finding_id = finding.get("id", "unknown")

    if classification == "founder_gated":
        return {
            "type": "escalation",
            "action": "founder_gated_issue",
            "reason": f"Protected path requires founder approval",
            "timestamp": datetime.utcnow().isoformat(),
        }
    elif classification == "proposal":
        return {
            "type": "proposal_issue",
            "action": "file_github_issue",
            "timestamp": datetime.utcnow().isoformat(),
        }
    else:
        return {
            "type": "auto_pr",
            "action": "create_pr",
            "timestamp": datetime.utcnow().isoformat(),
        }


def main(dry_run: bool = False) -> int:
    """Main healing loop with policy governance."""
    findings_file = "data/noos-audit-findings-v1.json"
    policy_file = "data/self-heal-policy-v1.json"

    policy = read_policy(policy_file)

    findings_path = Path(findings_file)
    if not findings_path.exists():
        print(json.dumps({"status": "no_findings"}))
        return 0

    with open(findings_path) as f:
        audit_data = json.load(f)

    all_findings = audit_data.get("blocking", []) + audit_data.get("dependencies", [])

    executions = []
    for finding in all_findings:
        classification = classify_finding(finding, policy)
        finding.update(classification)
        execution = execute_fix(finding)
        executions.append(execution)

    escalations = [e for e in executions if e.get("type") == "escalation"]
    report = {
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "findings": len(all_findings),
            "auto_pr": sum(1 for e in executions if e.get("type") == "auto_pr"),
            "proposal": sum(1 for e in executions if e.get("type") == "proposal_issue"),
            "escalation": len(escalations),
        },
        "executions": executions,
    }

    if not dry_run:
        Path("receipts/proof/noos-kaizen-self-heal-policy-gated-v1.json").parent.mkdir(parents=True, exist_ok=True)
        with open("receipts/proof/noos-kaizen-self-heal-policy-gated-v1.json", "w") as f:
            json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
