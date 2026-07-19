#!/usr/bin/env python3
"""
NOOS Specialist Agent v1 — Propose fixes based on researcher findings.

Reviews research reports and proposes high-confidence fixes:
- Systematic flakiness → add retry logic, improve thresholds
- Integration issues → add fallback, increase timeouts
- Config drift → revert risky changes, audit review gates

Proposes fixes for next healing cycle; escalates uncertain cases to human.

Usage:
  python3 scripts/noos_specialist_v1.py \
    --research-file data/noos-research-findings-v1.json \
    --output-file data/noos-specialist-proposals-v1.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def propose_systematic_fix(report: Dict[str, Any]) -> Dict[str, Any]:
    """Propose fix for systematic flakiness issues."""
    finding_id = report.get("finding_id")
    original_finding = report.get("original_finding", {})
    workflow = original_finding.get("metadata", {}).get("workflow_file")

    return {
        "proposal_id": f"prop_{finding_id}_retry",
        "finding_id": finding_id,
        "fix_type": "retry_logic",
        "risk_level": "low",
        "confidence": report.get("diagnosis", {}).get("confidence", 0.5),
        "proposed_changes": {
            "workflow": workflow,
            "changes": [
                {
                    "type": "add_retry",
                    "step": "*",  # All steps
                    "max_attempts": 3,
                    "backoff": "exponential",
                },
                {
                    "type": "adjust_timeout",
                    "adjustment": "+30%",
                },
            ],
        },
        "expected_improvement": "Reduce flakiness from 30% to <5% over next 10 runs",
        "requires_approval": False,  # Low-risk
        "ready_for_automation": True,
    }


def propose_integration_fix(report: Dict[str, Any]) -> Dict[str, Any]:
    """Propose fix for integration health issues."""
    finding_id = report.get("finding_id")
    original_finding = report.get("original_finding", {})
    integration = original_finding.get("metadata", {}).get("integration")

    return {
        "proposal_id": f"prop_{finding_id}_integration",
        "finding_id": finding_id,
        "fix_type": "integration_resilience",
        "risk_level": "low",
        "confidence": report.get("diagnosis", {}).get("confidence", 0.5),
        "proposed_changes": {
            "integration": integration,
            "changes": [
                {
                    "type": "add_fallback",
                    "service": integration,
                    "fallback": "cached_data",
                },
                {
                    "type": "increase_timeout",
                    "from_ms": 5000,
                    "to_ms": 10000,
                },
                {
                    "type": "add_circuit_breaker",
                    "threshold": 5,  # Fail after 5 consecutive failures
                    "reset_after_s": 60,
                },
            ],
        },
        "expected_improvement": f"Reduce {integration} dependency failures by 80%",
        "requires_approval": False,  # Low-risk resilience
        "ready_for_automation": True,
    }


def propose_config_fix(report: Dict[str, Any]) -> Dict[str, Any]:
    """Propose fix for configuration drift issues."""
    finding_id = report.get("finding_id")
    original_finding = report.get("original_finding", {})
    workflow = original_finding.get("metadata", {}).get("workflow_file")

    return {
        "proposal_id": f"prop_{finding_id}_config",
        "finding_id": finding_id,
        "fix_type": "config_stabilization",
        "risk_level": "medium",
        "confidence": report.get("diagnosis", {}).get("confidence", 0.5),
        "proposed_changes": {
            "workflow": workflow,
            "changes": [
                {
                    "type": "audit_gate",
                    "action": "require_approval",
                    "for_changes": ["concurrency", "timeout", "env"],
                },
                {
                    "type": "snapshot_baseline",
                    "create_checkpoint": True,
                },
            ],
        },
        "expected_improvement": "Prevent unintended config drift; enable safe experimentation",
        "requires_approval": True,  # Medium-risk config change
        "ready_for_automation": False,
        "human_review_notes": [
            "Recommend manual review before applying audit gate",
            "This blocks future config changes—ensure team consensus",
        ],
    }


def evaluate_proposal_confidence(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """Score proposal confidence and automation readiness."""
    confidence = proposal.get("confidence", 0.5)
    risk = proposal.get("risk_level")
    fix_type = proposal.get("fix_type")

    # Automation readiness heuristic
    can_automate = (
        confidence > 0.75
        and risk in ("low", "medium")
        and not proposal.get("requires_approval", False)
    )

    action = "auto_propose" if can_automate else "manual_review"

    return {
        "proposal_id": proposal.get("proposal_id"),
        "confidence_score": confidence,
        "risk_level": risk,
        "automation_ready": can_automate,
        "recommended_action": action,
        "review_priority": "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low",
    }


def build_specialist_report(research_output: Dict[str, Any]) -> Dict[str, Any]:
    """Build specialist's proposal report from researcher findings."""
    reports = research_output.get("reports", [])
    proposals = []

    for report in reports:
        diagnosis = report.get("diagnosis", {})
        root_cause = diagnosis.get("root_cause_category")

        if root_cause == "systematic":
            proposal = propose_systematic_fix(report)
        elif root_cause == "integration":
            proposal = propose_integration_fix(report)
        else:
            # Config drift or unknown
            proposal = propose_config_fix(report)

        # Evaluate each proposal
        evaluation = evaluate_proposal_confidence(proposal)
        proposal.update(evaluation)
        try:
            from noos_plan_motor_kernel_bridge_v1 import kernel_proposal_review

            proposal["kernel_review"] = kernel_proposal_review(proposal)
        except Exception as exc:
            proposal["kernel_review"] = {"ok": False, "error": str(exc)[:200]}
        proposals.append(proposal)

    # Aggregate critique
    auto_proposals = [p for p in proposals if p.get("automation_ready")]
    manual_proposals = [p for p in proposals if not p.get("automation_ready")]
    high_confidence = [p for p in proposals if p.get("confidence_score", 0) > 0.8]

    return {
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "source_research": research_output.get("timestamp"),
        "proposals_generated": len(proposals),
        "proposals": proposals,
        "summary": {
            "total_proposals": len(proposals),
            "ready_for_automation": len(auto_proposals),
            "require_manual_review": len(manual_proposals),
            "high_confidence_proposals": len(high_confidence),
        },
        "critique": {
            "overall_ok": len(high_confidence) > 0,
            "findings": [
                f"Generated {len(proposals)} fix proposals from research",
                f"{len(auto_proposals)} ready for automation",
                f"{len(manual_proposals)} require manual review",
            ],
            "next_steps": [
                "Review high-confidence proposals",
                "Schedule manual review for medium-confidence proposals",
                "Escalate uncertain proposals for specialist discussion",
            ],
        },
    }


def main() -> int:
    """Main specialist loop."""
    import argparse

    parser = argparse.ArgumentParser(description="NOOS Specialist Agent")
    parser.add_argument("--research-file", default="data/noos-research-findings-v1.json")
    parser.add_argument("--output-file", default="data/noos-specialist-proposals-v1.json")
    args = parser.parse_args()

    # Load research findings
    research_path = Path(args.research_file)
    if not research_path.exists():
        print(json.dumps({"status": "no_work", "message": "No research findings to review"}))
        return 0

    with open(research_path) as f:
        research_output = json.load(f)

    # Generate proposals
    specialist_report = build_specialist_report(research_output)

    # Write proposals
    with open(args.output_file, "w") as f:
        json.dump(specialist_report, f, indent=2)

    with open("receipts/proof/noos-kaizen-specialist-proposals-v1.json", "w") as f:
        json.dump(specialist_report, f, indent=2)

    print(json.dumps(specialist_report, indent=2))

    # Return 0 if proposals were generated, 1 if no actionable proposals
    return 0 if specialist_report["summary"]["total_proposals"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
