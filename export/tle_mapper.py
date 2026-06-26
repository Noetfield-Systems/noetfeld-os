"""
Map audit records to TLE v1 and board export bundles (Phase 3).
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from typing import Any


DECISION_TO_TLE_STATUS: dict[str, str] = {
    "APPROVE": "Approved",
    "REVIEW": "Conditional",
    "DECLINE": "Rejected",
}

DECISION_HEADLINE: dict[str, str] = {
    "APPROVE": "Go — policy and risk thresholds satisfied",
    "REVIEW": "Conditional — manual review required before execution",
    "DECLINE": "No-go — policy or corridor threshold not met",
}

APPROVAL_STEP_STATUS: dict[str, str] = {
    "APPROVE": "Approved",
    "REVIEW": "Conditional",
    "DECLINE": "Rejected",
}


def _sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _digest_ref(hex_digest: str) -> str:
    return f"sha256:{hex_digest}"


def _risk_severity(composite_score: float) -> str:
    if composite_score < 45:
        return "High"
    if composite_score < 70:
        return "Medium"
    return "Low"


def _tle_id_for_audit(audit_id: int) -> str:
    return f"TLE-AUD-{audit_id:08d}"


def audit_to_tle_v1(record: dict[str, Any]) -> dict[str, Any]:
    decision = str(record["decision"])
    status = DECISION_TO_TLE_STATUS.get(decision, "Draft")
    composite = float(record["composite_score"])
    confidence = round(min(max(composite / 100.0, 0.0), 1.0), 4)
    created_at = str(record["created_at"])
    if "T" in created_at:
        decision_date = created_at.split("T")[0]
        evidence_ts = created_at
    else:
        decision_date = date.today().isoformat()
        evidence_ts = datetime.now(tz=timezone.utc).isoformat()

    input_payload = record.get("input_payload") or {}
    payload_hash = _sha256_hex(json.dumps(input_payload, sort_keys=True))
    audit_id = int(record["id"])
    request_id = str(record["request_id"])

    breaches = list(record.get("corridor_breaches") or [])
    risk_summary: list[dict[str, str]] = []
    if breaches:
        for idx, name in enumerate(breaches, start=1):
            risk_summary.append(
                {
                    "id": f"RISK-{audit_id:04d}-{idx}",
                    "description": f"Corridor breach: {name}",
                    "severity": _risk_severity(composite),
                }
            )
    else:
        risk_summary.append(
            {
                "id": f"RISK-{audit_id:04d}-0",
                "description": f"Composite governance score {composite:.2f} under rule set "
                f"{record.get('rule_set_version', 'unknown')}",
                "severity": _risk_severity(composite),
            }
        )

    rule_set_id = str(record.get("rule_set_id") or "unknown")
    rule_set_version = str(record.get("rule_set_version") or "0.0.0")
    base_hash = str(record.get("policy_base_hash") or "")
    corridor_hash = str(record.get("policy_corridor_hash") or "")

    tle_core = {
        "tle_id": _tle_id_for_audit(audit_id),
        "source_rid": request_id,
        "decision": DECISION_HEADLINE.get(decision, decision),
        "date": decision_date,
        "owner": {
            "id": f"tenant-{record.get('tenant_id', 'unknown')}",
            "name": "Noetfield GEL",
            "role": "Governance Operator",
        },
        "status": status,
        "confidence_score": confidence,
        "confidence_factors": [
            {
                "factor": "composite_governance_score",
                "weight": 1.0,
                "value": confidence,
            }
        ],
        "evidence": [
            {
                "evidence_id": f"EV-AUDIT-{audit_id}",
                "source": "Manual",
                "title": "GEL pre-execution decision audit record",
                "metadata": {
                    "timestamp": evidence_ts,
                    "hash": _digest_ref(payload_hash),
                },
            }
        ],
        "risk_summary": risk_summary,
        "controls": [
            {
                "control_id": f"{rule_set_id}@{rule_set_version}",
                "description": f"Policy pack active at decision time (base={base_hash[:12]}...)",
            }
        ],
        "approval_chain": [
            {
                "approver": {
                    "id": "gel-runtime-v1",
                    "name": "Noetfield Governance Execution Layer",
                    "role": "Operator",
                },
                "status": APPROVAL_STEP_STATUS.get(decision, "Pending"),
                "signed_at": evidence_ts,
            }
        ],
        "signatures": [
            {
                "signer_id": "gel-runtime-v1",
                "signature_hash": f"sig:{_sha256_hex(request_id + rule_set_version)[:16]}",
                "key_id": f"nf-governance-v1-{rule_set_version}",
            }
        ],
        "metadata": {
            "applicant_id": record.get("applicant_id"),
            "policy_corridor_hash": corridor_hash,
            "policy_base_hash": base_hash,
            "api_key_id": record.get("api_key_id"),
        },
    }

    digest_material = json.dumps(
        {
            "tle_id": tle_core["tle_id"],
            "source_rid": request_id,
            "decision": decision,
            "rule_set_version": rule_set_version,
            "payload_hash": payload_hash,
            "base_hash": base_hash,
            "corridor_hash": corridor_hash,
        },
        sort_keys=True,
    )
    tle_core["audit_digest"] = _digest_ref(_sha256_hex(digest_material))
    return tle_core


def build_export_bundle(record: dict[str, Any]) -> dict[str, Any]:
    tle = audit_to_tle_v1(record)
    return {
        "export_version": "1.0",
        "export_type": "noetfeld-gel-evidence-bundle",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "audit_id": int(record["id"]),
        "request_id": str(record["request_id"]),
        "tenant_id": str(record.get("tenant_id", "unknown")),
        "gel_decision": str(record["decision"]),
        "rule_set_id": str(record.get("rule_set_id") or "unknown"),
        "rule_set_version": str(record.get("rule_set_version") or "0.0.0"),
        "policy_hashes": {
            "base": record.get("policy_base_hash"),
            "corridor": record.get("policy_corridor_hash"),
        },
        "audit": {
            "id": record["id"],
            "created_at": record["created_at"],
            "request_id": record["request_id"],
            "applicant_id": record["applicant_id"],
            "decision": record["decision"],
            "composite_score": record["composite_score"],
            "policy_decision": record.get("policy_decision"),
            "corridor_decision": record.get("corridor_decision"),
            "corridor_breaches": record.get("corridor_breaches") or [],
            "input_payload": record.get("input_payload"),
            "score_breakdown": record.get("score_breakdown"),
        },
        "tle_v1": tle,
    }


__all__ = ["audit_to_tle_v1", "build_export_bundle"]
