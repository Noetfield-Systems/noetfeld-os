"""Board-ready PDF stub from export bundle (Phase 3)."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from fpdf import FPDF


def _ascii_safe(text: str) -> str:
    return text.replace("\u2014", "-").replace("\u2013", "-").encode("ascii", "replace").decode("ascii")


def render_board_pdf(bundle: dict[str, Any]) -> bytes:
    tle = bundle["tle_v1"]
    audit = bundle["audit"]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Noetfield OS - Governance Evidence Summary", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated: {bundle['generated_at']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"TLE ID: {tle['tle_id']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Request ID: {bundle['request_id']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Decision", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, _ascii_safe(tle["decision"]))
    pdf.cell(
        0,
        6,
        f"Status: {tle['status']}  |  GEL outcome: {audit['decision']}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        0,
        6,
        f"Confidence: {tle['confidence_score']:.2f}  |  Composite score: {audit['composite_score']:.2f}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Policy version", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        0,
        6,
        f"Rule set: {bundle['rule_set_id']} @ {bundle['rule_set_version']}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(0, 6, f"Audit digest: {tle['audit_digest']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Risk summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for item in tle.get("risk_summary", []):
        pdf.multi_cell(0, 6, _ascii_safe(f"- [{item['severity']}] {item['description']}"))

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        0,
        5,
        "Non-custodial governance record only. No payment or execution authority. "
        "Prototype export - full cryptographic signing in production Trust Ledger path.",
    )

    out = BytesIO()
    pdf.output(out)
    return out.getvalue()


__all__ = ["render_board_pdf"]
