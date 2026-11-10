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
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )""")
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
    if not isinstance(item,dict) or set(item)!=required:
        raise ValueError("company_request_schema_invalid")
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

def _founder_project_record(projection, project_id, scope):
    """Use the authenticated Founder SSOT, never a Company-invented entity."""
    if not isinstance(projection, dict) or not isinstance(projection.get("projects"), list):
        return None
    items = [p for p in projection["projects"] if p.get("project_id") == project_id]
    if len(items) != 1:
        return None
    row = items[0]
    if (row.get("company_id") or "founder-portfolio") != scope:
        raise ValueError("sina_canonical_owner_scope_mismatch")
    return row


def receive(item, projection=None):
    """One approved advisory request -> one canonical Company task.

    Existing operating programs are reused. Missing scopes are admitted to
    analysis-only Company OS programs *only* when independently read from the
    canonical authenticated Founder portfolio. No company/legal tenant creation,
    external execution capability, new queue, or product-live assertion.
    """
    import core
    scope, role = _validated(item)
    wid = item["request_id"]
    canonical_project = item["project_id"]
    canonical = _founder_project_record(projection, canonical_project, scope)
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        init(db)
        original = db.execute(
            "SELECT task_id,company_id,project_id FROM sina_workstream_bindings WHERE workstream_id=?",
            (wid,),
        ).fetchone()
        # A previously accepted binding survives an upstream outage/restart.
        # Its canonical project is cryptographically tied to the stable
        # Founder-issued WorkRequest id; never recreate its task.
        if original:
            if original["company_id"] != scope:
                raise ValueError("reused_workstream_mismatched_tenant")
            if original["project_id"] != canonical_project:
                from founder_signal_transport import CANONICAL_ALIASES
                if CANONICAL_ALIASES.get(original["project_id"]) != canonical_project:
                    raise ValueError("reused_workstream_mismatched_project")
            return {"state": "EXISTING", "task_id": original["task_id"],
                    "company_id": scope, "workstream_id": wid}

        operating_id = canonical_project
        program = db.execute(
            "SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
            (scope, operating_id),
        ).fetchone()
        if (not program or program["status"] not in ACTIVE) and canonical is not None:
            # Three explicit legacy *product display aliases*, validated
            # against live Founder SSOT on every first admission. Prefer the
            # already-running Company program over a duplicate operating row.
            from founder_signal_transport import CANONICAL_ALIASES
            aliases = [local for local, target in CANONICAL_ALIASES.items()
                       if target == canonical_project]
            for alias in aliases:
                found = db.execute(
                    "SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
                    (scope, alias),
                ).fetchone()
                if found and found["status"] in ACTIVE:
                    operating_id, program = alias, found
                    break

        if not program or program["status"] not in ACTIVE:
            if canonical is None:
                return {"state": "PROJECT_NOT_COMMISSIONED", "company_id": scope,
                        "workstream_id": wid}
            # Advisory-only registration is a Company work SCOPE, not a
            # customer, new legal company, active product or marketing launch.
            # No health URL, baseline fanout, credentials or paid claims.
            when = datetime.now(timezone.utc).isoformat()
            name = str(canonical.get("name") or canonical_project)[:100]
            if len(name) < 3 or "@" in name:
                name = canonical_project
            db.execute(
                """INSERT OR IGNORE INTO product_programs
                   (company_id,project_id,name,vertical,objective,status,priority,
                    health_url,max_tasks_per_cycle,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (scope, canonical_project, name, "founder-advisory",
                 "Complete bounded internal evidence-based analysis for an existing "
                 "Founder portfolio project; no external effects without Governor permit.",
                 "SINA_ADVISORY_INTAKE_ONLY", 1, None, 2, when, when),
            )
            operating_id = canonical_project
            program = db.execute(
                "SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
                (scope, operating_id),
            ).fetchone()
        if not program or program["status"] not in (ACTIVE | {"SINA_ADVISORY_INTAKE_ONLY"}):
            return {"state": "PROJECT_NOT_COMMISSIONED", "company_id": scope,
                    "workstream_id": wid}
        title = (item["functional_unit"].replace("_", " ").title() + ": " +
                 canonical_project)[:140]
        objective = (
            "Founder OS organizational WorkPacket *request* " + wid +
            ". Source program " + item["program_id"] +
            ". " + item["task"] +
            ". Produce a concrete internal artifact and a next-action with evidence. "
            "No external outreach, code mutation, finance movement, legal commitments "
            "or production deployment without the separate Governor permit."
        )[:1800]
        task_id = core.add_task(
            db, None, None, "portfolio", role, title, objective,
            "Draft evidence-backed actionable work using existing Company OS workflow. "
            "Independent verification and governance remain external.",
        )
        db.execute(
            "UPDATE tasks SET company_id=?,project_id=?,observation_id=NULL WHERE id=?",
            (scope, operating_id, task_id),
        )
        when = datetime.now(timezone.utc).isoformat()
        db.execute(
            """INSERT INTO sina_workstream_bindings
               (workstream_id,task_id,company_id,project_id,created_at,updated_at)
               VALUES (?,?,?,?,?,?)""",
            (wid, task_id, scope, operating_id, when, when),
        )
        return {"state": "CREATED_CANONICAL_TASK", "task_id": task_id,
                "company_id": scope, "workstream_id": wid}


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
    # The portfolio read endpoint already validates the canonical SSOT SHA.
    # One bounded read supplies scope evidence for the entire batch.
    import founder_portfolio_bridge
    try:
        projection = founder_portfolio_bridge.fetch_projection()
    except (ValueError, RuntimeError, OSError, urllib.error.URLError):
        projection = None
    created=0; unmapped=0
    for item in items:
        try:
            response=receive(item, projection=projection)
            if response["state"]=="PROJECT_NOT_COMMISSIONED":
                unmapped+=1
            elif response["state"]=="CREATED_CANONICAL_TASK":
                created+=1
        except (ValueError,TypeError) as exc:
            print("SINA_ORG_WORK_REJECTED "+type(exc).__name__,flush=True)
    acknowledged=sync_existing(fetch)
    return {"state":"OBSERVED","canonical_tasks_created":created,
            "awaiting_product_registration":unmapped,
            "execution_states_reported":acknowledged,
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

