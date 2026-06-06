from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import AuditEvent, EvidenceIndex, TleEntry
from services.integrity import audit_integrity_hash

KMS_STUB_KEY_ID = "local-dev-kms-stub-v1"


def _tle_id() -> str:
    return f"TLE-{uuid.uuid4().hex[:12].upper()}"


def compute_confidence_score(evidence: list[dict[str, Any]]) -> tuple[float, list[dict[str, Any]]]:
    """Deterministic confidence from evidence coverage (0.00–1.00)."""
    base = 0.35
    factors: list[dict[str, Any]] = [
        {"factor": "baseline_governance", "weight": 0.35, "value": base},
    ]
    per_item = min(len(evidence) * 0.12, 0.48)
    if per_item:
        factors.append({"factor": "evidence_count", "weight": 0.48, "value": per_item})
    sources = {e.get("source") for e in evidence}
    purview_bonus = 0.07 if "Purview" in sources else 0.0
    if purview_bonus:
        factors.append({"factor": "purview_coverage", "weight": 0.07, "value": purview_bonus})
    entra_bonus = 0.05 if "EntraID" in sources else 0.0
    if entra_bonus:
        factors.append({"factor": "identity_coverage", "weight": 0.05, "value": entra_bonus})
    score = min(1.0, base + per_item + purview_bonus + entra_bonus)
    return round(score, 2), factors


def evidence_to_ref(row: EvidenceIndex) -> dict[str, Any]:
    ref: dict[str, Any] = {
        "evidence_id": row.evidence_id,
        "source": row.source,
        "title": row.title,
        "metadata": {
            "timestamp": row.ingested_at.isoformat(),
            "hash": row.content_hash,
        },
    }
    if row.sensitivity:
        ref["metadata"]["sensitivity_label"] = row.sensitivity
    if row.link:
        ref["link"] = row.link
    return ref


def default_approval_chain() -> list[dict[str, Any]]:
    return [
        {
            "approver": {"id": "cio-001", "name": "Chief Information Officer", "role": "CIO"},
            "status": "Pending",
        },
        {
            "approver": {"id": "legal-001", "name": "General Counsel", "role": "Legal"},
            "status": "Pending",
        },
        {
            "approver": {"id": "sec-001", "name": "CISO", "role": "Security"},
            "status": "Pending",
        },
    ]


def draft_from_evaluate(
    db: Session,
    *,
    tenant_id: uuid.UUID,
    source_rid: str | None,
    evidence_ids: list[str],
    owner: dict[str, str] | None = None,
) -> TleEntry:
    rows = list(
        db.scalars(
            select(EvidenceIndex).where(
                EvidenceIndex.tenant_id == tenant_id,
                EvidenceIndex.evidence_id.in_(evidence_ids),
            )
        ).all()
    )
    if len(rows) != len(evidence_ids):
        found = {r.evidence_id for r in rows}
        missing = [eid for eid in evidence_ids if eid not in found]
        raise ValueError(f"Evidence not found: {', '.join(missing)}")

    evidence_refs = [evidence_to_ref(r) for r in rows]
    score, factors = compute_confidence_score(evidence_refs)

    audit_event: AuditEvent | None = None
    if source_rid:
        audit_event = db.scalar(
            select(AuditEvent).where(
                AuditEvent.tenant_id == tenant_id,
                AuditEvent.rid == source_rid,
            )
        )

    decision = "Conditional Copilot rollout pending control completion"
    status = "Conditional"
    risk_summary = [
        {"id": "RISK-001", "description": "Data residency exposure in shared channels", "severity": "Medium"},
    ]
    controls = [
        {"control_id": "CTRL-DLP-01", "description": "Enforce DLP on Copilot-eligible sites"},
    ]
    if audit_event:
        if audit_event.decision == "deny":
            decision = "Copilot rollout not authorized"
            status = "Rejected"
        elif audit_event.decision == "allow":
            decision = "Copilot rollout authorized with standard controls"
            status = "Conditional"
        risk_summary = [
            {
                "id": f"RISK-{audit_event.risk_score:03d}",
                "description": audit_event.action[:120] or "Governance evaluation risk",
                "severity": "High" if audit_event.risk_score >= 70 else "Medium" if audit_event.risk_score >= 40 else "Low",
            }
        ]
        if audit_event.conditions:
            controls = [
                {"control_id": f"CTRL-{i+1:02d}", "description": c[:200]}
                for i, c in enumerate(audit_event.conditions[:5])
            ]

    owner_obj = owner or {"id": "owner-pilot", "name": "Governance Owner", "role": "Operator"}
    tle_id = _tle_id()
    today = date.today().isoformat()
    doc: dict[str, Any] = {
        "tle_id": tle_id,
        "source_rid": source_rid,
        "decision": decision,
        "date": today,
        "owner": owner_obj,
        "status": "Draft",
        "confidence_score": score,
        "confidence_factors": factors,
        "evidence": evidence_refs,
        "risk_summary": risk_summary,
        "controls": controls,
        "approval_chain": default_approval_chain(),
        "signatures": [],
        "audit_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
        "tenant_id": str(tenant_id),
        "metadata": {"generator": "tle_service_v1", "target_status": status},
    }

    row = TleEntry(
        tle_id=tle_id,
        tenant_id=tenant_id,
        status="Draft",
        source_rid=source_rid,
        confidence_score=score,
        document_json=doc,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def approve_step(
    db: Session,
    *,
    tle_id: str,
    tenant_id: uuid.UUID,
    approver_id: str,
    decision: str,
    conditions: str | None = None,
) -> TleEntry:
    row = db.scalar(
        select(TleEntry).where(TleEntry.tle_id == tle_id, TleEntry.tenant_id == tenant_id)
    )
    if row is None:
        raise LookupError("TLE not found")
    if row.status not in ("Draft", "Conditional"):
        raise ValueError("TLE is already finalized")

    doc = dict(row.document_json)
    chain = list(doc.get("approval_chain") or [])
    next_pending = next((s for s in chain if s.get("status") == "Pending"), None)
    if next_pending is None:
        raise ValueError("No pending approval step")
    expected_id = (next_pending.get("approver") or {}).get("id")
    if approver_id != expected_id:
        raise ValueError("Out-of-order approval")

    matched = False
    for step in chain:
        approver = step.get("approver") or {}
        if approver.get("id") == approver_id:
            step["status"] = decision
            step["signed_at"] = datetime.now(timezone.utc).isoformat()
            if conditions:
                step["conditions"] = conditions
            matched = True
            break
    if not matched:
        raise ValueError(f"Approver not in chain: {approver_id}")

    sig_payload = json.dumps(
        {"tle_id": tle_id, "approver_id": approver_id, "decision": decision},
        sort_keys=True,
    )
    sig_hash = hashlib.sha256(sig_payload.encode()).hexdigest()
    signatures = list(doc.get("signatures") or [])
    signatures.append(
        {
            "signer_id": approver_id,
            "signature_hash": f"sha256:{sig_hash}",
            "key_id": KMS_STUB_KEY_ID,
        }
    )
    doc["approval_chain"] = chain
    doc["signatures"] = signatures

    pending = [s for s in chain if s.get("status") == "Pending"]
    rejected = [s for s in chain if s.get("status") == "Rejected"]
    if rejected:
        doc["status"] = "Rejected"
        row.status = "Rejected"
    elif not pending:
        target = (doc.get("metadata") or {}).get("target_status", "Approved")
        doc["status"] = target if target != "Draft" else "Approved"
        row.status = doc["status"]
        digest_src = {k: v for k, v in doc.items() if k != "audit_digest"}
        doc["audit_digest"] = audit_integrity_hash(digest_src)
        row.audit_digest = doc["audit_digest"]
        row.finalized_at = datetime.now(timezone.utc)
    else:
        doc["status"] = "Draft"

    row.document_json = doc
    db.commit()
    db.refresh(row)
    return row


def board_pack_export(row: TleEntry) -> dict[str, Any]:
    doc = row.document_json
    return {
        "export_type": "board_pack_v1",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "tle_id": row.tle_id,
        "status": row.status,
        "confidence_score": row.confidence_score,
        "audit_digest": row.audit_digest,
        "decision": doc.get("decision"),
        "evidence_count": len(doc.get("evidence") or []),
        "approval_chain": doc.get("approval_chain"),
        "risk_summary": doc.get("risk_summary"),
        "controls": doc.get("controls"),
        "signature_block": build_signature_block(doc),
        "document": doc,
    }


def build_signature_block(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "key_id": KMS_STUB_KEY_ID,
        "digest_algorithm": "sha256",
        "signatures": list(doc.get("signatures") or []),
        "verify_hint": (
            "Recompute sha256 over sorted JSON of {tle_id, approver_id, decision} per signature entry; "
            "final audit_digest uses canonical document JSON excluding audit_digest field."
        ),
    }
