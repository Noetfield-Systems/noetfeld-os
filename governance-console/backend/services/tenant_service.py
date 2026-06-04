from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import PILOT_TENANT_ID, Tenant

PILOT_TENANT_SLUG = "copilot-pilot-01"


def ensure_pilot_tenant(db: Session) -> Tenant:
    row = db.scalar(select(Tenant).where(Tenant.tenant_id == PILOT_TENANT_ID))
    if row is not None:
        return row
    row = db.scalar(select(Tenant).where(Tenant.slug == PILOT_TENANT_SLUG))
    if row is not None:
        return row
    tenant = Tenant(
        tenant_id=PILOT_TENANT_ID,
        slug=PILOT_TENANT_SLUG,
        display_name="Copilot Governance Pilot",
        status="pilot",
        metadata_json={"pack": "copilot-governance", "lane": "A"},
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def resolve_tenant_id(header_value: str | None, db: Session) -> uuid.UUID:
    if header_value and header_value.strip():
        raw = header_value.strip()
        try:
            return uuid.UUID(raw)
        except ValueError:
            row = db.scalar(select(Tenant).where(Tenant.slug == raw))
            if row is not None:
                return row.tenant_id
    return ensure_pilot_tenant(db).tenant_id
