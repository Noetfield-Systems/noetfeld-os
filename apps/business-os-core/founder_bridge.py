"""Resident Sina Founder OS ↔ Company OS execution bridge.

Runs INSIDE the existing Business OS event worker, not a second scheduler.
Pulls only typed, advisory/zero-spend requests from the Founder OS
organization control plane and places them in core.tasks (the canonical queue).
Acknowledges on persisted admission and on specialist draft/block transitions.
Also forwards genuine aggregate commercial-intake signals to the Founder OS.

Neither a specialist draft nor an upstream acknowledgement is an external
execution, Governor permit, independent verification, sale or revenue event.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

import core

BASE = "https://sina-founder-os-staging-staging.up.railway.app"
SCHEMA = "sina.company-os.workpacket-request.v1"
ROLE_MAP = {
    "research":"market_intelligence",
    "product":"product_strategy",
    "growth":"marketing_editorial",
    "revenue":"sales_qualification",
    "customer":"customer_success",
    "risk":"risk_governance",
    "finance":"roi_analyst",
    "verification":None,  # Cannot self-certify an independent verifier.
    "learning":"market_intelligence",
    "founder":"chief_of_staff",
}
ALLOWED_COMPANIES = {"noetfield-systems-inc", "founder-portfolio"}
ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
PROJECT_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,90}$")
EVENT_PATTERN = re.compile(r"^evt_[0-9a-f]{16}$")
ALLOWED_STATES = {"ACCEPTED", "DRAFTED", "BLOCKED"}
REQUIRED_GOVERNANCE = (
    "governor_decision_required", "NAC_workpacket_required",
    "independent_verifier_required", "a4_human_reserved",
)

class UnsafeRequest(ValueError):
    pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None

def _json(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)

def _digest(value):
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()

def configured():
    return bool(
        os.environ.get("SINA_ORG_BRIDGE_ENABLED", "").lower() == "true"
        and 40 <= len(os.environ.get("SINA_ORG_CONTINUOUS_TOKEN", "")) <= 256
    )

def _token():
    return os.environ["SINA_ORG_CONTINUOUS_TOKEN"]

def _request(method, path, payload=None):
    """Only fixed same-host HTTPS URLs. No redirects, browser headers, or logs of tokens."""
    if not path.startswith("/api/v2/organization/company/"):
        raise ValueError("invalid_path")
    body = None if payload is None else _json(payload).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + _token(),
        "Accept": "application/json",
        "User-Agent": "Noetfield-Company-OS-Continuous/1",
        "Content-Type": "application/json",
    }
    req = Request(BASE + path, data=body, headers=headers, method=method)
    with build_opener(NoRedirect()).open(req, timeout=7) as response:
        if response.status not in (200,201):
            raise ValueError("upstream_non_success")
        raw = response.read(96 * 1024 + 1)
        if len(raw) > 96 * 1024:
            raise ValueError("upstream_oversize")
        parsed = json.loads(raw)
        if not isinstance(parsed,dict):
            raise ValueError("upstream_invalid_json")
        return parsed

def init():
    with core.connect() as db:
        # A transport binding ledger, not another job queue or source of work truth.
        db.executescript("""
            CREATE TABLE IF NOT EXISTS founder_org_bindings(
                request_id TEXT PRIMARY KEY,
                payload_digest TEXT NOT NULL,
                tenant_scope TEXT NOT NULL,
                project_id TEXT NOT NULL,
                canonical_task_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                last_acked TEXT NOT NULL DEFAULT '',
                last_ack_at TEXT
            );
            CREATE TABLE IF NOT EXISTS founder_org_signals(
                source_event_id TEXT PRIMARY KEY,
                sent_at TEXT NOT NULL
            );
        """)

def validate_request(item, project_allowlist):
    if not isinstance(item,dict):
        raise UnsafeRequest("invalid_body")
    if item.get("schema")!=SCHEMA or item.get("origin")!="sina_autonomous_organization":
        raise UnsafeRequest("invalid_schema")
    if item.get("authority")!="ADVISORY_ONLY_NO_PERMIT":
        raise UnsafeRequest("authority_invalid")
    if item.get("routing_state")!="NOT_DISPATCHED_COMPANY_OS_OWNS_EXECUTION":
        raise UnsafeRequest("routing_state_invalid")
    wid=item.get("request_id")
    tenant=item.get("tenant_scope")
    project=item.get("project_id")
    if not isinstance(wid,str) or not ID_PATTERN.fullmatch(wid):
        raise UnsafeRequest("request_id_invalid")
    if tenant not in ALLOWED_COMPANIES:
        raise UnsafeRequest("tenant_not_allowed")
    if not isinstance(project,str) or not PROJECT_PATTERN.fullmatch(project) or project not in project_allowlist:
        raise UnsafeRequest("project_not_allowed")
    if (tenant=="founder-portfolio" and item.get("company_id") is not None) or (
        tenant=="noetfield-systems-inc" and item.get("company_id")!=tenant
    ):
        raise UnsafeRequest("company_tenant_mismatch")
    unit=item.get("functional_unit")
    role=ROLE_MAP.get(unit)
    if not role or role not in {x[0] for x in core.AGENTS}:
        raise UnsafeRequest("role_not_commissioned")
    if item.get("requested_role") is None:
        raise UnsafeRequest("missing_role_intent")
    task=item.get("task")
    if not isinstance(task,str) or not 12<=len(task)<=2500:
        raise UnsafeRequest("task_invalid")
    if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",task):
        raise UnsafeRequest("task_contains_customer_identifier")
    priority=item.get("priority_score")
    if type(priority) is not int or not 0<=priority<=100:
        raise UnsafeRequest("priority_invalid")
    resources=item.get("resources")
    if not isinstance(resources,dict) or resources.get("budget_usd")!=0 or resources.get("financial_effect_allowed") is not False:
        raise UnsafeRequest("resource_scope_invalid")
    gov=item.get("governance")
    if not isinstance(gov,dict) or not all(gov.get(k) is True for k in REQUIRED_GOVERNANCE):
        raise UnsafeRequest("governance_missing")
    if any(gov.get(k) is not False for k in (
        "self_verification_allowed","customer_outreach_allowed",
        "production_mutation_allowed","cross_tenant_access"
    )):
        raise UnsafeRequest("unsafe_external_effect")
    return wid,tenant,project,unit,role,task,priority

def admit(item,project_allowlist):
    """Atomic idempotency across process restarts and remote callback failures."""
    wid,tenant,project,unit,role,task,priority=validate_request(item,project_allowlist)
    digest=_digest(item)
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        previous=db.execute("SELECT payload_digest,canonical_task_id FROM founder_org_bindings WHERE request_id=?",(wid,)).fetchone()
        if previous:
            if previous["payload_digest"]!=digest:
                db.rollback()
                raise UnsafeRequest("idempotency_payload_conflict")
            return previous["canonical_task_id"],False
        # Directly to the existing Company OS tasks table; unlike a separate
        # dispatcher, the canonical department workers claim these immediately.
        title=core.clean("Sina "+unit+" / "+project,100)
        action=("Prepare an internal evidence-linked specialist recommendation only. "
                "No outreach, external effect, spend, deploy or verification claim. "
                "Escalate any required Governor permit to Founder.")
        tid=core.add_task(db,None,None,"noetfield",role,title,core.clean(task,1800),action)
        db.execute("UPDATE tasks SET priority_rank=? WHERE id=?", (max(10,100-priority),tid))
        db.execute("""INSERT INTO founder_org_bindings
          (request_id,payload_digest,tenant_scope,project_id,canonical_task_id,created_at)
          VALUES (?,?,?,?,?,?)""",(wid,digest,tenant,project,tid,core.now()))
        db.commit()
        return tid,True

def _allowed_projects():
    raw=os.environ.get("SINA_ORG_BRIDGE_PROJECT_IDS","")
    projects={x.strip() for x in raw.split(",") if x.strip()}
    if not projects or len(projects)>100 or any(not PROJECT_PATTERN.fullmatch(x) for x in projects):
        raise ValueError("invalid_project_allowlist")
    return projects

def _due():
    interval=max(30,min(900,int(os.environ.get("SINA_ORG_BRIDGE_INTERVAL_SECONDS","60"))))
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT value FROM state WHERE key='founder_bridge_last_attempt'").fetchone()
        now=time.time()
        if row and now-float(row["value"])<interval:
            db.rollback()
            return False
        db.execute("""INSERT INTO state(key,value) VALUES('founder_bridge_last_attempt',?)
          ON CONFLICT(key) DO UPDATE SET value=excluded.value""",(str(now),))
        db.commit()
        return True

def reconcile(limit=40):
    rows=[]
    with core.connect() as db:
        rows=db.execute("""SELECT b.request_id,b.tenant_scope,b.project_id,b.canonical_task_id,
                   b.last_acked,t.status
            FROM founder_org_bindings b JOIN tasks t ON t.id=b.canonical_task_id
            WHERE b.last_acked != CASE
              WHEN t.status IN ('drafted','approved') THEN 'DRAFTED'
              WHEN t.status IN ('blocked','failed') THEN 'BLOCKED'
              ELSE 'ACCEPTED' END
            ORDER BY b.created_at LIMIT ?""",(limit,)).fetchall()
    published=0
    for row in rows:
        status={"queued":"ACCEPTED","running":"ACCEPTED","drafted":"DRAFTED",
                "approved":"DRAFTED","blocked":"BLOCKED","failed":"BLOCKED"}.get(row["status"],"ACCEPTED")
        if status==row["last_acked"]:
            continue
        result=_request("POST","/api/v2/organization/company/ack",{
            "workstream_id":row["request_id"],
            "task_id":row["canonical_task_id"],
            "company_id":row["tenant_scope"],
            "status":status,
        })
        if result.get("workstream_id")!=row["request_id"]:
            raise ValueError("ack_response_mismatch")
        with core.connect() as db:
            db.execute("""UPDATE founder_org_bindings SET last_acked=?,last_ack_at=?
                WHERE request_id=? AND canonical_task_id=?""",
                (status,core.now(),row["request_id"],row["canonical_task_id"]))
        published+=1
    return published

def publish_commercial_signals(limit=8):
    """Only genuine processed public intakes, no PII, simulated buyer or inferred sales."""
    project="noetfield-company-os-commercial-product"
    if project not in _allowed_projects():
        return 0
    stamp=(datetime.now(timezone.utc)-timedelta(days=1)).isoformat()
    with core.connect() as db:
        rows=db.execute("""SELECT e.id,e.created_at FROM events e
          LEFT JOIN founder_org_signals s ON s.source_event_id=e.id
          WHERE e.event_type='intake.received' AND e.source='public_web'
          AND e.status='processed' AND e.created_at>=? AND s.source_event_id IS NULL
          ORDER BY e.created_at LIMIT ?""",(stamp,limit)).fetchall()
    delivered=0
    for row in rows:
        if not EVENT_PATTERN.fullmatch(row["id"]):
            continue
        payload={
            "source_id":"companyos",
            "source_event_id":"intake:"+row["id"],
            "event_type":"commercial_intake",
            "company_id":"noetfield-systems-inc",
            "project_id":project,
            "observed_at":row["created_at"],
            "summary":"A genuine public Company OS commercial inquiry was processed by the internal specialist intake queue.",
            "confidence":0.8,"impact":2,
        }
        result=_request("POST","/api/v2/organization/company/signal",payload)
        if not isinstance(result.get("signal_id"),str):
            raise ValueError("signal_receipt_invalid")
        with core.connect() as db:
            db.execute("INSERT OR IGNORE INTO founder_org_signals VALUES(?,?)",(row["id"],core.now()))
        delivered+=1
    return delivered

def tick():
    if not configured():
        return {"state":"NOT_CONFIGURED"}
    init()
    if not _due():
        return {"state":"NEXT_POLL_NOT_DUE"}
    allowed=_allowed_projects()
    # Still reconcile drafts and retry missing ACKs even if there are no new requests.
    acknowledgements=reconcile()
    result=_request("GET","/api/v2/organization/company/requests")
    if result.get("schema")!="sina.company-os.work-intake.v1" or not isinstance(result.get("items"),list):
        raise ValueError("founder_intake_contract_invalid")
    accepted=0
    rejected=0
    for item in result["items"][:12]:
        try:
            _,created=admit(item,allowed)
            accepted+=int(created)
        except UnsafeRequest:
            rejected+=1
    acknowledgements+=reconcile()
    signals=publish_commercial_signals()
    with core.connect() as db:
        db.execute("""INSERT INTO state(key,value) VALUES('founder_bridge_last_success',?)
          ON CONFLICT(key) DO UPDATE SET value=excluded.value""",(core.now(),))
        db.execute("""INSERT INTO state(key,value) VALUES('founder_bridge_last_error_type','')
          ON CONFLICT(key) DO UPDATE SET value=excluded.value""")
    return {"state":"LIVE","accepted":accepted,"rejected":rejected,
            "acknowledged":acknowledgements,"source_signals":signals,
            "external_effects":0,"independent_receipts":0}


def record_failure(exc):
    """Persist a safe diagnostic category; never raw network exception or token."""
    if not configured():
        return
    kind=type(exc).__name__[:64]
    with core.connect() as db:
        db.execute("""INSERT INTO state(key,value) VALUES('founder_bridge_last_error_type',?)
          ON CONFLICT(key) DO UPDATE SET value=excluded.value""",(kind,))


def health():
    """Aggregate truth only; use with the existing read-only deep health API."""
    if not configured():
        return {"configured":False,"connection":"NOT_CONFIGURED",
                "work_packets_claimed":0,"pending_ack":0,
                "verified_outcomes":0,"external_effects":0}
    with core.connect() as db:
        rows={r["key"]:r["value"] for r in db.execute(
            "SELECT key,value FROM state WHERE key LIKE 'founder_bridge_%'")}
        stats=db.execute("""SELECT
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN b.last_acked='' THEN 1 ELSE 0 END),0) AS pending_ack,
            COALESCE(SUM(CASE WHEN t.status IN ('drafted','approved') THEN 1 ELSE 0 END),0) AS drafts,
            COALESCE(SUM(CASE WHEN t.status IN ('failed','blocked') THEN 1 ELSE 0 END),0) AS blocked
          FROM founder_org_bindings b JOIN tasks t ON t.id=b.canonical_task_id""").fetchone()
        source_count=db.execute("SELECT COUNT(*) FROM founder_org_signals").fetchone()[0]
    last_success=rows.get("founder_bridge_last_success")
    freshness=None
    if last_success:
        try:
            freshness=max(0,int((datetime.now(timezone.utc)-
                datetime.fromisoformat(last_success.replace("Z","+00:00"))).total_seconds()))
        except ValueError:
            freshness=None
    error_type=rows.get("founder_bridge_last_error_type") or None
    connection=("LIVE" if freshness is not None and freshness<=180 and not error_type
                else "DEGRADED" if error_type or freshness is not None else "AWAITING_FIRST_CYCLE")
    if freshness is not None and freshness>180:
        connection="STALE"
    return {
        "configured":True,"connection":connection,
        "last_success":last_success,"seconds_since_success":freshness,
        "last_error_type":error_type,
        "work_packets_claimed":int(stats["total"]),
        "internal_drafts":int(stats["drafts"]),
        "blocked_tasks":int(stats["blocked"]),
        "pending_ack":int(stats["pending_ack"]),
        "commercial_signals_sent":source_count,
        "verified_outcomes":0,"external_effects":0,
    }
