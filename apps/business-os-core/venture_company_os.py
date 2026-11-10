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
                "events_created":queued,"external_actions":False,
                "reported_real_users":0,"verified_cash":0,**sync}

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
            item["work"]={r["status"]:r["n"] for r in db.execute(
                "SELECT status,COUNT(*) n FROM tasks WHERE company_id=? AND project_id=? GROUP BY status",(c,p))}
            item["last_activity"]=dict(x) if (x:=db.execute(
                "SELECT id,role,status,updated_at FROM tasks WHERE company_id=? AND project_id=? "
                "ORDER BY updated_at DESC LIMIT 1",(c,p)).fetchone()) else None
            item["memory_scope"]=c+":"+p
            item["permitted_effects"]="INTERNAL_DRAFTS_ONLY"
            item["independent_verification"]=False
            item["physical_isolation"]="SHARED_RUNTIME_SCOPED_PROJECT_INSTANCE"
            output.append(item)
        return {"schema":SCHEMA,"instances":output,"count":len(output),
            "strategy_source":"SINA_FOUNDER_OS_PORTFOLIO",
            "execution_owner":"PROJECT_LOCAL_COMPANY_OS",
            "worker":"EXISTING_COMPANY_OS_CANONICAL_WORKER",
            "external_permit_issued":False}
