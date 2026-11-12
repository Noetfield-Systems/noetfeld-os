"""One deterministic Sina question -> product-local Company OS continuation.

Uses EXISTING pinned Sina service identity and EXISTING Company OS
product_observations -> events -> tasks -> workers. Does not start another
scheduler, create a global agent registry or let the portfolio head implement
product features. Decision responses are advisory and not Governor permits.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
import urllib.error

QUESTION_SCHEMA="sina.agent-question.v1"
DECISION_SCHEMA="sina.agent-decision.v1"
COMPANY_DECISION_SCHEMA="noetfield.company-os.local-decision-continuation.v1"
DECISION_PATH="/api/v2/agent/decision"
LOCAL_STATES={"PROCEED_IN_LOCAL_COMPANY_OS","CHECK_EVIDENCE_AND_CONTINUE",
              "CLARIFY_FROM_EVIDENCE_NOT_FOUNDER","RESEARCH_IN_LOCAL_COMPANY_OS"}
NO_MUTATION={"HONOR_FOUNDER_PAUSE","FOUNDER_RATIFICATION_REQUIRED",
             "GOVERNOR_AND_OWNER_AUTHORIZATION_REQUIRED",
             "RECONCILE_CANONICAL_VENTURE_STATE"}
SAFE_ID=re.compile(r"^[a-z][a-z0-9-]{2,119}$")
SAFE_TASK_ID=re.compile(r"^task_[a-f0-9]{16}$")
DECISION_ID=re.compile(r"^[a-f0-9]{32}$")
REQUEST_KEYS={"schema","project_id","company_id","agent_role","intent",
              "proposed_action","question","options","evidence_refs","request_id"}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def init(db):
    db.execute("""CREATE TABLE IF NOT EXISTS venture_company_os_decisions (
      company_id TEXT NOT NULL,project_id TEXT NOT NULL,
      decision_ref TEXT NOT NULL,response_hash TEXT NOT NULL,
      disposition TEXT NOT NULL,task_id TEXT,
      event_id TEXT,owner TEXT NOT NULL DEFAULT 'PROJECT_LOCAL_COMPANY_OS',
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY(company_id,project_id,decision_ref))""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_local_decision_project ON venture_company_os_decisions(company_id,project_id,updated_at DESC)")
    db.execute("""CREATE TABLE IF NOT EXISTS venture_company_os_decision_feedback (
      feedback_id TEXT PRIMARY KEY,decision_ref TEXT NOT NULL,
      company_id TEXT NOT NULL,project_id TEXT NOT NULL,
      status TEXT NOT NULL,source_ref TEXT NOT NULL,
      delivery_state TEXT NOT NULL DEFAULT 'PENDING',
      attempts INTEGER NOT NULL DEFAULT 0,delivered_at TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_company_decision_feedback_outbox ON venture_company_os_decision_feedback(delivery_state,created_at)")

def _canonical_project(db,scope,local_project):
    """Alias must have an existing, scoped Founder mandate, never guessed."""
    found=db.execute("""SELECT founder_project_id FROM venture_company_os_mandates
       WHERE company_id=? AND project_id=? ORDER BY updated_at DESC LIMIT 1""",
       (scope,local_project)).fetchone()
    return found["founder_project_id"] if found else local_project

def _assert_local(scope,project):
    import core
    import venture_company_os
    if (not isinstance(scope,str) or not SAFE_ID.fullmatch(scope) or
        not isinstance(project,str) or not SAFE_ID.fullmatch(project)):
        raise ValueError("canonical local Company OS scope required")
    with core.connect() as db:
        venture_company_os.init(db)
        local=db.execute("""SELECT * FROM venture_company_os WHERE company_id=?
            AND project_id=? AND operating_state='ACTIVE_LOCAL_EXECUTIVE'""",
            (scope,project)).fetchone()
        if not local:
            raise ValueError("product-local Company OS is not active")
        canonical_project=_canonical_project(db,scope,project)
        return canonical_project,local["instance_id"]

def _get_decision(body, *,fetch=None):
    import sina_work_bridge
    if not sina_work_bridge.configured():
        raise RuntimeError("Sina Goalkeeper service identity not configured")
    response=sina_work_bridge._request(DECISION_PATH,method="POST",body=body,fetch=fetch)
    if not isinstance(response,dict) or response.get("schema")!=DECISION_SCHEMA:
        raise ValueError("Sina Goalkeeper response schema mismatch")
    if (response.get("execution_owner")!="PROJECT_LOCAL_COMPANY_OS" or
        response.get("portfolio_owner")!="SINA_FOUNDER_OS" or
        response.get("governor_permit_issued") is not False or
        response.get("external_effect_authorized") is not False or
        response.get("agent_execution_permit") is not False):
        raise ValueError("Sina Goalkeeper authority mismatch")
    if (not isinstance(response.get("decision_ref"),str) or
        not DECISION_ID.fullmatch(response["decision_ref"])):
        raise ValueError("Sina Goalkeeper decision reference invalid")
    if response.get("decision") not in LOCAL_STATES|NO_MUTATION:
        raise ValueError("unrecognized Goalkeeper disposition")
    return response

def _store_answer(db,scope,project,result,*,task_id=None,event_id=None):
    from datetime import datetime,timezone
    init(db)
    # Feedback counters and transport audit flags may change on a replay,
    # but the decision's actual authority and directive may not.
    stable={key:result.get(key) for key in (
        "schema","decision_ref","decision","project_id","company_scope",
        "next_action","founder_question_required","founder_question",
        "policy_version","authority","governor_permit_issued",
        "external_effect_authorized")}
    stable["founder_policy_digest"]=(
        (result.get("founder_intent_memory") or {}).get("digest"))
    h=hashlib.sha256(canonical(stable).encode()).hexdigest()
    record=db.execute("""SELECT response_hash,event_id,task_id FROM venture_company_os_decisions
       WHERE company_id=? AND project_id=? AND decision_ref=?""",
       (scope,project,result["decision_ref"])).fetchone()
    if record:
        # Status of the same decision may be reviewed but never silently
        # swapped with a different response or Governor meaning.
        if record["response_hash"]!=h:
            raise ValueError("decision_ref replay mutated the authority envelope")
        return {"recorded":False,"event_id":record["event_id"],"task_id":record["task_id"]}
    db.execute("""INSERT INTO venture_company_os_decisions
      (company_id,project_id,decision_ref,response_hash,disposition,task_id,event_id,updated_at)
      VALUES(?,?,?,?,?,?,?,?)""",
      (scope,project,result["decision_ref"],h,result["decision"],
       task_id,event_id,datetime.now(timezone.utc).isoformat(timespec="seconds")))
    return {"recorded":True,"event_id":event_id,"task_id":task_id}

def submit_question(data,*,fetch=None):
    """Authenticated Company administrator submits a typed question for one local product."""
    import core
    import product_loops
    if not isinstance(data,dict) or set(data)-REQUEST_KEYS:
        raise ValueError("invalid Company OS agent question")
    local_project=data.get("project_id")
    local_scope=data.get("company_id")
    if local_scope is None:
        local_scope="founder-portfolio"
    canonical_project,instance=_assert_local(local_scope,local_project)
    if not data.get("request_id"):
        request_hash=hashlib.sha256(canonical(data).encode()).hexdigest()[:32]
        data={**data,"request_id":"company-decision:"+request_hash}
    body={**data,"schema":QUESTION_SCHEMA,"project_id":canonical_project,
          "company_id":None if local_scope=="founder-portfolio" else local_scope}
    # Only read-only questions are forwarded; caller cannot insert permission
    # or a fabricated signed Founder decision in the payload.
    answer=_get_decision(body,fetch=fetch)
    if (answer.get("project_id")!=canonical_project or
        answer.get("company_scope")!=local_scope):
        raise ValueError("Goalkeeper response crossed project scope")
    proceed=answer["decision"] in LOCAL_STATES and (
        answer.get("founder_question_required") is False)
    with core.connect() as db:
        product_loops.init(db)
        init(db)
        db.execute("BEGIN IMMEDIATE")
        if proceed:
            # SAME transaction as the existing observation/event outbox.
            summary=("Goalkeeper decision "+answer["decision_ref"]+" routed to the "
                     "product-local executive. "+str(answer.get("next_action") or ""))[:498]
            source={
                "source_event_id":"venture_agent_decision:"+answer["decision_ref"],
                "source_kind":"REPORTED_OPERATIONAL",
                "source_ref":"company-os:local-agent-decision",
                "signal":"feature_request" if data.get("proposed_action") in (
                    "IMPLEMENT_CODE","PREPARE_DEPLOY","INTERNAL_RESEARCH") else "feedback",
                "summary":summary,"severity":2
            }
            observed=product_loops._insert_observation(db,local_scope,local_project,source,verified=False)
            event_id=observed["event_id"] if not observed.get("idempotent") else None
        else:
            event_id=None
        stored=_store_answer(db,local_scope,local_project,answer,event_id=event_id)
        if proceed:
            _enqueue_feedback(db,
                feedback_id="company-decision:"+answer["decision_ref"]+":STARTED",
                decision_ref=answer["decision_ref"],company=local_scope,
                project=canonical_project,status="STARTED",
                source_ref="companyos:decision:"+answer["decision_ref"])
        db.commit()
    return {
        "schema":COMPANY_DECISION_SCHEMA,
        "company_os_instance_id":instance,
        "company_scope":local_scope,"project_id":local_project,
        "founder_project_id":canonical_project,
        "decision_ref":answer["decision_ref"],
        "decision":answer["decision"],
        "next_action":answer.get("next_action"),
        "founder_question_required":answer.get("founder_question_required"),
        "founder_question":answer.get("founder_question"),
        "queued_for_company_os":bool(proceed and (stored["recorded"] or stored["event_id"])),
        "event_id":stored["event_id"],
        "replay":not stored["recorded"],
        "execution_owner":"PROJECT_LOCAL_COMPANY_OS",
        "company_os_worker":"EXISTING_PRODUCT_SIGNALS_AND_CANONICAL_TASKS",
        "source_reported_only":True,
        "governor_permit_issued":False,
        "verified_completion":False,
        "independent_code_deployment_proven":False,
    }

def consult_existing_task(task,*,fetch=None):
    """Product worker asks Goalkeeper before next coding step. No task clone."""
    import core
    if not isinstance(task,dict) or not SAFE_TASK_ID.fullmatch(str(task.get("id") or "")):
        raise ValueError("real canonical Company OS task required")
    scope,project=task.get("company_id"),task.get("project_id")
    if not scope or not project:
        return {"state":"NOT_VENTURE_TASK"}
    canonical_project,instance=_assert_local(scope,project)
    role=task.get("role")
    if role not in ("chief_of_staff","engineering_operator","product_strategy",
                   "market_intelligence","marketing_content","customer_success",
                   "risk_governance","roi_analyst"):
        return {"state":"ROLE_OUTSIDE_GATEWAY"}
    objective=str(task.get("objective") or "")[:450]
    action=("IMPLEMENT_CODE" if role in ("engineering_operator","product_strategy")
            else "READ_EVIDENCE" if role in ("risk_governance","roi_analyst")
            else "INTERNAL_RESEARCH")
    request={
        "schema":QUESTION_SCHEMA,"project_id":canonical_project,
        "company_id":None if scope=="founder-portfolio" else scope,
        "agent_role":"COMPANY_OS_AGENT",
        "intent":"NEXT_STEP","proposed_action":action,
        "question":"Continue existing "+role+" task with scoped evidence: "+objective,
        "options":[],"evidence_refs":[],
        "request_id":"company-task:"+task["id"],
    }
    response=_get_decision(request,fetch=fetch)
    if response.get("project_id")!=canonical_project or response.get("company_scope")!=scope:
        raise ValueError("task decision crossed venture boundary")
    with core.connect() as db:
        _store_answer(db,scope,project,response,task_id=task["id"])
    return {
        "state":"CONSULTED","decision_ref":response["decision_ref"],
        "disposition":response["decision"],
        "next_action":str(response.get("next_action") or "")[:1100],
        "founder_question_required":response.get("founder_question_required") is True,
        "external_permit":False,"company_os_instance_id":instance,
        "source":"SINA_AUTHENTICATED_GOALKEEPER",
    }

def _enqueue_feedback(db,*,feedback_id,decision_ref,company,project,status,source_ref):
    init(db)
    db.execute("""INSERT OR IGNORE INTO venture_company_os_decision_feedback
       (feedback_id,decision_ref,company_id,project_id,status,source_ref)
       VALUES(?,?,?,?,?,?)""",
       (feedback_id,decision_ref,company,project,status,source_ref))

def record_task_feedback(task_id,provider):
    """Existing worker calls AFTER it committed the real draft/run."""
    import core
    if not SAFE_TASK_ID.fullmatch(str(task_id or "")):
        return {"queued":False,"reason":"INVALID_TASK"}
    with core.connect() as db:
        init(db)
        row=db.execute("""SELECT company_id,project_id,decision_ref FROM venture_company_os_decisions
            WHERE task_id=? ORDER BY updated_at DESC LIMIT 1""",(task_id,)).fetchone()
        if not row:
            return {"queued":False,"reason":"TASK_HAS_NO_AUTHENTICATED_DECISION"}
        status="FAILED" if provider in ("specialist_degraded","provider_error") else "DRAFTED"
        fid="company-task:"+task_id+":"+status
        _enqueue_feedback(db,feedback_id=fid,decision_ref=row["decision_ref"],
                          company=row["company_id"],project=row["project_id"],
                          status=status,source_ref="companyos:task:"+task_id)
        return {"queued":True,"feedback_id":fid,"status":status,
                "verified":False}

def flush_feedback(*,fetch=None,limit=3):
    """Use the EXISTING Company OS 40s tick. No extra scheduler or queue worker."""
    import core
    import sina_work_bridge
    with core.connect() as db:
        init(db)
        rows=db.execute("""SELECT * FROM venture_company_os_decision_feedback
          WHERE delivery_state='PENDING' ORDER BY created_at,feedback_id LIMIT ?""",
          (max(1,min(limit,5)),)).fetchall()
    delivered=0
    retry=0
    contract_rejected=0
    for row in rows:
        data={
            "schema":"sina.agent-decision-feedback.v1",
            "feedback_id":row["feedback_id"],"decision_ref":row["decision_ref"],
            "project_id":row["project_id"],"company_scope":row["company_id"],
            "status":row["status"],"source_ref":row["source_ref"]
        }
        try:
            result=sina_work_bridge._request(
                sina_work_bridge.AGENT_FEEDBACK_PATH,method="POST",body=data,fetch=fetch)
            if result.get("evidence_status")!="SOURCE_REPORTED_UNVERIFIED":
                raise ValueError("Sina feedback receipt lacks source-reported boundary")
            with core.connect() as db:
                db.execute("""UPDATE venture_company_os_decision_feedback
                  SET delivery_state='DELIVERED',attempts=attempts+1,
                      delivered_at=CURRENT_TIMESTAMP WHERE feedback_id=?""",
                  (row["feedback_id"],))
            delivered+=1
        except urllib.error.HTTPError as exc:
            if exc.code in (400,403,404,409,422):
                # The Founder rejected this exact decision/scope/identity.
                # Retrying unchanged every tick cannot repair permanent bad
                # source data. Keep it auditable, not falsely delivered.
                with core.connect() as db:
                    db.execute("""UPDATE venture_company_os_decision_feedback
                      SET delivery_state='REJECTED_CONTRACT',attempts=attempts+1
                      WHERE feedback_id=? AND delivery_state='PENDING'""",
                      (row["feedback_id"],))
                contract_rejected+=1
            else:
                with core.connect() as db:
                    db.execute("""UPDATE venture_company_os_decision_feedback
                      SET attempts=attempts+1 WHERE feedback_id=?""",
                      (row["feedback_id"],))
                retry+=1
        except Exception:
            # Only transient failures remain eligible for normal replay.
            with core.connect() as db:
                db.execute("""UPDATE venture_company_os_decision_feedback
                    SET attempts=attempts+1 WHERE feedback_id=?""",
                    (row["feedback_id"],))
            retry+=1
    return {"delivered":delivered,"pending_retry":retry,
            "contract_rejected":contract_rejected,
            "independent_verification":False,"new_scheduler":False}

def history(scope,project,limit=20):
    import core
    _assert_local(scope,project)
    with core.connect() as db:
        init(db)
        rows=db.execute("""SELECT decision_ref,disposition,task_id,event_id,updated_at
            FROM venture_company_os_decisions
            WHERE company_id=? AND project_id=? ORDER BY updated_at DESC LIMIT ?""",
            (scope,project,max(1,min(limit,100)))).fetchall()
        counts=db.execute("""SELECT delivery_state,COUNT(*) n
            FROM venture_company_os_decision_feedback WHERE company_id=?
            AND project_id=? GROUP BY delivery_state""",(scope,project)).fetchall()
        return {"schema":"noetfield.company-os.local-decision-history.v1",
                "project_id":project,"company_scope":scope,
                "items":[dict(x) for x in rows],
                "feedback_transport":{x["delivery_state"]:x["n"] for x in counts},
                "feedback_receipts_source_reported_only":True,
                "completion_verified":False}
