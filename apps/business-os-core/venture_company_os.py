"""Venture-native Company OS instances on the EXISTING Noetfield Company OS runtime.

Sina Founder OS owns the portfolio and sends strategic intent; it is NOT the
executive team of each product. Every active project has a durable, isolated
operating identity, its own executive director, specialist remits, mission,
cadence, scoped memory, operating evidence and canonical task pipeline.

This deliberately reuses core events/tasks/runs, product_loops, Agent Fabric,
Governor, Paperclip and independent verification. It does not invent a legal
entity, duplicate agent registry, grant a production permit or pretend a
single shared cloud service means isolated infrastructure.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
from datetime import datetime, timezone

SCHEMA="noetfield.company-os.venture-instance.v1"
ACTIVE={"INTERNAL_ACTIVE","FOUNDER_PROJECT_ACTIVE_NOT_LEGAL_TENANT"}
# Project-specific operating doctrine, NOT a replacement portfolio registry.
# Sources and repos are evidence hints for specialist research; never write permits.
DOCTRINE={
 "noetfield-web3-launchpad":("creator_web3","RHEVO creator onboarding, Devnet mint verification, legitimate discovery and creator retention","Noetfield-Systems/sina_founder_os/apps/web3-launchpad"),
 "cairn-season-0":("community_web3","Cairn BNB Season 0 participation, free creator quests, authentic referral and playable onboarding","railway:cairn"),
 "buildrelay-bridge-economy":("founder_network","BuildRelay contributor missions, founder matching, real collaboration and repeat participation","Noetfield-Systems/BuildRelay"),
 "trade-radar":("market_intelligence","Trade Radar source-linked market research, free educational utilities and subscriber value","Noetfield-Systems/TRADE-RADAR"),
 "trade-radar-platform":("market_intelligence","Trade Radar source-linked market research, free educational utilities and subscriber value","Noetfield-Systems/TRADE-RADAR"),
 "signalforge":("market_intelligence","SignalForge signal quality, source provenance, onboarding, user retention and paid research","railway:signalforge-ai"),
 "signal-forge":("market_intelligence","SignalForge signal quality, source provenance, onboarding, user retention and paid research","railway:signalforge-ai"),
 "social-games-lab":("social_games","Playable cooperative games, recurring challenges, real player retention and friend invitation","railway:company-os"),
 "noetfield-earnloop":("rewards_economy","EarnLoop earn, redeem, refer, legitimate offerwall economics and authentic community","Noetfield-Systems/sina_founder_os/apps/earnloop"),
 "venture-formation-lab":("founder_network","Founder team formation, authenticated contributions, matching and community retention","Noetfield-Systems/venture-formation-lab"),
 "atelier":("community","Atelier consensual adult community activation, matching and privacy","Noetfield-Systems/Atelier"),
 "buildworkflow-field-change-handoff":("saas","BuildWorkflow contractor workflow completion, verified handoff and paid buyer value","railway:fieldchange-desk"),
 "trading-exchange-lab":("market_intelligence","Client exchange research, testnet integration and transparent price discovery","railway:company-os"),
 "client-exchange-platform":("market_intelligence","Client exchange research, testnet integration and transparent price discovery","railway:company-os"),
 "founders-room-messenger":("messaging","Founders Room private messaging, trusted invitations and authentic returning founders","railway:venture-formation-lab"),
 "room-private-messaging":("messaging","Founders Room private messaging, trusted invitations and authentic returning founders","Noetfield-Systems/Room"),
}
ROLE_FOCUS={
 "chief_of_staff":"Act as this product's executive director. Review the local product's evidence, order engineering, growth and customer priorities, and track unresolved dependencies.",
 "engineering_operator":"Inspect the designated product code and release quality. Specify actual changes, acceptance criteria, bounded implementation and source-linked next steps.",
 "product_strategy":"Own this product's UX, feature choices, onboarding and activation. Prioritize a measurable release rather than generic corporate strategy.",
 "market_intelligence":"Investigate this product's actual competitors, real demand, technical alternatives and externally verifiable source information.",
 "marketing_content":"Own product-specific organic distribution, conversion experiments, shareable utility and truthful user acquisition.",
 "sales_qualification":"Own product-specific buying intent, real paid conversion and evidence-backed pricing; never fabricate sales.",
 "customer_success":"Own this product's real user friction, onboarding, community quality, retention and feedback loops.",
 "risk_governance":"Check this product's privacy, security, token and financial authority boundaries without blocking ordinary internal coding.",
 "roi_analyst":"Track this product's actual cost per delivery, economic conversion and cash-margin evidence separate from credits and hypothetical value.",
 "partnerships":"Explore product-specific partner distribution and integrations without unapproved outreach.",
}
TEAM_BY_DOMAIN={
 "creator_web3":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","risk_governance","roi_analyst"),
 "community_web3":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","risk_governance"),
 "rewards_economy":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","roi_analyst","risk_governance"),
 "social_games":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","risk_governance"),
 "market_intelligence":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","roi_analyst","risk_governance"),
 "founder_network":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","partnerships","roi_analyst"),
 "messaging":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","risk_governance"),
 "community":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","risk_governance"),
 "saas":("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","sales_qualification","roi_analyst"),
}
DEFAULT_TEAM=("chief_of_staff","engineering_operator","product_strategy","market_intelligence","marketing_content","customer_success","risk_governance")
# A stable person-to-role mapping on the ORIGINAL local Company OS executive.
# The alias is NOT a Paperclip commissioned agent, a legal entity, or a new
# runtime. Only original model runs created after this mapping is passed into
# the real inference request can demonstrate the named person participated.
NAMED_MANAGER_SEATS={
    ("founder-portfolio","buildrelay-bridge-economy"):{
        "actor_id":"gm-buildrelay-farid",
        "display_name":"Farid",
        "role":"chief_of_staff",
        "reports_to_actor_id":"sina-founder-os",
        "mandate":"BuildRelay's real founder activation, matching, seven-day collaborations, referral growth and bilateral evidence, retaining Web3 Season 0 original Founder mission",
    }
}

def named_manager(company,project,role):
    """Person identity for a mapped *real* local company role, not a new agent."""
    seat=NAMED_MANAGER_SEATS.get((company,project))
    return dict(seat) if seat and role==seat["role"] else None


INTERVAL_SECONDS=300
MAX_ACTIVE_TASKS=10
GLOBAL_BACKPRESSURE=80

def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def instance_id(company,project):
    return "vcos_"+hashlib.sha256((company+":"+project).encode()).hexdigest()[:20]

def doctrine(project,vertical):
    domain,focus,source=DOCTRINE.get(project,("saas","Product-specific engineering, onboarding, organic acquisition and measurable customer value","company-os:canonical-program"))
    return domain,focus,source

def init(db:sqlite3.Connection):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS venture_company_os(
      company_id TEXT NOT NULL,project_id TEXT NOT NULL,instance_id TEXT NOT NULL UNIQUE,
      director_role TEXT NOT NULL,domain TEXT NOT NULL,focus TEXT NOT NULL,source_asset TEXT NOT NULL,
      operating_objective TEXT NOT NULL,operating_state TEXT NOT NULL,last_heartbeat TEXT,
      created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
      PRIMARY KEY(company_id,project_id)
    );
    CREATE TABLE IF NOT EXISTS venture_company_os_specialists(
      company_id TEXT NOT NULL,project_id TEXT NOT NULL,role TEXT NOT NULL,
      remit TEXT NOT NULL,created_at TEXT NOT NULL,
      PRIMARY KEY(company_id,project_id,role),
      FOREIGN KEY(company_id,project_id) REFERENCES venture_company_os(company_id,project_id)
    );
    CREATE INDEX IF NOT EXISTS idx_venture_os_state ON venture_company_os(operating_state,last_heartbeat);
    -- A bounded recovery ledger, NOT a task queue or a new autonomous worker.
    -- Original Company OS tasks and runs remain the source of truth.
    CREATE TABLE IF NOT EXISTS venture_company_os_manager_recovery(
      task_id TEXT PRIMARY KEY,
      manager_actor_id TEXT NOT NULL,
      original_failure_run_id TEXT NOT NULL,
      retried_at TEXT NOT NULL
    );
    -- Bounded cap-revision readmission bookkeeping, not a second task queue.
    CREATE TABLE IF NOT EXISTS venture_company_os_manager_capacity_recovery(
      task_id TEXT PRIMARY KEY,
      policy_revision TEXT NOT NULL,
      original_failure_run_id TEXT NOT NULL,
      retried_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS venture_company_os_mandates(
      company_id TEXT NOT NULL,project_id TEXT NOT NULL,
      founder_project_id TEXT NOT NULL,program_id TEXT NOT NULL,
      mission_id TEXT NOT NULL,objective TEXT NOT NULL,
      success_metric TEXT NOT NULL,priority_score INTEGER NOT NULL,
      payload_sha256 TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
      PRIMARY KEY(company_id,project_id,program_id),
      FOREIGN KEY(company_id,project_id) REFERENCES venture_company_os(company_id,project_id)
    );
    """)

def reconcile(db:sqlite3.Connection):
    """Materialize actual product-specific management/team scope, not new agents."""
    # Caller initializes the schema before transaction admission. An
    # executescript here would implicitly COMMIT a BEGIN IMMEDIATE transaction.
    rows=db.execute("SELECT * FROM product_programs ORDER BY company_id,project_id").fetchall()
    created=0
    for p in rows:
        if p["company_id"] not in ("noetfield-systems-inc","founder-portfolio"):
            continue
        company,project=p["company_id"],p["project_id"]
        domain,focus,source=doctrine(project,p["vertical"])
        existing=db.execute("SELECT instance_id FROM venture_company_os WHERE company_id=? AND project_id=?",
                            (company,project)).fetchone()
        state="ACTIVE_LOCAL_EXECUTIVE" if p["status"] in ACTIVE else "PAUSED"
        if existing is None:
            db.execute("""INSERT INTO venture_company_os VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(
                company,project,instance_id(company,project),"chief_of_staff",domain,
                focus,source,p["objective"],state,None,utc(),utc()))
            created+=1
        else:
            db.execute("""UPDATE venture_company_os SET operating_state=?,updated_at=?
                       WHERE company_id=? AND project_id=? AND operating_state!=?""",
                       (state,utc(),company,project,state))
        for role in TEAM_BY_DOMAIN.get(domain,DEFAULT_TEAM):
            remit=ROLE_FOCUS[role]+" Local focus: "+focus+"."
            db.execute("""INSERT OR IGNORE INTO venture_company_os_specialists
                (company_id,project_id,role,remit,created_at) VALUES(?,?,?,?,?)""",
                (company,project,role,remit,utc()))
    return {"instances_created":created,"instances_total":db.execute(
        "SELECT COUNT(*) FROM venture_company_os").fetchone()[0]}

def adopt_founder_mandate(item):
    """One portfolio objective enters the product's OWN Company OS.

    The Company OS, not Sina, decomposes that outcome through its local
    executive and specialist roles into canonical tasks. Founder never
    appoints per-project engineering or marketing agents through this feed.
    """
    import core
    import product_loops
    import sina_work_bridge
    import hashlib
    required={"schema","program_id","mission_id","project_id","company_id",
              "tenant_scope","objective","priority_score","success_metric",
              "authority","execution_owner","source_ref"}
    if not isinstance(item,dict) or set(item)!=required:
        raise ValueError("venture_mandate_shape_invalid")
    if item["schema"]!="sina.company-os.venture-mandate.v1" or (
        item["authority"]!="PORTFOLIO_DIRECTIVE_ONLY_NO_PERMIT" or
        item["execution_owner"]!="PROJECT_LOCAL_COMPANY_OS"):
        raise ValueError("venture_mandate_authority_invalid")
    scope=item["company_id"] or "founder-portfolio"
    if scope not in ("noetfield-systems-inc","founder-portfolio") or item["tenant_scope"]!=scope:
        raise ValueError("venture_mandate_tenant_invalid")
    if (not re.fullmatch(r"[a-f0-9]{32}",str(item["program_id"]))
        or not re.fullmatch(r"M[0-9]{2}-[A-Z0-9-]{3,58}",str(item["mission_id"]))
        or not re.fullmatch(r"[a-z][a-z0-9-]{2,90}",str(item["project_id"]))
        or not re.fullmatch(r"strategic:M[0-9]{2}-[A-Z0-9-]{3,58}:v[0-9]{1,4}",str(item["source_ref"]))):
        raise ValueError("venture_mandate_identity_invalid")
    if (not isinstance(item["objective"],str) or
        not 30<=len(item["objective"])<=1400 or
        not re.fullmatch(r"[a-z][a-z0-9_]{7,119}",str(item["success_metric"])) or
        type(item["priority_score"]) is not int or not 60<=item["priority_score"]<=100):
        raise ValueError("venture_mandate_goal_invalid")
    if "@" in item["objective"] or re.search(r"(?i)(bearer\s|api[_-]?key|password)",item["objective"]):
        raise ValueError("venture_mandate_private_text")
    # Resolve the product against independently fetched Founder SSOT; existing
    # internal operational aliases are reused, never cloned or cast as a new
    # legal tenant. The private source identity alone cannot invent projects.
    operational=sina_work_bridge._resolve_operating_project(
        scope,item["project_id"],{"priority_score":item["priority_score"]})
    digest=hashlib.sha256(json.dumps(item,sort_keys=True,
        ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    with core.connect() as db:
        init(db)
        db.execute("BEGIN IMMEDIATE")
        reconcile(db)
        local= db.execute(
            "SELECT instance_id,operating_state FROM venture_company_os "
            "WHERE company_id=? AND project_id=?",(scope,operational)).fetchone()
        if not local or local["operating_state"]!="ACTIVE_LOCAL_EXECUTIVE":
            db.rollback()
            raise ValueError("local_company_os_not_active")
        old=db.execute("SELECT payload_sha256 FROM venture_company_os_mandates "
            "WHERE company_id=? AND project_id=? AND program_id=?",
            (scope,operational,item["program_id"])).fetchone()
        if old and old["payload_sha256"]==digest:
            db.commit()
            return {"state":"UNCHANGED","company_os_instance_id":local["instance_id"]}
        db.execute("""INSERT INTO venture_company_os_mandates VALUES (?,?,?,?,?,?,?,?,?,?,?)
             ON CONFLICT(company_id,project_id,program_id) DO UPDATE SET
               objective=excluded.objective,success_metric=excluded.success_metric,
               priority_score=excluded.priority_score,payload_sha256=excluded.payload_sha256,
               updated_at=excluded.updated_at""",(
             scope,operational,item["project_id"],item["program_id"],
             item["mission_id"],item["objective"],item["success_metric"],
             item["priority_score"],digest,utc(),utc()))
        # The local Company OS director owns the product plan. This goal does
        # NOT become one specialist task per Founder departmental suggestion.
        db.execute("""UPDATE venture_company_os
           SET operating_objective=?,updated_at=? WHERE company_id=? AND project_id=?""",
           (item["objective"],utc(),scope,operational))
        # One local company-owned signal triggers its own developer, product,
        # customer and executive task graph. Changes are idempotent by digest.
        obs=product_loops._insert_observation(db,scope,operational,{
           "source_event_id":"company_mandate:"+item["program_id"]+":"+digest[:12],
           "source_kind":"REPORTED_OPERATIONAL",
           "source_ref":"company-os:portfolio-directive",
           "signal":"feature_request",
           "summary":("Local Company OS "+operational+" received strategic goal "+
             item["mission_id"]+". Its own director must plan engineering, "
             "onboarding and user evidence for the measurable outcome. "
             "No external authority or verified result is conveyed."),
           "severity":2,
        },verified=False)
        db.commit()
        return {"state":"ADOPTED_LOCAL_COMPANY_OS",
            "company_os_instance_id":local["instance_id"],
            "event_id":obs.get("event_id"),"external_actions":False}


def specialist(db,company,project,role):
    if not all(isinstance(x,str) for x in (company,project,role)):
        return None
    row=db.execute("""SELECT i.instance_id,i.focus,i.source_asset,i.operating_objective,
                 s.role,s.remit FROM venture_company_os i
                 JOIN venture_company_os_specialists s
                   ON s.company_id=i.company_id AND s.project_id=i.project_id
                 WHERE i.company_id=? AND i.project_id=? AND s.role=?
                 AND i.operating_state='ACTIVE_LOCAL_EXECUTIVE'""",
                 (company,project,role)).fetchone()
    return dict(row) if row else None

def _queue_first_named_manager_source_assignment(db):
    """One true source-backed BuildRelay manager assignment through the ORIGINAL
    Company OS observations/events/tasks queue. Never a fabricated member signal.

    Requires an accepted BuildRelay source observation OR a genuinely adopted
    Founder mandate with an exact source-bound digest. No existing members,
    analytics or partner records are required to start authorized internal work.
    This is an internal source triage task; it is NOT CEO mandate ACK, a
    Paperclip commissioning event, external delivery or manager success.
    """
    company,project="founder-portfolio","buildrelay-bridge-economy"
    seat=named_manager(company,project,"chief_of_staff")
    if seat is None:
        return {"state":"NO_NAMED_MANAGER_MAPPING","queued":False}
    local=db.execute("""SELECT operating_state FROM venture_company_os
        WHERE company_id=? AND project_id=?""",(company,project)).fetchone()
    if not local or local["operating_state"]!="ACTIVE_LOCAL_EXECUTIVE":
        return {"state":"LOCAL_MANAGER_NOT_ACTIVE","queued":False}
    event_key="manager-first-source:"+seat["actor_id"]+":v1"
    existing=db.execute("""SELECT id FROM product_observations
        WHERE company_id=? AND project_id=? AND source_event_id=?""",
        (company,project,event_key)).fetchone()
    if existing:
        return {"state":"ALREADY_QUEUED","queued":False,
                "new_observation_id":existing["id"],"actor_id":seat["actor_id"],
                "external_actions":False,"independently_verified":False}
    original=db.execute("""
        SELECT id,source_event_id,metric_name,verification
        FROM product_observations
        WHERE company_id=? AND project_id=?
          AND source_event_id LIKE 'br-%'
          AND source_kind='REPORTED_OPERATIONAL'
        ORDER BY recorded_at DESC,id DESC LIMIT 1
    """,(company,project)).fetchone()
    source_kind="BUILDRELAY_OPERATIONAL_OBSERVATION"
    if original is None:
        # First use must not require a pre-existing member/analytics cohort.
        # A genuinely adopted, source-bound Founder mandate is enough to
        # request an INTERNAL investigation by the named Company OS manager.
        # Require the canonical mandate digest so an arbitrary observation
        # or a model-supplied "company_mandate:" label cannot commission work.
        original=db.execute("""
            SELECT o.id,o.source_event_id,o.metric_name,o.verification
            FROM venture_company_os_mandates m
            JOIN product_observations o
              ON o.company_id=m.company_id AND o.project_id=m.project_id
             AND o.source_event_id=(
                 'company_mandate:' || m.program_id || ':' ||
                 substr(m.payload_sha256,1,12))
            WHERE m.company_id=? AND m.project_id=?
              AND o.source_kind='REPORTED_OPERATIONAL'
            ORDER BY m.updated_at DESC,o.recorded_at DESC,o.id DESC LIMIT 1
        """,(company,project)).fetchone()
        source_kind="ORIGINAL_FOUNDER_MANDATE"
    if not original:
        return {"state":"NO_AUTHENTIC_MANAGER_SOURCE_OR_FOUNDER_MANDATE",
                "queued":False}
    # Reserve only one original source-derived event for this stable seat;
    # process_signal decides which existing specialist tasks to create.
    import product_loops
    result=product_loops._insert_observation(db,company,project,{
        "source_event_id":event_key,
        "source_kind":"REPORTED_OPERATIONAL",
        "source_ref":"company-os:buildrelay-source-manager-assignment",
        "signal":"feature_request",
        "summary":(
            "BuildRelay local manager "+seat["actor_id"]+
            " must acknowledge and investigate authenticated "+source_kind+
            " source "+original["source_event_id"]+
            " and choose a useful first member activation or collaboration "+
            "task with measurable evidence and proper specialist owner. "+
            "This is operational triage, not verified member growth, "+
            "deployment, cash or independent verification."
        )[:500],
        "severity":2,
    },verified=False)
    return {
        "state":"ALREADY_QUEUED" if result.get("idempotent") else "QUEUED_IN_ORIGINAL_COMPANY_OS",
        "queued":not result.get("idempotent",False),
        "original_source_observation_id":original["id"],
        "original_event_id":original["source_event_id"],
        "original_source_kind":source_kind,
        "new_observation_id":result.get("observation_id"),
        "original_queue_event_id":result.get("event_id"),
        "actor_id":seat["actor_id"],
        "external_actions":False,
        "independently_verified":False,
    }


def _queue_manager_source_followup(db):
    """One source-backed INTERNAL follow-up from a real BuildRelay GM model run.

    No independent verification is inferred. This consumes only a first-GM
    source case and never recursively generates more follow-up events.
    The ORIGINAL product observations/events/tasks pipeline owns all work.
    """
    company,project="founder-portfolio","buildrelay-bridge-economy"
    seat=named_manager(company,project,"chief_of_staff")
    if not seat:
        return {"state":"GM_IDENTITY_UNMAPPED","queued":False}
    followup_id="manager-followup:"+seat["actor_id"]+":v1"
    existing=db.execute("""SELECT id FROM product_observations
        WHERE company_id=? AND project_id=? AND source_event_id=?""",
        (company,project,followup_id)).fetchone()
    if existing:
        return {"state":"FOLLOWUP_ALREADY_QUEUED","queued":False,
                "source_observation_id":existing["id"],
                "independent_verification":False}
    source_id="manager-first-source:"+seat["actor_id"]+":v1"
    rows=db.execute("""
        SELECT r.id AS run_id,r.result AS run_result,r.provider,
               t.id AS task_id,t.status AS task_status
        FROM runs r JOIN tasks t ON t.id=r.task_id
        JOIN product_observations o ON o.id=t.observation_id
        WHERE t.company_id=? AND t.project_id=? AND t.role='chief_of_staff'
          AND o.company_id=? AND o.project_id=?
          AND o.source_event_id=? AND r.role='chief_of_staff'
          AND r.status='completed' AND t.status IN ('drafted','approved')
        ORDER BY r.finished_at ASC,r.id ASC LIMIT 8
    """,(company,project,company,project,source_id)).fetchall()
    for row in rows:
        if not (str(row["provider"] or "").startswith("sina-")
                or row["provider"]=="openai-compatible"):
            continue
        try:
            output=json.loads(row["run_result"] or "{}")
        except (TypeError,ValueError):
            continue
        if (not isinstance(output,dict)
                or output.get("manager_actor_id")!=seat["actor_id"]
                or output.get("external_execution_verified") is not False
                or output.get("independent_business_outcome_verified") is not False):
            continue
        proposal=output.get("next_best_action")
        if (not isinstance(proposal,str) or not 24<=len(proposal.strip())<=500
                or "@" in proposal
                or re.search(r"(?i)(bearer\\s|password|api[_-]?key|secret\\s*[:=])",proposal)):
            continue
        # Model output is an untrusted proposal, never execution authority.
        # Preserve original run references without relaying raw instructions.
        import product_loops
        receipt=product_loops._insert_observation(db,company,project,{
            "source_event_id":followup_id,
            "source_kind":"REPORTED_OPERATIONAL",
            "source_ref":"company-os:run:"+row["run_id"],
            "signal":"feature_request",
            "summary":(
                "Following original BuildRelay GM model run "+row["run_id"]+
                ", inspect its recorded next_best_action, first manager task "+
                row["task_id"]+", and actual user or code evidence. Choose one "
                "bounded internal improvement. No outreach, payment, deployment, "
                "token issuance or independent success is authorized."
            )[:500],
            "severity":2,
        },verified=False)
        return {
            "state":"SOURCE_BACKED_MANAGER_FOLLOWUP_QUEUED" if not receipt.get("idempotent")
                    else "FOLLOWUP_ALREADY_QUEUED",
            "queued":not receipt.get("idempotent",False),
            "original_manager_run_id":row["run_id"],
            "original_manager_task_id":row["task_id"],
            "actor_id":seat["actor_id"],
            "source_observation_id":receipt["observation_id"],
            "original_queue_event_id":receipt.get("event_id"),
            "independent_verification":False,"external_actions":False,
        }
    return {"state":"WAITING_FOR_REAL_MANAGER_MODEL_REPLY","queued":False}


def _recover_named_manager_tasks(db,limit=3):
    """Retry a failed named BuildRelay management-chain task ONCE in the original queue.

    This never creates a new task, permit, model call, customer event or success.
    Original CEO-mandate or BuildRelay-source provenance must be present.
    Retry candidates have a real failed model run, an elapsed cooldown, an
    ACTIVE local company, and existing configured specialist inference.
    """
    import sina_work_bridge
    actor="gm-buildrelay-farid"
    company,project="founder-portfolio","buildrelay-bridge-economy"
    if named_manager(company,project,"chief_of_staff") is None:
        return {"state":"NO_NAMED_MANAGER_MAPPING","requeued_count":0}
    if not sina_work_bridge.specialist_configured():
        return {"state":"SPECIALIST_PROVIDER_NOT_CONFIGURED","requeued_count":0}
    local=db.execute("""SELECT operating_state FROM venture_company_os
        WHERE company_id=? AND project_id=?""",(company,project)).fetchone()
    if not local or local["operating_state"]!="ACTIVE_LOCAL_EXECUTIVE":
        return {"state":"MANAGER_SCOPE_NOT_ACTIVE","requeued_count":0}
    rows=db.execute("""
        SELECT t.id AS task_id,r.id AS failed_run_id,r.result AS failure_result
        FROM tasks t JOIN product_observations o
          ON o.id=t.observation_id AND o.company_id=t.company_id
         AND o.project_id=t.project_id
        JOIN runs r ON r.task_id=t.id
        WHERE t.company_id=? AND t.project_id=? AND t.status='drafted'
          AND (o.source_event_id='manager-first-source:gm-buildrelay-farid:v1'
               OR o.source_event_id LIKE 'company_mandate:%')
          AND r.id=(SELECT r2.id FROM runs r2 WHERE r2.task_id=t.id
                    ORDER BY r2.finished_at DESC,r2.id DESC LIMIT 1)
          AND r.provider='specialist_degraded'
          AND datetime(t.updated_at)<datetime('now','-2 minutes')
          AND NOT EXISTS (
             SELECT 1 FROM venture_company_os_manager_recovery rec
             WHERE rec.task_id=t.id)
        ORDER BY t.updated_at,t.id LIMIT ?
    """,(company,project,max(1,min(int(limit),3)))).fetchall()
    recovered=[]
    for row in rows:
        try:
            failure=json.loads(row["failure_result"] or "{}")
        except (ValueError,TypeError):
            failure={}
        # HTTP 429 is capacity/limit evidence, not a reason to burn a blind
        # two-minute retry. Wait for explicit operator cap revision instead.
        if isinstance(failure,dict) and failure.get("model_issue_code")=="MODEL_HTTP_429":
            continue
        db.execute("""INSERT OR IGNORE INTO venture_company_os_manager_recovery
            (task_id,manager_actor_id,original_failure_run_id,retried_at)
            VALUES (?,?,?,?)""",(row["task_id"],actor,row["failed_run_id"],utc()))
        updated=db.execute("""UPDATE tasks SET status='queued',updated_at=?
            WHERE id=? AND status='drafted'""",(utc(),row["task_id"]))
        if updated.rowcount==1:
            recovered.append(row["task_id"])
    return {"state":"ONE_SHOT_ORIGINAL_TASK_RECOVERY" if recovered else "NO_RECOVERABLE_TASKS",
            "requeued_count":len(recovered),"original_task_ids":recovered,
            "actor_id":actor,"external_actions":False,
            "verified_delivery":False}


def _recover_named_manager_capacity(db,limit=3):
    """Reopen exact ORIGINAL BuildRelay tasks once after an explicit cap revision.

    The specialist daily cap is owned by Agent Fabric. This method cannot
    change the cap, issue a permit or invent a fresh task. It only requeues a
    source-linked task with an observed HTTP 429 after an operator sets the
    matching deployment revision on the existing Company OS service.
    """
    revision=os.getenv("COMPANY_OS_FARID_CAPACITY_REVISION","").strip()
    if not re.fullmatch(r"[a-z0-9_-]{1,40}",revision):
        return {"state":"AWAITING_EXPLICIT_CAPACITY_REVISION","requeued_count":0}
    import sina_work_bridge
    if not sina_work_bridge.specialist_configured():
        return {"state":"SPECIALIST_PROVIDER_NOT_CONFIGURED","requeued_count":0}
    company,project="founder-portfolio","buildrelay-bridge-economy"
    if named_manager(company,project,"chief_of_staff") is None:
        return {"state":"NO_NAMED_MANAGER_MAPPING","requeued_count":0}
    local=db.execute("""SELECT operating_state FROM venture_company_os
        WHERE company_id=? AND project_id=?""",(company,project)).fetchone()
    if not local or local["operating_state"]!="ACTIVE_LOCAL_EXECUTIVE":
        return {"state":"MANAGER_SCOPE_NOT_ACTIVE","requeued_count":0}
    candidates=db.execute("""
        SELECT t.id AS task_id,r.id AS failure_run_id,r.result AS failure_result
        FROM tasks t JOIN product_observations o
          ON o.id=t.observation_id AND o.company_id=t.company_id
         AND o.project_id=t.project_id
        JOIN runs r ON r.task_id=t.id
        WHERE t.company_id=? AND t.project_id=? AND t.status='drafted'
          AND (o.source_event_id='manager-first-source:gm-buildrelay-farid:v1'
               OR o.source_event_id LIKE 'company_mandate:%')
          AND r.id=(SELECT r2.id FROM runs r2 WHERE r2.task_id=t.id
                    ORDER BY r2.finished_at DESC,r2.id DESC LIMIT 1)
          AND r.provider='specialist_degraded'
          AND datetime(t.updated_at)<datetime('now','-2 minutes')
          AND NOT EXISTS(
            SELECT 1 FROM venture_company_os_manager_capacity_recovery c
            WHERE c.task_id=t.id)
        ORDER BY t.updated_at,t.id LIMIT 30
    """,(company,project)).fetchall()
    queued=[]
    for row in candidates:
        if len(queued)>=max(1,min(int(limit),3)):
            break
        try:
            issue=json.loads(row["failure_result"] or "{}")
        except (ValueError,TypeError):
            issue={}
        if not isinstance(issue,dict) or issue.get("model_issue_code")!="MODEL_HTTP_429":
            continue
        db.execute("""INSERT OR IGNORE INTO venture_company_os_manager_capacity_recovery
           (task_id,policy_revision,original_failure_run_id,retried_at)
           VALUES (?,?,?,?)""",(row["task_id"],revision,row["failure_run_id"],utc()))
        changed=db.execute("""UPDATE tasks SET status='queued',updated_at=?
           WHERE id=? AND status='drafted'""",(utc(),row["task_id"]))
        if changed.rowcount==1:
            queued.append(row["task_id"])
    return {"state":"CAPACITY_REOPENED_ORIGINAL_TASKS" if queued else "NO_CAPACITY_TASKS_ELIGIBLE",
            "requeued_count":len(queued),"original_task_ids":queued,
            "actor_id":"gm-buildrelay-farid","policy_revision":revision,
            "external_actions":False,"independently_verified":False}


def tick(clock=None,limit=1):
    """Continue each local company's daily operational mission without Founder prompts.

    Emits one source-labelled *internal* product observation into the EXISTING
    Company OS events queue, with per-company idempotency and backpressure.
    """
    import core
    import product_loops
    epoch=(clock or time.time)()
    with core.connect() as db:
        init(db)
        db.execute("BEGIN IMMEDIATE")
        sync=reconcile(db)
        last=db.execute("SELECT value FROM state WHERE key='venture_os_cycle_at'").fetchone()
        if last and epoch-float(last["value"])<INTERVAL_SECONDS:
            db.commit()
            return {"state":"NOT_DUE",**sync}
        db.execute("""INSERT INTO state(key,value) VALUES('venture_os_cycle_at',?)
           ON CONFLICT(key) DO UPDATE SET value=excluded.value""",(str(epoch),))
        running=db.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('queued','running')").fetchone()[0]
        if running>=GLOBAL_BACKPRESSURE:
            db.commit()
            return {"state":"BACKPRESSURE","queued":running,**sync}
        manager_activation=_queue_first_named_manager_source_assignment(db)
        manager_followup=_queue_manager_source_followup(db)
        manager_recovery=_recover_named_manager_tasks(db)
        capacity_recovery=_recover_named_manager_capacity(db)
        candidates=db.execute("""SELECT i.*,p.name FROM venture_company_os i
          JOIN product_programs p ON p.company_id=i.company_id AND p.project_id=i.project_id
          WHERE i.operating_state='ACTIVE_LOCAL_EXECUTIVE'
            AND (i.last_heartbeat IS NULL OR
                 julianday(i.last_heartbeat) < julianday('now','-24 hours'))
          ORDER BY COALESCE(i.last_heartbeat,'') ASC,i.project_id LIMIT 60""").fetchall()
        queued=0
        started=[]
        bucket=datetime.fromtimestamp(epoch,timezone.utc).strftime("%Y%m%d")
        for row in candidates:
            if queued>=max(1,min(limit,3)):
                break
            company,project=row["company_id"],row["project_id"]
            outstanding=db.execute("""SELECT COUNT(*) FROM tasks WHERE company_id=? AND project_id=?
                                  AND status IN ('queued','running')""",(company,project)).fetchone()[0]
            if outstanding>=MAX_ACTIVE_TASKS:
                continue
            eid="venture_company_os:"+project+":"+bucket
            payload={
                "source_event_id":eid,
                "source_kind":"REPORTED_OPERATIONAL",
                "source_ref":"company-os:venture-local-loop",
                "signal":"opportunity",
                "summary":("Local Company OS executive cycle for "+row["name"]+
                           ": inspect project-specific engineering, user onboarding, organic growth, actual "
                           "feedback and cost evidence. Build the next useful internal artifact; "
                           "do not infer real customers, execution or revenue from this scheduled cycle.")[:500],
                "severity":1,
            }
            result=product_loops._insert_observation(db,company,project,payload,verified=False)
            db.execute("""UPDATE venture_company_os SET last_heartbeat=?,updated_at=?
                         WHERE company_id=? AND project_id=?""",(utc(),utc(),company,project))
            if not result.get("idempotent"):
                queued+=1
                started.append(project)
        db.commit()
        return {"state":"COMPANY_LOOPS_ADVANCED","local_companies_advanced":started,
                "events_created":queued,"manager_source_assignment":manager_activation,
                "manager_recovery":manager_recovery,
                "manager_source_followup":manager_followup,
                "manager_capacity_recovery":capacity_recovery,"external_actions":False,
                "reported_real_users":0,"verified_cash":0,**sync}

def _manager_founder_mandate_cases(db,company,project,seat,limit=8):
    """Read the ORIGINAL Sina→Company mandate→tasks→runs lineage.

    A persisted Sina directive is not a Farid acknowledgment. An original
    manager-tagged successful model reply is NOT a verified product release,
    acceptance of Founder authority, or a subsequent autonomous action.
    No generated dialogue, duplicate work queue or inferred run duration.
    """
    mandate_rows=db.execute("""
        SELECT program_id,mission_id,success_metric,priority_score,
               created_at,updated_at FROM venture_company_os_mandates
        WHERE company_id=? AND project_id=?
        ORDER BY updated_at DESC,program_id DESC LIMIT ?
    """,(company,project,max(1,min(int(limit),12)))).fetchall()
    cases=[]
    for mandate in mandate_rows:
        m=dict(mandate)
        # Prefix is wholly derived from an original 32-hex program identity.
        prefix="company_mandate:"+m["program_id"]+":"
        sources=db.execute("""
            SELECT id,source_event_id,recorded_at,verification
            FROM product_observations
            WHERE company_id=? AND project_id=? AND source_event_id LIKE ?
            ORDER BY recorded_at DESC,id DESC LIMIT 6
        """,(company,project,prefix+"%")).fetchall()
        case={
            "founder_program_id":m["program_id"],
            "mission_id":m["mission_id"],
            "success_metric":m["success_metric"],
            "priority_score":m["priority_score"],
            "original_mandate_at":m["created_at"],
            "last_mandate_update_at":m["updated_at"],
            "source_observation_ids":[x["id"] for x in sources],
            "original_source_event_ids":[x["source_event_id"] for x in sources],
            "source_evidence_state":"ORIGINAL_MANDATE_AND_OBSERVATION" if sources
                                   else "ORIGINAL_MANDATE_OBSERVATION_NOT_CAPTURED",
            "original_specialist_task_ids":[],
            "original_manager_task_ids":[],
            "manager_model_reply_refs":[],
            "original_specialist_failure_run_ids":[],
            "manager_ack_verified":False,
            "manager_reviewed_team_verified":False,
            "independent_product_delivery_verified":False,
            "autonomous_next_action_verified":False,
        }
        if not sources:
            case["state"]="MANDATE_ADOPTED_NO_SOURCE_OBSERVATION"
            cases.append(case)
            continue
        tasks={}
        manager_replies=[]
        failed_team_runs=[]
        for source in sources:
            rows=db.execute("""
                SELECT t.id AS task_id,t.role,t.status AS task_status,
                       t.event_id,r.id AS run_id,r.provider,r.model,
                       r.status AS run_status,r.result AS run_result
                FROM tasks t LEFT JOIN runs r ON r.task_id=t.id
                WHERE t.company_id=? AND t.project_id=? AND t.observation_id=?
                ORDER BY t.created_at,r.started_at LIMIT 100
            """,(company,project,source["id"])).fetchall()
            for row in rows:
                data=dict(row)
                tasks[data["task_id"]]={"id":data["task_id"],
                                        "role":data["role"],
                                        "status":data["task_status"],
                                        "event_id":data["event_id"]}
                if data["role"]!=seat["role"] and data["provider"]=="specialist_degraded":
                    failed_team_runs.append(data["run_id"])
                if (data["role"]!=seat["role"] or not data["run_id"]
                    or data["run_status"]!="completed"
                    or not (str(data["provider"] or "").startswith("sina-")
                            or data["provider"]=="openai-compatible")):
                    continue
                try:
                    original_result=json.loads(data["run_result"] or "{}")
                except (ValueError,TypeError):
                    original_result={}
                if (isinstance(original_result,dict)
                    and original_result.get("manager_actor_id")==seat["actor_id"]):
                    manager_replies.append({
                        "original_manager_run_id":data["run_id"],
                        "original_manager_task_id":data["task_id"],
                        "model":data["model"],
                        "provider":data["provider"],
                        "evidence":"ACTUAL_TAGGED_MANAGER_MODEL_REPLY_NOT_ACK"
                    })
        case["original_specialist_task_ids"]=sorted(
            k for k,v in tasks.items() if v["role"]!=seat["role"])
        case["original_manager_task_ids"]=sorted(
            k for k,v in tasks.items() if v["role"]==seat["role"])
        case["manager_model_reply_refs"]=manager_replies[:8]
        case["original_specialist_failure_run_ids"]=failed_team_runs[:12]
        case["original_task_count_visible"]=len(tasks)
        case["original_manager_model_reply_count_visible"]=len(manager_replies)
        case["source_evidence_state"]="SOURCE_LINKED_TASKS" if tasks else "SOURCE_OBSERVED_NO_TASKS"
        case["state"]=("MANAGER_MODEL_REPLY_OBSERVED_REVIEW_PENDING" if manager_replies
                       else "TASKS_CREATED_NO_NAMED_MANAGER_REPLY" if tasks
                       else "MANDATE_ADOPTED_NO_TASKS")
        cases.append(case)
    return cases


def _manager_source_history(db,company,project,role="chief_of_staff"):
    """Read original task/run records: no generated conversation or work hours.

    Legacy role runs must not be credited to a new named identity. The
    manager_actor_id is source-recorded inside the original run result only
    when the runtime actually used the identity after commissioning changes.
    """
    seat=named_manager(company,project,role)
    if seat is None:
        return None
    rows=db.execute("""
       SELECT t.id AS task_id,t.event_id,t.status AS task_status,
              t.created_at AS task_created_at,t.updated_at AS task_updated_at,
              r.id AS run_id,r.provider,r.model,r.status AS run_status,
              r.input_tokens,r.output_tokens,r.started_at,r.finished_at,
              r.result AS original_run_result
       FROM tasks t LEFT JOIN runs r ON r.task_id=t.id AND r.role=t.role
       WHERE t.company_id=? AND t.project_id=? AND t.role=?
       ORDER BY COALESCE(r.started_at,t.updated_at) DESC LIMIT 30
    """,(company,project,role)).fetchall()
    latest=[]
    confirmed_invocations=0
    mapped_run_count=0
    for raw in rows:
        x=dict(raw)
        payload={}
        try:
            payload=json.loads(x.pop("original_run_result") or "{}")
        except (ValueError,TypeError):
            x.pop("original_run_result",None)
        if not isinstance(payload,dict):
            payload={}
        tagged=payload.get("manager_actor_id")==seat["actor_id"]
        # Only recorded successful existing model inference counts as the
        # executive personality responding. Deterministic/degraded drafts
        # are correctly retained as role activities but not person inference.
        provider=str(x.get("provider") or "")
        model_reply=tagged and x.get("run_status")=="completed" and (
            provider.startswith("sina-") or provider=="openai-compatible")
        mapped_run_count+=int(tagged and bool(x.get("run_id")))
        confirmed_invocations+=int(model_reply)
        x["named_identity_in_original_run"]=tagged
        x["named_manager_model_reply_observed"]=model_reply
        x["external_action_verified"]=False
        x["verified_delivery"]=False
        x["actual_active_minutes"]=None
        latest.append(x)
    return {
        "actor_id":seat["actor_id"],"display_name":seat["display_name"],
        "role":seat["role"],"reports_to_actor_id":seat["reports_to_actor_id"],
        "company_id":company,"project_id":project,
        "mandate":seat["mandate"],
        "identity_basis":"MAPPED_EXISTING_COMPANY_OS_ROLE_NOT_PAPERCLIP_AGENT",
        "status":("MODEL_RESPONSE_OBSERVED" if confirmed_invocations else
                   "ROLE_MAPPED_AWAITING_NAMED_RUNTIME_RESPONSE"),
        "named_model_reply_count_visible":confirmed_invocations,
        "original_runtime_records_with_identity_visible":mapped_run_count,
        "historical_role_runs_not_attributed_to_named_person":True,
        "original_role_task_and_run_history_latest":latest,
        "degraded_original_model_runs_visible":sum(
            1 for row in latest if row.get("provider")=="specialist_degraded"),
        # Specialist failures are TEAM evidence, never silently attributed as
        # the named manager's own model run or an individually failed decision.
        "team_degraded_model_runs_recorded":db.execute("""
           SELECT COUNT(*) FROM runs r JOIN tasks t ON t.id=r.task_id
           WHERE t.company_id=? AND t.project_id=? AND t.role!=?
             AND r.provider='specialist_degraded'
        """,(company,project,seat["role"])).fetchone()[0],
        "one_shot_original_task_recoveries_visible":db.execute("""
           SELECT COUNT(*) FROM venture_company_os_manager_recovery
           WHERE manager_actor_id=?""",(seat["actor_id"],)).fetchone()[0],
        "original_founder_mandate_cases":_manager_founder_mandate_cases(
            db,company,project,seat),
        "capacity_recovery_count_visible":db.execute("""
           SELECT COUNT(*) FROM venture_company_os_manager_capacity_recovery
           WHERE task_id IN (SELECT id FROM tasks WHERE company_id=? AND project_id=?)
        """,(company,project)).fetchone()[0],
        "executive_delegation_verified":False,
        "sina_to_manager_mandate_ack_verified":False,
        "independent_product_delivery_verified":False,
        "caveat":"Original role tasks and model runs do not prove an autonomous manager's acceptance, delegation, independent delivery, or reply to SinaOS. Pre-mapping runs are not credited to Farid.",
    }


def portfolio(company_id=None,project_id=None):
    """Read each project's OWN work state, executive and specialist configuration."""
    import core
    with core.connect() as db:
        init(db)
        sql="SELECT * FROM venture_company_os WHERE 1=1"
        params=[]
        if company_id:
            sql+=" AND company_id=?";params.append(company_id)
        if project_id:
            sql+=" AND project_id=?";params.append(project_id)
        sql+=" ORDER BY company_id,project_id LIMIT 100"
        output=[]
        for row in db.execute(sql,params):
            item=dict(row)
            c,p=item["company_id"],item["project_id"]
            item["specialists"]=[dict(x) for x in db.execute(
                "SELECT role,remit FROM venture_company_os_specialists WHERE company_id=? AND project_id=? ORDER BY role",
                (c,p))]
            item["manager"]=_manager_source_history(db,c,p,item["director_role"])
            item["work"]={r["status"]:r["n"] for r in db.execute(
                "SELECT status,COUNT(*) n FROM tasks WHERE company_id=? AND project_id=? GROUP BY status",(c,p))}
            item["last_activity"]=dict(x) if (x:=db.execute(
                "SELECT id,role,status,updated_at FROM tasks WHERE company_id=? AND project_id=? "
                "ORDER BY updated_at DESC LIMIT 1",(c,p)).fetchone()) else None
            item["memory_scope"]=c+":"+p
            item["active_mandates"]=[dict(x) for x in db.execute(
                "SELECT founder_project_id,program_id,mission_id,objective,success_metric,priority_score,updated_at "
                "FROM venture_company_os_mandates WHERE company_id=? AND project_id=? ORDER BY priority_score DESC",
                (c,p))]
            item["permitted_effects"]="INTERNAL_DRAFTS_ONLY"
            item["independent_verification"]=False
            item["physical_isolation"]="SHARED_RUNTIME_SCOPED_PROJECT_INSTANCE"
            output.append(item)
        return {"schema":SCHEMA,"instances":output,"count":len(output),
            "strategy_source":"SINA_FOUNDER_OS_PORTFOLIO",
            "execution_owner":"PROJECT_LOCAL_COMPANY_OS",
            "worker":"EXISTING_COMPANY_OS_CANONICAL_WORKER",
            "external_permit_issued":False}
