"""Portfolio operations INSIDE the existing Business OS queue, not another OS.

Sina Founder OS owns the canonical portfolio. This module consumes a narrowly
authenticated read-only projection, samples public engineering signals, and
schedules project-scoped department tasks using EXISTING events/tasks/runs.
No tenant creation, model-produced permits, customer outreach or deployment.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import logging
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SCHEMA = "sina.company-os.portfolio-projection.v1"
EVENT_SCHEMA = "noos.portfolio-operations-cycle.v1"
FEED_HOST = "sina-founder-os-staging-staging.up.railway.app"
FEED_PATH = "/api/v1/internal/company-portfolio"
CADENCE_SECONDS = 20 * 60
MAX_PROJECTS_PER_TICK = 4
ALLOWED_COMPANY_IDS = {None, "noetfield-systems-inc"}
PROJECT_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,90}$")
REPO_PATTERN = re.compile(r"^Noetfield-Systems/([A-Za-z0-9_.-]{1,90})$")
log = logging.getLogger("noetfield.business_os.portfolio_studio")

# One shared company queue; department seats map to existing NOOS roles.
DEPARTMENTS = (
    ("market_intelligence", "External discovery and market intelligence"),
    ("product_strategy", "Product discovery and user journeys"),
    ("engineering_operator", "Engineering, release planning and maintainability"),
    ("marketing_editorial", "PLG, free resources and owned distribution"),
    ("customer_success", "Community, genuine onboarding and retention"),
    ("partnerships", "Ecosystem, creator and network distribution"),
    ("roi_analyst", "Growth analytics and outcome measurement"),
    ("risk_governance", "Consent, quality and independent QA readiness"),
    ("chief_of_staff", "Synthesis, resource allocation and next decision"),
)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def configured():
    url = os.getenv("SINA_PORTFOLIO_FEED_URL", "").strip()
    token = os.getenv("SINA_COMPANY_PORTFOLIO_TOKEN", "").strip()
    parsed = urllib.parse.urlsplit(url)
    return (len(token) >= 40 and parsed.scheme == "https"
            and parsed.hostname == FEED_HOST and parsed.port in (None, 443)
            and parsed.path == FEED_PATH and not parsed.query and not parsed.fragment
            and not parsed.username and not parsed.password)


def _read_json(request, limit=120_000, timeout=8):
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout) as response:
        raw = response.read(limit + 1)
        if len(raw) > limit:
            raise ValueError("remote_response_too_large")
        if response.status != 200:
            raise ValueError("remote_http_not_200")
    return json.loads(raw)


def fetch_portfolio():
    if not configured():
        raise ValueError("portfolio_feed_not_configured")
    request = urllib.request.Request(
        os.environ["SINA_PORTFOLIO_FEED_URL"],
        headers={
            "X-Sina-Portfolio-Token": os.environ["SINA_COMPANY_PORTFOLIO_TOKEN"],
            "Accept": "application/json",
            "User-Agent": "Noetfield-CompanyOS-PortfolioSensor/1",
        },
        method="GET",
    )
    payload = _read_json(request)
    if (not isinstance(payload, dict) or payload.get("schema") != SCHEMA
            or payload.get("owner") != "sina_founder_os"
            or payload.get("execution_permit_issued") is not False
            or payload.get("runtime_states_verified") is not False
            or payload.get("customer_metrics_included") is not False
            or payload.get("company_entity_provisioning_authorized") is not False):
        raise ValueError("portfolio_projection_schema_invalid")
    items = payload.get("projects")
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ValueError("portfolio_projects_invalid")
    ids = set()
    required = {"project_id", "name", "company_id", "owner_scope", "type",
                "status", "source_repository", "product_id"}
    for project in items:
        if (not isinstance(project, dict) or set(project) != required
                or not PROJECT_PATTERN.fullmatch(str(project["project_id"]))
                or project["project_id"] in ids
                or project["company_id"] not in ALLOWED_COMPANY_IDS):
            raise ValueError("portfolio_project_boundary_invalid")
        ids.add(project["project_id"])
        for field in ("name", "owner_scope", "type", "status", "source_repository", "product_id"):
            if not isinstance(project[field], str) or len(project[field]) > 160:
                raise ValueError("portfolio_project_string_invalid")
        if project["source_repository"] and not REPO_PATTERN.fullmatch(project["source_repository"]):
            raise ValueError("portfolio_repo_not_allowlisted")
    canonical = json.dumps(items, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(fingerprint, str(payload.get("projection_sha256", ""))):
        raise ValueError("portfolio_projection_digest_invalid")
    return payload


def probe_public_repository(project):
    """Unauthenticated PUBLIC GitHub metadata. Not proof of users or traction."""
    match = REPO_PATTERN.fullmatch(project["source_repository"])
    if not match:
        return {"status": "NO_REPOSITORY_REFERENCE", "user_traction": "UNKNOWN"}
    url = "https://api.github.com/repos/Noetfield-Systems/" + match.group(1)
    req = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json",
                      "User-Agent": "Noetfield-CompanyOS-ReadOnly/1"}, method="GET")
    observation = {"source": url, "observed_at": utc_now(),
                   "user_traction": "UNKNOWN", "revenue": "UNKNOWN"}
    try:
        data = _read_json(req, limit=32_768, timeout=5)
        if not isinstance(data, dict) or data.get("full_name") != project["source_repository"]:
            return {**observation, "status": "INVALID_PUBLIC_REPO_RESPONSE"}
        return {**observation, "status": "PUBLIC_REPO_OBSERVED",
                "pushed_at": str(data.get("pushed_at") or "")[:30],
                "open_issues_including_prs": data.get("open_issues_count")
                if type(data.get("open_issues_count")) is int else None,
                "stargazers_not_users": data.get("stargazers_count")
                if type(data.get("stargazers_count")) is int else None}
    except urllib.error.HTTPError as err:
        return {**observation, "status": "REPO_HTTP_" + str(err.code)}
    except (OSError, ValueError, UnicodeError):
        return {**observation, "status": "REPO_UNAVAILABLE"}


def score_hypothesis(project, observation, feedback_count=0):
    """Prioritize opportunity for investigation, never invent market validation."""
    kind = (project["type"] + " " + project["name"]).lower()
    score = 30
    if any(x in kind for x in ("match", "community", "social", "messaging", "founder", "network")):
        score += 30  # Founder-declared consumer/network-effect priority
    if any(x in kind for x in ("trade", "token", "web3", "creator", "data-tool")):
        score += 17
    if any(x in kind for x in ("saas", "verification", "workflow")):
        score += 10
    if observation.get("status") == "PUBLIC_REPO_OBSERVED":
        score += 5  # Accessible source, NOT product-market fit
    score += min(12, 4 * feedback_count)  # Only actual stored product feedback
    return min(100, score)


def _state_get(db, key):
    row = db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
    return row["value"] if row else None


def _state_put(db, key, value):
    db.execute("INSERT INTO state(key,value) VALUES(?,?) ON CONFLICT(key) "
               "DO UPDATE SET value=excluded.value", (key, str(value)))


def tick(fetcher=None, probe=None, timestamp=None):
    """Existing Business OS coordinator calls this. No second scheduler.

    State prevents duplicate cycles across restarts; a 20-minute round-robin
    means several products are active in the same company operating window.
    """
    from core import connect
    current = time.time() if timestamp is None else float(timestamp)
    if not configured() and fetcher is None:
        with connect() as db:
            _state_put(db, "portfolio_studio_state", "NOT_CONFIGURED")
        return {"state": "NOT_CONFIGURED", "queued": 0}
    with connect() as db:
        last = float(_state_get(db, "portfolio_studio_last_attempt") or 0)
        # Recover provider/auth outages promptly without spawning a second timer.
        retry_window = 90 if _state_get(db, "portfolio_studio_state") == "BLOCKED" else CADENCE_SECONDS
        if current - last < retry_window:
            return {"state": "DEFERRED", "queued": 0}
        _state_put(db, "portfolio_studio_last_attempt", current)
    try:
        feed = (fetcher or fetch_portfolio)()
        projects = feed["projects"]
        # Always validate injected test fetchers as strictly as the live HTTP path.
        if fetcher is not None:
            encoded = json.dumps(projects, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            expected = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
            if feed.get("schema") != SCHEMA or feed.get("owner") != "sina_founder_os" or not hmac.compare_digest(expected, str(feed.get("projection_sha256", ""))):
                raise ValueError("injected_feed_invalid")
        today = datetime.fromtimestamp(current, timezone.utc).date().isoformat()
        with connect() as db:
            pending = []
            for item in projects:
                if item["company_id"] not in ALLOWED_COMPANY_IDS:
                    continue
                fingerprint = hashlib.sha256((today + ":" + item["project_id"]).encode()).hexdigest()[:28]
                event_id = "evt_studio_" + fingerprint
                existing = db.execute("SELECT id FROM events WHERE id=?", (event_id,)).fetchone()
                if existing is None:
                    feedback = db.execute(
                        "SELECT COUNT(*) n FROM feedback WHERE brand=?",
                        ("project:" + item["project_id"],)).fetchone()["n"]
                    # Sorting before probes keeps expensive calls capped to 4.
                    estimated = score_hypothesis(item, {"status": "NOT_PROBED"}, feedback)
                    pending.append((-estimated, item["project_id"], event_id, item, feedback))
        pending.sort()
        selected = pending[:MAX_PROJECTS_PER_TICK]
        generated = []
        for _, pid, eid, item, feedback in selected:
            signal = (probe or probe_public_repository)(item)
            score = score_hypothesis(item, signal, feedback)
            generated.append((eid, {
                "schema": EVENT_SCHEMA, "project": item, "observation": signal,
                "hypothesis_score": score, "score_basis": "STRATEGIC_HEURISTIC_NOT_TRACTION",
                "feedback_events_observed": feedback, "cycle_day": today,
                "registry_source_sha256": feed["projection_sha256"],
                "source_of_truth": feed.get("source_of_truth"),
                "external_action_executed": False,
            }))
        with connect() as db:
            for eid, payload in generated:
                db.execute(
                    "INSERT OR IGNORE INTO events "
                    "(id,event_type,source,brand,payload,status,created_at) "
                    "VALUES(?,?,?,?,?,'queued',?)",
                    (eid, "portfolio.studio.cycle", "sina_founder_os_verified_projection",
                     "project:" + payload["project"]["project_id"],
                     json.dumps(payload, ensure_ascii=False, sort_keys=True), utc_now()))
            _state_put(db, "portfolio_studio_state", "QUEUED" if generated else "CURRENT")
            _state_put(db, "portfolio_studio_last_success", utc_now())
            _state_put(db, "portfolio_studio_source_sha", feed["projection_sha256"])
            _state_put(db, "portfolio_studio_last_error", "")
        print("company_portfolio_cycle=" + json.dumps({
            "registry_projects": len(projects), "new_project_cycles": len(generated),
            "project_ids": [p["project"]["project_id"] for _, p in generated],
            "read_only": True, "source_sha": feed["projection_sha256"][:16],
        }, sort_keys=True), flush=True)
        return {"state": "QUEUED" if generated else "CURRENT", "queued": len(generated)}
    except Exception as exc:
        with connect() as db:
            _state_put(db, "portfolio_studio_state", "BLOCKED")
            _state_put(db, "portfolio_studio_last_error", type(exc).__name__)
        log.warning("portfolio_cycle_blocked error_type=%s", type(exc).__name__)
        return {"state": "BLOCKED", "queued": 0, "error_type": type(exc).__name__}


def process_event(event):
    """Use existing NOOS multi-role task queue and dependency graph."""
    from core import connect, add_task, add_task_dependency, now
    payload = json.loads(event["payload"])
    if payload.get("schema") != EVENT_SCHEMA or payload.get("external_action_executed") is not False:
        raise ValueError("portfolio_event_invalid")
    project = payload["project"]
    pid = project["project_id"]
    if not PROJECT_PATTERN.fullmatch(pid) or event["brand"] != "project:" + pid:
        raise ValueError("portfolio_event_scope_mismatch")
    title = project["name"]
    score = payload["hypothesis_score"]
    signal = payload["observation"]
    evidence = (signal.get("source") or "no_public_repository") + ": " + signal.get("status", "unverified")
    remit = {
        "market_intelligence": ("Research target members, competing products and market shifts; distinguish actual links from hypotheses.", "Produce a source-backed discovery agenda and updated assumptions."),
        "product_strategy": ("Map real onboarding, matching, sharing and repeat-use journeys; select experiments worth developing.", "Propose an instrumentable product change with acceptance metrics."),
        "engineering_operator": ("Inspect the referenced product repository and operational problems through a governed work packet, not direct uncontrolled deployment.", "Specify the next bounded code change and tests for an authorized builder."),
        "marketing_editorial": ("Prepare free useful tools, SEO, learning content and opt-in community distribution; exclude cold email and fabricated social proof.", "Draft one truthful organic acquisition artifact, do not publish."),
        "customer_success": ("Design invite, activation, referral, retention and moderation operations for actual humans; synthetic QA users must remain explicitly labeled and excluded from traction.", "Propose opt-in community activation and a synthetic journey test plan."),
        "partnerships": ("Discover creators, ecosystem communities and distribution mechanisms; do not send unsolicited messages.", "Prepare one opt-in ecosystem collaboration hypothesis."),
        "roi_analyst": ("Separate verified users, synthetic test users, signup conversion, D1/D7 retention, cost and revenue; UNKNOWN is not zero.", "Specify observable event instrumentation and decision thresholds."),
        "risk_governance": ("Review privacy, claims, third-party integrations and release gates. Treat test actors as synthetic and protect real-user consent.", "Document release risks and independent verification requirements."),
        "chief_of_staff": ("Review completed departmental findings and actual signal provenance; allocate bounded work across this product and recommend continuation.", "Recommend the next highest-impact governed WorkPacket; no deployment, spend or public claim without permit."),
    }
    with connect() as db:
        exists = db.execute("SELECT COUNT(*) n FROM tasks WHERE event_id=?", (event["id"],)).fetchone()["n"]
        if exists:
            db.execute("UPDATE events SET status='processed',processed_at=? WHERE id=?", (now(),event["id"]))
            return {"created": 0, "deduplicated": True}
        specialist_ids = []
        for role, dept in DEPARTMENTS:
            desc, action = remit[role]
            task_id = add_task(db,event["id"],None,event["brand"],role,
                title[:85] + " · " + dept,
                "PROJECT: " + pid + ". Portfolio scope: " + str(project["owner_scope"]) +
                ". Evidence: " + evidence[:190] +
                ". Registry status unverified as live. " + desc,
                action)
            db.execute("UPDATE tasks SET priority_rank=? WHERE id=?", (max(1,100-score),task_id))
            if role == "chief_of_staff":
                for dependency in specialist_ids:
                    add_task_dependency(db,task_id,dependency)
            else:
                specialist_ids.append(task_id)
        db.execute("UPDATE events SET status='processed',processed_at=? WHERE id=?",
                   (now(),event["id"]))
    print("company_departments_started="+json.dumps({"project_id":pid,"departments":len(DEPARTMENTS),"external_effect":False},sort_keys=True),flush=True)
    return {"created": len(DEPARTMENTS), "project_id": pid}


def process_task(task):
    """No fake agent/model/user results; structured evidence-based internal work."""
    from core import connect, idof, now
    with connect() as db:
        row = db.execute("SELECT payload FROM events WHERE id=? AND event_type='portfolio.studio.cycle'",
                         (task["event_id"],)).fetchone()
        if row is None:
            return False
        payload = json.loads(row["payload"])
        if task["brand"] != "project:" + payload["project"]["project_id"]:
            raise ValueError("portfolio_task_scope_mismatch")
        participants = db.execute(
            "SELECT role,status,result FROM tasks WHERE event_id=? AND id<>?",
            (task["event_id"],task["id"])).fetchall()
    role = task["role"]
    project,obs = payload["project"],payload["observation"]
    evidence = {
        "source": obs.get("source"), "observed_at": obs.get("observed_at"),
        "repo_status": obs.get("status"), "registry_projection_sha256": payload["registry_source_sha256"],
    }
    known = obs.get("status") == "PUBLIC_REPO_OBSERVED"
    notes = {
        "market_intelligence": "External public-repo signal obtained; demand, competitors and human interest still need sourced discovery." if known else "Public source unavailable. Market and user-demand evidence remain unknown.",
        "product_strategy": "Explore a free first-success journey, sharing, network matching and retention loops; instrument a genuine conversion funnel before ranking improvements.",
        "engineering_operator": "Candidate governed repository inspection and scoped feature PR; no source code was written by this task.",
        "marketing_editorial": "Draft useful free-content and participation pathways, SEO and transparent invitations; no messages were sent and no campaign launched.",
        "customer_success": "Prepare member activation, moderation, genuine retention and clearly identified synthetic/agentic QA cohorts. No fake human traction.",
        "partnerships": "Identify opt-in communities and creator ecosystems after evidence review; no outreach performed.",
        "roi_analyst": "Signups, activated humans, verified retention, product events, conversions and revenue are UNKNOWN until a scoped analytics connector supplies real data.",
        "risk_governance": "External action requires valid Governor permit and separate QA; synthetic accounts must never masquerade as real users.",
        "chief_of_staff": "Departmental internal drafts are gathered; select two reversible development/PLG experiments when Governor and runtime are ready.",
    }
    dependencies = [p["role"] for p in participants if p["status"] in ("drafted","approved")]
    recommendation = {
        "schema": "noos.portfolio-department-result.v1",
        "project_id": project["project_id"], "company_id": project["company_id"],
        "role": role, "assessment": notes.get(role,"Internal task only."),
        "source_evidence": evidence,
        "strategic_hypothesis_score": payload["hypothesis_score"],
        "score_is_market_validation": False,
        "verified_human_users": None, "synthetic_user_count": None,
        "revenue_collected": None,
        "departments_completed_before_synthesis": dependencies if role=="chief_of_staff" else [],
        "next_best_action": task["next_action"],
        "requires_governor_for_external_effect": True,
        "external_action_executed": False,
        "actual_product_mutation": False,
    }
    with connect() as db:
        db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (idof("run"),task["id"],role,"deterministic-evidence","none",
                    "completed",0,0,now(),now(),json.dumps(recommendation,ensure_ascii=False)))
        db.execute("UPDATE tasks SET status='drafted',result=?,updated_at=? WHERE id=?",
                   (json.dumps({"provider":"deterministic-evidence",
                     "recommendation":recommendation,"external_action":"not_executed"},
                    ensure_ascii=False),now(),task["id"]))
    if role == "chief_of_staff":
        print("company_executive_synthesis=" + json.dumps({
            "project_id": project["project_id"],
            "specialist_drafts_read": len(dependencies),
            "governor_permit": False, "public_actions": 0
        },sort_keys=True),flush=True)
    return True


def overview():
    """Current evidence-backed departmental operating picture, not a success badge."""
    from core import connect
    with connect() as db:
        state = {k: _state_get(db,k) for k in (
            "portfolio_studio_state","portfolio_studio_last_success",
            "portfolio_studio_last_error","portfolio_studio_source_sha")}
        rows = db.execute(
            "SELECT e.brand,e.id,e.created_at,e.status,e.payload,"
            " COUNT(t.id) departments,"
            " SUM(CASE WHEN t.status IN ('drafted','approved') THEN 1 ELSE 0 END) completed,"
            " SUM(CASE WHEN t.status IN ('blocked','failed') THEN 1 ELSE 0 END) blocked "
            "FROM events e LEFT JOIN tasks t ON t.event_id=e.id "
            "WHERE e.event_type='portfolio.studio.cycle' "
            "GROUP BY e.id ORDER BY e.created_at DESC LIMIT 80").fetchall()
        items = []
        for r in rows:
            p = json.loads(r["payload"])
            items.append({
                "project_id": p["project"]["project_id"],"name":p["project"]["name"],
                "company_id":p["project"]["company_id"], "source_repo":p["project"]["source_repository"],
                "evidence_status":p["observation"].get("status"),
                "hypothesis_score_not_traction":p["hypothesis_score"],
                "department_tasks":r["departments"],"internal_drafts":r["completed"],
                "blocked_tasks":r["blocked"],"event_status":r["status"],
                "cycle_started_at":r["created_at"],
            })
    return {"schema":"noos.portfolio-operations-overview.v1",
            "state":state,"project_cycles":items,
            "autonomous_product_build_verified":False,
            "automatic_public_distribution_enabled":False,
            "synthetic_activity_counted_as_traction":False,
            "source_registry_owner":"sina_founder_os",
            "execution_queue_owner":"existing_business_os_core"}
