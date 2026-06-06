from __future__ import annotations

from io import BytesIO
from typing import Any

from fpdf import FPDF

from db.models import TleEntry
from services.tle_service import build_signature_block


def _pdf_safe(text: str) -> str:
    """fpdf2 Helvetica is Latin-1 only — normalize common Unicode punctuation."""
    if not text:
        return ""
    return (
        text.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2026", "...")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def _hash_prefix(ev: dict[str, Any]) -> str:
    h = (ev.get("metadata") or {}).get("hash") or ""
    if len(h) > 20:
        return _pdf_safe(h[:20] + "...")
    return _pdf_safe(h) or "-"


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
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(
        0,
        14,
        _pdf_safe(f"Confidence: {row.confidence_score:.0%}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0,
        8,
        _pdf_safe(f"Decision: {doc.get('decision', 'Pending')}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, _pdf_safe(f"TLE ID: {row.tle_id}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(
        0,
        6,
        _pdf_safe(f"Date: {doc.get('date', '')}  |  Status: {row.status}"),
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
        eid = _pdf_safe(str(ev.get("evidence_id", ""))[:18])
        src = _pdf_safe(str(ev.get("source", ""))[:12])
        title = _pdf_safe(str(ev.get("title", ""))[:40])
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
        name = _pdf_safe(str(approver.get("name", ""))[:22])
        role = _pdf_safe(str(approver.get("role", ""))[:12])
        status = _pdf_safe(str(step.get("status", ""))[:12])
        signed = _pdf_safe(str(step.get("signed_at", ""))[:22] or "-")
        pdf.cell(acol[0], 6, name, border=1)
        pdf.cell(acol[1], 6, role, border=1)
        pdf.cell(acol[2], 6, status, border=1)
        pdf.cell(acol[3], 6, signed, border=1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Audit digest", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8)
    digest = _pdf_safe(row.audit_digest or "pending final approval")
    pdf.multi_cell(180, 5, digest)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Signatures (KMS stub)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8)
    pdf.multi_cell(180, 5, _pdf_safe(f"key_id: {sig_block.get('key_id', '')}"))
    for sig in sig_block.get("signatures") or []:
        line = _pdf_safe(f"{sig.get('signer_id')}: {sig.get('signature_hash', '')}")
        pdf.multi_cell(180, 5, line)
    if exported_at:
        pdf.ln(2)
        pdf.cell(0, 5, _pdf_safe(f"Exported: {exported_at}"), new_x="LMARGIN", new_y="NEXT")

    out = pdf.output()
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()
