"""Durable Railway PostgreSQL authority for NOOS loop cycles and coding jobs.

Opt-in with NOOS_STORAGE_BACKEND=railway_postgres. The historical Supabase
store is left untouched; this is a new epoch, not a claim that old rows have
been migrated. No new database/service is provisioned.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

import asyncpg

BACKEND = "railway_postgres"
REPO_RE = re.compile(r"^Noetfield-Systems/[A-Za-z0-9_.-]{2,100}$")
ID_RE = re.compile(r"^[a-zA-Z0-9_.:-]{8,128}$")

SCHEMA = """
CREATE TABLE IF NOT EXISTS noos_runtime_cycle_counters (
  factory_id TEXT PRIMARY KEY, last_number BIGINT NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS noos_runtime_cycles (
  factory_id TEXT NOT NULL, cycle_number BIGINT NOT NULL,
  status TEXT NOT NULL, receipt JSONB NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (factory_id, cycle_number)
);
CREATE TABLE IF NOT EXISTS noos_runtime_liveness (
  loop_id TEXT PRIMARY KEY, event_type TEXT, interval_minutes INT NOT NULL,
  last_fired_at TIMESTAMPTZ NOT NULL, last_cycle_status TEXT NOT NULL,
  host TEXT NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS noos_runtime_coding_jobs (
  job_id UUID PRIMARY KEY, workpacket_id TEXT UNIQUE NOT NULL,
  project_id TEXT NOT NULL, repo TEXT NOT NULL, prompt TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'QUEUED',
  lease_token UUID, lease_until TIMESTAMPTZ, attempts INT NOT NULL DEFAULT 0,
  max_attempts INT NOT NULL DEFAULT 3,
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (state IN ('QUEUED','LEASED','PR_OPENED','VERIFIED','FAILED','BLOCKED')),
  CHECK (attempts >= 0 AND attempts <= max_attempts)
);
CREATE INDEX IF NOT EXISTS noos_runtime_coding_claim_idx
 ON noos_runtime_coding_jobs (state,lease_until,created_at);
"""

def configured() -> bool:
    return os.environ.get("NOOS_STORAGE_BACKEND", "").strip() == BACKEND

def _dsn() -> str:
    url = (os.environ.get("NOOS_RUNTIME_DATABASE_URL")
           or os.environ.get("DATABASE_URL") or "").strip()
    if not url or not url.startswith(("postgresql://", "postgres://")):
        raise RuntimeError("NOOS_RUNTIME_DATABASE_URL_NOT_CONFIGURED")
    return url

async def _with_database(fn):
    connection = await asyncpg.connect(_dsn(), timeout=12, command_timeout=20)
    try:
        await connection.execute(SCHEMA)
        return await fn(connection)
    finally:
        await connection.close()

def _run(fn):
    if not configured():
        raise RuntimeError("RAILWAY_POSTGRES_BACKEND_NOT_ENABLED")
    return asyncio.run(_with_database(fn))

def probe() -> dict[str, Any]:
    try:
        async def op(db):
            return await db.fetchval("SELECT 1")
        return {"ok": _run(op) == 1, "backend": BACKEND, "schema": "noos-runtime-pg.v1"}
    except Exception as exc:
        return {"ok": False, "backend": BACKEND, "reason": type(exc).__name__}

def allocate_cycle(factory_id: str) -> tuple[int | None, dict[str, Any]]:
    try:
        async def op(db):
            row = await db.fetchrow("""
                INSERT INTO noos_runtime_cycle_counters(factory_id,last_number)
                VALUES($1,1) ON CONFLICT(factory_id) DO UPDATE
                SET last_number=noos_runtime_cycle_counters.last_number+1,
                    updated_at=now()
                RETURNING last_number
            """, "pgv1:" + factory_id)
            return int(row["last_number"])
        number = _run(op)
        return number, {"ok": True, "backend": BACKEND, "epoch": "pgv1",
                        "factory_id": factory_id, "cas": {"verdict": "ACCEPTED"}}
    except Exception as exc:
        return None, {"ok": False, "backend": BACKEND, "reason": type(exc).__name__}

def store_cycle(factory_id: str, cycle: dict[str, Any]) -> dict[str, Any]:
    number = int(cycle.get("cycle_number") or 0)
    if number < 1:
        return {"ok": False, "reason": "invalid_cycle_number"}
    try:
        async def op(db):
            return await db.fetchval("""
                INSERT INTO noos_runtime_cycles
                 (factory_id,cycle_number,status,receipt)
                VALUES($1,$2,$3,$4::jsonb)
                ON CONFLICT(factory_id,cycle_number) DO NOTHING
                RETURNING cycle_number
            """, "pgv1:" + factory_id, number, str(cycle.get("status") or "unknown"),
                 json.dumps(cycle, ensure_ascii=False))
        inserted = _run(op)
        return {"ok": inserted == number, "backend": BACKEND, "epoch": "pgv1",
                "cycle_number": number,
                "collision": inserted != number,
                "reason": "cycle_number_collision" if inserted != number else None}
    except Exception as exc:
        return {"ok": False, "backend": BACKEND, "reason": type(exc).__name__}

def upsert_liveness(*, loop_id: str, event_type: str | None,
                    interval_minutes: int, last_cycle_status: str,
                    host: str, last_fired_at: str) -> dict[str, Any]:
    try:
        fired = datetime.fromisoformat(last_fired_at.replace("Z", "+00:00"))
        if fired.tzinfo is None:
            fired = fired.replace(tzinfo=timezone.utc)
        async def op(db):
            await db.execute("""
                INSERT INTO noos_runtime_liveness
                 (loop_id,event_type,interval_minutes,last_fired_at,
                  last_cycle_status,host)
                VALUES($1,$2,$3,$4::timestamptz,$5,$6)
                ON CONFLICT (loop_id) DO UPDATE SET
                 event_type=EXCLUDED.event_type,
                 interval_minutes=EXCLUDED.interval_minutes,
                 last_fired_at=EXCLUDED.last_fired_at,
                 last_cycle_status=EXCLUDED.last_cycle_status,
                 host=EXCLUDED.host,updated_at=now()
            """,loop_id,event_type,interval_minutes,fired,
                 last_cycle_status,host)
        _run(op)
        return {"ok": True, "backend": BACKEND, "loop_id": loop_id,
                "last_fired_at": last_fired_at}
    except Exception as exc:
        return {"ok": False, "backend": BACKEND, "reason": type(exc).__name__}

def allowed_repo(repo: str) -> bool:
    allow = {x.strip() for x in os.environ.get(
        "NOOS_CODING_ALLOWED_REPOS", "Noetfield-Systems/noetfeld-os").split(",") if x.strip()}
    return bool(REPO_RE.fullmatch(repo)) and repo in allow

def enqueue_job(packet: dict[str, Any]) -> dict[str, Any]:
    workpacket = str(packet.get("workpacket_id") or "")
    repo = str(packet.get("repo") or "")
    prompt = str(packet.get("prompt") or "")
    project_id = str(packet.get("project_id") or "")
    if (not ID_RE.fullmatch(workpacket) or not allowed_repo(repo)
            or not ID_RE.fullmatch(project_id)
            or len(prompt) < 20 or len(prompt) > 10000
            or packet.get("founder_authorized") is not True):
        raise ValueError("INVALID_OR_UNAUTHORIZED_WORKPACKET")
    try:
        async def op(db):
            row = await db.fetchrow("""
                INSERT INTO noos_runtime_coding_jobs
                 (job_id,workpacket_id,project_id,repo,prompt)
                VALUES($1,$2,$3,$4,$5)
                ON CONFLICT(workpacket_id) DO UPDATE SET
                 updated_at=noos_runtime_coding_jobs.updated_at
                RETURNING job_id,state,repo,workpacket_id
            """,uuid.uuid4(),workpacket,project_id,repo,prompt)
            if row["repo"] != repo:
                raise ValueError("WORKPACKET_REPO_CONFLICT")
            return dict(row)
        row = _run(op)
        return {"ok": True, **{k:str(v) for k,v in row.items()}, "backend": BACKEND}
    except ValueError:
        raise
    except Exception as exc:
        return {"ok": False, "reason": type(exc).__name__}

def claim_job(repo: str, *, lease_minutes: int = 15) -> dict[str, Any]:
    if not allowed_repo(repo):
        raise ValueError("REPO_NOT_AUTHORIZED")
    if not 1 <= lease_minutes <= 60:
        raise ValueError("INVALID_LEASE")
    try:
        async def op(db):
            return await db.fetchrow("""
                WITH chosen AS (
                  SELECT job_id FROM noos_runtime_coding_jobs
                  WHERE repo=$1 AND attempts < max_attempts AND
                    (state='QUEUED' OR (state='LEASED' AND lease_until<now()))
                  ORDER BY created_at, job_id
                  FOR UPDATE SKIP LOCKED LIMIT 1
                )
                UPDATE noos_runtime_coding_jobs j SET
                  state='LEASED', lease_token=$2,
                  lease_until=now()+($3::int*interval '1 minute'),
                  attempts=j.attempts+1,updated_at=now()
                FROM chosen
                WHERE j.job_id=chosen.job_id
                RETURNING j.job_id,j.workpacket_id,j.project_id,
                    j.repo,j.prompt,j.lease_token,j.attempts
            """,repo,uuid.uuid4(),lease_minutes)
        row = _run(op)
        return {"ok": True, "state": "LEASED" if row else "IDLE",
                "job": {k:str(v) for k,v in dict(row).items()} if row else None}
    except Exception as exc:
        return {"ok": False, "reason": type(exc).__name__}

def report_job(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        job_id = uuid.UUID(str(payload.get("job_id") or ""))
        token = uuid.UUID(str(payload.get("lease_token") or ""))
    except ValueError as exc:
        raise ValueError("INVALID_JOB_ID_OR_LEASE") from exc
    state = str(payload.get("state") or "")
    if state not in {"PR_OPENED","VERIFIED","FAILED","BLOCKED"}:
        raise ValueError("INVALID_COMPLETION_STATE")
    evidence = payload.get("evidence")
    if not isinstance(evidence,dict) or len(json.dumps(evidence))>10000:
        raise ValueError("INVALID_EVIDENCE")
    # Only the holder of a non-expired lease can complete its own job.
    try:
        async def op(db):
            return await db.fetchrow("""
                UPDATE noos_runtime_coding_jobs SET
                  state=$3, evidence=$4::jsonb,lease_token=NULL,
                  lease_until=NULL,updated_at=now()
                WHERE job_id=$1 AND lease_token=$2 AND state='LEASED'
                  AND lease_until>now()
                RETURNING job_id,workpacket_id,state
            """,job_id,token,state,json.dumps(evidence))
        row = _run(op)
        return {"ok": bool(row), "job": {k:str(v) for k,v in dict(row).items()}
                if row else None, "reason":None if row else "LEASE_INVALID_OR_EXPIRED"}
    except Exception as exc:
        return {"ok": False, "reason": type(exc).__name__}

def queue_status() -> dict[str, Any]:
    try:
        async def op(db):
            rows = await db.fetch("""
                SELECT state,count(*) AS n FROM noos_runtime_coding_jobs
                 GROUP BY state ORDER BY state
            """)
            last = await db.fetchval("SELECT max(updated_at) FROM noos_runtime_liveness")
            return {r["state"]:int(r["n"]) for r in rows},last
        counts,last = _run(op)
        return {"ok": True, "backend": BACKEND,
                "counts":counts, "last_liveness_at":last.isoformat() if last else None}
    except Exception as exc:
        return {"ok": False, "reason": type(exc).__name__}
