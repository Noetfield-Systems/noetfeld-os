"""Capability-scoped, PII-free status for one consented Company OS intake.

Tokens grant *only* a projection of the canonical event/tasks queue.
They are not login credentials, tenancy, a WorkPacket permit, or a way to
read the internal draft, buyer record, LLM prompts, memory or revenue data.
"""
import hashlib
import hmac
import re
import secrets
import time

import core

REF_RE = re.compile(r"^evt_[a-f0-9]{16}$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{40,96}$")
POLL_HITS = {}

def init():
    with core.connect() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS intake_progress_capabilities(
            event_id TEXT PRIMARY KEY,
            token_sha256 TEXT NOT NULL,
            issued_at TEXT NOT NULL,
            revoked_at TEXT
        )""")

def issue(event_id):
    if not REF_RE.fullmatch(str(event_id)):
        raise ValueError("INVALID_EVENT_REFERENCE")
    init()
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    with core.connect() as db:
        db.execute(
            "INSERT INTO intake_progress_capabilities(event_id,token_sha256,issued_at) VALUES(?,?,?)",
            (event_id,digest,core.now())
        )
    return token

def _authorized(event_id,token):
    if not REF_RE.fullmatch(str(event_id)) or not TOKEN_RE.fullmatch(str(token)):
        return False
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    with core.connect() as db:
        row = db.execute(
            "SELECT token_sha256,revoked_at FROM intake_progress_capabilities WHERE event_id=?",
            (event_id,)
        ).fetchone()
    return bool(row and row["revoked_at"] is None and hmac.compare_digest(row["token_sha256"],digest))

def snapshot(event_id,token):
    if not _authorized(event_id,token):
        return None

    # A capability still gets bounded polling to reduce accidental load.
    now = time.monotonic()
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    recent = [t for t in POLL_HITS.get(digest,[]) if now-t<60]
    if len(recent)>=20:
        return {"rate_limited":True}
    recent.append(now)
    POLL_HITS[digest]=recent
    if len(POLL_HITS)>2000:
        POLL_HITS.clear()

    with core.connect() as db:
        event = db.execute(
            "SELECT status,created_at,processed_at FROM events WHERE id=? AND event_type='intake.received'",
            (event_id,)
        ).fetchone()
        if not event:
            return None
        tasks = db.execute(
            "SELECT role,status FROM tasks WHERE event_id=? ORDER BY created_at,id",
            (event_id,)
        ).fetchall()
    states = [{"role":r["role"],"status":r["status"]} for r in tasks]
    total=len(states)
    finished=sum(1 for t in states if t["status"] in {"drafted","approved"})
    failed=sum(1 for t in states if t["status"] in {"failed","blocked"})
    active=sum(1 for t in states if t["status"] in {"running","queued"})

    if event["status"] in {"failed","dead_letter"}:
        stage="intake_failed"
    elif event["status"] != "processed":
        stage="intake_queued"
    elif failed:
        stage="internal_review_required"
    elif total == 0:
        stage="specialist_assignment_pending"
    elif finished == total:
        stage="internal_drafts_ready"
    elif active:
        stage="specialists_working"
    else:
        stage="internal_review_required"

    return {
        "schema":"noetfield.business-os-intake-progress.v1",
        "reference":event_id,
        "stage":stage,
        "created_at":event["created_at"],
        "updated_at":event["processed_at"] or event["created_at"],
        "tasks_total":total,
        "tasks_drafted":finished,
        "tasks_blocked":failed,
        "roles":states,
        "external_execution":"NOT_AUTHORIZED",
        "customer_workpacket":"NOT_DISPATCHED",
        "independent_verification":"NOT_PERFORMED",
        "artifacts_shared":0,
        "note":"Internal specialist draft progress only. No customer system change or external delivery is implied.",
    }
