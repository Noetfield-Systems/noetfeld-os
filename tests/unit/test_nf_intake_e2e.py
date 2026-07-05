"""Unit tests for nf_intake_e2e helpers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nf_intake_e2e import (  # noqa: E402
    TERMINAL_STATUSES,
    build_receipt,
    make_request_id,
    platform_status_url,
)


def test_make_request_id_format() -> None:
    rid = make_request_id()
    assert rid.startswith("RID-E2E-")
    assert re.fullmatch(r"RID-E2E-\d+", rid)


def test_platform_status_url() -> None:
    url = platform_status_url("https://platform.noetfield.com", "RID-E2E-123")
    assert "request_id=RID-E2E-123" in url
    assert url.startswith("https://platform.noetfield.com/api/intake/status")


def test_build_receipt_pass() -> None:
    receipt = build_receipt(
        ok=True,
        status="pass",
        request_id="RID-E2E-1",
        intake_url="https://www.noetfield.com/api/intake",
        platform_base="https://platform.noetfield.com",
        reason=None,
        submit={"intake_id": "INT-ABC", "http_status": 200},
        poll={"attempts": 2, "final_status": "delivered", "timed_out": False},
    )
    assert receipt["ok"] is True
    assert receipt["status"] == "pass"
    assert receipt["intake_id"] == "INT-ABC"
    assert "delivered" in TERMINAL_STATUSES
