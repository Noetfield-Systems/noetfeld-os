"""
NOETFELD OS — SQLite layer.

Responsibilities
----------------
* init_db()        – create schema on startup (idempotent).
* insert_audit()   – write one decisioning event to the audit log.
* get_audit()      – retrieve audit rows with optional filters.
"""

import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

from config import AUDIT_TABLE_NAME
import config

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

@contextmanager
def _get_conn() -> Generator[sqlite3.Connection, None, None]:
    """Yield a WAL-mode connection with row_factory set to Row."""
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CREATE_AUDIT_TABLE = f"""
CREATE TABLE IF NOT EXISTS {AUDIT_TABLE_NAME} (
    id              INTEGER  PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT     NOT NULL,
    request_id      TEXT     NOT NULL UNIQUE,
    applicant_id    TEXT     NOT NULL,
    tenant_id       TEXT     NOT NULL DEFAULT 'unknown',
    decision        TEXT     NOT NULL,
    composite_score REAL     NOT NULL,
    input_payload   TEXT     NOT NULL,
    score_breakdown TEXT     NOT NULL,
    policy_decision TEXT,
    corridor_decision TEXT,
    corridor_breaches TEXT   NOT NULL DEFAULT '[]',
    rule_set_id     TEXT     NOT NULL DEFAULT 'unknown',
    rule_set_version TEXT    NOT NULL DEFAULT '0.0.0',
    policy_base_hash TEXT,
    policy_corridor_hash TEXT,
    api_key_id      TEXT,
    correlation_id  TEXT,
    notes           TEXT
);
"""

_CREATE_INDEXES = [
    f"CREATE INDEX IF NOT EXISTS idx_audit_applicant_id ON {AUDIT_TABLE_NAME}(applicant_id);",
    f"CREATE INDEX IF NOT EXISTS idx_audit_created_at   ON {AUDIT_TABLE_NAME}(created_at);",
    f"CREATE INDEX IF NOT EXISTS idx_audit_decision      ON {AUDIT_TABLE_NAME}(decision);",
    f"CREATE INDEX IF NOT EXISTS idx_audit_tenant_id     ON {AUDIT_TABLE_NAME}(tenant_id);",
]

_MIGRATION_COLUMNS: list[tuple[str, str]] = [
    ("tenant_id", "TEXT NOT NULL DEFAULT 'unknown'"),
    ("policy_decision", "TEXT"),
    ("corridor_decision", "TEXT"),
    ("corridor_breaches", "TEXT NOT NULL DEFAULT '[]'"),
    ("rule_set_id", "TEXT NOT NULL DEFAULT 'unknown'"),
    ("rule_set_version", "TEXT NOT NULL DEFAULT '0.0.0'"),
    ("policy_base_hash", "TEXT"),
    ("policy_corridor_hash", "TEXT"),
    ("api_key_id", "TEXT"),
    ("correlation_id", "TEXT"),
]


def _migrate_schema(conn: sqlite3.Connection) -> None:
    existing = {
        row[1] for row in conn.execute(f"PRAGMA table_info({AUDIT_TABLE_NAME})").fetchall()
    }
    if not existing:
        return
    for column, ddl in _MIGRATION_COLUMNS:
        if column not in existing:
            conn.execute(f"ALTER TABLE {AUDIT_TABLE_NAME} ADD COLUMN {column} {ddl}")


def init_db() -> None:
    """Create tables and indexes if they do not already exist (idempotent)."""
    with _get_conn() as conn:
        conn.execute(_CREATE_AUDIT_TABLE)
        _migrate_schema(conn)
        for stmt in _CREATE_INDEXES:
            conn.execute(stmt)


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def insert_audit(
    *,
    request_id: str,
    applicant_id: str,
    tenant_id: str,
    decision: str,
    composite_score: float,
    input_payload: dict[str, Any],
    score_breakdown: dict[str, float],
    policy_decision: str,
    corridor_decision: str | None,
    corridor_breaches: list[str],
    rule_set_id: str,
    rule_set_version: str,
    policy_base_hash: str,
    policy_corridor_hash: str,
    api_key_id: str | None = None,
    correlation_id: str | None = None,
    notes: str | None = None,
) -> int:
    created_at = datetime.now(tz=timezone.utc).isoformat()
    sql = f"""
        INSERT INTO {AUDIT_TABLE_NAME}
            (created_at, request_id, applicant_id, tenant_id, decision,
             composite_score, input_payload, score_breakdown,
             policy_decision, corridor_decision, corridor_breaches,
             rule_set_id, rule_set_version, policy_base_hash, policy_corridor_hash,
             api_key_id, correlation_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        created_at,
        request_id,
        applicant_id,
        tenant_id,
        decision,
        composite_score,
        json.dumps(input_payload, sort_keys=True),
        json.dumps(score_breakdown, sort_keys=True),
        policy_decision,
        corridor_decision,
        json.dumps(corridor_breaches),
        rule_set_id,
        rule_set_version,
        policy_base_hash,
        policy_corridor_hash,
        api_key_id,
        correlation_id,
        notes,
    )
    with _get_conn() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def _row_to_record(row: sqlite3.Row) -> dict[str, Any]:
    record = dict(row)
    record["input_payload"] = json.loads(record["input_payload"])
    record["score_breakdown"] = json.loads(record["score_breakdown"])
    breaches = record.get("corridor_breaches")
    if isinstance(breaches, str):
        record["corridor_breaches"] = json.loads(breaches)
    return record


def get_audit_by_id(audit_id: int) -> dict[str, Any] | None:
    with _get_conn() as conn:
        row = conn.execute(
            f"SELECT * FROM {AUDIT_TABLE_NAME} WHERE id = ? LIMIT 1",
            (audit_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_record(row)


def get_audit_by_request_id(request_id: str) -> dict[str, Any] | None:
    with _get_conn() as conn:
        row = conn.execute(
            f"SELECT * FROM {AUDIT_TABLE_NAME} WHERE request_id = ? LIMIT 1",
            (request_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_record(row)


def get_audit(
    *,
    request_id: str | None = None,
    applicant_id: str | None = None,
    tenant_id: str | None = None,
    decision: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if request_id is not None:
        conditions.append("request_id = ?")
        params.append(request_id)
    if applicant_id is not None:
        conditions.append("applicant_id = ?")
        params.append(applicant_id)
    if tenant_id is not None:
        conditions.append("tenant_id = ?")
        params.append(tenant_id)
    if decision is not None:
        conditions.append("decision = ?")
        params.append(decision)
    if since is not None:
        conditions.append("created_at >= ?")
        params.append(since.astimezone(timezone.utc).isoformat())
    if until is not None:
        conditions.append("created_at <= ?")
        params.append(until.astimezone(timezone.utc).isoformat())

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    sql = f"""
        SELECT *
        FROM   {AUDIT_TABLE_NAME}
        {where_clause}
        ORDER  BY created_at DESC
        LIMIT  ? OFFSET ?
    """
    params.extend([limit, offset])

    with _get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    return [_row_to_record(row) for row in rows]
