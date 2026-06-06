from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import AuditEvent, TleEntry
from services.board_pack_pdf import render_board_pack_pdf
from services.tle_service import board_pack_export

README_PROCUREMENT = """Noetfield Trust Ledger — Procurement Pack
================================================

This archive contains a Trust Ledger Entry (TLE v1) board pack for diligence review.

Contents:
- board_pack.json — structured export (signatures, evidence, approval chain)
- board_pack.pdf — print-ready board pack for governance meetings
- audit_export_slice.json — governance evaluation event(s) linked to this TLE (if source RID present)

Framework alignment (orientation only — not legal advice):
- NIST AI RMF Govern/Manage — decision documentation
- ISO/IEC 42001-style evidence and approval records
- Microsoft Purview / M365 evidence metadata (when connector ingested)

References: docs/reference/GOVERNANCE_SOURCES_BOOK_v1.md (Noetfield implementation repo)

Noetfield does not initiate payments, custody, or external execution.
"""


def _audit_slice_for_rid(db: Session, tenant_id, source_rid: str | None) -> dict[str, Any] | None:
    if not source_rid or not str(source_rid).strip():
        return None
    rid = str(source_rid).strip().upper()
    row = db.scalar(
        select(AuditEvent).where(
            AuditEvent.tenant_id == tenant_id,
            AuditEvent.rid == rid,
        )
    )
    if row is None:
        return None
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source_rid": rid,
        "event": {
            "rid": row.rid,
            "actor": row.actor,
            "action": row.action,
            "decision": row.decision,
            "risk_score": row.risk_score,
            "integrity_hash": row.integrity_hash,
            "recorded_at": row.recorded_at.isoformat() if row.recorded_at else None,
        },
    }


def build_procurement_pack_zip(
    db: Session,
    row: TleEntry,
    *,
    pack: dict[str, Any] | None = None,
) -> bytes:
    pack = pack or board_pack_export(row)
    pdf_bytes = render_board_pack_pdf(row, pack)
    audit_slice = _audit_slice_for_rid(db, row.tenant_id, row.source_rid)

    buf = BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "board_pack.json",
            json.dumps(pack, indent=2, default=str).encode("utf-8"),
        )
        zf.writestr("board_pack.pdf", pdf_bytes)
        zf.writestr("README-procurement.txt", README_PROCUREMENT.encode("utf-8"))
        if audit_slice is not None:
            zf.writestr(
                "audit_export_slice.json",
                json.dumps(audit_slice, indent=2).encode("utf-8"),
            )
    return buf.getvalue()
