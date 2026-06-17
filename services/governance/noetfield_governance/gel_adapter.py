"""HTTP adapter bridge to noetfeld-os GEL (POST /v1/decision)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request

GEL_DECISION_MAP = {
    "APPROVE": "PROCEED",
    "REVIEW": "REQUIRE_HUMAN_REVIEW",
    "DECLINE": "REJECT",
}


@dataclass(frozen=True)
class GelDecisionResult:
    request_id: str
    gel_decision: str
    platform_decision: str
    composite_score: float
    policy_base_hash: str
    policy_corridor_hash: str
    available: bool = True


class GelAdapter:
    """Optional credit-lane adapter; degrades gracefully when GEL is offline."""

    def __init__(self, base_url: str | None = None, *, timeout: float = 5.0) -> None:
        self.base_url = (base_url or os.environ.get("GEL_ADAPTER_URL", "")).rstrip("/")
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def evaluate_sync(
        self,
        *,
        tenant_id: str,
        applicant_id: str,
        request_id: str,
        input_payload: dict[str, Any] | None = None,
    ) -> GelDecisionResult | None:
        if not self.enabled:
            return None
        body = {
            "tenant_id": tenant_id,
            "applicant_id": applicant_id,
            "request_id": request_id,
            "input_payload": input_payload or {},
        }
        url = f"{self.base_url}/v1/decision"
        req = request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (error.URLError, error.HTTPError, json.JSONDecodeError, TimeoutError):
            return None

        gel_decision = str(payload.get("decision", "REVIEW")).upper()
        return GelDecisionResult(
            request_id=str(payload.get("request_id", request_id)),
            gel_decision=gel_decision,
            platform_decision=GEL_DECISION_MAP.get(gel_decision, "REQUIRE_HUMAN_REVIEW"),
            composite_score=float(payload.get("composite_score", 0.0)),
            policy_base_hash=str(payload.get("policy_base_hash", "")),
            policy_corridor_hash=str(payload.get("policy_corridor_hash", "")),
        )
