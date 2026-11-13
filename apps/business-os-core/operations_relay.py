"""Company OS operations supervisor and truthful agent-to-agent activity relay.

Uses the existing Business OS SQLite queue, role workers and 5s worker tick.
No second scheduler, motor, model router, permit, or verification authority.
Only deterministic reversible recovery is automatic; unproven fixes stay open.
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone

INTERVAL_SECONDS = 60
RETRY_AFTER_SECONDS = 300
MAX_PROVIDER_ATTEMPTS = 3  # one original + two retries
MAX_RECOVERY_PER_TICK = 4
MAX_NEW_DIAGNOSES_PER_DAY = 8
SCHEMA = "noetfield.company-os.operations-relay.v1"
LEDGER_KEY = "operations_relay_last_actions"
TICK_KEY = "operations_relay_last_tick"
DAY_KEY_PREFIX = "operations_relay_diagnosis_day:"
EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")


def _safe_text(value, limit=240):
    return PHONE.sub("[redacted phone]", EMAIL.sub("[redacted email]", str(value or "")))[:limit]


def _get(db, key, default=""):
    row = db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def _put(db, key, value):
    db.execute(
        "INSERT INTO state(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )


def _history(db):
    try:
        value=json.loads(_get(db, LEDGER_KEY, "[]"))
        return value if isinstance(value, list) else []
    except (TypeError, ValueError):
        return []


def supervised_model_authorized(task):
    """Only our own persisted no-customer-data diagnostic handoff may call the LLM.

    A browser-created task, a raw prompt or arbitrary autonomy string alone
    cannot activate agent inference on internal jobs.
    """
    import core
    if (not isinstance(task, dict)
            or task.get("autonomy")!="internal_diagnostic_model"
            or task.get("event_id") is not None
            or task.get("opportunity_id") is not None
            or task.get("brand")!="noetfield"):
        return False
    role=task.get("role")
    title=str(task.get("title") or "")
    patterns={
        "engineering_operator": (
            ("Repair event processing ",r"[a-z0-9_]{8,72}","operations_relay_event:"),
            ("Diagnose Founder handoff ",r"[a-z0-9-]{3,90}","operations_relay_bridge_eng:"),
        ),
        "chief_of_staff": (
            ("Follow up event processing ",r"[a-z0-9_]{8,72}","operations_relay_manager:"),
            ("Review Founder handoff ",r"[a-z0-9-]{3,90}","operations_relay_bridge_manager:"),
        ),
    }
    for prefix,pattern,key_prefix in patterns.get(role,()):
        if title.startswith(prefix):
            item_id=title[len(prefix):]
            if not re.fullmatch(pattern,item_id):
                return False
            with core.connect() as db:
                return _get(db,key_prefix+item_id)==task.get("id")
    return False


def upstream_evidence(task):
    """Minimum internal specialist result for the dependent manager's prompt."""
    import core
    if not supervised_model_authorized(task):
        return []
    with core.connect() as db:
        rows=db.execute("""
          SELECT p.role,p.status,p.result FROM task_dependencies d
          JOIN tasks p ON p.id=d.depends_on_task_id
          WHERE d.task_id=? ORDER BY p.updated_at DESC LIMIT 3
        """,(task["id"],)).fetchall()
    evidence=[]
    for row in rows:
        try:
            result=json.loads(row["result"])
            recommendation=result.get("recommendation",{}) if isinstance(result,dict) else {}
            note=(recommendation.get("assessment","") if isinstance(recommendation,dict) else "")
        except (ValueError,TypeError):
            note=""
        evidence.append({"role":row["role"],"state":row["status"],
                         "assessment":_safe_text(note,450)})
    return evidence


def tick(*, timestamp=None):
    """One lease-protected pulse within the *existing* Company OS worker.

    Requeue only genuinely recoverable states; never duplicate already-recorded
    diagnosis tasks, reauthorize a blocked WorkPacket, or claim a product fix.
    """
    import core
    current = float(time.time() if timestamp is None else timestamp)
    stamp = datetime.fromtimestamp(current, timezone.utc).isoformat(timespec="seconds")
    actions = []
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            last = float(_get(db, TICK_KEY, "0"))
            if current - last < INTERVAL_SECONDS:
                db.rollback()
                return {"state": "NOT_DUE", "actions": 0}
            _put(db, TICK_KEY, current)

            # True automatic recovery: a dependency-blocked task may resume if
            # its actual dependencies have subsequently produced drafts.
            blocked = db.execute("""
              SELECT t.id FROM tasks t
              WHERE t.status='blocked'
                AND EXISTS(SELECT 1 FROM task_dependencies td WHERE td.task_id=t.id)
                AND NOT EXISTS(
                  SELECT 1 FROM task_dependencies td
                  LEFT JOIN tasks dep ON dep.id=td.depends_on_task_id
                  WHERE td.task_id=t.id AND (dep.id IS NULL OR dep.status NOT IN ('drafted','approved'))
                )
              ORDER BY t.updated_at LIMIT ?
            """, (MAX_RECOVERY_PER_TICK,)).fetchall()
            for row in blocked:
                db.execute("UPDATE tasks SET status='queued',updated_at=? WHERE id=? AND status='blocked'",
                           (stamp, row["id"]))
                actions.append({"at": stamp, "action": "DEPENDENCY_RECOVERED",
                                "task_id": row["id"], "owner": "Company OS worker",
                                "evidence": "all recorded dependencies drafted or approved",
                                "result": "REQUEUED_NOT_COMPLETED"})

            # Real bounded retry, not a second agent: only provider errors from
            # consented opportunities. No AI invocation without configured model.
            budget = max(0, MAX_RECOVERY_PER_TICK - len(actions))
            if budget and all(os.getenv(k) for k in ("LLM_BASE_URL","LLM_API_KEY","LLM_MODEL")):
                failures = db.execute("""
                  SELECT t.id,t.updated_at,COUNT(r.id) AS attempts
                  FROM tasks t JOIN opportunities o ON o.id=t.opportunity_id AND o.ai_consent=1
                  JOIN runs r ON r.task_id=t.id AND r.provider='provider_error'
                  WHERE t.status='drafted'
                    AND json_extract(t.result,'$.provider')='provider_error'
                    AND julianday(t.updated_at)<=julianday(?,'-300 seconds')
                  GROUP BY t.id
                  HAVING COUNT(r.id) < ?
                  ORDER BY t.updated_at ASC LIMIT ?
                """, (stamp, MAX_PROVIDER_ATTEMPTS, budget)).fetchall()
                for row in failures:
                    db.execute("UPDATE tasks SET status='queued',updated_at=? WHERE id=? AND status='drafted'",
                               (stamp, row["id"]))
                    actions.append({"at": stamp, "action": "CONSENTED_MODEL_RETRY",
                                    "task_id": row["id"], "owner": "Existing specialist worker",
                                    "evidence": str(row["attempts"])+" previous provider errors, consent verified",
                                    "result": "REQUEUED_NOT_COMPLETED"})

            # An actual terminal event error gets a bounded, idempotent
            # engineering diagnosis in the existing specialist queue.
            # This is not misrepresented as a completed repair or code change.
            day = stamp[:10]
            day_key = DAY_KEY_PREFIX + day
            used = int(_get(db, day_key, "0") or "0")
            budget = min(2, max(0, MAX_NEW_DIAGNOSES_PER_DAY-used))
            if budget:
                rows = db.execute("""
                  SELECT id,event_type,status,error FROM events
                  WHERE status IN ('dead_letter','failed')
                  ORDER BY COALESCE(processed_at,created_at) DESC LIMIT 120
                """).fetchall()
                new_count = 0
                for row in rows:
                    if new_count >= budget:
                        break
                    marker = "operations_relay_event:" + row["id"]
                    if _get(db, marker):
                        continue
                    # No free-form event payload, customer PII or credentials
                    # are copied into prompts or new tasks.
                    action = ("Investigate real failed Company OS event "+row["id"]+
                              "; event type "+_safe_text(row["event_type"],80)+
                              "; status "+_safe_text(row["status"],30)+
                              ". Classify the logged exception, identify root cause and select an exact bounded repair. "
                              "Do not claim that code was changed or deployment succeeded without source receipts.")
                    # The existing Worker claims the engineer's task, and only
                    # after its recorded draft does it release the manager
                    # dependency. These are real inter-agent work handoffs.
                    if not re.fullmatch(r"[a-z0-9_]{8,72}",row["id"]):
                        continue
                    tid = core.add_task(db,None,None,"noetfield","engineering_operator",
                                        "Repair event processing "+row["id"],action,
                                        "Diagnose source event; return evidence and next repair step.")
                    manager=core.add_task(db,None,None,"noetfield","chief_of_staff",
                                        "Follow up event processing "+row["id"],
                                        "Review the assigned engineering specialist's actual result for "+row["id"]+
                                        ". Choose the next bounded corrective action and evidence requirement. "
                                        "A drafted diagnosis is not repaired code, a passed test or completed deployment.",
                                        "Review specialist evidence; route next authorized repair without self-certification.")
                    core.add_task_dependency(db,manager,tid)
                    db.execute("UPDATE tasks SET autonomy='internal_diagnostic_model',priority_rank=15 WHERE id=?",(tid,))
                    db.execute("UPDATE tasks SET autonomy='internal_diagnostic_model',priority_rank=16 WHERE id=?",(manager,))
                    _put(db, marker, tid)
                    _put(db,"operations_relay_manager:"+row["id"],manager)
                    new_count += 1
                    actions.append({"at":stamp,"action":"BLOCKER_OWNER_ASSIGNED",
                                    "task_id":tid,"source_event_id":row["id"],
                                    "owner":"Engineering Delivery",
                                    "evidence":"persisted "+row["status"]+" event",
                                    "result":"DIAGNOSIS_QUEUED_NOT_REPAIRED"})
                    actions.append({"at":stamp,"action":"MANAGER_FOLLOWUP_SCHEDULED",
                                    "task_id":manager,"source_event_id":row["id"],
                                    "owner":"Chief of Staff",
                                    "evidence":"recorded dependency on engineering diagnosis",
                                    "result":"WAITS_FOR_ENGINEERING_DRAFT"})
                _put(db,day_key,used+new_count)

            # Real Founder handoff rejections are themselves actionable
            # operational incidents. Route scoped Noetfield cases into the
            # SAME specialist queue, not another agent platform or scheduler.
            try:
                denied=json.loads(_get(db,"founder_bridge_last_rejected_projects","[]"))
            except (TypeError,ValueError):
                denied=[]
            if isinstance(denied,list):
                for rejected in denied[:2]:
                    if (not isinstance(rejected,dict)
                        or rejected.get("reason_code")!="project_not_allowed"
                        or rejected.get("company_id")!="noetfield-systems-inc"):
                        continue
                    project=rejected.get("project_id")
                    if not isinstance(project,str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,89}",project):
                        continue
                    marker="operations_relay_bridge_eng:"+project
                    if _get(db,marker):
                        continue
                    engineer=core.add_task(
                        db,None,None,"noetfield","engineering_operator",
                        "Diagnose Founder handoff "+project,
                        "The authenticated Sina Founder OS submitted an advisory-only WorkPacket for project "+
                        project+" which Company OS rejected as project_not_allowed. "
                        "Inspect the existing project registry, company tenant, allowlist and Governor scope. "
                        "Identify the exact mismatch and propose the minimal correction in the owning system. "
                        "Do not expand permissions blindly or claim that code was changed.",
                        "Find the exact owner and routing fix, with source evidence.")
                    manager=core.add_task(
                        db,None,None,"noetfield","chief_of_staff",
                        "Review Founder handoff "+project,
                        "Review Engineering's recorded diagnosis of the project_not_allowed WorkPacket "+
                        "for "+project+". Select the existing authorized Company OS or scoped integration "+
                        "that must act next. Require a later accepted WorkPacket receipt before claiming resolution.",
                        "Follow the engineering evidence and route the next eligible bounded action.")
                    core.add_task_dependency(db,manager,engineer)
                    db.execute("UPDATE tasks SET autonomy='internal_diagnostic_model',priority_rank=12 WHERE id=?",(engineer,))
                    db.execute("UPDATE tasks SET autonomy='internal_diagnostic_model',priority_rank=13 WHERE id=?",(manager,))
                    _put(db,marker,engineer)
                    _put(db,"operations_relay_bridge_manager:"+project,manager)
                    actions.append({"at":stamp,"action":"FOUNDER_HANDOFF_OWNER_ASSIGNED",
                                    "task_id":engineer,"project_id":project,
                                    "owner":"Engineering Delivery",
                                    "evidence":"persisted rejected Founder WorkPacket: project_not_allowed",
                                    "result":"ROUTING_DIAGNOSIS_QUEUED"})
                    actions.append({"at":stamp,"action":"FOUNDER_HANDOFF_MANAGER_SCHEDULED",
                                    "task_id":manager,"project_id":project,
                                    "owner":"Chief of Staff",
                                    "evidence":"dependency on engineering diagnosis",
                                    "result":"WAITS_FOR_ENGINEERING_DRAFT"})
            previous = _history(db)
            _put(db, LEDGER_KEY, json.dumps((actions+previous)[:30],separators=(",",":")))
            _put(db,"operations_relay_last_success",stamp)
            db.commit()
        except Exception:
            db.rollback()
            raise
    return {"state":"EXECUTED","actions":len(actions),
            "action_types":[a["action"] for a in actions]}


def snapshot():
    """Founder-only projection of actual task handoffs, model calls and blockers."""
    import core
    with core.connect() as db:
        states={r["status"]:r["n"] for r in db.execute(
            "SELECT status,COUNT(*) AS n FROM tasks GROUP BY status").fetchall()}
        provider_rows=db.execute("""
          SELECT provider,COUNT(*) AS n FROM runs GROUP BY provider ORDER BY n DESC
        """).fetchall()
        nodes=db.execute("""
          SELECT t.id,t.title,t.objective,t.role,t.status,t.brand,t.created_at,t.updated_at,
                 t.next_action,t.event_id,r.provider,r.status AS run_status,r.model,
                 r.input_tokens,r.output_tokens,r.started_at,r.finished_at,
                 e.event_type,
                 b.request_id AS founder_workpacket
          FROM tasks t
          LEFT JOIN runs r ON r.id=(
             SELECT id FROM runs rr WHERE rr.task_id=t.id ORDER BY started_at DESC,id DESC LIMIT 1
          )
          LEFT JOIN events e ON e.id=t.event_id
          LEFT JOIN founder_org_bindings b ON b.canonical_task_id=t.id
          WHERE t.status IN ('queued','running','blocked','failed')
             OR r.id IS NOT NULL
          ORDER BY t.updated_at DESC,t.id DESC LIMIT 22
        """).fetchall()
        task_ids=[r["id"] for r in nodes]
        dependencies={}
        for tid in task_ids:
            dependencies[tid]=[dict(x) for x in db.execute("""
              SELECT dep.id,dep.role,dep.status FROM task_dependencies td
              JOIN tasks dep ON dep.id=td.depends_on_task_id
              WHERE td.task_id=? ORDER BY dep.updated_at DESC LIMIT 12
            """,(tid,)).fetchall()]
        recent_providers=[{"provider":r["provider"],"count":r["n"]} for r in provider_rows]
        issues=db.execute("""
            SELECT id,event_type,status,created_at,error FROM events
            WHERE status IN ('failed','dead_letter')
            ORDER BY created_at DESC LIMIT 6
        """).fetchall()
        latest_tick=_get(db,"operations_relay_last_success")
        history=_history(db)
        raw_rejections=_get(db,"founder_bridge_last_rejections","{}")
        raw_rejected_projects=_get(db,"founder_bridge_last_rejected_projects","[]")
    try:
        rejections=json.loads(raw_rejections)
        if not isinstance(rejections,dict):
            rejections={}
    except (ValueError,TypeError):
        rejections={}
    try:
        scoped_projects=json.loads(raw_rejected_projects)
        if not isinstance(scoped_projects,list):
            scoped_projects=[]
    except (ValueError,TypeError):
        scoped_projects=[]
    scoped_projects=[
        p for p in scoped_projects[:12]
        if isinstance(p,dict) and p.get("reason_code")=="project_not_allowed"
        and p.get("company_id")=="noetfield-systems-inc"
        and isinstance(p.get("project_id"),str)
        and re.fullmatch(r"[a-z0-9][a-z0-9-]{2,89}",p["project_id"])
    ]
    handoffs=[]
    for row in nodes:
        d=dict(row)
        deps=dependencies.get(d["id"],[])
        # A dependency edge is a real recorded work handoff. It is NOT a
        # model-to-model prompt unless the provider records a model call.
        source="Founder OS" if d["founder_workpacket"] else (
            "Company OS operations supervisor" if str(d["title"]).startswith(
                ("Repair event processing ","Follow up event processing ",
                 "Diagnose Founder handoff ","Review Founder handoff "))
            else "Company OS portfolio coordinator" if d["event_type"]=="portfolio.studio.cycle"
            else "Company OS task queue")
        actual_model=d["provider"]=="openai-compatible" and d["run_status"]=="completed"
        handoffs.append({
            "task_id":d["id"],"title":_safe_text(d["title"],120),
            "prompt_excerpt":_safe_text(d["objective"],280),
            "owner_role":d["role"],"brand":d["brand"],"status":d["status"],
            "created_at":d["created_at"],"updated_at":d["updated_at"],
            "next_action":_safe_text(d["next_action"],180),
            "from":source if not deps else ", ".join(x["role"] for x in deps),
            "to":d["role"],
            "dependencies":[{"task_id":v["id"],"role":v["role"],"state":v["status"]} for v in deps],
            "provider":d["provider"] or "not_invoked",
            "model":d["model"] or "none",
            "actual_model_call_observed":actual_model,
            "input_tokens":d["input_tokens"] or 0,
            "output_tokens":d["output_tokens"] or 0,
            "run_status":d["run_status"] or "none",
            "source_event_type":d["event_type"],
            "source_workpacket_present":bool(d["founder_workpacket"]),
            "result_kind":"INTERNAL_DRAFT" if d["status"] in ("drafted","approved")
                          else "WORK_NOT_COMPLETE",
            "independently_verified":False,
        })
    return {
        "schema":SCHEMA,"source":"Company OS persisted tasks, runs and dependencies",
        "last_supervisor_tick":latest_tick or None,
        "supervisor_running_evidence":bool(latest_tick),
        "counts":{
            "queued":states.get("queued",0),"running":states.get("running",0),
            "blocked":states.get("blocked",0),"failed":states.get("failed",0),
            "drafted":states.get("drafted",0),"approved":states.get("approved",0),
            "tasks_needing_execution":sum(states.get(s,0) for s in ("queued","running")),
            "needs_attention":sum(states.get(s,0) for s in ("blocked","failed")),
        },
        "provider_history":recent_providers,
        "handoffs":handoffs,
        "actions":history[:15],
        "blockers":[
            {"source_event_id":r["id"],"reason_code":_safe_text(r["error"],90),
             "state":r["status"],"owner":"Engineering Delivery",
             "next_action":"Inspect persisted event and perform bounded repair"}
            for r in issues
        ] + [
            {"reason_code":"project_not_allowed","project_id":p["project_id"],
             "state":"FOUNDER_HANDOFF_REJECTED",
             "owner":"Engineering Delivery → Chief of Staff",
             "next_action":"Resolve scoped project ownership then prove a later accepted WorkPacket"}
            for p in scoped_projects
        ] + [
            {"reason_code":str(k),"count":v,"state":"FOUNDER_HANDOFF_REJECTED",
             "owner":"Company OS / owning Company OS tenant",
             "next_action":"Identify canonical project ownership; correct routing, not bypass authority"}
            for k,v in rejections.items()
            if isinstance(k,str) and re.fullmatch(r"[a-z_]{3,64}",k)
            and type(v) is int and v>0
        ],
        "independent_verification_inferred":False,
        "end_to_end_motor_execution_proven":False,
        "scope":"REAL_QUEUE_RECOVERY_AND_OBSERVATION_NOT_AUTONOMOUS_CODE_MERGE",
    }
