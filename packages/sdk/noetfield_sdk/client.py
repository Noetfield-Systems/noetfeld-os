"""Python SDK for Noetfield Tier 1 (GTM) + Tier 2 (governance pilot) APIs."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

import json
from urllib import error, request
from urllib.parse import urlencode


class NoetfieldAPIError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        self.status = status
        self.detail = detail
        super().__init__(f"HTTP {status}: {detail}")


class NoetfieldClient:
    """Minimal HTTP client aligned with docs/api/openapi.json."""

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = (api_key or "").strip()
        self.timeout = timeout

    def _headers(self, *, json_body: bool = True) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if json_body:
            headers["Content-Type"] = "application/json"
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, str | int | None] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        if query:
            params = {k: str(v) for k, v in query.items() if v is not None}
            if params:
                url = f"{url}?{urlencode(params)}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = request.Request(url, data=data, headers=self._headers(), method=method)
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise NoetfieldAPIError(exc.code, detail) from exc

    def evaluate(
        self,
        *,
        tenant_id: UUID,
        organization_id: UUID,
        action: str,
        resource_type: str,
        resource_id: str,
        request_id: str | None = None,
        correlation_id: str | None = None,
        mode: Literal["shadow", "enforce"] = "shadow",
        payload: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "tenant_id": str(tenant_id),
            "organization_id": str(organization_id),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "mode": mode,
            "payload": payload or {},
        }
        if request_id:
            body["request_id"] = request_id
        if correlation_id:
            body["correlation_id"] = correlation_id
        return self._request("POST", "/api/v1/governance/evaluate", body=body)

    def get_ledger(
        self,
        *,
        tenant_id: UUID | None = None,
        request_id: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        query: dict[str, str | int | None] = {"limit": limit}
        if tenant_id is not None:
            query["tenant_id"] = str(tenant_id)
        if request_id:
            query["request_id"] = request_id
        return self._request("GET", "/api/v1/governance/ledger", query=query)

    def audit_export(
        self,
        *,
        tenant_id: UUID | None = None,
        request_id: str | None = None,
        limit: int = 500,
    ) -> dict[str, Any]:
        query: dict[str, str | int | None] = {"limit": limit}
        if tenant_id is not None:
            query["tenant_id"] = str(tenant_id)
        if request_id:
            query["request_id"] = request_id
        return self._request("GET", "/api/v1/governance/audit-export", query=query)

    def submit_intake(
        self,
        *,
        organization: str,
        contact_email: str,
        message: str,
        request_id: str | None = None,
        sku: str = "trust_brief",
        vector: str = "sdk",
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "organization": organization,
            "contact_email": contact_email,
            "message": message,
            "sku": sku,
            "vector": vector,
            "source": "api",
        }
        if request_id:
            body["request_id"] = request_id
        return self._request("POST", "/api/intake", body=body)

    def vendor_evidence(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/governance/vendor-evidence")

    def approve_decision(
        self,
        *,
        approval_id: str,
        approved: bool,
        rationale: str,
        decided_by: str = "sdk-human",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/approvals/decide",
            body={
                "approval_id": approval_id,
                "approved": approved,
                "rationale": rationale,
                "decided_by": decided_by,
            },
        )
