"""Governance decision webhooks for pilot SIEM / GRC integrations."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
from dataclasses import dataclass, field
from typing import Any
from urllib import error, request

from pydantic import SecretStr

logger = logging.getLogger("noetfield.governance.webhooks")

EVENT_GOVERNANCE_DECISION_RECORDED = "governance.decision.recorded"


@dataclass
class GovernanceWebhookDispatcher:
    """Fire-and-forget webhook delivery for governance decisions (no PII by default)."""

    urls: list[str] = field(default_factory=list)
    signing_secret: str = ""

    @classmethod
    def from_settings(cls, urls_csv: str, secret: SecretStr | None) -> GovernanceWebhookDispatcher:
        urls = [u.strip() for u in urls_csv.split(",") if u.strip()]
        key = secret.get_secret_value().strip() if secret else ""
        return cls(urls=urls, signing_secret=key)

    def _sign(self, body: bytes) -> str | None:
        if not self.signing_secret:
            return None
        digest = hmac.new(self.signing_secret.encode(), body, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def _post_sync(self, url: str, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        headers = {"Content-Type": "application/json", "User-Agent": "Noetfield-Governance-Webhook/1.0"}
        signature = self._sign(body)
        if signature:
            headers["X-Noetfield-Signature"] = signature
        req = request.Request(url, data=body, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=8) as resp:
                if resp.status >= 400:
                    logger.warning("governance_webhook_http_error url=%s status=%s", url, resp.status)
        except error.URLError as exc:
            logger.warning("governance_webhook_delivery_failed url=%s error=%s", url, exc)

    async def emit_decision_recorded(self, payload: dict[str, Any]) -> None:
        if not self.urls:
            return
        envelope = {"event": EVENT_GOVERNANCE_DECISION_RECORDED, "data": payload}
        await asyncio.gather(
            *[asyncio.to_thread(self._post_sync, url, envelope) for url in self.urls],
            return_exceptions=True,
        )
