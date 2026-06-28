"""Notify operations when a new intake is recorded (Slack webhook + email inbox)."""

from __future__ import annotations

import json
import logging
import smtplib
import ssl
import urllib.error
import urllib.request
from email.message import EmailMessage
from typing import Protocol

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.intake_store import IntakeRecord

logger = logging.getLogger("noetfield.governance.intake.notify")


class IntakeEmailSettings(Protocol):
    intake_email_notify_enabled: bool
    intake_email_from: str
    intake_email_to: str
    intake_auto_ack_enabled: bool
    casl_mailing_address: str
    resend_api_key: object | None
    intake_smtp_host: str | None
    intake_smtp_port: int
    intake_smtp_user: str | None
    intake_smtp_password: object | None
    intake_smtp_use_tls: bool


def _secret(value: object | None) -> str:
    if value is None:
        return ""
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        return str(getter() or "").strip()
    return str(value).strip()


def _meta(record: IntakeRecord) -> dict:
    return record.metadata if isinstance(record.metadata, dict) else {}


def _meta_line(record: IntakeRecord) -> str:
    meta = _meta(record)
    lane = meta.get("program_lane") or meta.get("buyer_role") or meta.get("role") or ""
    topic = meta.get("topic") or ""
    band = meta.get("pilot_band") or ""
    engagement = meta.get("engagement") or ""
    page = meta.get("page") or ""
    form_id = meta.get("form_id") or ""
    parts = []
    if lane:
        parts.append(f"lane/role: {lane}")
    if topic and topic != lane:
        parts.append(f"topic: {topic}")
    if band:
        parts.append(f"pilot_band: {band}")
    if engagement:
        parts.append(f"engagement: {engagement}")
    if page:
        parts.append(f"page: {page}")
    if form_id:
        parts.append(f"form: {form_id}")
    if meta.get("async"):
        parts.append("async web submit")
    return " · ".join(parts)


def intake_label(record: IntakeRecord) -> str:
    meta = _meta(record)
    vector = (record.vector or "").lower()
    topic = (meta.get("topic") or meta.get("role") or meta.get("program_lane") or "").lower()
    sku = (record.sku or "").lower()
    form_id = (meta.get("form_id") or "").lower()

    if "sandbox" in vector or form_id in {"nfsandboxform", "nftrialaccountform"}:
        return "Sandbox signup"
    if vector == "investor-diligence" or topic == "investor-diligence":
        return "Investor diligence vault"
    if topic == "investor" or (vector == "work-with-us" and topic == "investor"):
        return "Investor brief"
    if vector == "work-with-us" or topic in {"connector", "facilitator", "co-partner", "partner"}:
        return "Work with Noetfield application"
    if "copilot" in vector or sku == "copilot" or topic == "pilot":
        return "Governance Pack apply"
    if "trust" in vector or sku == "trust_brief" or topic == "trust-brief":
        return "Trust Brief Intake"
    if "bank" in vector or sku == "bank_pilot" or topic == "bank-pilot":
        return "Bank Pilot inquiry"
    if topic == "federal":
        return "Federal Brief"
    if topic == "feedback":
        return "Site feedback"
    if topic == "partner":
        return "Partner program"
    if vector == "contact" and topic:
        return f"Contact — {topic}"
    if vector == "contact":
        return "Contact"
    return "Intake"


def intake_subject(record: IntakeRecord) -> str:
    rid = record.request_id or record.intake_id
    label = intake_label(record)
    vector = (record.vector or "").strip()
    if vector and f"[vector:{vector}]" not in label:
        return f"[vector:{vector}] Noetfield — {label} ({rid})"
    return f"Noetfield — {label} ({rid})"


def intake_body_text(record: IntakeRecord) -> str:
    meta = _meta(record)
    meta_line = _meta_line(record)
    lines = [
        "New Noetfield intake — reply to this thread to reach the submitter.",
        "",
        f"Intake ID: {record.intake_id}",
        f"RID: {record.request_id or '—'}",
        f"Organization: {record.organization}",
        f"Contact: {record.contact_name or '—'} <{record.contact_email}>",
        f"SKU: {record.sku}",
        f"Vector: {record.vector}",
        f"Source: {record.source}",
    ]
    if meta_line:
        lines.append(f"Context: {meta_line}")
    lines.extend(["", "Message:", record.message.strip(), ""])
    return "\n".join(lines)


def submitter_ack_subject(record: IntakeRecord) -> str:
    rid = record.request_id or record.intake_id
    return f"Noetfield — message received ({rid})"


def submitter_ack_body(record: IntakeRecord) -> str:
    rid = record.request_id or record.intake_id
    return (
        f"Hi{(' ' + record.contact_name) if record.contact_name else ''},\n\n"
        "Your message was saved instantly. Operations at Noetfield will follow up "
        "within one business day.\n\n"
        f"Reference: {rid}\n"
        f"Intake ID: {record.intake_id}\n\n"
        "Non-confidential only · include your Request ID in any follow-up.\n\n"
        "— Noetfield Operations\n"
        f"{CANONICAL_INTAKE_EMAIL}\n"
    )


def append_casl_footer(text: str, settings: IntakeEmailSettings) -> str:
    address = (settings.casl_mailing_address or "").strip()
    if not address:
        return text
    return (
        text.rstrip()
        + "\n\n"
        + "Commercial email compliance:\n"
        + "You can reply to this message to stop follow-up.\n"
        + address
        + "\n"
    )


def _send_via_resend(
    *,
    api_key: str,
    from_addr: str,
    to_addrs: list[str],
    subject: str,
    text: str,
    reply_to: str | None = None,
) -> bool:
    payload: dict[str, object] = {
        "from": from_addr,
        "to": to_addrs,
        "subject": subject,
        "text": text,
    }
    if reply_to:
        payload["reply_to"] = reply_to
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15.0) as response:
            return 200 <= response.status < 300
    except urllib.error.URLError as exc:
        logger.warning("intake_resend_failed subject=%s %s", subject[:80], exc)
        return False


def _send_via_smtp(
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    use_tls: bool,
    from_addr: str,
    to_addrs: list[str],
    subject: str,
    text: str,
    reply_to: str | None = None,
) -> bool:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(text)
    try:
        if use_tls:
            with smtplib.SMTP(host, port, timeout=15) as smtp:
                smtp.ehlo()
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP_SSL(host, port, timeout=15) as smtp:
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
        return True
    except (OSError, smtplib.SMTPException) as exc:
        logger.warning("intake_smtp_failed subject=%s %s", subject[:80], exc)
        return False


def send_intake_email(
    settings: IntakeEmailSettings,
    *,
    to_addrs: list[str],
    subject: str,
    text: str,
    reply_to: str | None = None,
) -> bool:
    if not settings.intake_email_notify_enabled:
        return False
    recipients = [addr.strip() for addr in to_addrs if addr and addr.strip()]
    if not recipients:
        return False
    from_addr = (settings.intake_email_from or "").strip()
    if not from_addr:
        logger.warning("intake_email_skipped missing from address subject=%s", subject[:80])
        return False

    resend_key = _secret(settings.resend_api_key)
    if resend_key:
        return _send_via_resend(
            api_key=resend_key,
            from_addr=from_addr,
            to_addrs=recipients,
            subject=subject,
            text=text,
            reply_to=reply_to,
        )

    smtp_host = (settings.intake_smtp_host or "").strip()
    if smtp_host:
        return _send_via_smtp(
            host=smtp_host,
            port=int(settings.intake_smtp_port or 587),
            user=(settings.intake_smtp_user or "").strip(),
            password=_secret(settings.intake_smtp_password),
            use_tls=bool(settings.intake_smtp_use_tls),
            from_addr=from_addr,
            to_addrs=recipients,
            subject=subject,
            text=text,
            reply_to=reply_to,
        )

    logger.info("intake_email_skipped no provider configured subject=%s", subject[:80])
    return False


def notify_ops_inbox(settings: IntakeEmailSettings, record: IntakeRecord) -> bool:
    inbox = (settings.intake_email_to or CANONICAL_INTAKE_EMAIL).strip()
    return send_intake_email(
        settings,
        to_addrs=[inbox],
        subject=intake_subject(record),
        text=intake_body_text(record),
        reply_to=record.contact_email,
    )


def notify_submitter_ack(settings: IntakeEmailSettings, record: IntakeRecord) -> bool:
    if not settings.intake_auto_ack_enabled:
        return False
    return send_intake_email(
        settings,
        to_addrs=[record.contact_email],
        subject=submitter_ack_subject(record),
        text=append_casl_footer(submitter_ack_body(record), settings),
        reply_to=CANONICAL_INTAKE_EMAIL,
    )


def intake_email_configured(settings: IntakeEmailSettings) -> bool:
    if not settings.intake_email_notify_enabled:
        return False
    if _secret(settings.resend_api_key):
        return True
    return bool((settings.intake_smtp_host or "").strip())


def notify_ops_webhook(webhook_url: str, record: IntakeRecord) -> bool:
    url = (webhook_url or "").strip()
    if not url:
        return False
    meta_line = _meta_line(record)
    extra_line = f"• {meta_line}\n" if meta_line else ""
    text = (
        f"*New Noetfield intake* `{record.intake_id}`\n"
        f"• Org: {record.organization}\n"
        f"• Email: {record.contact_email}\n"
        f"• SKU: {record.sku} · vector: {record.vector}\n"
        f"• RID: {record.request_id or '—'}\n"
        f"{extra_line}"
        f"• Inbox: {CANONICAL_INTAKE_EMAIL}\n"
        f"```{record.message[:1500]}```"
    )
    body = json.dumps({"text": text}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10.0) as response:
            return 200 <= response.status < 300
    except urllib.error.URLError as exc:
        logger.warning("intake_webhook_failed intake_id=%s %s", record.intake_id, exc)
        return False
