"""High-level Governance SDK wrapping the institutional evaluate API."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from noetfield_sdk.client import NoetfieldClient


class Governance:
    """Developer surface: check, audit, approve, log, sign."""

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        tenant_id: UUID | None = None,
        organization_id: UUID | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.client = NoetfieldClient(base_url, api_key=api_key, timeout=timeout)
        self.tenant_id = tenant_id
        self.organization_id = organization_id

    def check(
        self,
        *,
        action: str,
        resource_type: str = "governance",
        resource_id: str = "sdk-check",
        confidence: float = 1.0,
        mode: Literal["shadow", "enforce"] = "shadow",
        payload: dict[str, object] | None = None,
        tenant_id: UUID | None = None,
        organization_id: UUID | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        tenant = tenant_id or self.tenant_id
        org = organization_id or self.organization_id
        if tenant is None or org is None:
            raise ValueError("tenant_id and organization_id are required for check()")
        return self.client.evaluate(
            tenant_id=tenant,
            organization_id=org,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            mode=mode,
            request_id=request_id,
            payload={**(payload or {}), "confidence": confidence},
        )

    def audit(
        self,
        *,
        request_id: str | None = None,
        tenant_id: UUID | None = None,
        limit: int = 500,
    ) -> dict[str, Any]:
        return self.client.audit_export(
            tenant_id=tenant_id or self.tenant_id,
            request_id=request_id,
            limit=limit,
        )

    def approve(
        self,
        *,
        approval_id: str,
        approved: bool,
        rationale: str,
        decided_by: str = "sdk-human",
    ) -> dict[str, Any]:
        return self.client.approve_decision(
            approval_id=approval_id,
            approved=approved,
            rationale=rationale,
            decided_by=decided_by,
        )

    def log(self, *, request_id: str | None = None, tenant_id: UUID | None = None) -> dict[str, Any]:
        return self.client.get_ledger(
            tenant_id=tenant_id or self.tenant_id,
            request_id=request_id,
        )

    def sign(self, *, request_id: str) -> dict[str, Any]:
        export = self.audit(request_id=request_id)
        return {
            "request_id": request_id,
            "export_type": export.get("export_type"),
            "entry_count": export.get("entry_count"),
            "signed": bool(export.get("entries")),
        }
