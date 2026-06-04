from __future__ import annotations

from io import BytesIO

from fpdf import FPDF

from db.models import TleEntry


def render_board_pack_pdf(row: TleEntry) -> bytes:
    doc = row.document_json or {}
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Trust Ledger Board Pack", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, f"TLE: {row.tle_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Status: {row.status}  |  Confidence: {row.confidence_score:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Decision: {doc.get('decision', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Digest: {row.audit_digest or 'pending'}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Evidence", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    col_w = 180
    for ev in doc.get("evidence") or []:
        line = f"- {ev.get('source', '')}: {ev.get('title', '')}"
        pdf.multi_cell(col_w, 6, line)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Approval chain", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    for step in doc.get("approval_chain") or []:
        approver = (step.get("approver") or {}).get("name", "")
        pdf.cell(0, 6, f"- {approver}: {step.get('status', '')}", new_x="LMARGIN", new_y="NEXT")
    buf = BytesIO()
    out = pdf.output()
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    pdf.output(buf)
    return buf.getvalue()
