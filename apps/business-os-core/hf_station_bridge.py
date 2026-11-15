"""Company OS owner-side connector for the existing SINA HF compute station.

No new agent dispatcher, scheduler, verified outcome or Governor. External HF
inference is only a bounded authorized founder/Company OS subtask.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import re
import time
from datetime import datetime, timezone
from urllib import request, error

STATION_URL="https://sina-hf-station-production.up.railway.app"
ID=re.compile(r"^[a-zA-Z0-9_.:-]{3,128}$")
MAX_INPUT=6500
MAX_CALLBACK=14000
class StationError(ValueError): pass

def configured():
    return len(os.getenv("HF_STATION_INGRESS_KEY",""))>=32

def init(db):
    db.execute("""CREATE TABLE IF NOT EXISTS hf_station_missions(
      workpacket_id TEXT PRIMARY KEY,
      task_id TEXT NOT NULL,
      company_id TEXT NOT NULL,
      project_id TEXT NOT NULL,
      role_id TEXT NOT NULL,
      packet_hash TEXT NOT NULL,
      state TEXT NOT NULL,
      output_hash TEXT,
      raw_projection TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL)""")
    db.execute("CREATE INDEX IF NOT EXISTS hf_station_task_idx ON hf_station_missions(task_id)")

def _stamp():
    return datetime.now(timezone.utc).isoformat()
def _sign(secret,ts,raw):
    return hmac.new(secret.encode(),b"hf-station.v3\n"+str(ts).encode()+b"\n"+raw,hashlib.sha256).hexdigest()

def _http(path,method="GET",body=None):
    if not configured():raise StationError("STATION_INGRESS_NOT_CONFIGURED")
    if path not in ("/health","/v1/status","/v1/roles","/v1/plan","/v1/jobs","/v1/outbox/flush"):
        raise StationError("UNKNOWN_STATION_ROUTE")
    raw=None if body is None else json.dumps(body,sort_keys=True,separators=(",",":")).encode()
    headers={"Accept":"application/json","Authorization":"Bearer "+os.environ["HF_STATION_INGRESS_KEY"]}
    if raw is not None:
        ts=str(int(time.time()))
        headers.update({"Content-Type":"application/json","X-Station-Timestamp":ts,
                        "X-Station-Signature":_sign(os.environ["HF_STATION_INGRESS_KEY"],ts,raw)})
    req=request.Request(STATION_URL+path,data=raw,method=method,headers=headers)
    try:
        with request.urlopen(req,timeout=65 if path=="/v1/jobs" else 9) as resp:
            data=resp.read(96000)
            if resp.status not in (200,201,202) or len(data)>=96000:
                raise StationError("STATION_RESPONSE_UNACCEPTABLE")
            return json.loads(data)
    except error.HTTPError as exc:
        raise StationError("STATION_HTTP_"+str(exc.code)) from None
    except (error.URLError,OSError,ValueError,TypeError):
        raise StationError("STATION_TRANSPORT_OR_SCHEMA_ERROR") from None

def _validate_request(data):
    expected={"task_id","role_id","goal_id","decision_ref","expires_at","prompt","max_cost_usd","max_tokens"}
    if not isinstance(data,dict) or set(data)-expected:
        raise StationError("INVALID_COMPUTE_REQUEST")
    for k in ("task_id","role_id","goal_id","decision_ref"):
        if not isinstance(data.get(k),str) or not ID.fullmatch(data[k]):
            raise StationError("INVALID_"+k.upper())
    if not isinstance(data.get("prompt"),str) or not data["prompt"].strip() or len(data["prompt"])>MAX_INPUT:
        raise StationError("INVALID_SANITIZED_PROMPT")
    if "@" in data["prompt"] or "Bearer " in data["prompt"] or "api_key" in data["prompt"].lower():
        raise StationError("UNSANITIZED_INPUT_DENIED")
    if type(data.get("max_cost_usd")) not in (int,float) or not 0 < data["max_cost_usd"]<=0.035:
        raise StationError("INVALID_COST_ENVELOPE")
    if type(data.get("max_tokens",256)) is not int or not 1<=data.get("max_tokens",256)<=512:
        raise StationError("INVALID_TOKEN_LIMIT")
    try:
        exp=datetime.fromisoformat(data["expires_at"].replace("Z","+00:00"))
        if exp.tzinfo is None or exp.timestamp()<=time.time():
            raise StationError("EXPIRED_WORKPACKET")
    except (AttributeError,ValueError,TypeError,OverflowError):
        raise StationError("INVALID_EXPIRY") from None
    return data

def _owning_task(db, task_id):
    init(db)
    # Use the REAL authenticated Goalkeeper decision bound to the real
    # Company OS task. The legacy sina_workstream_bindings table is not the
    # active Agent Fabric work queue and is not an execution permit.
    row=db.execute("""SELECT t.id,t.company_id,t.project_id,t.status,
          d.decision_ref,d.disposition
        FROM tasks t JOIN venture_company_os_decisions d
          ON d.task_id=t.id AND d.company_id=t.company_id
          AND d.project_id=t.project_id
        WHERE t.id=? AND d.disposition IN (
          'PROCEED_IN_LOCAL_COMPANY_OS','CHECK_EVIDENCE_AND_CONTINUE',
          'CLARIFY_FROM_EVIDENCE_NOT_FOUNDER','RESEARCH_IN_LOCAL_COMPANY_OS')
        ORDER BY d.updated_at DESC LIMIT 1""",(task_id,)).fetchone()
    if not row:raise StationError("AUTHENTICATED_GOALKEEPER_TASK_NOT_FOUND")
    if row["company_id"] not in ("noetfield-systems-inc","founder-portfolio"):
        raise StationError("CROSS_COMPANY_TASK_DENIED")
    program=db.execute("""SELECT status FROM product_programs
        WHERE company_id=? AND project_id=?""",(row["company_id"],row["project_id"])).fetchone()
    if not program or program["status"] not in ("INTERNAL_ACTIVE","FOUNDER_PROJECT_ACTIVE_NOT_LEGAL_TENANT"):
        raise StationError("PROJECT_NOT_ACTIVE")
    return row

def dispatch(data):
    """Use only an existing canonical owned task; never mint a new OS mission."""
    import core
    data=_validate_request(data)
    if not configured():raise StationError("STATION_INGRESS_NOT_CONFIGURED")
    with core.connect() as db:
        row=_owning_task(db,data["task_id"])
        if row["decision_ref"]!=data["decision_ref"]:
            raise StationError("GOALKEEPER_DECISION_REF_MISMATCH")
        workpacket_id=data["task_id"]+"-hf-"+data["role_id"]
        if len(workpacket_id)>128:raise StationError("WORKPACKET_ID_TOO_LONG")
        packet={"workpacket_id":workpacket_id,"tenant_id":row["company_id"],
          "project_id":row["project_id"],"goal_id":data["goal_id"],
          "decision_ref":row["decision_ref"],"nac_workpacket_ref":None,
          "authorization_mode":"SINA_GOALKEEPER_A0_ANALYSIS",
          "role_id":data["role_id"],"expires_at":data["expires_at"],
          "data_classification":"approved_sanitized","max_cost_usd":data["max_cost_usd"],
          "authorized":True,"input":{"prompt":data["prompt"]},"max_tokens":data.get("max_tokens",256)}
        raw=json.dumps(packet,sort_keys=True,separators=(",",":")).encode()
        sha=hashlib.sha256(raw).hexdigest()
        now=_stamp()
        old=db.execute("SELECT packet_hash FROM hf_station_missions WHERE workpacket_id=?",(workpacket_id,)).fetchone()
        if old and old["packet_hash"]!=sha:raise StationError("WORKPACKET_REPLAY_CONFLICT")
        if not old:
            db.execute("""INSERT INTO hf_station_missions
             (workpacket_id,task_id,company_id,project_id,role_id,packet_hash,state,created_at,updated_at)
             VALUES (?,?,?,?,?,?,'REQUESTED',?,?)""",
             (workpacket_id,data["task_id"],row["company_id"],row["project_id"],data["role_id"],sha,now,now))
    result=_http("/v1/jobs","POST",packet)
    # The remote station has a separate idempotency store. Never infer
    # deployment, code execution, actual dollars or independent verification.
    return {"schema":"company-os.hf-station.dispatch.v1",
      "workpacket_id":workpacket_id,"task_id":data["task_id"],
      "status":result.get("status"),"verification":"SOURCE_REPORTED_UNVERIFIED",
      "station_output_sha256":result.get("output_sha256"),
      "provider_report":result.get("provider_receipt"),
      "reason":result.get("reason"),
      "response":result}

def callback_authorized(auth):
    expected=os.getenv("HF_STATION_CALLBACK_TOKEN","")
    supplied=(auth or "").removeprefix("Bearer ").strip()
    return len(expected)>=40 and bool(supplied) and hmac.compare_digest(expected,supplied)

def receive_projection(payload):
    import core
    required={"schema","workpacket_id","tenant_id","project_id","role_id",
              "decision_ref","nac_workpacket_ref","status","output_sha256",
              "provider_receipt","cost_usd","verification"}
    if not isinstance(payload,dict) or set(payload)!=required:
        raise StationError("INVALID_CALLBACK_SCHEMA")
    if payload["schema"]!="sina.hf-station.result-projection.v1":
        raise StationError("UNKNOWN_CALLBACK_SCHEMA")
    if payload["verification"]!="SOURCE_REPORTED_UNVERIFIED" or payload["cost_usd"] is not None:
        raise StationError("UNVERIFIED_COST_OR_PROOF_DENIED")
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"))
    if len(raw)>MAX_CALLBACK:raise StationError("CALLBACK_TOO_LARGE")
    if payload["status"] not in ("INFERENCE_RETURNED","FAILED","BLOCKED","PROVIDER_UNAVAILABLE"):
        raise StationError("INVALID_STATION_STATUS")
    with core.connect() as db:
        init(db)
        row=db.execute("""SELECT company_id,project_id,role_id,raw_projection
            FROM hf_station_missions WHERE workpacket_id=?""",(payload["workpacket_id"],)).fetchone()
        if not row:raise StationError("UNKNOWN_WORKPACKET")
        if (payload["tenant_id"]!=row["company_id"] or payload["project_id"]!=row["project_id"] or
              payload["role_id"]!=row["role_id"]):
            raise StationError("TENANT_OR_ROLE_MISMATCH")
        if row["raw_projection"] and row["raw_projection"]!=raw:
            raise StationError("CONFLICTING_CALLBACK")
        db.execute("""UPDATE hf_station_missions SET state=?,output_hash=?,
                 raw_projection=?,updated_at=? WHERE workpacket_id=?""",
                 (payload["status"],payload["output_sha256"],raw,_stamp(),payload["workpacket_id"]))
    return {"accepted":True,"idempotent":bool(row["raw_projection"]),
            "verification":"SOURCE_REPORTED_UNVERIFIED","workpacket_id":payload["workpacket_id"]}

def status():
    import core
    with core.connect() as db:
        init(db)
        rows=db.execute("SELECT state,COUNT(*) n FROM hf_station_missions GROUP BY state").fetchall()
    return {"provider":"SINA-HF-STATION","station_configured":configured(),
      "callback_configured":len(os.getenv("HF_STATION_CALLBACK_TOKEN",""))>=40,
      "owner":"Existing Company OS","role_declaration_count":24,
      "outcomes_by_state":{r["state"]:r["n"] for r in rows},
      "independent_verification":"REQUIRES_EXTERNAL_VERIFIER"}

def flush():
    # Only retries preexisting station outbox; never creates new work.
    return _http("/v1/outbox/flush","POST",{} )


def recommend(data):
    """Only rank real existing owner tasks with evidence; never create or spend."""
    import core
    if not isinstance(data,dict) or set(data)-{"task_id","signal_kind","evidence_refs","severity"}:
        raise StationError("INVALID_SIGNAL_REQUEST")
    task=data.get("task_id")
    if not isinstance(task,str) or not ID.fullmatch(task):
        raise StationError("INVALID_TASK_ID")
    if not isinstance(data.get("signal_kind"),str) or len(data["signal_kind"])>50:
        raise StationError("INVALID_SIGNAL_KIND")
    refs=data.get("evidence_refs")
    if not isinstance(refs,list) or len(refs)>6 or any(
        not isinstance(x,str) or not ID.fullmatch(x) for x in refs):
        raise StationError("INVALID_EVIDENCE_REFS")
    severity=data.get("severity",2)
    if type(severity) is not int or not 0<=severity<=4:
        raise StationError("INVALID_SEVERITY")
    with core.connect() as db:
        row=_owning_task(db,task)
    return _http("/v1/plan","POST",{
        "tenant_id":row["company_id"],"project_id":row["project_id"],
        "owner_task_ref":task,"signal_kind":data["signal_kind"],
        "evidence_refs":refs,"severity":severity})
