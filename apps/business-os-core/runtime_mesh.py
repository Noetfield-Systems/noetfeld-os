"""Read-only federation of existing Sina, Fabric and Runway health endpoints.

This is a presentation adapter within Business OS Core. It cannot dispatch tasks,
issue permits, declare code completion or act as a second Runway/Company OS.
All upstream addresses are pinned. A healthy endpoint is not an E2E receipt.
"""
from __future__ import annotations

import concurrent.futures
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone

SCHEMA = "noetfield.company-os.runtime-mesh-observation.v1"
MAX_BODY = 16 * 1024
PROBES = (
    ("sina_founder", "Sina Founder OS", "https://sina-founder-os-staging-staging.up.railway.app/healthz",
     "founder", "https://sina-founder-os-staging-staging.up.railway.app/"),
    ("agent_fabric", "Agent Fabric", "https://noetfield-agent-fabric-staging-staging.up.railway.app/healthz",
     "fabric", "https://noetfield-agent-fabric-staging-staging.up.railway.app/"),
    ("runway_goal", "Runway Goal Kernel", "https://noetfield-runway-live-staging.sina-kazemnezhad-ca.workers.dev/v1/goals/health",
     "runway", "https://github.com/Noetfield-Systems/NOETFIELD-RUNWAY"),
    ("paperclip", "Paperclip Workforce", "https://paperclip-agent-workforce-staging.up.railway.app/",
     "html", "https://paperclip-agent-workforce-staging.up.railway.app/"),
)
LINKS = (
    ("business_os", "Company OS / NOOS", "https://business-os-core-production.up.railway.app/control"),
    ("company_floor", "Factory World", "https://sina-company-floor-production.up.railway.app/factory"),
    ("workforce_os", "WorkforceOS", "https://workforce-web-production-2d15bf32.up.railway.app/"),
)
EDGES = (
    ("sina_founder", "business_os", "Founder WorkPacket intake", "ACK_ONLY"),
    ("business_os", "agent_fabric", "Specialist assignment", "NOT_E2E_VERIFIED"),
    ("agent_fabric", "runway_motor", "Governed coding / Motor execution", "NOT_E2E_VERIFIED"),
    ("runway_motor", "independent_verifier", "Independent result receipt", "NOT_E2E_VERIFIED"),
    ("independent_verifier", "sina_founder", "Outcome reconciliation and next task", "NOT_E2E_VERIFIED"),
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _probe(item, opener):
    ident, name, url, kind, link = item
    report = {
        "id": ident, "label": name, "url": link,
        "state": "UNREACHABLE", "http_status": None,
        "authenticated": False, "e2e_verified": False,
    }
    try:
        request = urllib.request.Request(url, method="GET", headers={
            "Accept": "text/html" if kind == "html" else "application/json",
            "User-Agent": "Noetfield-Company-OS-ReadOnly-Mesh/1",
        })
        with opener.open(request, timeout=3) as response:
            report["http_status"] = response.status
            if response.status != 200:
                report["state"] = "HTTP_ERROR"
                return report
            data = response.read(MAX_BODY + 1)
            content_type = response.headers.get("Content-Type", "").lower()
        if len(data) > MAX_BODY:
            report["state"] = "INVALID_RESPONSE"
        elif kind == "html":
            report["state"] = "HTTP_REACHABLE_ONLY"
        elif "application/json" not in content_type:
            report["state"] = "INVALID_RESPONSE"
        else:
            payload = json.loads(data.decode("utf-8"))
            if not isinstance(payload, dict):
                report["state"] = "INVALID_RESPONSE"
            elif kind == "fabric" and payload.get("service") == "noetfield-agent-fabric" and payload.get("status") == "ok":
                report["state"] = "SERVICE_HEALTH_REPORTED"
            elif kind == "runway" and payload.get("goal_runtime") is True:
                report["state"] = "GOAL_KERNEL_HEALTH_REPORTED"
            elif kind == "founder" and (payload.get("status") == "ok" or payload.get("ok") is True):
                report["state"] = "SERVICE_HEALTH_REPORTED"
            else:
                report["state"] = "SCHEMA_UNCONFIRMED"
    except (OSError, ValueError, TypeError, TimeoutError, UnicodeError,
            urllib.error.HTTPError, json.JSONDecodeError):
        pass
    return report


def snapshot(*, opener=None, founder_bridge_status=None):
    """Observe existing systems once. Never infer an authorized delivery from health."""
    client = opener or urllib.request.build_opener(NoRedirect())
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(PROBES)) as pool:
        observed = list(pool.map(lambda item: _probe(item, client), PROBES))
    bridge = founder_bridge_status if isinstance(founder_bridge_status, dict) else {}
    nodes = [
        {"id": "business_os", "label": "Company OS / NOOS",
         "url": LINKS[0][2], "state": "LOCAL_CONTROL_SURFACE",
         "authenticated": False, "e2e_verified": False},
        *observed,
        {"id": "runway_motor", "label": "Runway Motor / execution adapter",
         "url": "https://github.com/Noetfield-Systems/NOETFIELD-RUNWAY",
         "state": "EXECUTION_NOT_OBSERVED", "authenticated": False,
         "e2e_verified": False},
        {"id": "independent_verifier", "label": "Independent Verifier",
         "url": "https://github.com/Noetfield-Systems/Verification_Layer",
         "state": "RECEIPT_NOT_OBSERVED", "authenticated": False,
         "e2e_verified": False},
    ]
    edges = [
        {"source": source, "target": target, "label": label, "state": state,
         "e2e_verified": False}
        for source, target, label, state in EDGES
    ]
    return {
        "schema": SCHEMA,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "nodes": nodes,
        "edges": edges,
        "founder_handoff": {
            "state": bridge.get("connection", "NOT_OBSERVED"),
            "work_packets_claimed": bridge.get("work_packets_claimed", 0),
            "pending_ack": bridge.get("pending_ack", 0),
            "last_cycle_rejection_reasons": bridge.get("last_cycle_rejection_reasons", {}),
            "last_cycle_rejected_projects": bridge.get("last_cycle_rejected_projects", []),
            "verified_outcomes": bridge.get("verified_outcomes", 0),
            "external_effects": bridge.get("external_effects", 0),
        },
        "links": [{"id": key, "label": label, "url": url} for key, label, url in LINKS],
        "summary": {
            "observed_endpoint_count": len(observed),
            "healthy_reports": sum(n["state"] in (
                "SERVICE_HEALTH_REPORTED", "GOAL_KERNEL_HEALTH_REPORTED",
                "HTTP_REACHABLE_ONLY") for n in observed),
            "verified_edges": 0, "runway_e2e_commissioned": False,
            "independent_receipt_observed": False,
        },
        "scope": "READ_ONLY_HEALTH_AND_HANDOFF_NO_MOTOR_DISPATCH_OR_E2E_PROOF",
    }
