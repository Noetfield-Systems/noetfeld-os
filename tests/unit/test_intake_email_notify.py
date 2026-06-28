"""Intake inbox email delivery — operations@ + submitter ack."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import patch

from noetfield_governance.intake_notify import (
    intake_email_configured,
    intake_label,
    intake_subject,
    notify_ops_inbox,
    notify_submitter_ack,
)
from noetfield_governance.intake_store import IntakeRecord


@dataclass
class _EmailSettings:
    intake_email_notify_enabled: bool = True
    intake_email_from: str = "Noetfield Intake <notifications@noetfield.com>"
    intake_email_to: str = "operations@noetfield.com"
    intake_auto_ack_enabled: bool = True
    casl_mailing_address: str = "7816 Windsor St\nVancouver, BC, V5X 4A8\nCanada"
    resend_api_key: object | None = "re_test_key"
    intake_smtp_host: str | None = None
    intake_smtp_port: int = 587
    intake_smtp_user: str | None = None
    intake_smtp_password: object | None = None
    intake_smtp_use_tls: bool = True


def _record(**overrides) -> IntakeRecord:
    base = dict(
        intake_id="INT-ABC123",
        created_at="2026-06-13T12:00:00+00:00",
        request_id="RID-2026-0613-TEST",
        organization="Acme Bank",
        contact_name="Alex",
        contact_email="alex@acme.example",
        sku="copilot",
        vector="copilot-governance",
        source="web",
        message="Interested in Governance Pack pilot.",
        metadata={"async": True, "topic": "pilot"},
    )
    base.update(overrides)
    return IntakeRecord(**base)


def test_intake_label_pilot() -> None:
    assert intake_label(_record()) == "Governance Pack apply"


def test_intake_label_investor() -> None:
    rec = _record(vector="work-with-us", sku="general", metadata={"role": "investor"})
    assert intake_label(rec) == "Investor brief"


def test_intake_label_investor_diligence() -> None:
    rec = _record(vector="investor-diligence", sku="general", metadata={"engagement": "shadow-brief"})
    assert intake_label(rec) == "Investor diligence vault"


def test_intake_subject_includes_vector_and_rid() -> None:
    subject = intake_subject(_record())
    assert "Governance Pack apply" in subject
    assert "RID-2026-0613-TEST" in subject
    assert "[vector:copilot-governance]" in subject


def test_intake_email_configured_resend() -> None:
    assert intake_email_configured(_EmailSettings()) is True


def test_intake_email_configured_smtp_only() -> None:
    settings = _EmailSettings(resend_api_key=None, intake_smtp_host="smtp.example.com")
    assert intake_email_configured(settings) is True


def test_intake_email_configured_disabled() -> None:
    settings = _EmailSettings(intake_email_notify_enabled=False)
    assert intake_email_configured(settings) is False


def test_notify_ops_inbox_uses_resend() -> None:
    settings = _EmailSettings()
    record = _record()
    with patch("noetfield_governance.intake_notify._send_via_resend", return_value=True) as send:
        assert notify_ops_inbox(settings, record) is True
    send.assert_called_once()
    kwargs = send.call_args.kwargs
    assert kwargs["to_addrs"] == ["operations@noetfield.com"]
    assert kwargs["reply_to"] == "alex@acme.example"
    assert "Governance Pack apply" in kwargs["subject"]


def test_notify_submitter_ack() -> None:
    settings = _EmailSettings()
    record = _record()
    with patch("noetfield_governance.intake_notify._send_via_resend", return_value=True) as send:
        assert notify_submitter_ack(settings, record) is True
    kwargs = send.call_args.kwargs
    assert kwargs["to_addrs"] == ["alex@acme.example"]
    assert kwargs["reply_to"] == "operations@noetfield.com"
    assert "message received" in kwargs["subject"].lower()
    assert "7816 Windsor St" in kwargs["text"]
    assert "Vancouver, BC, V5X 4A8" in kwargs["text"]
    assert "reply to this message to stop follow-up" in kwargs["text"]


def test_notify_submitter_ack_respects_disable() -> None:
    settings = _EmailSettings(intake_auto_ack_enabled=False)
    with patch("noetfield_governance.intake_notify._send_via_resend") as send:
        assert notify_submitter_ack(settings, _record()) is False
    send.assert_not_called()


def test_notify_ops_inbox_falls_back_to_smtp() -> None:
    settings = _EmailSettings(resend_api_key=None, intake_smtp_host="smtp.example.com")
    with patch("noetfield_governance.intake_notify._send_via_smtp", return_value=True) as send:
        assert notify_ops_inbox(settings, _record()) is True
    send.assert_called_once()
