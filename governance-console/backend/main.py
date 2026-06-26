from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.bootstrap import init_schema, migrate_audit_logs_to_events, migrate_dev_schema_patches, seed_pilot_evidence
from db.session import SessionLocal, engine
from routes import audit, connectors, evaluate, evidence, sandbox, tle

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_schema()
    migrate_dev_schema_patches()
    db = SessionLocal()
    try:
        migrate_audit_logs_to_events(db)
        seed_pilot_evidence(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Noetfield Governance Console API",
    description="Pre-execution governance evaluation — no payments, custody, or execution.",
    version="1.0.0",
    lifespan=lifespan,
)

origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,"
    "http://localhost:13080,http://127.0.0.1:13080,"
    "http://localhost:13000,http://127.0.0.1:13000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evaluate.router)
app.include_router(audit.router)
app.include_router(evidence.router)
app.include_router(connectors.router)
app.include_router(tle.router)
app.include_router(sandbox.router)


_health_cache: tuple[float, dict[str, str]] | None = None
_HEALTH_TTL_SEC = 2.0


@app.get("/health")
def health() -> dict[str, str]:
    import time

    global _health_cache
    now = time.monotonic()
    if _health_cache is not None and now - _health_cache[0] < _HEALTH_TTL_SEC:
        return _health_cache[1]
    db: Session = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()
    payload = {"status": "ok", "service": "governance-console-api", "database": "ok"}
    _health_cache = (now, payload)
    return payload
