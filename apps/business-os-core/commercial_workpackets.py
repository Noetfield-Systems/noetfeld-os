"""Real Company OS commercial WorkPackets on its existing durable SQLite/agent queue.

Internal work only. A durable 202 ACK is not work completion, an agent draft
is not independent verification, and a payment event ID is not accepted from
a browser. Only the trusted Noetfield Platform can invoke this receiver.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

import core

BASE_URL = "https://business-os-core-production.up.railway.app"
INTAKE_RE = re.compile(r"^INT-[A-Z0-9]{12}$")
EVENT_RE = re.compile(r"^evt_[A-Za-z0-9]{8,100}$")
SCOPE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{4,100}$")


class CommercialWorkPacketError(ValueError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def init() -> None:
    with core.connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS commercial_workpackets (
          id TEXT PRIMARY KEY,
          idempotency_key TEXT NOT NULL UNIQUE,
          request_hash TEXT NOT NULL,
          source_intake_id TEXT NOT NULL,
          engine TEXT NOT NULL,
          scope_ref TEXT NOT NULL,
          payment_event_id TEXT NOT NULL,
          state TEXT NOT NULL DEFAULT 'QUEUED',
          engineer_task_id TEXT NOT NULL,
          reviewer_task_id TEXT NOT NULL,
          artifact_json TEXT,
          artifact_hash TEXT,
          artifact_capability_hash TEXT NOT NULL,
          last_error_code TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS commercial_wp_state_idx ON commercial_workpackets(state,created_at)")


def validate(payload: dict[str, Any]) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise CommercialWorkPacketError("WORKPACKET_OBJECT_REQUIRED")
    expected={"idempotency_key","source_intake_id","engine","scope_ref",
              "payment_event_id","requested_work"}
    if set(payload)!=expected or any(not isinstance(payload[k],str) for k in expected):
        raise CommercialWorkPacketError("STRICT_WORKPACKET_CONTRACT_REQUIRED")
    try:
        key = str(uuid.UUID(payload["idempotency_key"]))
    except (ValueError, AttributeError) as exc:
        raise CommercialWorkPacketError("UUID_IDEMPOTENCY_REQUIRED") from exc
    intake=payload["source_intake_id"].strip()
    engine=payload["engine"].strip()
    scope=payload["scope_ref"].strip()
    event=payload["payment_event_id"].strip()
    work=payload["requested_work"].strip()
    if not INTAKE_RE.fullmatch(intake) or not SCOPE_RE.fullmatch(scope):
        raise CommercialWorkPacketError("REAL_INTAKE_AND_SIGNED_SCOPE_REQUIRED")
    if engine!="COMPANY_OS" or not EVENT_RE.fullmatch(event):
        raise CommercialWorkPacketError("COMPANY_OS_LIVE_PAYMENT_CONTRACT_REQUIRED")
    if (len(work)<20 or len(work)>400 or any(x in work.upper() for x in ("DEMO-", "MOCK-", "SIMULATED"))):
        raise CommercialWorkPacketError("BOUNDED_REAL_WORK_REQUIRED")
    return {"idempotency_key":key,"source_intake_id":intake,"engine":engine,
            "scope_ref":scope,"payment_event_id":event,"requested_work":work}


def _capability() -> tuple[str, str]:
    raw=secrets.token_urlsafe(32)
    return raw,hashlib.sha256(raw.encode()).hexdigest()


def _receipt_id(identifier: str) -> str:
    return BASE_URL+"/api/commercial/receipts/"+identifier


def admit(payload: dict[str, Any]) -> dict[str, Any]:
    item=validate(payload)
    digest=hashlib.sha256(canonical(item).encode()).hexdigest()
    init()
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        existing=db.execute("SELECT id,request_hash,state FROM commercial_workpackets WHERE idempotency_key=?",
                            (item["idempotency_key"],)).fetchone()
        if existing:
            if not hmac.compare_digest(existing["request_hash"],digest):
                raise CommercialWorkPacketError("IDEMPOTENCY_PAYLOAD_CONFLICT")
            return {"status":"ACCEPTED","engine":"COMPANY_OS",
                    "source_intake_id":item["source_intake_id"],
                    "workpacket_id":existing["id"],"idempotent":True,
                    "provider_receipt_url":_receipt_id(existing["id"]),
                    "execution_state":existing["state"],"work_completed":False}
        wid="cwp_"+uuid.uuid4().hex
        # Each accepted commercial scope creates genuine, persisted, separately
        # traceable Company OS specialist tasks with a dependent risk review.
        # No contact details or raw client documents are sent to the model.
        objective=("Prepare a scoped implementation blueprint and executable acceptance "
            "tests for an AI Sales OS pilot. Accepted SOW reference "+item["scope_ref"]+
            "; original intake "+item["source_intake_id"]+
            ". Product work: lead source mapping, duplicate control, owner assignment, "
            "human-reviewed outreach, explicit failure paths and reporting. "
            "Return exact unknowns and verifiable test plan. Do not claim deployed software, "
            "customer contact, verified delivery or paid revenue.")
        engineer=core.add_task(db,None,None,"noetfield","engineering_operator",
             "Paid AI Sales OS pilot — implementation plan",objective,
             "Produce bounded engineering artifact with acceptance checks.")
        reviewer=core.add_task(db,None,None,"noetfield","risk_governance",
             "Paid AI Sales OS pilot — independent risk review",
             "Evaluate the same accepted SOW "+item["scope_ref"]+
             ": data minimization, buyer contact permission, duplicate prevention, "
             "provider outages and deployment evidence. Identify exact missing proofs.",
             "Identify gaps for independent verification.")
        db.execute("UPDATE tasks SET priority_rank=10 WHERE id IN (?,?)",(engineer,reviewer))
        cap,cap_hash=_capability()
        current=now()
        db.execute("""INSERT INTO commercial_workpackets
          (id,idempotency_key,request_hash,source_intake_id,engine,scope_ref,
           payment_event_id,state,engineer_task_id,reviewer_task_id,
           artifact_capability_hash,created_at,updated_at)
          VALUES(?,?,?,?,?,?,?,'QUEUED',?,?,?,?,?)""",
          (wid,item["idempotency_key"],digest,item["source_intake_id"],item["engine"],
           item["scope_ref"],item["payment_event_id"],engineer,reviewer,
           cap_hash,current,current))
        # Capability is only distributed once when artifact is finished, never
        # stored in a browser or claimed to be a verifier signature.
    return {"status":"ACCEPTED","engine":"COMPANY_OS",
            "source_intake_id":item["source_intake_id"],
            "workpacket_id":wid,"idempotent":False,
            "provider_receipt_url":_receipt_id(wid),
            "execution_state":"QUEUED","work_completed":False}


def is_commercial_specialist(task_id: str) -> bool:
    try:
        with core.connect() as db:
            return db.execute("""SELECT 1 FROM commercial_workpackets
                 WHERE (engineer_task_id=? OR reviewer_task_id=?)
                 AND state IN ('QUEUED','RUNNING','BLOCKED_MODEL') LIMIT 1""",
                 (task_id,task_id)).fetchone() is not None
    except sqlite3.OperationalError:
        return False


def _task(db: sqlite3.Connection, tid: str) -> dict[str, Any] | None:
    row=db.execute("SELECT id,role,status,result,updated_at FROM tasks WHERE id=?",(tid,)).fetchone()
    return dict(row) if row else None


def _public_status(row: sqlite3.Row) -> dict[str, Any]:
    return {"schema":"noetfield.company-os-commercial-receipt.v1",
            "external_workpacket_id":row["id"],"engine":"COMPANY_OS",
            "status":row["state"],"provider_admitted":True,
            "artifact_ready":row["state"]=="ARTIFACT_READY",
            "artifact_sha256":row["artifact_hash"] if row["state"]=="ARTIFACT_READY" else None,
            "work_completed_and_independently_verified":False,
            "created_at":row["created_at"],"updated_at":row["updated_at"]}


def public_receipt(wid: str) -> dict[str, Any]:
    if not re.fullmatch(r"cwp_[a-f0-9]{32}",wid):
        raise CommercialWorkPacketError("INVALID_WORKPACKET_ID")
    init()
    with core.connect() as db:
        row=db.execute("SELECT * FROM commercial_workpackets WHERE id=?",(wid,)).fetchone()
        if row is None:
            raise CommercialWorkPacketError("WORKPACKET_NOT_FOUND")
        return _public_status(row)


def readback(wid: str) -> dict[str, Any]:
    if not re.fullmatch(r"cwp_[a-f0-9]{32}",wid):
        raise CommercialWorkPacketError("INVALID_WORKPACKET_ID")
    init()
    with core.connect() as db:
        row=db.execute("SELECT * FROM commercial_workpackets WHERE id=?",(wid,)).fetchone()
        if row is None:
            raise CommercialWorkPacketError("WORKPACKET_NOT_FOUND")
        output=_public_status(row)
        output.update({"source_intake_id":row["source_intake_id"],
           "scope_ref":row["scope_ref"],"payment_event_id":row["payment_event_id"],
           "tasks":{"engineering":_task(db,row["engineer_task_id"]),
                    "risk":_task(db,row["reviewer_task_id"])},
           "artifact":json.loads(row["artifact_json"]) if row["artifact_json"] else None,
           "last_error_code":row["last_error_code"]})
        return output


def reconcile(limit: int=20) -> dict[str, int]:
    """Actual existing workers process the tasks; this creates an artifact only
    when both provider-backed specialist runs are demonstrably complete."""
    init()
    advanced=0;blocked=0
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        rows=db.execute("""SELECT * FROM commercial_workpackets
              WHERE state IN ('QUEUED','RUNNING','BLOCKED_MODEL')
              ORDER BY created_at LIMIT ?""",(min(100,max(1,limit)),)).fetchall()
        for row in rows:
            engineer=_task(db,row["engineer_task_id"])
            reviewer=_task(db,row["reviewer_task_id"])
            if not engineer or not reviewer:
                db.execute("UPDATE commercial_workpackets SET state='BLOCKED_MODEL',last_error_code='TASK_NOT_FOUND',updated_at=? WHERE id=?",(now(),row["id"]))
                blocked+=1
                continue
            tasks=[engineer,reviewer]
            if any(t["status"] in {"blocked","failed"} for t in tasks):
                if row["state"]!="BLOCKED_MODEL":
                    db.execute("UPDATE commercial_workpackets SET state='BLOCKED_MODEL',last_error_code='SPECIALIST_BLOCKED',updated_at=? WHERE id=?",(now(),row["id"]))
                    blocked+=1
                continue
            if not all(t["status"] in {"drafted","approved"} for t in tasks):
                if row["state"]=="QUEUED":
                    db.execute("UPDATE commercial_workpackets SET state='RUNNING',updated_at=? WHERE id=?",(now(),row["id"]))
                continue
            evidence=[]
            bad=False
            for task in tasks:
                try: result=json.loads(task["result"] or "{}")
                except (TypeError,ValueError):result={}
                recommendation=result.get("recommendation") or {}
                if (result.get("provider")!="openai-compatible" or
                    not isinstance(recommendation,dict) or
                    len(str(recommendation.get("assessment") or ""))<25 or
                    len(str(recommendation.get("next_best_action") or ""))<15):
                    bad=True;break
                evidence.append({"task_id":task["id"],"role":task["role"],
                    "provider":result["provider"],"recommendation":recommendation})
            if bad:
                db.execute("UPDATE commercial_workpackets SET state='BLOCKED_MODEL',last_error_code='SUBSTANTIVE_PROVIDER_EVIDENCE_REQUIRED',updated_at=? WHERE id=?",(now(),row["id"]))
                blocked+=1;continue
            artifact={
              "schema":"noetfield.company-os-commercial-artifact.v1",
              "workpacket_id":row["id"],"engine":"COMPANY_OS",
              "source_intake_id":row["source_intake_id"],
              "scope_ref":row["scope_ref"],
              "payment_event_id":row["payment_event_id"],
              "work_product_kind":"AI_SALES_OS_IMPLEMENTATION_BLUEPRINT_DRAFT",
              "work_product_stage":"INTERNAL_REVIEW_READY_NOT_DEPLOYED",
              "agent_results":evidence,
              "acceptance_tests":[
                 {"id":"INTAKE","criterion":"Real authorized lead enters one source-bound queue","verified":False},
                 {"id":"DEDUPE","criterion":"Duplicate submission does not duplicate opportunity","verified":False},
                 {"id":"OWNERSHIP","criterion":"Each accepted source has one accountable owner","verified":False},
                 {"id":"CONTACT","criterion":"No customer email sent without source permission","verified":False},
                 {"id":"RETRY","criterion":"Provider failures are visible; no false sent or booked claims","verified":False}
              ],
              "product_delivered":False,"customer_accepted":False,
              "independent_verification":False,"generated_at":now()
            }
            content=canonical(artifact)
            digest=hashlib.sha256(content.encode()).hexdigest()
            db.execute("""UPDATE commercial_workpackets SET state='ARTIFACT_READY',
                artifact_json=?,artifact_hash=?,last_error_code=NULL,updated_at=?
                WHERE id=? AND state!='ARTIFACT_READY'""",(content,digest,now(),row["id"]))
            advanced+=1
    return {"artifact_ready":advanced,"blocked":blocked}


def artifact_for_verifier(wid: str) -> dict[str, Any]:
    data=readback(wid)
    if data["status"]!="ARTIFACT_READY" or not data["artifact"]:
        raise CommercialWorkPacketError("ARTIFACT_NOT_READY")
    return {"schema":"noetfield.company-os-artifact-verification-input.v1",
            "workpacket_id":wid,
            "source_intake_id":data["source_intake_id"],
            "engine":data["engine"],
            "scope_ref":data["scope_ref"],
            "payment_event_id":data["payment_event_id"],
            "artifact":data["artifact"],
            "artifact_sha256":data["artifact_sha256"],
            "origin":"business-os-core-production",
            "independently_verified":False}
