"""Return real Company OS observations to Sina's EXISTING organizational intake.

One source event -> one durable Company OS event -> one authenticated Sina signal.
No second event queue, scheduler, memory, company registry or Governor. This
adapter cannot execute tools, contact buyers, sign permits or claim D4 proof.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

EVENT = "company.founder_signal"
SINA_ORIGIN = "https://sina-founder-os-staging-staging.up.railway.app"
SINA_PATH = "/api/v1/organization/events"
TOKEN_ENV = "COMPANY_OS_SINA_EVENT_TOKEN"
MAX_BODY = 4096
MAX_RESPONSE = 16000
RETRY_LIMIT = 6
SOURCE_ID = "companyos"
# Only aliases independently identified across both repos. Sina's live SSOT
# projection resolves ownership, not this list. Unknown aliases fail closed.
CANONICAL_ALIASES = {
    "signalforge": "signal-forge",
    "atelier": "atelier-community",
    "trade-radar": "trade-radar-platform",
}
_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,90}$")
_OBS = re.compile(r"^obs_[0-9a-f]{32}$")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def make_signal(observation: dict) -> dict | None:
    """Only derived, anonymous and truly observed signals are eligible."""
    obs = observation.get("id")
    project = observation.get("project_id")
    company = observation.get("company_id")
    if not isinstance(obs, str) or not _OBS.fullmatch(obs):
        return None
    if not isinstance(project, str) or not _ID.fullmatch(project):
        return None
    if company is not None and (not isinstance(company, str) or not _ID.fullmatch(company)):
        return None
    kind, name = observation.get("source_kind"), observation.get("signal")
    severity = observation.get("severity")
    if type(severity) is not int or not 0 <= severity <= 4:
        return None
    if kind == "FIRST_PARTY_HTTP_HEALTH" and name == "service_health" and severity >= 2:
        event_type = "service_degraded"
        summary = "Company OS directly observed a degraded approved first-party product health endpoint; operational diagnosis required"
        confidence, impact = 0.8, 4
        metrics = {"errors": 1}
    elif kind == "REPORTED_PUBLIC_MARKET" and name in ("market_shift", "competition"):
        event_type = "market_signal"
        summary = "Company OS detected a public developer-market headline relevant to an existing operating product; demand unverified"
        confidence, impact = 0.25, 1
        metrics = {}
    elif kind == "REPORTED_OPERATIONAL" and name == "app_error" and severity >= 2:
        event_type = "service_degraded"
        summary = "Company OS received a source-reported product error; independently recheck availability before any recovery action"
        confidence, impact = 0.2, 2
        metrics = {"errors": 1}
    else:
        return None

    observed = observation.get("observed_at")
    if not isinstance(observed, str) or len(observed) > 40:
        return None
    try:
        stamp = datetime.fromisoformat(observed.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            return None
    except ValueError:
        return None
    return {
        "source_id": SOURCE_ID,
        "source_event_id": "companyos:" + obs,
        "event_type": event_type,
        "project_id": project,
        "company_id": company,
        "observed_at": observed,
        "summary": summary,
        "evidence_ref": "receipt:noetfield/company-os/" + obs,
        "metrics": metrics,
        "confidence": confidence,
        "impact": impact,
    }


def enqueue_in_existing_events(db: sqlite3.Connection, observation: dict) -> str | None:
    """Called from the SAME observation transaction; retry is idempotent."""
    body = make_signal(observation)
    if body is None:
        return None
    obs_id = observation["id"]
    event_id = "evt_" + hashlib.sha256(("founder-federation:" + obs_id).encode()).hexdigest()[:32]
    key = "company-sina:" + obs_id
    db.execute("""INSERT OR IGNORE INTO events
      (id,event_type,source,brand,payload,status,created_at,idempotency_key,priority_score)
      VALUES (?,?,?,?,?,'queued',?,?,?)""",
      (event_id, EVENT, "company-os-federation", "portfolio",
       json.dumps(body, sort_keys=True, separators=(",", ":")),
       datetime.now(timezone.utc).isoformat(), key,
       # Process the owning product signal FIRST, then federate the outcome.
       # A feedback event cannot starve the original Company OS work.
       1 if body["event_type"] == "service_degraded" else 0))
    return event_id


def configured() -> bool:
    token = os.getenv(TOKEN_ENV, "")
    return 40 <= len(token) <= 256


def deliver(event: dict, *, opener=None) -> dict:
    """Send bounded non-PII signal to pinned Founder ingress, never free-form URL."""
    if event.get("event_type") != EVENT or event.get("source") != "company-os-federation":
        raise ValueError("sina_federation_event_class_invalid")
    if not configured():
        raise RuntimeError("sina_federation_identity_not_configured")
    body = json.loads(event["payload"])
    if not isinstance(body, dict) or set(body) != {
        "source_id", "source_event_id", "event_type", "project_id", "company_id",
        "observed_at", "summary", "evidence_ref", "metrics", "confidence", "impact",
    } or body.get("source_id") != SOURCE_ID:
        raise ValueError("sina_federation_payload_invalid")
    # Reconstruct the allowed event rather than forwarding arbitrary caller text.
    # The exact event is from our own insert transaction and must be immutable.
    if not body["source_event_id"].startswith("companyos:obs_"):
        raise ValueError("sina_federation_origin_invalid")

    # Do not trust Company OS's local product aliases as canonical legal scope.
    # Recheck the actual authenticated Founder SSOT through the existing
    # read-only portfolio adapter (outside all SQLite write transactions).
    import founder_portfolio_bridge
    canonical_id = CANONICAL_ALIASES.get(body["project_id"], body["project_id"])
    source = founder_portfolio_bridge.fetch_projection()
    matching = [p for p in source["projects"] if p["project_id"] == canonical_id]
    if len(matching) != 1:
        raise ValueError("sina_federation_project_unmapped_in_canonical_ssot")
    canonical_company = matching[0]["company_id"]
    company_scope = None if body["company_id"] == "founder-portfolio" else body["company_id"]
    if canonical_company != company_scope:
        raise ValueError("sina_federation_owner_scope_conflict")
    body["project_id"] = canonical_id
    body["company_id"] = canonical_company

    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_BODY:
        raise ValueError("sina_federation_body_too_large")
    req = urllib.request.Request(
        SINA_ORIGIN + SINA_PATH, data=raw, method="POST",
        headers={
            "Authorization": "Bearer " + os.environ[TOKEN_ENV],
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Noetfield-CompanyOS-EventBridge/1.0",
        })
    client = opener or urllib.request.build_opener(NoRedirect())
    try:
        with client.open(req, timeout=8) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError("sina_federation_unaccepted_http")
            raw_response = resp.read(MAX_RESPONSE + 1)
            if len(raw_response) > MAX_RESPONSE:
                raise ValueError("sina_federation_response_oversized")
            out = json.loads(raw_response)
    except urllib.error.HTTPError as exc:
        if exc.code in (400, 401, 403, 404, 409, 422):
            raise ValueError("sina_federation_rejected_" + str(exc.code)) from None
        raise RuntimeError("sina_federation_upstream_" + str(exc.code)) from None
    if not isinstance(out, dict) or out.get("created") not in (True, False):
        raise ValueError("sina_federation_ack_invalid")
    signal = out.get("signal")
    if not isinstance(signal, dict) or signal.get("source_id") != SOURCE_ID or signal.get("source_event_id") != body["source_event_id"]:
        raise ValueError("sina_federation_ack_scope_invalid")
    return {
        "status": "DELIVERED_TO_SINA_INGRESS",
        "created": out["created"],
        "source_event_id": body["source_event_id"],
        "execution_permit_issued": False,
        "independent_verification": False,
    }


def process(event: dict, *, sender=None) -> dict:
    """Existing Company event is the ONLY retry/lease/receipt owner."""
    import core
    if event.get("event_type") != EVENT:
        raise ValueError("wrong_company_event")
    try:
        receipt = (sender or deliver)(event)
    except (ValueError, RuntimeError, urllib.error.URLError, TimeoutError, OSError) as exc:
        with core.connect() as db:
            attempts = int(event.get("attempts") or 1)
            terminal = attempts >= RETRY_LIMIT or isinstance(exc, ValueError)
            db.execute(
                "UPDATE events SET status=?,error=?,claimed_at=NULL,processed_at=? WHERE id=?",
                ("dead_letter" if terminal else "deferred", type(exc).__name__,
                 datetime.now(timezone.utc).isoformat(), event["id"]),
            )
        return {"status": "DEAD_LETTER" if terminal else "RETRY_DEFERRED",
                "failure_type": type(exc).__name__}
    with core.connect() as db:
        db.execute(
            "UPDATE events SET status='processed',error=NULL,processed_at=?,claimed_at=NULL WHERE id=?",
            (datetime.now(timezone.utc).isoformat(), event["id"]),
        )
    return receipt


def resume_deferred(*, now_epoch=None) -> int:
    """Restart-safe backoff using the EXISTING event attempt counter."""
    import core
    if not configured():
        return 0
    now = float(time.time() if now_epoch is None else now_epoch)
    count = 0
    with core.connect() as db:
        rows = db.execute(
            "SELECT id,attempts,processed_at FROM events WHERE event_type=? AND status='deferred' ORDER BY created_at LIMIT 30",
            (EVENT,),
        ).fetchall()
        for item in rows:
            attempts = int(item["attempts"] or 1)
            if attempts >= RETRY_LIMIT:
                db.execute("UPDATE events SET status='dead_letter' WHERE id=?", (item["id"],))
                continue
            try:
                t = datetime.fromisoformat(str(item["processed_at"]).replace("Z", "+00:00")).timestamp()
            except (ValueError, TypeError):
                t = 0
            if now - t >= min(3600, 45 * (2 ** max(0, attempts - 1))):
                db.execute("UPDATE events SET status='queued',error=NULL WHERE id=?", (item["id"],))
                count += 1
    return count


def snapshot() -> dict:
    """Read-only factual projection; no alternative action states."""
    import core
    with core.connect() as db:
        totals = {r["status"]: r["n"] for r in db.execute(
            "SELECT status,COUNT(*) n FROM events WHERE event_type=? GROUP BY status",
            (EVENT,),
        )}
        recent = [dict(r) for r in db.execute(
            "SELECT id,status,attempts,processed_at,error FROM events WHERE event_type=? ORDER BY created_at DESC LIMIT 20",
            (EVENT,),
        )]
    return {
        "schema": "noetfield.company-os.sina-federation.v1",
        "configured": configured(),
        "source": "existing Company OS product observations",
        "destination": SINA_PATH,
        "canonical_queue": "events",
        "statuses": totals,
        "recent": recent,
        "external_execution_permitted": False,
    }
