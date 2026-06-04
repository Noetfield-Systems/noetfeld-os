from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.bootstrap import init_schema, migrate_audit_logs_to_events, seed_pilot_evidence
from db.session import SessionLocal, engine
from routes import audit, connectors, evaluate, evidence, tle

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_schema()
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


@app.get("/health")
def health() -> dict[str, str]:
    db: Session = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()
    return {"status": "ok", "service": "governance-console-api"}
