from __future__ import annotations

from io import BytesIO
from typing import Any

from fpdf import FPDF

from db.models import TleEntry
from services.tle_service import build_signature_block


def _hash_prefix(ev: dict[str, Any]) -> str:
    h = (ev.get("metadata") or {}).get("hash") or ""
    if len(h) > 20:
        return h[:20] + "…"
    return h or "—"


def render_board_pack_pdf(row: TleEntry, pack: dict[str, Any] | None = None) -> bytes:
    doc = row.document_json or {}
    pack = pack or {}
    sig_block = pack.get("signature_block") or build_signature_block(doc)
    exported_at = pack.get("exported_at", "")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Noetfield Trust Ledger", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Board Pack (Procurement Export)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"TLE ID: {row.tle_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Date: {doc.get('date', '')}  |  Status: {row.status}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(
        0,
        6,
        f"Decision: {doc.get('decision', '')}  |  Confidence: {row.confidence_score:.0%}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Evidence index", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 9)
    col_w = [42, 28, 75, 35]
    headers = ["Evidence ID", "Source", "Title", "Hash"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 6, h, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", size=8)
    for ev in doc.get("evidence") or []:
        eid = str(ev.get("evidence_id", ""))[:18]
        src = str(ev.get("source", ""))[:12]
        title = str(ev.get("title", ""))[:40]
        hp = _hash_prefix(ev)
        pdf.cell(col_w[0], 6, eid, border=1)
        pdf.cell(col_w[1], 6, src, border=1)
        pdf.cell(col_w[2], 6, title, border=1)
        pdf.cell(col_w[3], 6, hp, border=1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Approval chain", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 9)
    acol = [45, 25, 25, 45]
    for i, h in enumerate(["Approver", "Role", "Status", "Signed at"]):
        pdf.cell(acol[i], 6, h, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", size=8)
    for step in doc.get("approval_chain") or []:
        approver = step.get("approver") or {}
        name = str(approver.get("name", ""))[:22]
        role = str(approver.get("role", ""))[:12]
        status = str(step.get("status", ""))[:12]
        signed = str(step.get("signed_at", ""))[:22]
        pdf.cell(acol[0], 6, name, border=1)
        pdf.cell(acol[1], 6, role, border=1)
        pdf.cell(acol[2], 6, status, border=1)
        pdf.cell(acol[3], 6, signed or "—", border=1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Audit digest", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8)
    digest = row.audit_digest or "pending final approval"
    pdf.multi_cell(180, 5, digest)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Signatures (KMS stub)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8)
    pdf.multi_cell(180, 5, f"key_id: {sig_block.get('key_id', '')}")
    for sig in sig_block.get("signatures") or []:
        line = f"{sig.get('signer_id')}: {sig.get('signature_hash', '')}"
        pdf.multi_cell(180, 5, line)
    if exported_at:
        pdf.ln(2)
        pdf.cell(0, 5, f"Exported: {exported_at}", new_x="LMARGIN", new_y="NEXT")

    out = pdf.output()
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()
