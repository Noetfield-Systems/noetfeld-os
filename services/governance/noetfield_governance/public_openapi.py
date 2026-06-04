"""Public OpenAPI surface — Tier 1 (GTM) + Tier 2 (governance pilot) only."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

PUBLIC_PATH_PREFIXES = (
    "/health",
    "/api/status",
    "/api/public/",
    "/api/intake",
    "/api/ecosystem/",
    "/api/v1/governance/",
    "/api/v1/tle",
    "/api/v1/evidence",
    "/api/v1/connectors",
)

PUBLIC_EXACT_PATHS = frozenset({"/api/intake"})


def install_public_openapi(app: FastAPI) -> None:
    """Replace app.openapi with a filtered schema for institutional buyers."""

    def public_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title="Noetfield Institutional API",
            version=app.version,
            description=(
                "Public and pilot governance APIs for Noetfield. "
                "Pre-execution policy evaluation only — not payments or custody."
            ),
            routes=app.routes,
        )
        filtered: dict = {}
        for path, item in schema.get("paths", {}).items():
            if path in PUBLIC_EXACT_PATHS or any(
                path == prefix.rstrip("/") or path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES
            ):
                filtered[path] = item
        schema["paths"] = filtered
        schema["info"]["x-non-psp"] = (
            "Noetfield does not execute payments, hold custody, or operate as a PSP/MSB."
        )
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = public_openapi  # type: ignore[method-assign]
