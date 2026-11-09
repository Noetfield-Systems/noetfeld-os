"""Read-only Company Floor projection over canonical Business OS Core records.

This module does NOT own work, mutate statuses, generate users or duplicate a queue.
Buyer/contact fields, free-form task text and model outputs never leave Core.
"""
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

import core

SCHEMA="noetfield.company-floor.snapshot.v1"

def authorized(supplied):
    expected=(os.getenv("COMPANY_FLOOR_CORE_READ_TOKEN") or "").strip()
    return bool(expected and isinstance(supplied,str) and hmac.compare_digest(supplied,expected))

def snapshot(limit=80):
    limit=min(100,max(1,int(limit)))
    with core.connect() as db:
        task_rows=db.execute("""
          SELECT t.id,t.event_id,t.brand,t.role,t.priority_rank,t.status,t.created_at,t.updated_at,
                 (SELECT COUNT(*) FROM task_dependencies td WHERE td.task_id=t.id) dependencies,
                 (SELECT COUNT(*) FROM task_dependencies td
                    JOIN tasks d ON d.id=td.depends_on_task_id
                    WHERE td.task_id=t.id AND d.status NOT IN ('drafted','approved')) pending_dependencies,
                 (SELECT r.provider FROM runs r WHERE r.task_id=t.id
                    ORDER BY r.started_at DESC LIMIT 1) provider,
                 (SELECT r.model FROM runs r WHERE r.task_id=t.id
                    ORDER BY r.started_at DESC LIMIT 1) model,
                 (SELECT r.status FROM runs r WHERE r.task_id=t.id
                    ORDER BY r.started_at DESC LIMIT 1) run_status,
                 (SELECT r.result FROM runs r WHERE r.task_id=t.id
                    ORDER BY r.started_at DESC LIMIT 1) run_result
          FROM tasks t ORDER BY t.priority_rank ASC,t.updated_at DESC LIMIT ?
        """,(limit,)).fetchall()
        signal_count=db.execute("SELECT COUNT(*) FROM platform_intake_signals").fetchone()[0]
        totals={r["status"]:r["n"] for r in db.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
        last=db.execute("SELECT MAX(updated_at) FROM tasks").fetchone()[0]
    tasks=[]
    activity={}
    for record in task_rows:
        r=dict(record)
        role=r["role"] if r["role"] in {x[0] for x in core.AGENTS} else "other"
        seat=core.company_role_for_runtime(role) if role!="other" else None
        department=seat["title"] if seat else "Operations"
        activity[role]=activity.get(role,0)+1
        evidence_hash=(hashlib.sha256(str(r["run_result"]).encode()).hexdigest()
                       if r["run_result"] else None)
        tasks.append({
           "id":r["id"],"source":"company_os_core","program_id":None,
           "source_ref":r["event_id"],"brand":r["brand"] if r["brand"] in core.BRANDS else "other",
           "role":role,"department":department,
           "title":role.replace("_"," ").title()+" · "+(r["brand"] if r["brand"] in core.BRANDS else "Operations"),
           "state":r["status"],"priority":r["priority_rank"],
           "created_at":r["created_at"],"updated_at":r["updated_at"],
           "dependencies":r["dependencies"],"pending_dependencies":r["pending_dependencies"],
           "provider":r["provider"],"model":r["model"],"runtime_state":r["run_status"],
           "evidence_hash":evidence_hash,
           "verification":"NOT_INDEPENDENTLY_VERIFIED",
           "requires_founder_review":r["status"]=="drafted",
           "execution_claim":"REAL_RUNTIME_RECORD" if r["run_status"] else "QUEUED_OR_INTERNAL_ONLY",
        })
    roster=[]
    for agent in core.agent_roster():
        roster.append({
            "id":agent["role"],"name":agent["name"],"role":agent["role"],
            "department":agent["company_role_title"],"activation":agent["company_role_activation"],
            "recorded_tasks":activity.get(agent["role"],0),
            "type":"CONFIGURED_ROLE_NOT_PROOF_OF_EXECUTION",
        })
    return {
      "schema":SCHEMA,"source":"company_os_core",
      "observed_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "source_last_updated_at":last,
      "canonical_owner":"Noetfield Business OS Core SQLite",
      "read_only":True,"pii_included":False,"synthetic_counted_as_revenue":False,
      "counts":{"tasks_by_state":totals,"intake_signals_not_qualified_leads":signal_count},
      "tasks":tasks,"agents":roster,"cash_collected":None,
      "cash_evidence_state":"NOT_CONNECTED",
    }
