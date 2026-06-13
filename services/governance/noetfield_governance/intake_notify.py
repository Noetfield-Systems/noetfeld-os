"""Notify operations when a new intake is recorded (Slack-compatible webhook)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.intake_store import IntakeRecord

logger = logging.getLogger("noetfield.governance.intake.notify")


def notify_ops_webhook(webhook_url: str, record: IntakeRecord) -> bool:
    url = (webhook_url or "").strip()
    if not url:
        return False
    meta = record.metadata if isinstance(record.metadata, dict) else {}
    lane = meta.get("program_lane") or meta.get("buyer_role") or ""
    band = meta.get("pilot_band") or ""
    async_flag = meta.get("async")
    extras = []
    if lane:
        extras.append(f"lane/role: {lane}")
    if band:
        extras.append(f"pilot_band: {band}")
    if async_flag:
        extras.append("async web submit")
    extra_line = f"• {' · '.join(extras)}\n" if extras else ""
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
