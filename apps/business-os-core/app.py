import asyncio, os, re, time, hmac
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
import core
import paperclip_bridge as paperclip
import product_loops

TOKEN=os.getenv("FOUNDER_API_TOKEN","")
INTERVAL=max(2,int(os.getenv("WORKER_INTERVAL_SECONDS","5")))
WORKER_PARALLELISM=max(1,min(4,int(os.getenv("COMPANY_OS_WORKER_PARALLELISM","3"))))
STATIC=Path(__file__).parent/"static"
RATE:dict[str,list[float]]={}
STOP=asyncio.Event()
WORKER_JOB:asyncio.Task|None=None

def authorize(value:str|None):
    import hmac
    if not TOKEN: raise HTTPException(503,"Founder access is not configured.")
    supplied=(value or "").removeprefix("Bearer ").strip()
    if not supplied or not hmac.compare_digest(supplied,TOKEN):
        raise HTTPException(401,"Founder authentication required.")

def throttle(req:Request,key_override:str|None=None):
    import hashlib
    ip=req.client.host if req.client else "unknown"
    key=key_override or hashlib.sha256(ip.encode()).hexdigest()
    now=time.time()
    hits=[x for x in RATE.get(key,[]) if now-x<600]
    if len(hits)>=6: raise HTTPException(429,"Too many submissions. Try later.")
    hits.append(now);RATE[key]=hits
    if len(RATE)>4000:
        RATE.clear()
        RATE[key]=hits

def authorize_public_intake_proxy(request:Request)->str|None:
    required=os.getenv("COMPANY_OS_REQUIRE_PROXY_AUTH","false").lower()=="true"
    expected=os.getenv("COMPANY_OS_PROXY_TOKEN","")
    supplied=request.headers.get("x-company-os-proxy-token","")
    if required and not expected:
        raise HTTPException(503,"Secure intake gateway is not configured.")
    if required or supplied:
        if not expected or not supplied or not hmac.compare_digest(supplied,expected):
            raise HTTPException(401,"Authenticated intake gateway required.")
        client_hash=request.headers.get("x-company-os-client-hash","")
        if not re.fullmatch(r"[a-f0-9]{64}",client_hash):
            raise HTTPException(400,"Invalid intake client fingerprint.")
        return client_hash
    return None

async def worker():
    while not STOP.is_set():
        try:
            await asyncio.to_thread(core.daily_tick)
            event=await asyncio.to_thread(core.claim,"events")
            if event:
                await asyncio.to_thread(core.process_event,event)
                continue
            # Distinct eligible Company OS tasks execute concurrently while
            # atomic SQLite claims and dependency checks remain canonical.
            batch=[]
            for _ in range(WORKER_PARALLELISM):
                task=await asyncio.to_thread(core.claim,"tasks")
                if task is None: break
                batch.append(task)
            if batch:
                results=await asyncio.gather(
                    *(asyncio.to_thread(core.process_task,t) for t in batch),
                    return_exceptions=True)
                for error in results:
                    if isinstance(error,Exception):
                        import logging
                        logging.error("company_os_specialist_failed error_type=%s",type(error).__name__)
                continue
            await asyncio.sleep(INTERVAL)
        except asyncio.CancelledError: raise
        except Exception:
            import logging
            logging.exception("business_os_worker_iteration_failed")
            await asyncio.sleep(INTERVAL)

@asynccontextmanager
async def lifespan(app):
    global WORKER_JOB
    core.init();STOP.clear()
    with core.connect() as db:
        paperclip.create_binding_table(db)
    WORKER_JOB=asyncio.create_task(worker())
    yield
    STOP.set();WORKER_JOB.cancel()
    try: await WORKER_JOB
    except asyncio.CancelledError: pass
    WORKER_JOB=None

app=FastAPI(title="Noetfield Business OS",version="0.1.0",lifespan=lifespan)

@app.middleware("http")
async def public_body_limit(request:Request,call_next):
    if request.url.path in {"/api/intake","/api/feedback"} and request.method=="POST":
        try:
            size=int(request.headers.get("content-length","0") or 0)
        except ValueError:
            return JSONResponse({"detail":"Invalid Content-Length."},status_code=400)
        if size>24000:
            return JSONResponse({"detail":"Submission too large."},status_code=413)
    return await call_next(request)

class Intake(BaseModel):
    model_config=ConfigDict(extra="forbid")
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
    website:str=Field(default="",max_length=200)
    idempotency_key:str|None=Field(default=None,min_length=8,max_length=64,pattern=r"^[A-Za-z0-9._:-]+$")
class Feedback(BaseModel):
    model_config=ConfigDict(extra="ignore")
    brand:str="noetfield"
    rating:int=Field(ge=1,le=5)
    comment:str=Field(min_length=5,max_length=2000)
    consent:bool=False

class ProductProgram(BaseModel):
    model_config=ConfigDict(extra="forbid")
    company_id:str=Field(pattern=r"^[a-z][a-z0-9-]{2,79}$")
    project_id:str=Field(pattern=r"^[a-z][a-z0-9-]{2,79}$")
    name:str=Field(min_length=3,max_length=100)
    vertical:str=Field(pattern=r"^[a-z][a-z0-9-]{2,79}$")
    objective:str=Field(min_length=18,max_length=1200)
    priority:int=Field(default=3,ge=1,le=5)
    max_tasks_per_cycle:int=Field(default=7,ge=2,le=7)
    health_url:str|None=Field(default=None,max_length=220)
    market_keywords:list[str]=Field(default_factory=list,max_length=8)

class ProductObservation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    company_id:str=Field(pattern=r"^[a-z][a-z0-9-]{2,79}$")
    project_id:str=Field(pattern=r"^[a-z][a-z0-9-]{2,79}$")
    source_event_id:str=Field(min_length=8,max_length=128)
    source_kind:str
    source_ref:str=Field(min_length=8,max_length=220)
    signal:str
    summary:str=Field(min_length=12,max_length=500)
    severity:int=Field(default=1,ge=0,le=4)
    observed_at:str|None=None
    metric_name:str|None=None
    metric_value:float|None=None
    sample_count:int|None=Field(default=None,ge=0,le=100000000)

@app.get("/")
def home(): return FileResponse(STATIC/"index.html")
@app.get("/control")
def control(): return FileResponse(STATIC/"control.html")
@app.get("/company-os")
def company_os_product(): return FileResponse(STATIC/"company-os.html")
@app.get("/privacy")
def privacy(): return FileResponse(STATIC/"privacy.html")
@app.get("/health")
@app.get("/api/health")
def health():
    try:
        with core.connect() as db: db.execute("SELECT 1")
        return {"ok":True,"service":"business-os-core","version":"0.1.0","storage":"ready","worker_interval_seconds":INTERVAL,
                "company_worker_parallelism":WORKER_PARALLELISM}
    except Exception: return JSONResponse({"ok":False,"storage":"unavailable"},status_code=503)
@app.get("/ready")
def ready():
    try:
        with core.connect() as db:
            db.execute("SELECT 1")
        running=WORKER_JOB is not None and not WORKER_JOB.done()
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
            required={"contacts","opportunities","events","tasks","runs","memories","task_dependencies"}
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
            "company_worker_parallelism":WORKER_PARALLELISM,
            "product_operating_loops":"EXISTING_EVENTS_TASKS_WORKER"}
        return payload if ok else JSONResponse(payload,status_code=503)
    except Exception as exc:
        return JSONResponse({"ok":False,"error":type(exc).__name__},status_code=503)

@app.post("/api/intake")
async def intake(data:Intake,request:Request):
    if data.website.strip():
        return {"accepted":True}
    client_hash=authorize_public_intake_proxy(request)
    throttle(request,client_hash)
    if not data.consent:
        raise HTTPException(400,"Consent is required.")
    email=core.clean(data.email,254).lower()
    local_part,separator,domain=email.partition("@")
    if (not separator or not local_part or not domain or any(char.isspace() for char in email)
        or "." not in domain or domain.startswith(".") or domain.endswith(".")):
        raise HTTPException(400,"Enter a valid email.")
    if data.idempotency_key and not re.fullmatch(r"[A-Za-z0-9._:-]{8,64}",data.idempotency_key):
        raise HTTPException(400,"Invalid idempotency key.")
    brand=data.brand if data.brand in core.BRANDS else "noetfield"
    audience=data.audience if data.audience in core.AUDIENCES else "other"
    intent=data.intent if data.intent in core.INTENTS else "other"
    urgency=data.urgency if data.urgency in {"now","30_days","quarter","exploring"} else "exploring"
    payload=data.model_dump()
    payload.update({"brand":brand,"audience":audience,"intent":intent,"urgency":urgency,
      "name":core.clean(data.name,120),"email":email,
      "company":core.clean(data.company,140),"role":core.clean(data.role,100),
      "problem":core.clean(data.problem,2500),"ai_consent":bool(data.ai_consent)})
    route,_,_=core.route_for(brand,audience,intent)
    event_id=core.add_event("intake.received",
        "company_os_staging_proxy" if client_hash else "public_web",
        brand,payload,idempotency_key=data.idempotency_key)
    return JSONResponse({"accepted":True,"reference":event_id,"route":route,
      "idempotent":bool(data.idempotency_key),
      "message":"Request accepted and queued for its specialist workflow."},status_code=202)

@app.post("/api/feedback")
async def feedback(data:Feedback,request:Request):
    throttle(request)
    if not data.consent: raise HTTPException(400,"Consent is required.")
    brand=data.brand if data.brand in core.BRANDS else "noetfield"
    event_id=core.add_event("feedback.received","public_feedback",brand,
      {"brand":brand,"rating":data.rating,"comment":core.clean(data.comment,2000)})
    return JSONResponse({"accepted":True,"reference":event_id},status_code=202)

@app.get("/api/control/product-programs")
def product_programs(authorization:str|None=Header(default=None),company_id:str|None=None):
    authorize(authorization)
    try:
        return product_loops.portfolio(company_id)
    except ValueError as exc:
        raise HTTPException(400,str(exc)) from None

@app.post("/api/control/product-programs")
def create_product_program(payload:ProductProgram,authorization:str|None=Header(default=None)):
    authorize(authorization)
    try:
        return product_loops.register(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(409 if "existing_product" in str(exc) else 400,str(exc)) from None

@app.post("/api/control/product-observations")
def submit_product_observation(payload:ProductObservation,authorization:str|None=Header(default=None)):
    authorize(authorization)
    body=payload.model_dump(exclude_none=True)
    company,project=body.pop("company_id"),body.pop("project_id")
    try:
        result=product_loops.observe(company,project,body)
    except ValueError as exc:
        raise HTTPException(409 if ("conflicts" in str(exc) or "not_operational" in str(exc)) else 400,str(exc)) from None
    return JSONResponse({"accepted":True,**result,"external_actions":"NOT_AUTHORIZED",
                         "real_user_traction_verified":False},
                        status_code=200 if result["idempotent"] else 202)

class PaperclipBacklog(BaseModel):
    model_config=ConfigDict(extra="forbid")
    title:str=Field(min_length=12,max_length=140)
    objective:str=Field(min_length=12,max_length=1100)
    source_ref:str=Field(min_length=12,max_length=300)
    idempotency_key:str=Field(min_length=12,max_length=100,pattern=r"^[A-Za-z0-9._:-]+$")

@app.get("/api/control/paperclip/status")
def paperclip_status(authorization:str|None=Header(default=None)):
    authorize(authorization)
    return paperclip.status()

@app.get("/api/control/paperclip/snapshot")
def paperclip_snapshot(authorization:str|None=Header(default=None)):
    authorize(authorization)
    try:
        return paperclip.snapshot()
    except paperclip.PaperclipError as exc:
        raise HTTPException(exc.http_status,exc.code) from None

@app.post("/api/control/paperclip/backlog")
def paperclip_backlog(body:PaperclipBacklog,authorization:str|None=Header(default=None)):
    authorize(authorization)
    try:
        with core.connect() as db:
            return paperclip.submit_backlog(
                db,title=body.title,objective=body.objective,source_ref=body.source_ref,
                idempotency_key=body.idempotency_key
            )
    except paperclip.PaperclipError as exc:
        raise HTTPException(exc.http_status,exc.code) from None

@app.get("/api/control/overview")
def overview(authorization:str|None=Header(default=None)):
    authorize(authorization)
    result=core.overview()
    result.update({"worker_interval_seconds":INTERVAL,
      "llm_configured":bool(os.getenv("LLM_BASE_URL") and os.getenv("LLM_API_KEY") and os.getenv("LLM_MODEL")),
      "policy":"Analysis and internal reversible tasks are autonomous. External messaging, payments, deployments, legal/investment commitments require Founder approval."})
    return result
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

# NEXUS commercial bridge: narrowly scoped, PII-free input to the CANONICAL Company OS queue.
# No founder token delegation, payment authority, new scheduler, CRM, or autonomous outbound action.
class NexusGrowthObservation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    source_event_id:str=Field(pattern=r"^nexus\.(lead\.nxlead_[0-9a-f]{32}|order\.nx_[0-9a-f]{32}\.(created|paid))$",min_length=32,max_length=128)
    source_kind:str
    source_ref:str=Field(min_length=20,max_length=220)
    signal:str
    summary:str=Field(min_length=12,max_length=500)
    severity:int=Field(default=2,ge=0,le=4)
    observed_at:str
    metric_name:str
    metric_value:float=Field(ge=0,le=1)
    sample_count:int=Field(ge=0,le=1)

@app.post("/api/integrations/nexus/observations")
def nexus_growth_observation(payload:NexusGrowthObservation,x_nexus_bridge_token:str|None=Header(default=None)):
    expected=os.environ.get("COMPANY_OS_NEXUS_OBSERVATION_TOKEN","")
    if len(expected)<32:
        raise HTTPException(503,"NEXUS growth bridge not configured")
    if not x_nexus_bridge_token or not hmac.compare_digest(x_nexus_bridge_token,expected):
        raise HTTPException(401,"NEXUS bridge authentication required")
    data=payload.model_dump()
    eid=data["source_event_id"]
    if eid.startswith("nexus.lead."):
        expected_signal=("acquisition","inbound_inquiries",
                         "nexus:growth-lead:"+eid.removeprefix("nexus.lead."))
    elif eid.endswith(".created"):
        expected_signal=("conversion","orders_created",
                         "nexus:economic-order:"+eid.removeprefix("nexus.order.").removesuffix(".created"))
    elif eid.endswith(".paid"):
        expected_signal=("revenue","stripe_paid_reported",
                         "nexus:economic-order:"+eid.removeprefix("nexus.order.").removesuffix(".paid"))
    else:
        raise HTTPException(422,"Unknown NEXUS event kind")
    if (data["source_kind"]!="REPORTED_OPERATIONAL" or
        data["signal"]!=expected_signal[0] or
        data["metric_name"]!=expected_signal[1] or
        data["metric_value"]!=1 or data["sample_count"]!=1 or
        data["source_ref"]!=expected_signal[2]):
        raise HTTPException(422,"NEXUS source event mismatch")
    try:
        outcome=product_loops.observe("noetfield-systems-inc","nexus-economic-rail",data)
    except ValueError as exc:
        raise HTTPException(409 if "not_operational" in str(exc) else 422,str(exc)) from None
    return JSONResponse({"accepted":True,**outcome,
                         "company_id":"noetfield-systems-inc","project_id":"nexus-economic-rail",
                         "canonical_queue":True,"external_actions":"FOUNDER_RESERVED",
                         "real_user_traction_verified":False},
                        status_code=200 if outcome["idempotent"] else 202)

@app.get("/api/integrations/nexus/status")
def nexus_bridge_status(x_nexus_bridge_token:str|None=Header(default=None)):
    expected=os.environ.get("COMPANY_OS_NEXUS_OBSERVATION_TOKEN","")
    if len(expected)<32:
        raise HTTPException(503,"NEXUS growth bridge not configured")
    if not x_nexus_bridge_token or not hmac.compare_digest(x_nexus_bridge_token,expected):
        raise HTTPException(401,"NEXUS bridge authentication required")
    with core.connect() as db:
        row=db.execute("SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
                       ("noetfield-systems-inc","nexus-economic-rail")).fetchone()
    return {"ready":bool(row and row["status"]=="INTERNAL_ACTIVE"),
            "program":"nexus-economic-rail",
            "canonical_queue":"existing_company_os_events_tasks",
            "outbound_marketing":"FOUNDER_APPROVAL_REQUIRED",
            "verified_customer_revenue":None}
