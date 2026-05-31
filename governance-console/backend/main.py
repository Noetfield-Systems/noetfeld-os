from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.models import Base
from db.session import engine
from routes import audit, evaluate

load_dotenv()

app = FastAPI(
    title="Noetfield Governance Console API",
    description="Pre-execution governance evaluation — no payments, custody, or execution.",
    version="1.0.0",
)

origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
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


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "governance-console-api"}
