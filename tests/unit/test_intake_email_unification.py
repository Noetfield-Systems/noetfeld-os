"""Canonical intake email lock: operations@noetfield.com only on public surfaces."""

from pathlib import Path

import asyncio

ROOT = Path(__file__).resolve().parents[2]

PUBLIC_HTML = (
    ROOT / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "trust-brief" / "index.html",
    ROOT / "trust-brief" / "intake" / "index.html",
    ROOT / "copilot" / "index.html",
    ROOT / "console" / "index.html",
    ROOT / "gate" / "intake" / "index.html",
)

FORBIDDEN = (
    "mailto:contact@noetfield.com",
    "mailto:procurement@noetfield.com",
    "mailto:sales@noetfield.com",
    "contact@noetfield.com •",
    "procurement@noetfield.com",
    "sales@noetfield.com",
)


def test_canonical_constant_in_config() -> None:
    from noetfield_config import CANONICAL_INTAKE_EMAIL, LEGACY_INTAKE_ALIASES

    assert CANONICAL_INTAKE_EMAIL == "operations@noetfield.com"
    assert "procurement@noetfield.com" in LEGACY_INTAKE_ALIASES


def test_public_html_no_legacy_intake_mailtos() -> None:
    for path in PUBLIC_HTML:
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN:
            assert phrase not in text, f"{path.name}: {phrase}"


def test_trust_brief_intake_uses_operations() -> None:
    text = (ROOT / "trust-brief" / "intake" / "index.html").read_text(encoding="utf-8")
    assert "operations@noetfield.com" in text
    assert "intake_vector" in text
    assert "alert_destination" in text


def test_gate_intake_gateway_vectors() -> None:
    text = (ROOT / "gate" / "intake" / "index.html").read_text(encoding="utf-8")
    assert "operations@noetfield.com" in text
    assert "vector=bank-pilot" in text
    assert "vector=partner-gateway" in text


def test_offerings_locked_documents_canonical_inbox() -> None:
    text = (ROOT / "OFFERINGS_LOCKED.md").read_text(encoding="utf-8")
    assert "operations@noetfield.com" in text


def test_strategic_lock_documents_canonical_inbox() -> None:
    text = (ROOT / "STRATEGIC_LOCK.md").read_text(encoding="utf-8")
    assert "operations@noetfield.com" in text


def test_intake_email_audit_script() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_intake_email.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_evaluate_reject_logs_remediation_tip(caplog) -> None:
    from uuid import uuid4

    from httpx import ASGITransport, AsyncClient

    from noetfield_config import CANONICAL_INTAKE_EMAIL
    from noetfield_governance.api import app
    from tests.unit.test_governance_console_v3 import governance_test_client

    caplog.set_level("WARNING", logger="noetfield.governance.api")

    async def run() -> None:
        async with governance_test_client() as client:
            response = await client.post(
                "/v3/evaluate",
                json={
                    "tenant_id": str(uuid4()),
                    "organization_id": str(uuid4()),
                    "action": "initiate_payment",
                    "resource_type": "payment_intent",
                    "resource_id": "pi_test",
                },
            )
        assert response.status_code == 200
        assert response.json()["decision"] == "REJECT"

    asyncio.run(run())
    assert any(CANONICAL_INTAKE_EMAIL in r.message for r in caplog.records)
