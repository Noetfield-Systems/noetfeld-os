"""Public institutional site routes (Trust Ledger, Partner Gateway)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.applications import Starlette

from public_site.renderer import SITE_ROOT, load_page

logger = logging.getLogger(__name__)

router = APIRouter(tags=["site"])

templates = Jinja2Templates(directory=str(SITE_ROOT / "templates"))

INTAKE_LOG = SITE_ROOT / "data" / "partner_intake.jsonl"

_LEGACY_PARTNER_ROUTES: dict[str, str] = {
    "developers": "integrator",
    "integrators": "integrator",
    "engineering": "integrator",
    "issuers": "rwa_issuer",
    "rwa": "rwa_issuer",
    "assets": "rwa_issuer",
    "capital": "allocator",
    "allocators": "allocator",
    "funds": "allocator",
}


def _render(
    request: Request,
    relative_path: str,
    *,
    active: str,
    selected_vector: str | None = None,
    flash: str | None = None,
) -> HTMLResponse:
    page = load_page(relative_path)
    template_name = "gateway.html" if page.layout == "gateway" else "page.html"
    return templates.TemplateResponse(
        request,
        template_name,
        {
            "page": page,
            "active": active,
            "selected_vector": selected_vector,
            "flash": flash,
        },
    )


def _append_intake(record: dict[str, Any]) -> None:
    INTAKE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with INTAKE_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


@router.get("/")
async def home() -> RedirectResponse:
    return RedirectResponse(url="/trust-ledger/", status_code=302)


@router.get("/trust-ledger", response_class=HTMLResponse)
@router.get("/trust-ledger/", response_class=HTMLResponse)
async def trust_ledger(request: Request) -> HTMLResponse:
    return _render(request, "trust-ledger/index.md", active="trust-ledger")


@router.get("/gate/partners", response_class=HTMLResponse)
@router.get("/gate/partners/", response_class=HTMLResponse)
async def partner_hub(
    request: Request,
    vector: str | None = Query(default=None),
    submitted: str | None = Query(default=None),
) -> HTMLResponse:
    flash = None
    if submitted == "1":
        flash = (
            "Intake brief received. Noetfield Operations will process your submission "
            "within 48 business hours."
        )
    return _render(
        request,
        "gate/partners/index.md",
        active="partners",
        selected_vector=vector,
        flash=flash,
    )


@router.get("/gate/partners/{legacy_slug}", response_class=HTMLResponse)
async def partner_legacy(legacy_slug: str) -> RedirectResponse:
    vector = _LEGACY_PARTNER_ROUTES.get(legacy_slug.lower())
    if vector:
        return RedirectResponse(url=f"/gate/partners/?vector={vector}", status_code=302)
    return RedirectResponse(url="/gate/partners/", status_code=302)


@router.post("/gate/partners/submit")
async def partner_submit(
    organization: str = Form(...),
    domain: str = Form(...),
    vector: str = Form(...),
    footprint: str = Form(...),
    pubkey: str = Form(default=""),
) -> RedirectResponse:
    record = {
        "id": str(uuid4()),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "organization": organization.strip(),
        "domain": domain.strip(),
        "vector": vector,
        "footprint": footprint.strip(),
        "pubkey": pubkey.strip() or None,
    }
    _append_intake(record)
    logger.info("Partner intake received: %s (%s)", record["organization"], record["id"])
    return RedirectResponse(url="/gate/partners/?submitted=1", status_code=303)


def mount_static(app: Starlette) -> None:
    static_dir = SITE_ROOT / "static"
    if static_dir.is_dir():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


__all__ = ["router", "mount_static"]
