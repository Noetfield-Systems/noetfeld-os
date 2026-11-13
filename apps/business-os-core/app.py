import asyncio, json, os, re, time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
import core
import founder_bridge
import runtime_mesh
import operations_relay
import client_status
import floor_projection
import commercial_team
import portfolio_studio

TOKEN=os.getenv("FOUNDER_API_TOKEN","")
INTERVAL=max(2,int(os.getenv("WORKER_INTERVAL_SECONDS","5")))
STATIC=Path(__file__).parent/"static"
RATE:dict[str,list[float]]={}
STOP=asyncio.Event()
WORKER_JOB:asyncio.Task|None=None
TASK_WORKERS:list[asyncio.Task]=[]
TASK_WORKER_COUNT=3

def authorize(value:str|None):
    import hmac
    if not TOKEN: raise HTTPException(503,"Founder access is not configured.")
    supplied=(value or "").removeprefix("Bearer ").strip()
    if not supplied or not hmac.compare_digest(supplied,TOKEN):
        raise HTTPException(401,"Founder authentication required.")

def throttle(req:Request):
    import hashlib
    ip=req.client.host if req.client else "unknown"
    key=hashlib.sha256(ip.encode()).hexdigest()
    now=time.time()
    hits=[x for x in RATE.get(key,[]) if now-x<600]
    if len(hits)>=6: raise HTTPException(429,"Too many submissions. Try later.")
    hits.append(now);RATE[key]=hits
    if len(RATE)>4000:RATE.clear()

async def worker():
    while not STOP.is_set():
        try:
            await asyncio.to_thread(core.daily_tick)
            # Reuse the running Company OS event worker. An upstream outage
            # must not halt local intake, departments or the canonical queue.
            try:
                outcome=await asyncio.to_thread(founder_bridge.tick)
                if outcome.get("state")=="LIVE":
                    print("sina_company_org_bridge="+json.dumps(outcome,sort_keys=True),flush=True)
            except Exception as exc:
                import logging
                try:
                    await asyncio.to_thread(founder_bridge.record_failure,exc)
                except Exception:
                    logging.warning("sina_company_org_bridge_failure_record_failed")
                logging.warning("sina_company_org_bridge_retryable_error type=%s",type(exc).__name__)
            event=await asyncio.to_thread(core.claim,"events")
            if event:
                await asyncio.to_thread(core.process_event,event)
                continue
            await asyncio.sleep(INTERVAL)
        except asyncio.CancelledError: raise
        except Exception:
            import logging
            logging.exception("business_os_worker_iteration_failed")
            await asyncio.sleep(INTERVAL)

async def department_worker(worker_slot:int):
    """Three parallel claimers, same canonical SQLite task queue and lease logic."""
    while not STOP.is_set():
        try:
            task=await asyncio.to_thread(core.claim,"tasks")
            if task:
                await asyncio.to_thread(core.process_task,task)
                continue
            await asyncio.sleep(INTERVAL)
        except asyncio.CancelledError: raise
        except Exception:
            import logging
            logging.exception("company_department_worker_failed slot=%s",worker_slot)
            await asyncio.sleep(INTERVAL)

@asynccontextmanager
async def lifespan(app):
    global WORKER_JOB,TASK_WORKERS
    core.init();client_status.init();founder_bridge.init();STOP.clear()
    restored=portfolio_studio.overview()
    print("company_portfolio_resume="+json.dumps({
        "state":restored["state"].get("portfolio_studio_state"),
        "cycles":len(restored["project_cycles"]),
        "department_tasks":sum(x["department_tasks"] for x in restored["project_cycles"]),
        "internal_drafts":sum(x["internal_drafts"] for x in restored["project_cycles"]),
        "blocked_tasks":sum(x["blocked_tasks"] or 0 for x in restored["project_cycles"]),
        "projects":list(dict.fromkeys(x["project_id"] for x in restored["project_cycles"]))[:22],
        "department_workers":TASK_WORKER_COUNT,
        "external_product_deploys_claimed":0,
    },sort_keys=True),flush=True)
    WORKER_JOB=asyncio.create_task(worker())
    TASK_WORKERS=[asyncio.create_task(department_worker(n)) for n in range(TASK_WORKER_COUNT)]
    yield
    STOP.set()
    for job in [WORKER_JOB,*TASK_WORKERS]:
        job.cancel()
    await asyncio.gather(WORKER_JOB,*TASK_WORKERS,return_exceptions=True)
    WORKER_JOB=None
    TASK_WORKERS=[]

app=FastAPI(title="Noetfield Business OS",version="0.1.0",lifespan=lifespan)

class Intake(BaseModel):
    model_config=ConfigDict(extra="ignore")
    brand:str="noetfield"
    audience:str="other"
    intent:str="other"
    name:str=Field(min_length=2,max_length=120)
    email:str=Field(min_length=5,max_length=254)
    company:str=Field(default="",max_length=140)
    role:str=Field(default="",max_length=100)
    problem:str=Field(min_length=10,max_length=2500)
    urgency:str="exploring"
    estimated_value:float=Field(default=0,ge=0,le=50000000)
    consent:bool=False
    ai_consent:bool=False
    website:str=""
class Feedback(BaseModel):
    model_config=ConfigDict(extra="ignore")
    brand:str="noetfield"
    rating:int=Field(ge=1,le=5)
    comment:str=Field(min_length=5,max_length=2000)
    consent:bool=False

@app.get("/")
def home(): return FileResponse(STATIC/"index.html")
@app.get("/control")
def control(): return FileResponse(STATIC/"control.html")
@app.get("/control/premium.css", include_in_schema=False)
def control_premium_styles():
    return FileResponse(STATIC/"control-premium.css",media_type="text/css",headers={"Cache-Control":"public,max-age=300"})

@app.get("/control/premium.js", include_in_schema=False)
def control_premium_script():
    return FileResponse(STATIC/"control-premium.js",media_type="text/javascript",headers={"Cache-Control":"public,max-age=300"})

@app.get("/privacy")
def privacy(): return FileResponse(STATIC/"privacy.html")
@app.get("/health")
@app.get("/api/health")
def health():
    try:
        with core.connect() as db: db.execute("SELECT 1")
        return {"ok":True,"service":"business-os-core","version":"0.1.0","storage":"ready","worker_interval_seconds":INTERVAL}
    except Exception: return JSONResponse({"ok":False,"storage":"unavailable"},status_code=503)
@app.get("/ready")
def ready():
    try:
        with core.connect() as db:
            db.execute("SELECT 1")
        running=(WORKER_JOB is not None and not WORKER_JOB.done() and
                 len(TASK_WORKERS)==TASK_WORKER_COUNT and all(not x.done() for x in TASK_WORKERS))
        if not running:
            return JSONResponse({"ready":False,"worker":"not_running"},status_code=503)
        return {"ready":True,"worker":"running"}
    except Exception:
        return JSONResponse({"ready":False,"storage":"unavailable"},status_code=503)

@app.get("/health/deep")
def deep_health():
    try:
        with core.connect() as db:
            tables={r["name"] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
            required={"contacts","opportunities","events","tasks","runs","memories","task_dependencies","platform_intake_signals"}
            missing=sorted(required-tables)
            counts={
                "queued_events":db.execute("SELECT COUNT(*) n FROM events WHERE status='queued'").fetchone()["n"],
                "queued_tasks":db.execute("SELECT COUNT(*) n FROM tasks WHERE status='queued'").fetchone()["n"],
                "blocked_tasks":db.execute("SELECT COUNT(*) n FROM tasks WHERE status='blocked'").fetchone()["n"],
                "dead_letter_events":db.execute("SELECT COUNT(*) n FROM events WHERE status='dead_letter'").fetchone()["n"],
            }
        worker_running=WORKER_JOB is not None and not WORKER_JOB.done()
        ok=not missing and worker_running
        payload={"ok":ok,"service":"business-os-core","schema_missing":missing,
            "worker_running":worker_running,"worker_interval_seconds":INTERVAL,"queue":counts,
            "company_role_count":len(core.COMPANY_ROLES),
            "runtime_executor_count":len(core.AGENTS),"dependency_gating":True,
            "founder_mesh":founder_bridge.health()}
        return payload if ok else JSONResponse(payload,status_code=503)
    except Exception as exc:
        return JSONResponse({"ok":False,"error":type(exc).__name__},status_code=503)

@app.post("/api/intake")
async def intake(data:Intake,request:Request):
    throttle(request)
    if int(request.headers.get("content-length","0") or 0)>24000: raise HTTPException(413,"Submission too large.")
    if data.website.strip(): return {"accepted":True}
    if not data.consent: raise HTTPException(400,"Consent is required.")
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$",data.email): raise HTTPException(400,"Enter a valid email.")
    brand=data.brand if data.brand in core.BRANDS else "noetfield"
    audience=data.audience if data.audience in core.AUDIENCES else "other"
    intent=data.intent if data.intent in core.INTENTS else "other"
    urgency=data.urgency if data.urgency in {"now","30_days","quarter","exploring"} else "exploring"
    payload=data.model_dump()
    payload.update({"brand":brand,"audience":audience,"intent":intent,"urgency":urgency,
      "name":core.clean(data.name,120),"email":core.clean(data.email,254).lower(),
      "company":core.clean(data.company,140),"role":core.clean(data.role,100),
      "problem":core.clean(data.problem,2500)})
    route,_,_=core.route_for(brand,audience,intent)
    event_id=core.add_event("intake.received","public_web",brand,payload)
    status_token=client_status.issue(event_id)
    return JSONResponse({"accepted":True,"reference":event_id,"status_token":status_token,"route":route,
      "message":"Request accepted and queued for its specialist workflow."},status_code=202)

class IntakeProgressQuery(BaseModel):
    model_config=ConfigDict(extra="forbid")
    reference:str=Field(min_length=20,max_length=30)
    status_token:str=Field(min_length=40,max_length=96)

@app.post("/api/intake/progress")
async def intake_progress(payload:IntakeProgressQuery,request:Request):
    # Never put the opaque read capability in a GET query string or browser URL.
    try:
        size=int(request.headers.get("content-length","0") or 0)
    except ValueError:
        raise HTTPException(400,"Invalid content length")
    if size>2048:
        raise HTTPException(413,"Status request too large")
    result=client_status.snapshot(payload.reference,payload.status_token)
    if result is None:
        raise HTTPException(404,"Status reference not found")
    if result.get("rate_limited"):
        raise HTTPException(429,"Polling rate exceeded")
    return JSONResponse(result,headers={"Cache-Control":"no-store"})

@app.post("/api/feedback")
async def feedback(data:Feedback,request:Request):
    throttle(request)
    if not data.consent: raise HTTPException(400,"Consent is required.")
    brand=data.brand if data.brand in core.BRANDS else "noetfield"
    event_id=core.add_event("feedback.received","public_feedback",brand,
      {"brand":brand,"rating":data.rating,"comment":core.clean(data.comment,2000)})
    return JSONResponse({"accepted":True,"reference":event_id},status_code=202)

@app.get("/api/control/portfolio-studio")
def portfolio_studio_overview(authorization:str|None=Header(default=None)):
    authorize(authorization)
    return portfolio_studio.overview()


@app.get("/api/control/runtime-mesh")
def runtime_mesh_observation(authorization:str|None=Header(default=None)):
    """Founder-authenticated, bounded observation. Never dispatches the Motor."""
    authorize(authorization)
    return runtime_mesh.snapshot(founder_bridge_status=founder_bridge.health())

@app.get("/api/control/operations-relay")
def operations_relay_snapshot(authorization:str|None=Header(default=None)):
    """Actual persisted queue, causal handoffs, remediation and model-call evidence."""
    authorize(authorization)
    return operations_relay.snapshot()

@app.get("/api/control/overview")
def overview(authorization:str|None=Header(default=None)):
    authorize(authorization)
    result=core.overview()
    result.update({"worker_interval_seconds":INTERVAL,
      "llm_configured":bool(os.getenv("LLM_BASE_URL") and os.getenv("LLM_API_KEY") and os.getenv("LLM_MODEL")),
      "policy":"Analysis and internal reversible tasks are autonomous. External messaging, payments, deployments, legal/investment commitments require Founder approval."})
    return result

@app.get("/api/control/dashboard")
def dashboard(authorization:str|None=Header(default=None),
              brand:str|None=None,days:int=7):
    """Trusted live founder dashboard summary + truthful daily activity trend.

    Brand filter is explicit; company-team totals remain cross-portfolio.
    This endpoint neither infers revenue nor invents a customer conversion.
    """
    authorize(authorization)
    if brand and brand not in core.BRANDS:
        raise HTTPException(422,"Unsupported venture.")
    if days not in (7,30):
        raise HTTPException(422,"Choose 7 or 30 days.")
    from datetime import datetime,timezone,timedelta
    labels=[(datetime.now(timezone.utc).date()-timedelta(days=offset)).isoformat()
            for offset in range(days-1,-1,-1)]
    where=" WHERE brand=?" if brand else ""
    values=(brand,) if brand else ()
    with core.connect() as db:
        def count(table,suffix="",params=()):
            return db.execute(f"SELECT COUNT(*) AS n FROM {table}"+suffix,params).fetchone()["n"]
        open_states=("queued","running","drafted")
        twhere=" WHERE status IN (?,?,?)"+(" AND brand=?" if brand else "")
        pending=count("tasks",twhere,(*open_states,*values))
        status_rows=db.execute("SELECT status,COUNT(*) AS n FROM tasks"+
            (" WHERE brand=?" if brand else "")+" GROUP BY status",values).fetchall()
        status_counts={row["status"]:row["n"] for row in status_rows}
        actionable=sum(status_counts.get(k,0) for k in ("queued","running","blocked","failed"))
        review_drafts=status_counts.get("drafted",0)
        opportunities=count("opportunities",where,values)
        contacts=count("contacts",where,values)
        requested=count("opportunities",
            (" WHERE "+" AND ".join(["stage NOT IN ('lost','won')"]+(["brand=?"] if brand else []))),
            values)
        event_filter="created_at>=?"+(" AND brand=?" if brand else "")
        grouped=db.execute(
            f"SELECT substr(created_at,1,10) AS day,COUNT(*) n FROM events WHERE {event_filter} "
            "GROUP BY substr(created_at,1,10)",
            (labels[0],*values)).fetchall()
        daily={row["day"]:row["n"] for row in grouped}
        events=[{"date":day,"count":daily.get(day,0)} for day in labels]
        recent=sum(row["count"] for row in events)
        return {
            "source":"Company OS durable tables",
            "brand":brand or "all",
            "days":days,
            "as_of":datetime.now(timezone.utc).isoformat(),
            "counts":{
              "contacts":contacts,
              "opportunities":opportunities,
              "active_opportunities":requested,
              "pending_tasks":pending,
              "actionable_tasks":actionable,
              "drafts_awaiting_review":review_drafts,
              "task_status_breakdown":status_counts,
              "activity_events":recent,
            },
            "activity_daily":events,
            "collected_revenue":{"state":"not_connected","amount":None},
            "scope":"Brand filter applies to contacts, opportunities, tasks and activity; workforce capacity is company-wide",
        }

@app.get("/api/control/agents")
def agents(authorization:str|None=Header(default=None)):
    authorize(authorization)
    return {"agents":core.agent_roster()}

@app.get("/api/control/org")
def organization(authorization:str|None=Header(default=None)):
    authorize(authorization)
    seats=core.company_workforce_roster()
    agents=core.agent_roster()
    return {
        "organization":{
            "founder":core.FOUNDER_SEAT,
            "layers":3,
            "company_role_count":len(seats),
            "runtime_executor_count":len(agents),
            "canonical_registry":core.WORKFORCE_BINDING["canonical_source"],
            "operating_model":"canonical company seats -> bounded runtime capabilities -> specialist drafts -> dependency gate -> N-01 synthesis -> Founder ratification"
        },
        "seats":seats,
        "runtime_agents":agents
    }
@app.get("/api/control/opportunities")
def opportunities(authorization:str|None=Header(default=None),brand:str|None=None):
    authorize(authorization)
    with core.connect() as db:
        query="SELECT o.*,c.name,c.email,c.company,c.audience,c.role FROM opportunities o JOIN contacts c ON c.id=o.contact_id"
        rows=db.execute(query+(" WHERE o.brand=? " if brand in core.BRANDS else " ")+
           "ORDER BY o.created_at DESC LIMIT 150",(brand,) if brand in core.BRANDS else ()).fetchall()
    return {"opportunities":[dict(r) for r in rows]}

@app.get("/api/internal/company-floor/snapshot", include_in_schema=False)
def company_floor_snapshot(x_company_floor_token:str|None=Header(default=None)):
    if not (os.getenv("COMPANY_FLOOR_CORE_READ_TOKEN") or "").strip():
        raise HTTPException(503,"Company Floor service identity not configured")
    if not floor_projection.authorized(x_company_floor_token):
        raise HTTPException(401,"Company Floor service identity required")
    return floor_projection.snapshot()


@app.get("/api/internal/sina/revenue-queue", include_in_schema=False)
def sina_revenue_queue(x_sina_bridge_token:str|None=Header(default=None),limit:int=50):
    """Service-authenticated read-only observation; returns no buyer personal data."""
    if not (os.getenv("SINA_SEED_BRIDGE_TOKEN") or "").strip():
        raise HTTPException(503,"Sina revenue bridge is not configured")
    if not core.sina_bridge_authorized(x_sina_bridge_token):
        raise HTTPException(401,"Service authentication required")
    return {
        "schema":"noetfield.sina-seed.revenue-queue.v1",
        "source":"Noetfield Business OS Core platform_intake_signals",
        "pii_included":False,
        "items":core.sina_seed_revenue_items(limit),
        "commercial_workforce":{brand:commercial_team.status(brand) for brand in commercial_team.BRANDS},
    }


@app.get("/api/control/intake-signals")
def intake_signals(authorization:str|None=Header(default=None),limit:int=50):
    authorize(authorization)
    cap=max(1,min(int(limit),100))
    with core.connect() as db:
        rows=db.execute(
            """SELECT intake_id,request_id,source_created_at,received_at,sku,vector,
                      qualification_json,status,event_id,processed_at
               FROM platform_intake_signals
               ORDER BY source_created_at DESC,intake_id DESC LIMIT ?""",
            (cap,)
        ).fetchall()
        output=[]
        for row in rows:
            item=dict(row)
            item["qualification"]=json.loads(item.pop("qualification_json")) if item.get("qualification_json") else None
            item["task_count"]=db.execute(
                "SELECT COUNT(*) n FROM tasks WHERE event_id=?",
                (item["event_id"],)
            ).fetchone()["n"]
            output.append(item)
    return {"signals":output,"source_of_truth":"Noetfield Platform API public_intakes","pii_included":False}

@app.get("/api/control/connect-opportunities")
def connect_opportunities(authorization:str|None=Header(default=None),limit:int=50):
    """Founder-authenticated read-only relationship and opportunity desk.

    Displays only actual persisted Company OS source/task records. This is
    not a calendar, contact directory, or independently verified CRM outcome.
    """
    authorize(authorization)
    return {
        "schema":"noetfield.connect-opportunity-inbox.v1",
        "items":core.connect_opportunity_inbox(limit),
        "pii_included":False,
        "source":"Noetfield Platform Intake -> Company OS task queue",
    }


@app.patch("/api/control/connect-cases/{intake_id}")
def update_connect_case(intake_id:str,body:dict[str,Any],authorization:str|None=Header(default=None)):
    """Founder-authorized review decision with version conflict protection.

    This changes the internal case ledger only; it never sends outreach,
    books meetings, or marks cash collected.
    """
    authorize(authorization)
    try:
        case=core.update_connect_case(intake_id,body)
    except ValueError as exc:
        code=str(exc)
        if code=="connect_case_not_found":
            raise HTTPException(404,code) from exc
        if code=="connect_case_version_conflict":
            raise HTTPException(409,code) from exc
        raise HTTPException(400,code) from exc
    return {"updated":True,"case":case,"verified_cash_collected":None,
            "external_actions":0}


@app.get("/api/control/tasks")
def tasks(authorization:str|None=Header(default=None)):
    authorize(authorization)
    with core.connect() as db:
        rows=db.execute("""
            SELECT t.*,o.title AS opportunity_title,
                (SELECT COUNT(*) FROM task_dependencies td WHERE td.task_id=t.id) dependency_count,
                (SELECT COUNT(*) FROM task_dependencies td
                 JOIN tasks dep ON dep.id=td.depends_on_task_id
                 WHERE td.task_id=t.id AND dep.status NOT IN ('drafted','approved')) pending_dependencies
            FROM tasks t LEFT JOIN opportunities o ON o.id=t.opportunity_id
            ORDER BY t.created_at DESC LIMIT 150
        """).fetchall()
    tasks_out=[]
    for row in rows:
        item=dict(row)
        seat=core.company_role_for_runtime(item["role"])
        item["company_role_id"]=seat["role_id"]
        item["company_role_title"]=seat["title"]
        tasks_out.append(item)
    return {"tasks":tasks_out}
@app.get("/api/control/task-inbox")
def task_inbox(authorization:str|None=Header(default=None),limit:int=50,offset:int=0,
               status:str|None=None,brand:str|None=None,q:str=""):
    """Paged source-backed task inbox; no separate queue or implied completion."""
    authorize(authorization)
    if limit<1 or limit>100 or offset<0 or offset>100000:
        raise HTTPException(422,"Invalid page size or offset.")
    if status and status not in {"queued","running","drafted","approved","failed","blocked","completed","processing"}:
        raise HTTPException(422,"Unsupported work status.")
    if brand and brand not in core.BRANDS:
        raise HTTPException(422,"Unsupported venture.")
    query=q.strip()
    if len(query)>120:
        raise HTTPException(422,"Search text is too long.")
    conditions=[]
    params=[]
    if status:
        conditions.append("t.status=?");params.append(status)
    if brand:
        conditions.append("t.brand=?");params.append(brand)
    if query:
        conditions.append("(t.title LIKE ? ESCAPE '\\' OR t.objective LIKE ? ESCAPE '\\' OR t.id LIKE ? ESCAPE '\\')")
        escaped=query.replace("\\","\\\\").replace("%","\\%").replace("_","\\_")
        params.extend(["%"+escaped+"%"]*3)
    where=(" WHERE "+" AND ".join(conditions)) if conditions else ""
    with core.connect() as db:
        total=db.execute("SELECT COUNT(*) n FROM tasks t"+where,tuple(params)).fetchone()["n"]
        rows=db.execute("""
            SELECT t.*,o.title AS opportunity_title,
                (SELECT COUNT(*) FROM task_dependencies td WHERE td.task_id=t.id) dependency_count,
                (SELECT COUNT(*) FROM task_dependencies td JOIN tasks dep ON dep.id=td.depends_on_task_id
                 WHERE td.task_id=t.id AND dep.status NOT IN ('drafted','approved')) pending_dependencies
            FROM tasks t LEFT JOIN opportunities o ON o.id=t.opportunity_id
        """+where+"""
            ORDER BY CASE t.status
              WHEN 'failed' THEN 0 WHEN 'blocked' THEN 1 WHEN 'drafted' THEN 2
              WHEN 'queued' THEN 3 WHEN 'running' THEN 4 ELSE 5 END,
              t.created_at DESC,t.id DESC LIMIT ? OFFSET ?
        """,(*params,limit,offset)).fetchall()
        grouped=db.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status").fetchall()
    items=[]
    for row in rows:
        item=dict(row)
        seat=core.company_role_for_runtime(item["role"])
        item["company_role_id"]=seat["role_id"]
        item["company_role_title"]=seat["title"]
        items.append(item)
    return {"schema":"noetfield.business-os.task-inbox.v1","tasks":items,
            "offset":offset,"limit":limit,"total":total,
            "has_more":offset+len(items)<total,
            "status_counts":{r["status"]:r["n"] for r in grouped},
            "source":"Company OS durable tasks","verified_outcomes_inferred":False}

@app.get("/api/control/events")
def events(authorization:str|None=Header(default=None)):
    authorize(authorization)
    with core.connect() as db:
        rows=db.execute("SELECT id,event_type,source,brand,status,attempts,created_at,processed_at,error FROM events ORDER BY created_at DESC LIMIT 100").fetchall()
    return {"events":[dict(r) for r in rows]}
@app.get("/api/control/runs")
def runs(authorization:str|None=Header(default=None)):
    authorize(authorization)
    with core.connect() as db:
        rows=db.execute("SELECT id,task_id,role,provider,model,status,input_tokens,output_tokens,started_at,finished_at FROM runs ORDER BY started_at DESC LIMIT 100").fetchall()
    return {"runs":[dict(r) for r in rows]}
@app.get("/api/control/roi")
def roi(authorization:str|None=Header(default=None)):
    authorize(authorization)
    with core.connect() as db:
        rows=db.execute("SELECT brand,COUNT(*) leads,SUM(CASE WHEN score>=65 THEN 1 ELSE 0 END) qualified,SUM(CASE WHEN stage='won' THEN 1 ELSE 0 END) won,COALESCE(SUM(CASE WHEN stage NOT IN ('won','lost') THEN estimated_value*CASE WHEN score>=80 THEN .35 WHEN score>=65 THEN .2 ELSE .08 END ELSE 0 END),0) weighted_pipeline FROM opportunities GROUP BY brand").fetchall()
        count=db.execute("SELECT COUNT(*) n FROM events WHERE created_at>=datetime('now','-7 days')").fetchone()["n"]
    return {"brands":[dict(r) for r in rows],"events_last_7d":count,
      "actual_revenue":"Not connected. Weighted pipeline is not booked revenue.",
      "cost_tracking":"Token usage is logged. Infrastructure spend is not connected yet."}
@app.get("/api/control/memory")
def memory(authorization:str|None=Header(default=None),brand:str="noetfield",q:str=""):
    authorize(authorization);brand=brand if brand in core.BRANDS else "noetfield"
    if q: chunks=core.retrieve(brand,q,20)
    else:
        with core.connect() as db:
            chunks=[r["content"] for r in db.execute("SELECT content FROM memories WHERE brand=? ORDER BY created_at DESC LIMIT 20",(brand,)).fetchall()]
    return {"brand":brand,"retrieval":"SQLite FTS5 lexical retrieval; vector embeddings are not configured in this release.","chunks":chunks}
@app.patch("/api/control/opportunities/{oid}")
def update_opportunity(oid:str,body:dict[str,Any],authorization:str|None=Header(default=None)):
    authorize(authorization);stage=body.get("stage")
    if stage not in {"new","qualified","proposal","negotiation","won","lost","nurture"}: raise HTTPException(400,"Unsupported stage.")
    with core.connect() as db:
        cursor=db.execute("UPDATE opportunities SET stage=?,updated_at=? WHERE id=?",(stage,core.now(),oid))
        if not cursor.rowcount: raise HTTPException(404,"Opportunity not found.")
    return {"updated":True,"stage":stage}
@app.get("/api/control/commercial-team")
def commercial_team_status(brand:str="noetfield",authorization:str|None=Header(default=None)):
    authorize(authorization)
    if brand not in commercial_team.BRANDS:
        raise HTTPException(400,"Unsupported commercial product.")
    return commercial_team.status(brand)

@app.post("/api/control/commercial-team/commission")
def commission_commercial_team(body:dict[str,Any],authorization:str|None=Header(default=None)):
    """Founder-authenticated internal onboarding; never sends or publishes."""
    authorize(authorization)
    brand=body.get("brand","noetfield")
    if type(brand) is not str or brand not in commercial_team.BRANDS:
        raise HTTPException(400,"Unsupported commercial product.")
    return commercial_team.commission(brand)

@app.post("/api/control/tasks")
def create_task(body:dict[str,Any],authorization:str|None=Header(default=None)):
    authorize(authorization);role=body.get("role")
    if role not in {a[0] for a in core.AGENTS}: raise HTTPException(400,"Unknown role.")
    title=core.clean(body.get("title"),160);objective=core.clean(body.get("objective"),1200)
    if len(title)<3 or len(objective)<10: raise HTTPException(400,"Title and objective are required.")
    brand=body.get("brand") if body.get("brand") in core.BRANDS else "noetfield"
    dependencies=body.get("depends_on",[])
    if not isinstance(dependencies,list):
        raise HTTPException(422,"depends_on must be an array of task IDs.")
    if len(dependencies)>20:
        raise HTTPException(422,"A task may depend on at most 20 tasks.")
    with core.connect() as db:
        task_id=core.add_task(db,None,None,brand,role,title,objective,"Prepare internal recommendation only.")
        for dependency_id in dependencies:
            if not isinstance(dependency_id,str) or not dependency_id.strip():
                raise HTTPException(422,"Each dependency must be a non-empty task ID.")
            exists=db.execute("SELECT id,brand FROM tasks WHERE id=?",(dependency_id,)).fetchone()
            if not exists:
                raise HTTPException(422,"Dependency task does not exist.")
            if exists["brand"] != brand:
                raise HTTPException(422,"Dependency must belong to the same brand lane.")
            core.add_task_dependency(db,task_id,dependency_id)
    return {"created":True,"task_id":task_id}
@app.delete("/api/control/opportunities/{oid}")
def delete_contact_data(oid:str,authorization:str|None=Header(default=None)):
    authorize(authorization)
    with core.connect() as db:
        row=db.execute("SELECT contact_id FROM opportunities WHERE id=?",(oid,)).fetchone()
        if not row: raise HTTPException(404,"Opportunity not found.")
        contact_id=row["contact_id"]
        opportunity_rows=db.execute("SELECT id FROM opportunities WHERE contact_id=?",(contact_id,)).fetchall()
        opportunity_ids=[r["id"] for r in opportunity_rows]
        placeholders=",".join("?" for _ in opportunity_ids)
        task_rows=db.execute("SELECT event_id FROM tasks WHERE opportunity_id IN ("+placeholders+") AND event_id IS NOT NULL",opportunity_ids).fetchall()
        event_ids=list({r["event_id"] for r in task_rows})
        memory_rows=db.execute("SELECT id FROM memories WHERE source_id IN ("+placeholders+")",opportunity_ids).fetchall()
        memory_ids=[r["id"] for r in memory_rows]
        if memory_ids:
            try: db.executemany("DELETE FROM memory_fts WHERE memory_id=?",[(x,) for x in memory_ids])
            except Exception: pass
            db.executemany("DELETE FROM memories WHERE id=?",[(x,) for x in memory_ids])
        db.execute("DELETE FROM tasks WHERE opportunity_id IN ("+placeholders+")",opportunity_ids)
        if event_ids: db.executemany("DELETE FROM events WHERE id=?",[(x,) for x in event_ids])
        db.execute("DELETE FROM opportunities WHERE contact_id=?",(contact_id,))
        db.execute("DELETE FROM contacts WHERE id=?",(contact_id,))
    return {"deleted":True,"contact_removed":True,"opportunities_removed":len(opportunity_ids)}

@app.post("/api/control/tasks/{tid}/approve")
def approve_task(tid:str,authorization:str|None=Header(default=None)):
    authorize(authorization)
    with core.connect() as db:
        row=db.execute("SELECT id,status FROM tasks WHERE id=?",(tid,)).fetchone()
        if not row: raise HTTPException(404,"Task not found.")
        if row["status"]!="drafted": raise HTTPException(409,"Only completed drafts can be ratified.")
        db.execute("UPDATE tasks SET status='approved',updated_at=? WHERE id=?",(core.now(),tid))
        db.execute("INSERT INTO events(id,event_type,source,brand,payload,status,created_at,processed_at) VALUES(?,?,?,?,?,'processed',?,?)",
         (core.idof("evt"),"founder.approval.recorded","founder_control","portfolio",'{"task_id":"'+tid+'"}',core.now(),core.now()))
    return {"approved":True,"execution":"Approval recorded only; no external action was performed."}
