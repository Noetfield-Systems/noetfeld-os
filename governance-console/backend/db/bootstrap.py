from __future__ import annotations

from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session

from db.models import AuditEvent, AuditLog, Base, EvidenceIndex
from db.session import engine
from services.integrity import audit_integrity_hash
from services.tenant_service import ensure_pilot_tenant


def seed_pilot_evidence(db: Session) -> int:
    tenant = ensure_pilot_tenant(db)
    samples = [
        {
            "evidence_id": "EV-PURVIEW-001",
            "source": "Purview",
            "title": "Copilot sensitivity label coverage report",
            "content_hash": "sha256:abc111",
        },
        {
            "evidence_id": "EV-ENTRA-001",
            "source": "EntraID",
            "title": "Conditional access policy export",
            "content_hash": "sha256:abc222",
        },
        {
            "evidence_id": "EV-AUDIT-001",
            "source": "AuditLog",
            "title": "M365 unified audit log sample (metadata)",
            "content_hash": "sha256:abc333",
        },
    ]
    added = 0
    for s in samples:
        if db.get(EvidenceIndex, s["evidence_id"]):
            continue
        db.add(
            EvidenceIndex(
                evidence_id=s["evidence_id"],
                tenant_id=tenant.tenant_id,
                source=s["source"],
                title=s["title"],
                content_hash=s["content_hash"],
                sensitivity="confidential",
                retention_policy="7y",
                storage_ref="metadata-only/local-dev",
                ingest_mode="metadata_only",
            )
        )
        added += 1
    if added:
        db.commit()
    return added


def init_schema() -> None:
    Base.metadata.create_all(bind=engine)


def migrate_dev_schema_patches() -> None:
    """Lightweight ALTERs for SQLite dev DBs created before model changes."""
    insp = inspect(engine)
    if not insp.has_table("connectors"):
        return
    cols = {c["name"] for c in insp.get_columns("connectors")}
    if "oauth_json" not in cols:
        with engine.begin() as conn:
            conn.execute(
                text("ALTER TABLE connectors ADD COLUMN oauth_json TEXT NOT NULL DEFAULT '{}'")
            )


def migrate_audit_logs_to_events(db: Session) -> int:
    """One-time copy from legacy audit_logs into audit_events."""
    existing = db.scalar(select(func.count()).select_from(AuditEvent)) or 0
    if existing > 0:
        return 0
    tenant = ensure_pilot_tenant(db)
    logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.asc())).all()
    count = 0
    for log in logs:
        if db.scalar(select(AuditEvent).where(AuditEvent.rid == log.rid)):
            continue
        payload = {
            "tenant_id": str(tenant.tenant_id),
            "rid": log.rid,
            "actor": log.actor,
            "action": log.action,
            "decision": log.decision,
            "risk_score": log.risk_score,
            "recorded_at": log.created_at.isoformat(),
        }
        row = AuditEvent(
            tenant_id=tenant.tenant_id,
            rid=log.rid,
            event_type="governance.evaluate",
            actor=log.actor,
            action=log.action,
            context=log.context,
            metadata_json=log.metadata_json or {},
            decision=log.decision,
            risk_score=log.risk_score,
            reason=log.reason or [],
            conditions=log.conditions or [],
            integrity_hash=audit_integrity_hash(payload),
            recorded_at=log.created_at,
        )
        db.add(row)
        count += 1
    if count:
        db.commit()
    return count
