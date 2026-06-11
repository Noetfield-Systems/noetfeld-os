"""Minimal PDF board-pack stub (no external dependencies)."""

from __future__ import annotations


def minimal_pdf(lines: list[str], title: str = "Noetfield Trust Ledger Entry") -> bytes:
    """Build a valid minimal PDF 1.4 document."""
    text_ops: list[str] = []
    y = 750
    text_ops.append(f"BT /F1 14 Tf 72 {y} Td ({_pdf_escape(title)}) Tj ET")
    y -= 22
    for line in lines:
        text_ops.append(f"BT /F1 10 Tf 72 {y} Td ({_pdf_escape(line)}) Tj ET")
        y -= 14
    stream = "\n".join(text_ops) + "\n"
    stream_bytes = stream.encode("latin-1", errors="replace")

    parts: list[bytes] = [
        b"%PDF-1.4\n",
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n",
        f"4 0 obj<< /Length {len(stream_bytes)} >>stream\n".encode()
        + stream_bytes
        + b"endstream\nendobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]
    header = parts[0]
    body = b"".join(parts[1:])
    offsets: list[int] = []
    pos = 0
    for part in parts:
        offsets.append(pos)
        pos += len(part)
    xref = b"xref\n0 6\n"
    xref += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        xref += f"{off:010d} 00000 n \n".encode()
    trailer = (
        f"trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n{pos}\n%%EOF\n".encode("ascii")
    )
    return header + body + xref + trailer


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
