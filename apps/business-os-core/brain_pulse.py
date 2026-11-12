"""Company OS team-lead pulse: source-owned decisions, not the whole product.

Uses EXISTING Company OS SQLite and the EXISTING worker. One pulse records
whether the managerial loop actually reviewed/adopted/handed off a mandate;
one specialist action records each real local team decision and its outcome.
No new scheduler, status source, team registry, model call or task queue.
"""
from __future__ import annotations
import json
import sqlite3
import time
from datetime import datetime,timedelta,timezone

SCHEMA="sina.company-os.brain-pulse.v1"
WINDOWS={24,48,168,720}

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def safe_id(s,n=96):
    if not isinstance(s,str):return None
    return s[:n] if all(c.isalnum() or c in "_-.:/" for c in s) else None

def count(v):
    return v if type(v) is int and 0<=v<=1000000 else 0

def init(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS company_brain_pulses(
      seq INTEGER PRIMARY KEY AUTOINCREMENT,at TEXT NOT NULL,
      portfolio_state TEXT,mandate_state TEXT,local_team_state TEXT,
      market_state TEXT,local_events_created INTEGER NOT NULL DEFAULT 0,
      founder_mandates_adopted INTEGER NOT NULL DEFAULT 0,
      founder_mandates_blocked INTEGER NOT NULL DEFAULT 0,
      canonical_workpackets_created INTEGER NOT NULL DEFAULT 0,
      agent_feedback_delivered INTEGER NOT NULL DEFAULT 0,
      agent_feedback_pending INTEGER NOT NULL DEFAULT 0,
      agent_feedback_rejected INTEGER NOT NULL DEFAULT 0,
      local_drafts INTEGER NOT NULL DEFAULT 0,
      active_local_tasks INTEGER NOT NULL DEFAULT 0,
      reason_code TEXT NOT NULL,next_step TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_company_brain_pulses_at ON company_brain_pulses(at DESC,seq DESC);
    CREATE TABLE IF NOT EXISTS company_brain_actions(
      seq INTEGER PRIMARY KEY AUTOINCREMENT,at TEXT NOT NULL,
      task_id TEXT NOT NULL,project_id TEXT,company_id TEXT,role TEXT,
      decision_state TEXT NOT NULL,goalkeeper_disposition TEXT NOT NULL,
      model_source TEXT NOT NULL,model_tokens INTEGER NOT NULL,
      external_action_executed INTEGER NOT NULL DEFAULT 0,
      reason_code TEXT NOT NULL,next_step TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_company_brain_actions_at ON company_brain_actions(at DESC,seq DESC);
    CREATE INDEX IF NOT EXISTS ix_company_brain_actions_role ON company_brain_actions(role,at DESC);
    """)

def _reason(portfolio,mandate,local,market):
    state=mandate.get("state","UNOBSERVED")
    if state=="DEGRADED":
        return "MANDATE_BRIDGE_DEGRADED","REVIEW_CANONICAL_FOUNDER_HANDOFF"
    if count(mandate.get("agent_feedback_contract_rejected")):
        return "FOUNDER_FEEDBACK_REJECTED","RECONCILE_EXISTING_FEEDBACK_CONTRACT"
    if count(mandate.get("agent_feedback_pending_retry")):
        return "FOUNDER_FEEDBACK_PENDING_RETRY","RETRY_WITH_EXISTING_BACKOFF"
    if count(mandate.get("venture_mandates_blocked")):
        return "PROJECT_MANDATE_NOT_ADOPTED","INSPECT_SOURCE_MANDATE_REASON"
    if state=="MANDATES_ONLY_AGENT_FABRIC_OWNS_WORKPACKETS":
        return "FABRIC_IS_CANONICAL_WORKPACKET_OWNER","CONTINUE_LOCAL_TEAM_WITH_EXISTING_FABRIC_HANDOFF"
    if count(local.get("events_created")):
        return "LOCAL_COMPANY_CYCLE_DISPATCHED","CHECK_EXISTING_QUEUED_LOCAL_WORK"
    if portfolio.get("state")=="DEGRADED":
        return "FOUNDER_PORTFOLIO_FEED_DEGRADED","RETRY_EXISTING_FOUNDER_FEED"
    return "NO_NEW_EXECUTIVE_ACTION","CHECK_NEXT_ELIGIBLE_COMPANY_MANDATE"

def capture_cycle(db,*,portfolio,mandate,local,market,clock=None):
    if not all(isinstance(x,dict) for x in (portfolio,mandate,local,market)):
        raise ValueError("company_pulse_requires_actual_worker_results")
    init(db)
    at=clock or now()
    reason,step=_reason(portfolio,mandate,local,market)
    # Company OS local team actions are scoped to existing product tasks.
    local_drafts=db.execute("""SELECT COUNT(*) FROM tasks
        WHERE project_id IS NOT NULL AND company_id IS NOT NULL
        AND status='drafted'""").fetchone()[0]
    active=db.execute("""SELECT COUNT(*) FROM tasks
        WHERE project_id IS NOT NULL AND company_id IS NOT NULL
        AND status IN ('queued','running')""").fetchone()[0]
    values=(at,safe_id(portfolio.get("state")) or "UNOBSERVED",
       safe_id(mandate.get("state")) or "UNOBSERVED",
       safe_id(local.get("state")) or "UNOBSERVED",
       safe_id(market.get("state")) or "UNOBSERVED",
       count(local.get("events_created")),
       count(mandate.get("venture_mandates_adopted")),
       count(mandate.get("venture_mandates_blocked")),
       count(mandate.get("canonical_tasks_created")),
       count(mandate.get("agent_feedback_delivered")),
       count(mandate.get("agent_feedback_pending_retry")),
       count(mandate.get("agent_feedback_contract_rejected")),
       int(local_drafts),int(active),reason,step)
    previous=db.execute("""SELECT at,portfolio_state,mandate_state,
      local_team_state,market_state,local_events_created,founder_mandates_adopted,
      founder_mandates_blocked,canonical_workpackets_created,
      agent_feedback_delivered,agent_feedback_pending,agent_feedback_rejected,
      local_drafts,active_local_tasks,reason_code,next_step
      FROM company_brain_pulses ORDER BY seq DESC LIMIT 1""").fetchone()
    # No-op cycles are not managerial work. Record at most one idle heartbeat
    # every five minutes, but never suppress a change or a genuine new action.
    if previous:
        p=dict(previous)
        old=[p[k] for k in list(p)[1:]]
        material_action=any(values[i] for i in (5,6,7,8,9,10,11))
        urgent_failure=reason not in (
            "NO_NEW_EXECUTIVE_ACTION",
            "FABRIC_IS_CANONICAL_WORKPACKET_OWNER",
        )
        # A frequent NOT_DUE response alternating with the normal Fabric
        # ownership state is not a new executive decision. Still record every
        # actual handoff, material team event, or failure without delay.
        if not material_action and not urgent_failure:
            try:
                elapsed=(datetime.fromisoformat(at.replace("Z","+00:00"))-
                    datetime.fromisoformat(p["at"].replace("Z","+00:00"))).total_seconds()
                if 0<=elapsed<300:
                    return {"state":"NOT_MATERIAL","recorded":False,"reason_code":reason}
            except ValueError:pass
    db.execute("""INSERT INTO company_brain_pulses(
      at,portfolio_state,mandate_state,local_team_state,market_state,
      local_events_created,founder_mandates_adopted,founder_mandates_blocked,
      canonical_workpackets_created,agent_feedback_delivered,agent_feedback_pending,
      agent_feedback_rejected,local_drafts,active_local_tasks,reason_code,next_step)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",values)
    db.commit()
    return {"state":"RECORDED","recorded":True,"reason_code":reason,
            "mandates_adopted":values[6],"local_events_created":values[5],
            "source":"EXISTING_COMPANY_OS_WORKER","business_impact_verified":False}

def record_specialist(db,*,task,goalkeeper,provider,input_tokens,output_tokens,
                      resulted_state="drafted",clock=None):
    """One per actual local team member action, not entire task audit."""
    init(db)
    if not all(isinstance(task.get(k),str) and task[k] for k in (
       "id","company_id","project_id","role")):
        return {"recorded":False,"reason_code":"NO_SCOPED_COMPANY_ROLE"}
    at=clock or now()
    decision=goalkeeper.get("state","NOT_CONSULTED") if isinstance(goalkeeper,dict) else "NOT_CONSULTED"
    disposition=goalkeeper.get("disposition","NOT_RECORDED") if isinstance(goalkeeper,dict) else "NOT_RECORDED"
    if decision=="DEGRADED_NO_TRUSTED_GOALKEEPER_RESPONSE":
        reason,step="GOALKEEPER_UNAVAILABLE","RETRY_AUTHENTICATED_GOALKEEPER"
    elif provider in ("specialist_degraded","provider_error"):
        reason,step="SPECIALIST_MODEL_FAILED","RETRY_EXISTING_SPECIALIST_TASK"
    elif isinstance(provider,str) and (provider.startswith("sina-") or provider=="openai-compatible"):
        reason,step="MODEL_DRAFT_RECORDED","FOLLOW_EXISTING_REVIEW_OR_HANDOFF"
    else:
        reason,step="DETERMINISTIC_DRAFT_RECORDED","CHECK_CANONICAL_LOCAL_TASK_NEXT_STEP"
    db.execute("""INSERT INTO company_brain_actions(
      at,task_id,project_id,company_id,role,decision_state,
      goalkeeper_disposition,model_source,model_tokens,
      external_action_executed,reason_code,next_step)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
      (at,safe_id(task["id"]),safe_id(task["project_id"]),
       safe_id(task["company_id"]),safe_id(task["role"]),
       safe_id(decision) or "NOT_RECORDED",
       safe_id(disposition) or "NOT_RECORDED",
       safe_id(provider) or "NOT_RECORDED",
       count(input_tokens)+count(output_tokens),0,reason,step))
    db.commit()
    return {"recorded":True,"reason_code":reason}

def read(db,*,hours=48,limit=120,clock=None):
    if type(hours) is not int or hours not in WINDOWS:
        raise ValueError("invalid_brain_window")
    if type(limit) is not int or not 1<=limit<=240:
        raise ValueError("invalid_brain_limit")
    init(db)
    now_dt=clock or datetime.now(timezone.utc)
    if now_dt.tzinfo is None:raise ValueError("timezone_aware_clock_required")
    cutoff=(now_dt-timedelta(hours=hours)).isoformat(timespec="seconds").replace("+00:00","Z")
    pulses=[dict(row) for row in db.execute("""SELECT * FROM company_brain_pulses
         WHERE at>=? ORDER BY at DESC,seq DESC LIMIT ?""",(cutoff,limit))]
    actions=[dict(row) for row in db.execute("""SELECT * FROM company_brain_actions
         WHERE at>=? ORDER BY at DESC,seq DESC LIMIT ?""",(cutoff,limit))]
    return {"schema":SCHEMA,"source":"company_os","read_only":True,
       "window":{"hours":hours,"since":cutoff},
       "pulses":pulses,"role_actions":actions,
       "summary":{"recorded_management_cycles":len(pulses),
          "recorded_team_actions":len(actions),
          "model_drafts":sum(x["reason_code"]=="MODEL_DRAFT_RECORDED" for x in actions),
          "deterministic_drafts":sum(x["reason_code"]=="DETERMINISTIC_DRAFT_RECORDED" for x in actions),
          "goalkeeper_failures":sum(x["reason_code"]=="GOALKEEPER_UNAVAILABLE" for x in actions),
          "mandates_adopted_in_pulses":sum(x["founder_mandates_adopted"] for x in pulses),
          "local_events_in_pulses":sum(x["local_events_created"] for x in pulses)},
       "limitations":["Company OS is a team-level operator; its pulse is not a complete product or repository tracker.",
          "Source states and draft reports do not prove delivery or business impact.",
          "Goalkeeper disposition is saved authority/status, not hidden model reasoning.",
          "History begins with capture deployment. Old role actions are never fabricated."]}
