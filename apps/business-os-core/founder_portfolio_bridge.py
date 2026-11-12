"""Sina → Company OS SSOT event bridge (read-only; NO parallel job queue).

Reads only the pinned Founder OS portfolio projection through a scoped workload
token. Every new canonical projection hash generates ONE idempotent event in
the EXISTING Company OS events/tasks queue. It creates no tenant, deployment,
Governor permit, agent or customer claim.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

SCHEMA = "sina.company-os.portfolio-projection.v1"
EVENT = "portfolio.canonical_projection_observed"
URL = "https://sina-founder-os-staging-staging.up.railway.app/api/v1/internal/company-portfolio"
TOKEN_ENV = "SINA_FOUNDER_PORTFOLIO_READ_TOKEN"
MAX_BYTES = 150000
INTERVAL_SECONDS = 300
_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,90}$")
_SHA = re.compile(r"^[a-f0-9]{64}$")
_last_poll = 0.0
_poll_lock = threading.Lock()


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def verify_projection(data):
    """Verify integrity of the bounded, non-PII Founder registry projection."""
    root = {
        "schema", "owner", "source_of_truth", "source_version",
        "projection_sha256", "projects", "company_entity_provisioning_authorized",
        "runtime_states_verified", "customer_metrics_included", "execution_permit_issued",
    }
    if not isinstance(data, dict) or set(data) != root:
        raise ValueError("portfolio_projection_contract_invalid")
    if (data["schema"] != SCHEMA or data["owner"] != "sina_founder_os"
            or data["source_of_truth"] != "portfolio/PROJECT-AND-ASSET-REGISTRY.json"
            or any(data[x] is not False for x in (
                "company_entity_provisioning_authorized", "runtime_states_verified",
                "customer_metrics_included", "execution_permit_issued"))):
        raise ValueError("portfolio_projection_authority_invalid")
    if type(data["source_version"]) not in (str, int) or len(str(data["source_version"])) > 50:
        raise ValueError("portfolio_version_invalid")
    projects = data["projects"]
    if not isinstance(projects, list) or not 1 <= len(projects) <= 100:
        raise ValueError("portfolio_projects_count_invalid")
    allowed = {
        "project_id", "name", "company_id", "owner_scope", "type",
        "status", "source_repository", "product_id",
    }
    ids = set()
    for project in projects:
        if not isinstance(project, dict) or set(project) != allowed:
            raise ValueError("portfolio_project_shape_invalid")
        pid = project["project_id"]
        cid = project["company_id"]
        if (not isinstance(pid, str) or not _ID.fullmatch(pid) or pid in ids
                or (cid is not None and (not isinstance(cid, str) or not _ID.fullmatch(cid)))):
            raise ValueError("portfolio_project_identity_invalid")
        ids.add(pid)
        for field in ("name", "owner_scope", "type", "status", "source_repository", "product_id"):
            value = project[field]
            if not isinstance(value, str) or len(value) > 180 or any(ord(c) < 32 for c in value):
                raise ValueError("portfolio_project_field_invalid")
    digest = hashlib.sha256(canonical(projects).encode("utf-8")).hexdigest()
    if not isinstance(data["projection_sha256"], str) or not _SHA.fullmatch(data["projection_sha256"]):
        raise ValueError("portfolio_projection_sha_invalid")
    if not hmac.compare_digest(digest, data["projection_sha256"]):
        raise ValueError("portfolio_projection_integrity_mismatch")
    return {"projects": projects, "source_version": data["source_version"],
            "source_sha256": digest}


def fetch_projection():
    token = os.getenv(TOKEN_ENV, "")
    if len(token) < 40 or len(token) > 256:
        raise RuntimeError("portfolio_workload_identity_not_configured")
    parsed = urlsplit(URL)
    if parsed.scheme != "https" or parsed.hostname != "sina-founder-os-staging-staging.up.railway.app":
        raise RuntimeError("portfolio_origin_not_allowlisted")
    request = urllib.request.Request(URL, headers={
        "Accept": "application/json",
        "X-Sina-Portfolio-Token": token,
        "User-Agent": "Noetfield-CompanyOS-SSOT-Bridge/1.0",
    }, method="GET")
    with urllib.request.build_opener(NoRedirects()).open(request, timeout=7) as resp:
        if resp.status != 200 or "application/json" not in resp.headers.get("Content-Type", "").lower():
            raise RuntimeError("portfolio_response_not_json_200")
        raw = resp.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("portfolio_projection_oversized")
    return verify_projection(json.loads(raw.decode("utf-8")))


def reconcile_once(fetcher=None):
    """Persist a *projection change event*, not duplicate Founder or Company state."""
    import core
    projection = (fetcher or fetch_projection)()
    with core.connect() as db:
        programs = {(r["company_id"], r["project_id"]) for r in db.execute(
            "SELECT company_id,project_id FROM product_programs"
        ).fetchall()}
    known = []
    unknown = []
    for p in projection["projects"]:
        scope = p["company_id"] or "founder-portfolio"
        if (scope, p["project_id"]) in programs:
            known.append(p["project_id"])
        else:
            unknown.append(p["project_id"])
    source_sha = projection["source_sha256"]
    # Safe bounded event payload; no full catalog copy or tenant provisioning.
    event = {
        "schema": "noetfield.company-os.founder-ssot-observation.v1",
        "source_owner": "sina_founder_os",
        "source_schema": SCHEMA,
        "source_version": projection["source_version"],
        "source_sha256": source_sha,
        "project_count": len(projection["projects"]),
        "matched_program_count": len(known),
        "unmapped_project_count": len(unknown),
        "unmapped_project_ids": unknown[:12],
        "authority": "READ_ONLY_PROJECTION",
        "external_execution_authorized": False,
        "legal_entity_creation_authorized": False,
        "paid_customer_claimed": False,
    }
    eid = core.add_event(EVENT, "sina_founder_os_pinned_portfolio", "portfolio", event,
                         idempotency_key="sina-ssot:" + source_sha[:40])
    return {"ok": True, "source_sha256": source_sha,
            "canonical_queue": "EXISTING_COMPANY_OS_EVENTS", "event_id": eid,
            "matched_programs": len(known), "unmapped_projects": len(unknown),
            "external_execution_authorized": False}


def tick(fetcher=None, clock=None, force=False):
    """Piggyback on core.daily_tick; a failure never blocks other Company loops."""
    global _last_poll
    if fetcher is None and len(os.getenv(TOKEN_ENV, "")) < 40:
        return {"state": "NOT_CONFIGURED", "external_execution_authorized": False}
    now = (clock or time.monotonic)()
    with _poll_lock:
        if not force and now - _last_poll < INTERVAL_SECONDS:
            return {"state": "NOT_DUE"}
        _last_poll = now
    try:
        result = reconcile_once(fetcher)
        return {"state": "OBSERVED", **result}
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        # Error TYPE only: do not leak service credentials or HTTP response bodies.
        return {"state": "DEGRADED", "error_type": type(exc).__name__,
                "external_execution_authorized": False}
