"""Company OS product operating loops, using its existing events/tasks/runs worker.

One Company OS can operate MANY product programs concurrently. A program is a
company/project operating scope, not a new tenant or legal entity. All genuine
customer metrics remain unverified until an authenticated source adapter proves
them; synthetic QA is forever excluded from real-user traction.

This module introduces no model router, scheduler, agent table, policy issuer,
task queue, or separate worker. It feeds the existing event/task dependencies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit

SCHEMA = "noetfield.company-os.product-operating-loop.v1"
INTERNAL_COMPANY = "noetfield-systems-inc"
FOUNDER_PORTFOLIO = "founder-portfolio"
ACTIVE_STATES = frozenset({"INTERNAL_ACTIVE", "FOUNDER_PROJECT_ACTIVE_NOT_LEGAL_TENANT"})
KINDS = frozenset({
    "REPORTED_REAL_USER_ANALYTICS", "REPORTED_PUBLIC_MARKET",
    "REPORTED_OPERATIONAL", "SYNTHETIC_AGENT_QA",
})
SIGNALS = frozenset({
    "onboarding", "activation", "retention", "acquisition", "community",
    "feedback", "app_error", "security", "revenue", "market_shift",
    "opportunity", "conversion", "feature_request", "synthetic_qa",
    "service_health", "baseline", "competition", "support",
})
SAFE_ID = re.compile(r"^[a-z][a-z0-9-]{2,79}$")
SAFE_METRIC = re.compile(r"^[a-z][a-z0-9_-]{2,79}$")
EVIDENCE_REF = re.compile(r"^(https://[^\s]{8,220}|[a-z][a-z0-9_.:-]{7,220})$")
HEALTH_PATHS = frozenset({"/health", "/healthz", "/api/health", "/ready"})

ROLES = {
    "onboarding": ("customer_success", "product_strategy", "engineering_operator", "marketing_content"),
    "activation": ("product_strategy", "customer_success", "engineering_operator", "marketing_content"),
    "retention": ("customer_success", "product_strategy", "market_intelligence", "engineering_operator"),
    "acquisition": ("marketing_content", "market_intelligence", "product_strategy", "customer_success"),
    "community": ("customer_success", "marketing_content", "product_strategy", "risk_governance"),
    "feedback": ("customer_success", "product_strategy", "engineering_operator", "market_intelligence"),
    "app_error": ("engineering_operator", "customer_success", "product_strategy", "risk_governance"),
    "security": ("risk_governance", "engineering_operator", "customer_success"),
    "revenue": ("roi_analyst", "product_strategy", "marketing_content", "market_intelligence"),
    "market_shift": ("market_intelligence", "product_strategy", "partnerships", "marketing_content"),
    "opportunity": ("market_intelligence", "product_strategy", "partnerships", "marketing_content"),
    "conversion": ("product_strategy", "marketing_content", "engineering_operator", "roi_analyst"),
    "feature_request": ("product_strategy", "engineering_operator", "customer_success"),
    "synthetic_qa": ("engineering_operator", "product_strategy", "risk_governance", "customer_success"),
    "service_health": ("engineering_operator", "customer_success", "risk_governance"),
    "baseline": ("market_intelligence", "product_strategy", "marketing_content", "customer_success",
                 "engineering_operator", "roi_analyst", "risk_governance"),
    "competition": ("market_intelligence", "product_strategy", "marketing_content"),
    "support": ("customer_success", "engineering_operator", "product_strategy"),
}


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical(x) -> str:
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def fingerprint(x) -> str:
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def require_id(value: str, name: str) -> str:
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ValueError("invalid_" + name)
    return value


def validate_health_url(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str) or len(value) > 220:
        raise ValueError("health_url_invalid")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.port not in (None, 443)
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in HEALTH_PATHS):
        raise ValueError("health_url_scope_invalid")
    # A hostname configured on a program alone is NEVER permission for a network call.
    return value


def init(db: sqlite3.Connection) -> None:
    db.executescript("""
       CREATE TABLE IF NOT EXISTS product_programs (
           company_id TEXT NOT NULL,
           project_id TEXT NOT NULL,
           name TEXT NOT NULL,
           vertical TEXT NOT NULL,
           objective TEXT NOT NULL,
           status TEXT NOT NULL,
           priority INTEGER NOT NULL,
           health_url TEXT,
           max_tasks_per_cycle INTEGER NOT NULL,
           created_at TEXT NOT NULL,
           updated_at TEXT NOT NULL,
           PRIMARY KEY(company_id, project_id)
       );
       CREATE TABLE IF NOT EXISTS product_observations (
           id TEXT PRIMARY KEY,
           company_id TEXT NOT NULL,
           project_id TEXT NOT NULL,
           source_event_id TEXT NOT NULL,
           payload_sha256 TEXT NOT NULL,
           source_kind TEXT NOT NULL,
           source_ref TEXT NOT NULL,
           signal TEXT NOT NULL,
           metric_name TEXT,
           metric_value REAL,
           sample_count INTEGER,
           summary TEXT NOT NULL,
           severity INTEGER NOT NULL,
           observed_at TEXT NOT NULL,
           recorded_at TEXT NOT NULL,
           verification TEXT NOT NULL,
           FOREIGN KEY(company_id, project_id)
                REFERENCES product_programs(company_id, project_id),
           UNIQUE(company_id, project_id, source_event_id)
       );
       CREATE INDEX IF NOT EXISTS ix_product_observations_project
         ON product_observations(company_id, project_id, recorded_at DESC);
       CREATE INDEX IF NOT EXISTS ix_product_programs_live
         ON product_programs(status, priority DESC);
    """)
    # Existing company queue is the single canonical queue. One additive
    # column supports prioritizing product events without altering old writes.
    columns = {r["name"] for r in db.execute("PRAGMA table_info(events)")}
    if "priority_score" not in columns:
        db.execute("ALTER TABLE events ADD COLUMN priority_score INTEGER NOT NULL DEFAULT 0")
    columns = {r["name"] for r in db.execute("PRAGMA table_info(tasks)")}
    for col in ("company_id", "project_id", "observation_id"):
        if col not in columns:
            db.execute("ALTER TABLE tasks ADD COLUMN " + col + " TEXT")
    db.execute("CREATE INDEX IF NOT EXISTS ix_product_task_scope ON tasks(company_id,project_id,status)")
    db.execute("CREATE INDEX IF NOT EXISTS ix_events_priority ON events(status,priority_score DESC,created_at)")
    db.commit()


def register(data: dict) -> dict:
    """Founder-authenticated internal programs start; unknown client scopes stay pending."""
    import core
    if not isinstance(data, dict) or set(data) - {
        "company_id", "project_id", "name", "vertical", "objective",
        "priority", "health_url", "max_tasks_per_cycle"}:
        raise ValueError("product_program_shape_invalid")
    company = require_id(data.get("company_id"), "company_id")
    project = require_id(data.get("project_id"), "project_id")
    vertical = require_id(data.get("vertical"), "vertical")
    name = data.get("name")
    objective = data.get("objective")
    if not isinstance(name, str) or not 3 <= len(name.strip()) <= 100:
        raise ValueError("product_name_invalid")
    if not isinstance(objective, str) or not 18 <= len(objective.strip()) <= 1200:
        raise ValueError("product_objective_invalid")
    if ("@" in objective or "api_key" in objective.lower() or "bearer " in objective.lower()):
        raise ValueError("sensitive_objective_rejected")
    priority = data.get("priority", 3)
    cap = data.get("max_tasks_per_cycle", 7)
    if type(priority) is not int or not 1 <= priority <= 5:
        raise ValueError("product_priority_invalid")
    if type(cap) is not int or not 2 <= cap <= 7:
        raise ValueError("product_cycle_budget_invalid")
    health = validate_health_url(data.get("health_url"))
    status = ("INTERNAL_ACTIVE" if company == INTERNAL_COMPANY else
              "FOUNDER_PROJECT_ACTIVE_NOT_LEGAL_TENANT" if company == FOUNDER_PORTFOLIO
              else "CLIENT_OWNER_VERIFICATION_REQUIRED")
    created = False
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        existing = db.execute(
            "SELECT * FROM product_programs WHERE company_id=? AND project_id=?",
            (company, project)).fetchone()
        if existing:
            stable = ("name", "vertical", "objective", "priority", "health_url", "max_tasks_per_cycle")
            intended = dict(name=name.strip(), vertical=vertical, objective=objective.strip(),
                            priority=priority, health_url=health, max_tasks_per_cycle=cap)
            if any(existing[k] != intended[k] for k in stable):
                raise ValueError("existing_product_program_requires_versioned_change")
        else:
            db.execute("""INSERT INTO product_programs
               (company_id,project_id,name,vertical,objective,status,priority,
                health_url,max_tasks_per_cycle,created_at,updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
               (company, project, name.strip(), vertical, objective.strip(), status,
                priority, health, cap, utc(), utc()))
            created = True
        # A first baseline is a genuine internal readiness gap, NOT customer
        # traction. Auto-detect without requiring a Founder prompt each day.
        if created and status in ACTIVE_STATES:
            _insert_observation(db, company, project, {
                "source_event_id": "initial-product-baseline",
                "source_kind": "REPORTED_OPERATIONAL",
                "source_ref": "company-os:program-registration",
                "signal": "baseline",
                "summary": "New product program: establish baseline, analytics, audience, engineering, community and cost evidence before claiming outcomes.",
                "severity": 1,
            }, verified=False)
        db.commit()
        row = db.execute("SELECT * FROM product_programs WHERE company_id=? AND project_id=?",
                         (company, project)).fetchone()
        return {"program": dict(row), "created": created, "operating": status in ACTIVE_STATES,
                "execution_queue": "EXISTING_COMPANY_OS_EVENTS_AND_TASKS",
                "customer_tenant_live": False,
                "legal_entity_claimed": False if company == FOUNDER_PORTFOLIO else None}


def bootstrap_internal() -> dict:
    """Deploy-time replay-safe Company OS bootstrap from a read-only source snapshot.

    This file is a projected portfolio operating plan, not a replacement for
    Sina's canonical portfolio registry or company/customer SSOT. Client scopes
    are NEVER automatically activated.
    """
    from pathlib import Path
    manifest_path = Path(__file__).with_name("product_portfolio_seed_v1.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("schema") != "noetfield.company-os.portfolio-projection.v1"
            or manifest.get("source_of_truth") !=
            "Noetfield-Systems/sina_founder_os/portfolio/PROJECT-AND-ASSET-REGISTRY.json"
            or not isinstance(manifest.get("programs"), list)
            or len(manifest["programs"]) > 25):
        raise ValueError("company_operating_projection_invalid")
    outcomes = {"created": 0, "unchanged": 0, "drift_blocked": 0}
    for entry in manifest["programs"]:
        if entry.get("company_id") not in (INTERNAL_COMPANY, FOUNDER_PORTFOLIO):
            raise ValueError("client_program_cannot_be_autoseeded")
        program = {key: value for key, value in entry.items()
                   if key in {"company_id","project_id","name","vertical",
                              "objective","priority","health_url","max_tasks_per_cycle"}}
        try:
            record = register(program)
            outcomes["created" if record["created"] else "unchanged"] += 1
        except ValueError as exc:
            if str(exc) != "existing_product_program_requires_versioned_change":
                raise
            outcomes["drift_blocked"] += 1
    return {**outcomes, "source": manifest["source_of_truth"],
            "source_snapshot_sha": manifest.get("source_git_blob_sha"),
            "queue": "EXISTING_COMPANY_OS_EVENTS"}


def _priority(program, signal, severity, kind):
    if kind == "SYNTHETIC_AGENT_QA":
        return min(30, 8 + severity * 5)
    weight = {
        "security": 45, "app_error": 38, "retention": 34,
        "activation": 33, "onboarding": 28, "conversion": 27,
        "revenue": 26, "community": 25, "acquisition": 24,
        "market_shift": 23, "opportunity": 21, "baseline": 9,
    }.get(signal, 17)
    return min(100, weight + 9 * severity + program["priority"] * 4)


def _insert_observation(db, company: str, project: str, payload: dict, verified: bool):
    program = db.execute(
        "SELECT * FROM product_programs WHERE company_id=? AND project_id=?",
        (company, project),
    ).fetchone()
    if not program or program["status"] not in ACTIVE_STATES:
        raise ValueError("product_program_not_operational")
    if not isinstance(payload, dict) or set(payload) - {
        "source_event_id", "source_kind", "source_ref", "signal",
        "metric_name", "metric_value", "sample_count", "summary", "severity", "observed_at"}:
        raise ValueError("product_signal_shape_invalid")
    source_event_id = payload.get("source_event_id")
    if (not isinstance(source_event_id, str) or
            not re.fullmatch(r"[A-Za-z0-9_.:-]{8,128}", source_event_id)):
        raise ValueError("source_event_id_invalid")
    source_kind = payload.get("source_kind")
    if source_kind not in KINDS and not (verified and source_kind == "FIRST_PARTY_HTTP_HEALTH"):
        raise ValueError("source_kind_invalid")
    ref = payload.get("source_ref")
    if not isinstance(ref, str) or not EVIDENCE_REF.fullmatch(ref):
        raise ValueError("evidence_reference_invalid")
    signal = payload.get("signal")
    if signal not in SIGNALS:
        raise ValueError("signal_type_invalid")
    summary = payload.get("summary")
    if not isinstance(summary, str) or not 12 <= len(summary) <= 500:
        raise ValueError("summary_invalid")
    # No raw user identities or secrets in model/task evidence.
    if "@" in summary or re.search(r"(?i)(password|authorization:|bearer\s|api[_-]?key\s*=)", summary):
        raise ValueError("sensitive_signal_rejected")
    metric_name = payload.get("metric_name")
    if metric_name is not None and (
        not isinstance(metric_name, str) or not SAFE_METRIC.fullmatch(metric_name)):
        raise ValueError("invalid_metric_name")
    metric_value = payload.get("metric_value")
    if metric_value is not None and (
        type(metric_value) not in (float, int) or
        not -1e9 <= float(metric_value) <= 1e9):
        raise ValueError("metric_value_invalid")
    samples = payload.get("sample_count")
    if samples is not None and (type(samples) is not int or not 0 <= samples <= 100000000):
        raise ValueError("sample_count_invalid")
    severity = payload.get("severity", 1)
    if type(severity) is not int or not 0 <= severity <= 4:
        raise ValueError("severity_invalid")
    # Same source event with omitted timestamp reuses its original time, even
    # when a retry arrives hours later; divergent evidence still conflicts.
    previous = db.execute(
        """SELECT id,payload_sha256,observed_at FROM product_observations
           WHERE company_id=? AND project_id=? AND source_event_id=?""",
        (company, project, source_event_id),
    ).fetchone()
    observed_at = payload.get("observed_at") or (previous["observed_at"] if previous else utc())
    try:
        dt = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.timestamp() > time.time() + 300:
            raise ValueError()
    except (TypeError, AttributeError, ValueError, OverflowError):
        raise ValueError("observed_at_invalid") from None
    normalized = {
        "source_event_id": source_event_id, "source_kind": source_kind,
        "source_ref": ref, "signal": signal, "summary": summary,
        "metric_name": metric_name, "metric_value": metric_value,
        "sample_count": samples, "severity": severity, "observed_at": observed_at,
    }
    sha = fingerprint(normalized)
    old = previous
    if old:
        if old["payload_sha256"] != sha:
            raise ValueError("source_event_id_conflicts_with_existing_evidence")
        return {"observation_id": old["id"], "idempotent": True}
    obs_id = "obs_" + hashlib.sha256(
        (company + ":" + project + ":" + source_event_id).encode()).hexdigest()[:32]
    verification = "FIRST_PARTY_HTTP_TRANSPORT_OBSERVED" if verified else (
        "SYNTHETIC_TEST_ONLY" if source_kind == "SYNTHETIC_AGENT_QA"
        else "SOURCE_REPORTED_UNVERIFIED")
    score = _priority(program, signal, severity, source_kind)
    db.execute("""INSERT INTO product_observations
       (id,company_id,project_id,source_event_id,payload_sha256,source_kind,
        source_ref,signal,metric_name,metric_value,sample_count,summary,severity,
        observed_at,recorded_at,verification)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
       (obs_id, company, project, source_event_id, sha, source_kind, ref,
        signal, metric_name, metric_value, samples, summary, severity,
        observed_at, utc(), verification))
    eid = "evt_" + hashlib.sha256(("product:" + obs_id).encode()).hexdigest()[:32]
    db.execute("""INSERT INTO events
       (id,event_type,source,brand,payload,status,created_at,idempotency_key,priority_score)
       VALUES (?,?,?,?,?,'queued',?,?,?)""",
       (eid, "product.signal_observed", "company_operating_program",
        "portfolio", canonical({"company_id": company, "project_id": project,
                                "observation_id": obs_id, "priority_score": score}),
        utc(), "product-signal:" + obs_id, score))
    return {"observation_id": obs_id, "event_id": eid, "idempotent": False,
            "priority_score": score, "verification": verification}


def observe(company: str, project: str, payload: dict) -> dict:
    """Authenticated operator submits evidence; no raw users or fabricated traction."""
    import core
    require_id(company, "company_id")
    require_id(project, "project_id")
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        result = _insert_observation(db, company, project, payload, verified=False)
        db.commit()
        return result


def process_signal(event: dict) -> dict:
    """Turn one signal into simultaneous specialist work + dependency-gated CEO.

    Does not create a second task system. Workers claim the canonical tasks.
    """
    import core
    payload = json.loads(event["payload"])
    if set(payload) != {"company_id", "project_id", "observation_id", "priority_score"}:
        raise ValueError("company_signal_event_invalid")
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        o = db.execute(
            """SELECT * FROM product_observations
               WHERE id=? AND company_id=? AND project_id=?""",
            (payload["observation_id"], payload["company_id"], payload["project_id"]),
        ).fetchone()
        p = db.execute(
            "SELECT * FROM product_programs WHERE company_id=? AND project_id=?",
            (payload["company_id"], payload["project_id"]),
        ).fetchone()
        if not o or not p or p["status"] not in ACTIVE_STATES:
            raise ValueError("product_evidence_or_owner_unavailable")
        existing = db.execute(
            "SELECT COUNT(*) n FROM tasks WHERE event_id=?", (event["id"],)
        ).fetchone()["n"]
        if existing:
            db.execute("UPDATE events SET status='processed',processed_at=? WHERE id=?",
                       (utc(), event["id"]))
            return {"existing": True, "tasks": existing}
        signal = o["signal"]
        roles = list(ROLES[signal])[:p["max_tasks_per_cycle"]]
        # Synthetic users are never inputs to paid acquisition / demand claims.
        if o["source_kind"] == "SYNTHETIC_AGENT_QA":
            roles = [r for r in roles if r not in ("roi_analyst", "sales_qualification")]
            if not roles:
                roles = ["engineering_operator", "product_strategy"]
        # Fairness: cap per-project work in the existing shared queue.
        queued = db.execute(
            """SELECT COUNT(*) n FROM tasks WHERE company_id=? AND project_id=?
               AND status IN ('queued','running')""",
            (p["company_id"], p["project_id"]),
        ).fetchone()["n"]
        if queued > 42:
            db.execute("UPDATE events SET status='deferred',error='product_backpressure',processed_at=? WHERE id=?",
                       (utc(), event["id"]))
            return {"deferred": True, "pending_tasks": queued}
        ids = []
        scope = p["project_id"]
        basis = (
            "Program: " + p["name"] + "; vertical: " + p["vertical"] +
            "; standing objective: " + p["objective"] + "; " +
            "Signal: " + signal + "; evidence: " + o["source_ref"] +
            "; integrity: " + o["verification"] + "; observation: " + o["summary"]
        )[:2000]
        for role in roles:
            tid = core.add_task(
                db, event["id"], None, "portfolio", role,
                p["name"] + " · " + signal + " · " + role,
                basis + ". Evaluate this from your specialist discipline; propose specific valuable next steps and evidence needs.",
                "Create internal work with a measurable metric, draft experiment or engineering work scope. No unpermitted deployment, sending, spending or fabricated claims.",
            )
            db.execute(
                "UPDATE tasks SET company_id=?,project_id=?,observation_id=? WHERE id=?",
                (p["company_id"], p["project_id"], o["id"], tid),
            )
            ids.append(tid)
        leader = core.add_task(
            db, event["id"], None, "portfolio", "chief_of_staff",
            p["name"] + " · integrated operating decision",
            basis + ". Reconcile Engineering, Market, Growth, Community, Product, Revenue and Risk results without inventing absent departments.",
            "Produce a prioritized executable work portfolio: next build, next growth experiment, next community activity, owner, cost ceiling, acceptance metric, and Founder-reserved approvals.",
        )
        db.execute(
            "UPDATE tasks SET company_id=?,project_id=?,observation_id=? WHERE id=?",
            (p["company_id"], p["project_id"], o["id"], leader),
        )
        for tid in ids:
            core.add_task_dependency(db, leader, tid)
        db.execute("UPDATE events SET status='processed',processed_at=? WHERE id=?",
                   (utc(), event["id"]))
        return {"existing": False, "specialists": roles,
                "task_count": len(ids) + 1, "executive_task": leader}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _approved_health_host(url: str | None) -> bool:
    if not url:
        return False
    try:
        parsed = urlsplit(validate_health_url(url))
    except (ValueError, TypeError):
        return False
    hosts = {x.strip().lower() for x in
             os.getenv("COMPANY_OS_APPROVED_OBSERVATION_HOSTS", "").split(",") if x.strip()}
    return parsed.hostname.lower() in hosts


def _probe(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET",
                                 headers={"Accept": "application/json",
                                          "User-Agent": "Noetfield-CompanyOS-ReadOnly-Probe/1"})
    try:
        with urllib.request.build_opener(_NoRedirect).open(req, timeout=4) as res:
            body = res.read(2049)
            status = res.status
        if len(body) > 2048:
            return status, "BODY_TOO_LARGE"
        data = json.loads(body)
        if isinstance(data, dict) and (data.get("ok") is False or data.get("ready") is False):
            return status, "APPLICATION_REPORTS_UNHEALTHY"
        return status, "HTTP_OK" if status == 200 else "HTTP_ERROR"
    except urllib.error.HTTPError as e:
        return e.code, "HTTP_ERROR"
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, TypeError):
        return 0, "UPSTREAM_UNAVAILABLE"


def _resume_deferred(db: sqlite3.Connection) -> int:
    """Reclaim bounded paused signals after the existing project's backlog clears."""
    deferred = db.execute(
        "SELECT id,payload FROM events WHERE event_type='product.signal_observed' "
        "AND status='deferred' ORDER BY priority_score DESC LIMIT 20").fetchall()
    count = 0
    for event in deferred:
        payload = json.loads(event["payload"])
        running = db.execute(
            """SELECT COUNT(*) n FROM tasks WHERE company_id=? AND project_id=?
               AND status IN ('queued','running')""",
            (payload["company_id"], payload["project_id"])).fetchone()["n"]
        if running <= 15:
            db.execute("UPDATE events SET status='queued',processed_at=NULL,error=NULL WHERE id=?",
                       (event["id"],))
            count += 1
    return count


def tick_due() -> dict:
    """Called by existing core.daily_tick(); no parallel scheduler.

    Observe only exact first-party approved HTTPS health hosts. Polling is
    transport evidence, NEVER inferred signups, growth, revenue or engagement.
    """
    import core
    with core.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        resumed = _resume_deferred(db)
        db.commit()
        programs = [dict(x) for x in db.execute(
            "SELECT * FROM product_programs WHERE status IN "
            "('INTERNAL_ACTIVE','FOUNDER_PROJECT_ACTIVE_NOT_LEGAL_TENANT') "
            "AND health_url IS NOT NULL ORDER BY priority DESC LIMIT 20")]
        state = db.execute(
            "SELECT value FROM state WHERE key='product_health_poll_at'"
        ).fetchone()
    if state and time.time() - float(state["value"]) < 1800:
        return {"state": "NOT_DUE"}
    with core.connect() as db:
        db.execute("""INSERT INTO state(key,value) VALUES('product_health_poll_at',?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value""", (str(time.time()),))
    polled = 0
    for p in programs:
        if not _approved_health_host(p["health_url"]):
            continue
        status, outcome = _probe(p["health_url"])
        # Time bucket ensures idempotent recovery and suppresses periodic
        # reprocessing within the same 30-minute observation window.
        key = "health-%s-%s-%d" % (
            p["project_id"][:12], str(status), int(time.time() // 1800))
        payload = {
            "source_event_id": key,
            "source_kind": "FIRST_PARTY_HTTP_HEALTH",
            "source_ref": p["health_url"],
            "signal": "service_health",
            "summary": ("Read-only product HTTP health check: " + outcome +
                        "; transport status " + str(status) +
                        "; this is not evidence of real users, adoption or revenue."),
            "severity": 3 if status != 200 or outcome != "HTTP_OK" else 0,
            "metric_name": "http_status", "metric_value": status,
            "sample_count": 1,
        }
        with core.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                """SELECT metric_value,summary,recorded_at FROM product_observations
                   WHERE company_id=? AND project_id=? AND source_kind='FIRST_PARTY_HTTP_HEALTH'
                   ORDER BY recorded_at DESC LIMIT 1""",
                (p["company_id"], p["project_id"])).fetchone()
            unchanged = (prior is not None and prior["metric_value"] == status
                         and outcome in prior["summary"])
            if unchanged:
                try:
                    age = time.time()-datetime.fromisoformat(
                        prior["recorded_at"].replace("Z","+00:00")).timestamp()
                except ValueError:
                    age = 86400
                if age < 86400:
                    db.commit()
                    continue
            _insert_observation(db, p["company_id"], p["project_id"],
                                payload, verified=True)
            db.commit()
        polled += 1
    return {"state": "OBSERVED", "new_health_signals": polled,
            "deferred_resumed": resumed,
            "event_queue": "EXISTING_COMPANY_OS", "real_users_claimed": 0}


def _directional_forecasts(signals: list[dict]) -> list[dict]:
    """Transparent one-sample trend from source-reported aggregates, not ML or truth.

    Synthetic QA, health checks and self-asserted sales outcomes can never be
    represented as customer count or independently verified business forecasts.
    """
    groups: dict[str,list[float]] = {}
    for item in reversed(signals):
        if (item["source_kind"] not in ("REPORTED_REAL_USER_ANALYTICS","REPORTED_OPERATIONAL")
                or item["metric_name"] is None
                or item["metric_value"] is None):
            continue
        groups.setdefault(item["metric_name"],[]).append(float(item["metric_value"]))
    forecasts = []
    for metric, series in sorted(groups.items()):
        if len(series) < 3:
            continue
        latest = series[-5:]
        slope = (latest[-1] - latest[0]) / (len(latest)-1)
        direction = "INCREASING" if slope > 1e-8 else "DECREASING" if slope < -1e-8 else "FLAT"
        forecasts.append({
            "metric": metric, "recent_samples": len(latest),
            "direction": direction, "one_next_sample_heuristic": round(latest[-1]+slope,4),
            "change_per_observation": round(slope,4),
            "evidence_quality": "SOURCE_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
            "confidence": "LOW", "causal_claim": False,
            "business_forecast_verified": False,
        })
    return forecasts[:15]


def portfolio(company_id: str | None = None) -> dict:
    """Company-scoped operations, user/synthetic separation, and real run status."""
    import core
    with core.connect() as db:
        if company_id:
            require_id(company_id, "company_id")
        programs = [dict(x) for x in db.execute(
            "SELECT * FROM product_programs " + (
                "WHERE company_id=? " if company_id else "") +
            "ORDER BY priority DESC,created_at LIMIT 100",
            (company_id,) if company_id else (),
        )]
        items = []
        for p in programs:
            company, project = p["company_id"], p["project_id"]
            signals = [dict(x) for x in db.execute(
                """SELECT signal,source_kind,verification,metric_name,metric_value,
                   sample_count,severity,recorded_at,source_ref
                   FROM product_observations WHERE company_id=? AND project_id=?
                   ORDER BY recorded_at DESC,id DESC LIMIT 25""", (company, project))]
            statuses = [dict(x) for x in db.execute(
                """SELECT status,COUNT(*) AS count
                   FROM tasks WHERE company_id=? AND project_id=?
                   GROUP BY status""", (company, project))]
            real_reports = sum(x["source_kind"] == "REPORTED_REAL_USER_ANALYTICS"
                               for x in signals)
            synthetic = sum(x["source_kind"] == "SYNTHETIC_AGENT_QA" for x in signals)
            latest = db.execute(
                """SELECT id,role,status,updated_at FROM tasks
                   WHERE company_id=? AND project_id=?
                   ORDER BY updated_at DESC LIMIT 1""", (company, project)).fetchone()
            items.append({
                "company_id": company, "project_id": project,
                "name": p["name"], "vertical": p["vertical"],
                "objective": p["objective"], "status": p["status"],
                "priority": p["priority"], "health_monitoring_authorized":
                    _approved_health_host(p["health_url"]),
                "specialist_tasks_by_state": {s["status"]: s["count"] for s in statuses},
                "latest_task": dict(latest) if latest else None,
                "last_signals": signals,
                "directional_signal_forecasts": _directional_forecasts(signals),
                "synthetic_qa_observations": synthetic,
                "reported_real_user_observations_unverified": real_reports,
                "verified_real_users": None,
                "verified_revenue": None,
                "customer_tenant_verified": company == INTERNAL_COMPANY,
                "independent_verifier_connected": False,
            })
    return {"schema": SCHEMA, "source": "company-os-core",
            "queue": "existing events + tasks + runs",
            "worker": "same company core worker", "program_count": len(items),
            "programs": items, "real_user_metrics_status": "NOT_CONNECTED",
            "synthetic_qa_excluded_from_traction": True,
            "general_code_execution": "NOT_COMMISSIONED",
            "outbound_marketing_execution": "HUMAN_RESERVED"}
