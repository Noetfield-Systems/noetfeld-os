"""
Application entrypoint for NOETFELD OS.

Exposes a FastAPI app that wires together:
* health / readiness / policy meta
* core decisioning router
* portal (audit) routes
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth import KEY_STORE
from database import init_db
from health import router as health_router
from policy_meta import PolicyNotReadyError, PolicyRegistry
from portal.routes import router as portal_router
from public_site.routes import mount_static, router as site_router
from router import router as decision_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    KEY_STORE.load()
    try:
        PolicyRegistry.load()
    except PolicyNotReadyError:
        pass
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="NOETFELD OS", version="0.3.0", lifespan=lifespan)
    app.include_router(health_router)
    app.include_router(site_router)
    app.include_router(decision_router)
    app.include_router(portal_router)
    mount_static(app)
    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("run:app", host="0.0.0.0", port=8001, reload=True)
