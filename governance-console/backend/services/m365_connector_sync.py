from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import EvidenceIndex

M365_STUB_EVIDENCE: list[dict[str, Any]] = [
    {
        "evidence_id": "EV-PURVIEW-COPILOT-LABELS",
        "source": "Purview",
        "title": "Copilot sensitivity label coverage (M365 stub)",
        "content_hash": "sha256:m365-purview-stub-001",
        "sensitivity": "confidential",
        "storage_ref": "m365-stub/purview/metadata",
        "ingest_mode": "metadata_only",
    },
    {
        "evidence_id": "EV-ENTRA-CA-COPILOT",
        "source": "EntraID",
        "title": "Conditional Access — Copilot licensed users (M365 stub)",
        "content_hash": "sha256:m365-entra-stub-002",
        "sensitivity": "internal",
        "storage_ref": "m365-stub/entra/metadata",
        "ingest_mode": "metadata_only",
    },
    {
        "evidence_id": "EV-SPO-SITE-POLICY",
        "source": "SharePoint",
        "title": "SharePoint site policy export — Copilot-eligible sites (M365 stub)",
        "content_hash": "sha256:m365-spo-stub-003",
        "sensitivity": "internal",
        "storage_ref": "m365-stub/sharepoint/metadata",
        "ingest_mode": "metadata_only",
    },
]


def ingest_m365_stub_evidence(
    db: Session,
    *,
    tenant_id: UUID,
    connector_id: str,
) -> list[str]:
    """Upsert M365-shaped evidence after connector OAuth (idempotent)."""
    ingested_at = datetime.now(timezone.utc)
    ids: list[str] = []
    for item in M365_STUB_EVIDENCE:
        eid = item["evidence_id"]
        ids.append(eid)
        row = db.get(EvidenceIndex, eid)
        meta = {"connector_id": connector_id, "synced_at": ingested_at.isoformat()}
        if row is None:
            db.add(
                EvidenceIndex(
                    evidence_id=eid,
                    tenant_id=tenant_id,
                    source=item["source"],
                    title=item["title"],
                    content_hash=item["content_hash"],
                    sensitivity=item.get("sensitivity", "internal"),
                    retention_policy="standard",
                    storage_ref=item.get("storage_ref", ""),
                    ingest_mode=item.get("ingest_mode", "metadata_only"),
                    ingested_at=ingested_at,
                    metadata_json=meta,
                )
            )
        else:
            row.tenant_id = tenant_id
            row.source = item["source"]
            row.title = item["title"]
            row.content_hash = item["content_hash"]
            row.storage_ref = item.get("storage_ref", row.storage_ref)
            existing_meta = dict(row.metadata_json or {})
            existing_meta.update(meta)
            row.metadata_json = existing_meta
    db.commit()
    return ids
