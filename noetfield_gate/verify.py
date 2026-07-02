"""Chain verify — gate report + optional decision receipt (UPG-0158)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from noetfield_gate.boot import DEFAULT_RECEIPT, run_gate_checks, write_gate_report


def verify_chain(
    *,
    root: Path | None = None,
    gate_report: Path | None = None,
    receipt_path: Path | None = None,
    api_url: str | None = None,
) -> dict[str, Any]:
    report = run_gate_checks(root=root, api_url=api_url, strict=False)
    gate_path = gate_report or DEFAULT_RECEIPT
    if not gate_report:
        write_gate_report(report, gate_path)

    checks: list[dict[str, Any]] = []
    gate_ok = report.get("outcome") == "PASS"
    checks.append(
        {
            "id": "V1",
            "name": "gate_report",
            "ok": gate_ok,
            "reason": "PASS" if gate_ok else "; ".join(report.get("block_reasons") or []),
            "path": str(gate_path),
        }
    )

    receipt_ok = True
    receipt_reason = "no receipt path supplied"
    if receipt_path:
        receipt_ok = receipt_path.is_file()
        receipt_reason = "receipt found" if receipt_ok else f"missing {receipt_path}"
        if receipt_ok:
            try:
                doc = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt_ok = doc.get("schema") in ("noetfield-decision-receipt-v1", "noetfield-gate-report-v1")
                receipt_reason = f"schema={doc.get('schema')}"
            except (OSError, json.JSONDecodeError) as exc:
                receipt_ok = False
                receipt_reason = str(exc)
    checks.append({"id": "V2", "name": "decision_receipt", "ok": receipt_ok, "reason": receipt_reason})

    failed = [c for c in checks if not c.get("ok")]
    return {
        "schema": "noetfield-verify-report-v1",
        "outcome": "PASS" if not failed else "BLOCK",
        "checks": checks,
        "gate_report": report,
        "block_reasons": [c["reason"] for c in failed],
    }


__all__ = ["verify_chain"]
