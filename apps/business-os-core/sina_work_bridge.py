"""Sina Founder OS -> canonical Company OS workforce handoff.

This is an adapter to the EXISTING Company OS tasks, dependencies, role roster,
model router, database and worker. It does not add a competing scheduler or
execution registry, and it never accepts a source request as a Governor permit.
"""
from __future__ import annotations

import hmac
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

SOURCE_URL = "https://sina-founder-os-staging-staging.up.railway.app"
GET_PATH = "/api/v2/organization/company/requests"
ACK_PATH = "/api/v2/organization/company/ack"
TOKEN_ENV = "SINA_ORG_BRIDGE_TOKEN"
LIMIT = 8
MAX_BYTES = 160000
INTERVAL_SECONDS = 40
_LOCK = threading.Lock()
_LAST_TICK = 0.0

# All real tasks are processed by canonical Company OS worker. Independent
# verification remains separate; no Company OS builder self-certification.
ROLE_MAP = {
    "research": "market_intelligence",
    "product": "engineering_operator",
    "growth": "marketing_content",
    "revenue": "sales_qualification",
    "customer": "customer_success",
    "risk": "risk_governance",
    "finance": "roi_analyst",
    "learning": "chief_of_staff",
    "founder": "chief_of_staff",
}
ACTIVE = {"INTERNAL_ACTIVE", "FOUNDER_PROJECT_ACTIVE_NOT_LEGAL_TENANT"}
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,90}$")
SHA_ID = re.compile(r"^[0-9a-f]{32}$")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None

def configured():
    token=os.environ.get(TOKEN_ENV,"")
    return len(token)>=40 and not any(c.isspace() for c in token)

def init(db):
    db.execute("""
      CREATE TABLE IF NOT EXISTS sina_workstream_bindings (
        workstream_id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL UNIQUE,
        company_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        last_reported_state TEXT NOT NULL DEFAULT 'PENDING',
        specialist_retry_count INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )""")
    cols={r["name"] for r in db.execute("PRAGMA table_info(sina_workstream_bindings)")}
    if "specialist_retry_count" not in cols:
        db.execute("ALTER TABLE sina_workstream_bindings ADD COLUMN specialist_retry_count INTEGER NOT NULL DEFAULT 0")
    db.execute("CREATE INDEX IF NOT EXISTS ix_sina_binding_task ON sina_workstream_bindings(task_id)")

def _request(path, method="GET", body=None, fetch=None):
    if not configured():
        raise RuntimeError("sina_organization_bridge_not_configured")
    if path not in (GET_PATH, ACK_PATH):
        raise ValueError("destination outside fixed Sina Organization bridge")
    raw=None if body is None else json.dumps(
        body, sort_keys=True, separators=(",",":")).encode("utf-8")
    req=urllib.request.Request(
        SOURCE_URL+path,method=method,data=raw,
        headers={"Authorization":"Bearer "+os.environ[TOKEN_ENV],
                 "Accept":"application/json","Content-Type":"application/json"})
    opener=fetch or urllib.request.build_opener(NoRedirect())
    with opener.open(req,timeout=8) as resp:
        if resp.status not in (200,201):
            raise RuntimeError("organization_http_status_not_ok")
        data=resp.read(MAX_BYTES+1)
        if len(data)>MAX_BYTES:
            raise ValueError("organization_response_oversized")
        return json.loads(data.decode("utf-8"))

def _validated(item):
    required={
        "schema","request_id","program_id","origin","authority","company_id",
        "project_id","business_outcome","functional_unit","requested_role",
        "task","priority_score","resources","dependencies","acceptance",
        "governance","routing_state","tenant_scope"
    }
    # Founder OS strategic-mission WorkPackets carry these two canonical
    # bounded outcome fields. Previously the exact-key check rejected every
    # strategic request before it could become a Company OS task.
    optional={"strategic_mission_id","success_metric"}
    if not isinstance(item,dict) or not required.issubset(item) or set(item)-required-optional:
        raise ValueError("company_request_schema_invalid")
    if ("strategic_mission_id" in item) != ("success_metric" in item):
        raise ValueError("company_strategic_context_incomplete")
    if "strategic_mission_id" in item:
        if (not isinstance(item["strategic_mission_id"],str)
                or not re.fullmatch(r"M[0-9]{2}-[A-Z0-9-]{3,58}",item["strategic_mission_id"])):
            raise ValueError("company_strategic_mission_id_invalid")
        if (not isinstance(item["success_metric"],str)
                or not re.fullmatch(r"[a-z][a-z0-9_]{7,119}",item["success_metric"])):
            raise ValueError("company_success_metric_invalid")
    if item["schema"]!="sina.company-os.workpacket-request.v1" or \
       item["origin"]!="sina_autonomous_organization" or \
       item["authority"]!="ADVISORY_ONLY_NO_PERMIT" or \
       item["routing_state"]!="NOT_DISPATCHED_COMPANY_OS_OWNS_EXECUTION":
        raise ValueError("company_request_authority_invalid")
    if not SHA_ID.fullmatch(item["request_id"]):
        raise ValueError("company_request_id_invalid")
    if not SAFE_ID.fullmatch(item["project_id"]):
        raise ValueError("company_project_id_invalid")
    scope=item["company_id"] or "founder-portfolio"
    if item["tenant_scope"]!=scope or scope not in ("noetfield-systems-inc","founder-portfolio"):
        raise ValueError("company_tenant_denied")
    role=ROLE_MAP.get(item["functional_unit"])
    if not role or item["functional_unit"]=="verification":
        raise ValueError("independent_verification_not_in_company_workforce")
    if not isinstance(item["task"],str) or not 12<=len(item["task"])<=1300:
        raise ValueError("company_task_invalid")
    if "@" in item["task"] or "api_key" in item["task"].lower() or "bearer " in item["task"].lower():
        raise ValueError("sensitive_task_rejected")
    if (item["resources"]!={"budget_usd":0,"financial_effect_allowed":False}
        or item["governance"].get("governor_decision_required") is not True
        or item["governance"].get("NAC_workpacket_required") is not True
        or item["governance"].get("self_verification_allowed") is not False
        or item["governance"].get("customer_outreach_allowed") is not False
        or item["governance"].get("production_mutation_allowed") is not False
        or item["governance"].get("cross_tenant_access") is not False):
        raise ValueError("company_authority_scope_violation")
    return scope, role

def _resolve_operating_project(scope, canonical_project, item):
    """Use the EXISTING Company operating program for known canonical aliases.

    When an authenticated Founder scope introduces a valid new ACTIVE venture,
    enroll it through Company OS's existing program registration mechanism,
    instead of leaving seven real multi-venture workstreams stranded.
    No new tenant, role registry, scheduler, or Company OS executor.
    """
    import core
    import product_loops
    import founder_signal_transport
    with core.connect() as db:
        found=db.execute(
            "SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
            (scope,canonical_project)).fetchone()
        if found and found["status"] in ACTIVE:
            return canonical_project
        aliases=[source for source,target in
                 founder_signal_transport.CANONICAL_ALIASES.items()
                 if target==canonical_project]
        for alias in aliases:
            previous=db.execute(
                "SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
                (scope,alias)).fetchone()
            if previous and previous["status"] in ACTIVE:
                return alias
    # This is a new operating scope. Its name and legal owner MUST come from
    # the independently fetched, hash-verified canonical Founder SSOT. A
    # signed advisory request alone is not permission to invent a company.
    import founder_portfolio_bridge
    projection = founder_portfolio_bridge.fetch_projection()
    matches = [p for p in projection["projects"]
               if p["project_id"] == canonical_project]
    if len(matches) != 1:
        raise ValueError("sina_workstream_project_not_in_canonical_ssot")
    canonical_owner = matches[0]["company_id"] or "founder-portfolio"
    if canonical_owner != scope:
        raise ValueError("sina_workstream_owner_conflicts_with_ssot")
    priority=int(item["priority_score"])
    product_loops.register({
        "company_id":scope,
        "project_id":canonical_project,
        "name":str(matches[0]["name"])[:100],
        "vertical":"founder-managed-operating-program",
        "objective":("Advance the canonical Founder portfolio project with genuine "
                     "internal product, user, commercial and engineering evidence. "
                     "No external action without separately issued Governor permit."),
        "priority":max(1,min(5,round(priority/20))),
        "max_tasks_per_cycle":6,
    })
    return canonical_project


def receive(item):
    """Claim exactly once into existing Company OS tasks; no parallel state."""
    import core
    scope,role=_validated(item)
    wid=item["request_id"]
    operational_project=_resolve_operating_project(scope,item["project_id"],item)
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        init(db)
        existing=db.execute(
            "SELECT task_id,company_id,project_id FROM sina_workstream_bindings WHERE workstream_id=?",
            (wid,)).fetchone()
        if existing:
            if existing["company_id"]!=scope or existing["project_id"]!=item["project_id"]:
                raise ValueError("reused_workstream_mismatched_tenant")
            return {"state":"EXISTING","task_id":existing["task_id"],
                    "company_id":scope,"workstream_id":wid}
        program=db.execute(
            "SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
            (scope,operational_project)).fetchone()
        if not program or program["status"] not in ACTIVE:
            return {"state":"PROJECT_NOT_COMMISSIONED","company_id":scope,
                    "workstream_id":wid}
        # Product scope is never inferred from a brand; workstream specifies it.
        title=(item["functional_unit"].replace("_"," ").title()+": "+
               item["project_id"])[:140]
        objective=(
            "Founder OS organizational WorkPacket *request* "+wid+
            ". Source program "+item["program_id"]+
            ". "+item["task"]+
            ((". Strategic mission "+item["strategic_mission_id"]+
              "; evidence-based success metric "+item["success_metric"]+".")
             if "strategic_mission_id" in item else "")+
            ". Produce a concrete internal artifact and a next-action with evidence. "+
            "No external outreach, code mutation, finance movement, legal commitments "+
            "or production deployment without the separate Governor permit."
        )[:1800]
        task_id=core.add_task(
            db,None,None,"portfolio",role,title,objective,
            "Draft evidence-backed actionable work using existing Company OS workflow. "+
            "Independent verification and governance remain external.")
        db.execute(
            "UPDATE tasks SET company_id=?,project_id=?,observation_id=NULL WHERE id=?",
            (scope,operational_project,task_id))
        now=datetime.now(timezone.utc).isoformat()
        db.execute("""
            INSERT INTO sina_workstream_bindings
            (workstream_id,task_id,company_id,project_id,created_at,updated_at)
            VALUES (?,?,?,?,?,?)""",
            (wid,task_id,scope,item["project_id"],now,now))
        return {"state":"CREATED_CANONICAL_TASK","task_id":task_id,
                "company_id":scope,"operational_project_id":operational_project,
                "founder_canonical_project_id":item["project_id"],
                "workstream_id":wid}

def _ack(workstream_id,task_id,scope,status,fetch=None):
    data={"workstream_id":workstream_id,"task_id":task_id,
          "company_id":scope,"status":status}
    response=_request(ACK_PATH,"POST",data,fetch)
    if response.get("company_os_task_ref")!="company-os:"+task_id:
        raise ValueError("company_ack_ref_mismatch")
    return response

def sync_existing(fetch=None):
    """Report actual canonical tasks, not fake completions, back to Founder."""
    import core
    sent=0
    with core.connect() as db:
        init(db)
        rows=db.execute("""
          SELECT b.*,t.status FROM sina_workstream_bindings b
          JOIN tasks t ON t.id=b.task_id
          WHERE b.last_reported_state NOT IN ('DRAFTED','BLOCKED')
          ORDER BY b.created_at LIMIT 20""").fetchall()
    for r in rows:
        if r["status"] in ("failed","blocked"):
            state="BLOCKED"
        elif r["status"] in ("drafted","approved"):
            state="DRAFTED"  # still NOT independently verified
        else:
            state="ACCEPTED"
        if r["last_reported_state"]==state:
            continue
        try:
            _ack(r["workstream_id"],r["task_id"],r["company_id"],state,fetch)
        except (ValueError,OSError,RuntimeError,urllib.error.URLError):
            continue
        with core.connect() as db:
            db.execute(
                "UPDATE sina_workstream_bindings SET last_reported_state=?,updated_at=? WHERE workstream_id=?",
                (state,datetime.now(timezone.utc).isoformat(),r["workstream_id"]))
        sent+=1
    return sent

def cycle(fetch=None):
    """Piggyback existing Company OS core.daily_tick() and worker; no new loop."""
    if not configured():
        return {"state":"NOT_CONFIGURED","task_creations":0}
    result=_request(GET_PATH,fetch=fetch)
    if result.get("schema")!="sina.company-os.work-intake.v1":
        raise ValueError("work_intake_invalid")
    items=result.get("items")
    if not isinstance(items,list) or len(items)>20:
        raise ValueError("work_intake_size_invalid")
    created=0; unmapped=0
    for item in items:
        try:
            response=receive(item)
            if response["state"]=="PROJECT_NOT_COMMISSIONED":
                unmapped+=1
            elif response["state"]=="CREATED_CANONICAL_TASK":
                created+=1
        except (ValueError,TypeError) as exc:
            print("SINA_ORG_WORK_REJECTED "+type(exc).__name__,flush=True)
    acknowledged=sync_existing(fetch)
    retry_scheduled=retry_degraded()
    return {"state":"OBSERVED","canonical_tasks_created":created,
            "awaiting_product_registration":unmapped,
            "execution_states_reported":acknowledged,
            "specialist_retry_scheduled":retry_scheduled,
            "external_actions_performed":False}

def tick(fetch=None,clock=None,force=False):
    global _LAST_TICK
    if not configured():return {"state":"NOT_CONFIGURED"}
    now=(clock or time.monotonic)()
    with _LOCK:
        if not force and now-_LAST_TICK<INTERVAL_SECONDS:
            return {"state":"NOT_DUE"}
        _LAST_TICK=now
    try:
        return cycle(fetch)
    except (ValueError,OSError,RuntimeError,urllib.error.URLError) as exc:
        return {"state":"DEGRADED","error_type":type(exc).__name__}



# Model specialization uses the existing Agent Fabric provider and Company OS
# task identity. It never becomes a second Company OS task engine.
SPECIALIST_ENDPOINT = "https://noetfield-agent-fabric-staging-staging.up.railway.app/api/internal/v1/organization/specialist"
SPECIALIST_TOKEN_ENV = "SINA_ORG_SPECIALIST_TOKEN"
SPECIALIST_MAX_BYTES = 22000
EMAIL_LIKE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
CREDENTIAL_LIKE = re.compile(r"(?i)(api[_-]?key|bearer\s+[A-Za-z0-9_-]{16}|sk-[A-Za-z0-9_-]{16})")

def specialist_configured():
    return len(os.environ.get(SPECIALIST_TOKEN_ENV, "")) >= 40

def is_sina_task(task_id: str) -> bool:
    import core
    if not isinstance(task_id, str) or not re.fullmatch(r"task_[a-f0-9]{16}", task_id):
        return False
    with core.connect() as db:
        result=db.execute(
            "SELECT 1 FROM sina_workstream_bindings WHERE task_id=?", (task_id,)
        ).fetchone()
    return result is not None

def specialist_proposal(task: dict, *, fetch=None) -> dict:
    """Return a useful model-produced internal artifact for a *real* Company task."""
    if not specialist_configured():
        raise RuntimeError("organization_specialist_not_configured")
    if not is_sina_task(task.get("id")):
        raise ValueError("non_sina_work_task_not_authorized")
    for key in ("company_id","project_id","role","objective"):
        if not isinstance(task.get(key),str):
            raise ValueError("specialist_task_scope_missing")
    objective=task["objective"].strip()
    if EMAIL_LIKE.search(objective) or CREDENTIAL_LIKE.search(objective):
        raise ValueError("sensitive_company_work_task_rejected")
    body={
        "task_id":task["id"],
        "company_id":task["company_id"],
        "project_id":task["project_id"],
        "role":task["role"],
        "objective":objective[:1800],
        "max_cost_usd":0.015,
    }
    raw=json.dumps(body,separators=(",",":"),sort_keys=True).encode("utf-8")
    request=urllib.request.Request(SPECIALIST_ENDPOINT,method="POST",data=raw,
        headers={
            "Authorization":"Bearer "+os.environ[SPECIALIST_TOKEN_ENV],
            "Content-Type":"application/json","Accept":"application/json",
        })
    opener=fetch or urllib.request.build_opener(NoRedirect())
    with opener.open(request,timeout=43) as response:
        if response.status!=200:
            raise RuntimeError("specialist_model_http_not_ok")
        data=response.read(SPECIALIST_MAX_BYTES+1)
        if len(data)>SPECIALIST_MAX_BYTES:
            raise ValueError("specialist_model_result_too_large")
        payload=json.loads(data.decode("utf-8"))
    if (not isinstance(payload,dict)
        or payload.get("schema")!="sina.organization.specialist-draft.v1"
        or payload.get("task_id")!=task["id"]
        or payload.get("company_id")!=task["company_id"]
        or payload.get("project_id")!=task["project_id"]
        or payload.get("role")!=task["role"]
        or payload.get("authority")!="ADVISORY_INTERNAL_ONLY"
        or payload.get("external_actions_executed") is not False
        or not isinstance(payload.get("result"),dict)
        or payload["result"].get("external_action")!="NOT_EXECUTED"):
        raise ValueError("specialist_result_not_attested_to_task")
    return payload


def retry_degraded(limit=2):
    """One automatic recovery per genuine Sina-origin Company OS task.

    Uses the original canonical task, the original role and the existing
    Company OS worker; no additional scheduler, agents, queue or arbitrary
    external mutation. Failed model results remain internal-only drafts.
    """
    if not specialist_configured():return 0
    import core
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        init(db)
        rows=db.execute("""
            SELECT b.workstream_id,b.task_id FROM sina_workstream_bindings b
            JOIN tasks t ON t.id=b.task_id
            WHERE b.specialist_retry_count=0
              AND t.status='drafted'
              AND datetime(t.updated_at) < datetime('now','-2 minutes')
              AND EXISTS (SELECT 1 FROM runs r WHERE r.task_id=t.id
                          AND r.provider='specialist_degraded')
            ORDER BY t.updated_at LIMIT ?""",(max(1,min(int(limit),3)),)).fetchall()
        for row in rows:
            db.execute("""UPDATE sina_workstream_bindings
                          SET specialist_retry_count=1,updated_at=?
                          WHERE workstream_id=? AND specialist_retry_count=0""",
                       (datetime.now(timezone.utc).isoformat(),row["workstream_id"]))
            db.execute("""UPDATE tasks SET status='queued',updated_at=?
                          WHERE id=? AND status='drafted'""",
                       (datetime.now(timezone.utc).isoformat(),row["task_id"]))
    return len(rows)


# Deliver actual Company OS work artifacts to their Founder missions. This is a
# scoped read projection over existing canonical tasks, not another result store.
def results_for_founder(task_ids: list[str]):
    """Only internally prepared, Sina-originated work; no contact, raw source
    text, credentials, customer PII, or invented independent verification."""
    if not isinstance(task_ids,list) or len(task_ids)>20 or len(set(task_ids))!=len(task_ids):
        raise ValueError("invalid_organization_task_ids")
    if any(not isinstance(t,str) or not re.fullmatch(r"task_[0-9a-f]{16}",t) for t in task_ids):
        raise ValueError("organization_task_ids_must_be_canonical")
    import core
    def safe(value, size=350):
        if not isinstance(value,str):return ""
        value=value[:size*3]
        value=re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}","[email redacted]",value)
        value=re.sub(r"(?i)(bearer\s+|api[_-]?key\s*[=:]\s*|sk-)[A-Za-z0-9_.-]{16,}","[credential redacted]",value)
        value=re.sub(r"[\r\n\t]+"," ",value)
        return value[:size]
    out=[]
    if not task_ids:
        return {"schema":"sina.company-os.mission-artifacts.v1","items":[],"verified_receipts":0}
    with core.connect() as db:
        init(db)
        placeholders=",".join("?" for _ in task_ids)
        rows=db.execute(f"""
          SELECT t.id,t.role,t.company_id,t.project_id,t.status,t.result,t.updated_at
          FROM tasks t JOIN sina_workstream_bindings b ON b.task_id=t.id
          WHERE t.id IN ({placeholders}) ORDER BY t.updated_at DESC LIMIT 20
        """,task_ids).fetchall()
    for r in rows:
        try:
            envelope=json.loads(r["result"] or "{}")
            if not isinstance(envelope,dict):envelope={}
        except (ValueError,TypeError):
            envelope={}
        rec=envelope.get("recommendation")
        if not isinstance(rec,dict):rec={}
        draft=rec.get("draft_artifact")
        if not isinstance(draft,dict):draft={}
        deliverables=draft.get("deliverables",[])
        if not isinstance(deliverables,list):deliverables=[]
        deliverables=[safe(x,530) for x in deliverables if isinstance(x,str)][:6]
        # Only output artifacts, never raw task inputs or potentially sensitive
        # internal customer records from other Company OS workstreams.
        provider=envelope.get("provider","unknown")
        out.append({
          "task_id":r["id"],"project_id":r["project_id"],"company_id":r["company_id"],
          "role":r["role"],"state":r["status"],
          "updated_at":r["updated_at"],
          "provider":safe(provider,60),
          "assessment":safe(rec.get("assessment"),700),
          "deliverables":deliverables,
          "next_best_action":safe(rec.get("next_best_action"),420),
          "success_metric":safe(rec.get("success_metric"),270),
          "result_class":"INTERNAL_DRAFT_NOT_INDEPENDENTLY_VERIFIED",
          "external_action_executed":False,
          "independent_receipt":None,
        })
    return {"schema":"sina.company-os.mission-artifacts.v1","items":out,
            "verified_receipts":0,"truth_boundary":"COMPANY_OS_INTERNAL_WORK_ONLY",
            "requested":len(task_ids),"found":len(out)}
