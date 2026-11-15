#!/usr/bin/env python3
"""Read-only readiness test for reusing the EXISTING active Portfolio Spine Supabase.

Strict non-mutation: no SQL execution, no POST, no data rows returned or logged.
Do not substitute URLs/keys or merge tenants merely because both endpoints respond.
"""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ACTIVE_PROJECT_REF = "ldfruywifqnfpwsfgmdl"
REQUIRED_TABLES = (
    "runway_runtime_jobs_v1",
    "runway_runtime_auth_nonces_v1",
    "runway_runtime_events_v1",
    "runway_runtime_queue_summary_v1",
)
REQUIRED_RPC = (
    "consume_runway_runtime_nonce_v1",
    "enqueue_runway_runtime_job_v1",
    "claim_runway_runtime_job_v1",
    "finalize_runway_runtime_job_v1",
)
SCHEMA = "uos-ri.active-supabase-readiness.v1"


def probe(*, url: str | None = None, key: str | None = None, opener=None) -> dict:
    alias_url = os.getenv("NOETFIELD_ACTIVE_SUPABASE_URL", "")
    alias_key = os.getenv("NOETFIELD_ACTIVE_SUPABASE_SERVICE_ROLE_KEY", "")
    source_url = os.getenv("PORTFOLIO_SPINE_SUPABASE_URL", "")
    source_key = os.getenv("PORTFOLIO_SPINE_SERVICE_ROLE_KEY", "")
    alias_configured = bool(alias_url and alias_key)
    source_alias_consistent = alias_configured and alias_url.rstrip("/") == source_url.rstrip("/") and alias_key == source_key
    url = (url if url is not None else alias_url or source_url).rstrip("/")
    key = key if key is not None else alias_key or source_key
    opener = opener or urllib.request.urlopen
    host = urlsplit(url).hostname if url else None
    result = {
        "schema": SCHEMA,
        "mode": "READ_ONLY_NO_SQL",
        "active_project_match": host == ACTIVE_PROJECT_REF + ".supabase.co",
        "credential_present": bool(key),
        "alias_configured": alias_configured,
        "alias_matches_existing_source": source_alias_consistent,
        "http_status": None,
        "authenticated_openapi": False,
        "tables": {name: None for name in REQUIRED_TABLES},
        "rpcs": {name: None for name in REQUIRED_RPC},
        "ready_for_cutover": False,
    }
    if not result["active_project_match"] or not key or not url.startswith("https://"):
        result["reason"] = "EXPECTED_ACTIVE_PROJECT_OR_CREDENTIAL_NOT_CONFIGURED"
        return result
    headers = {
        "apikey": key,
        "Authorization": "Bearer " + key,
        "Accept": "application/openapi+json",
        "User-Agent": "Noetfield-UOS-RI-readiness/1",
    }
    request = urllib.request.Request(url + "/rest/v1/", method="GET", headers=headers)
    try:
        with opener(request, timeout=12) as response:
            result["http_status"] = response.status
            # OpenAPI shape, not table rows; bounded read to protect memory.
            raw = response.read(2_000_000)
            data = json.loads(raw)
    except urllib.error.HTTPError as exc:
        result["http_status"] = exc.code
        result["reason"] = "OPENAPI_HTTP_ERROR"
        return result
    except (OSError, TimeoutError, ValueError, TypeError):
        result["reason"] = "OPENAPI_READ_FAILED"
        return result
    result["authenticated_openapi"] = result["http_status"] == 200 and isinstance(data, dict)
    if not result["authenticated_openapi"]:
        result["reason"] = "OPENAPI_UNCONFIRMED"
        return result
    paths = data.get("paths")
    if not isinstance(paths, dict):
        result["reason"] = "OPENAPI_PATHS_UNAVAILABLE"
        return result
    for name in REQUIRED_TABLES:
        result["tables"][name] = "/" + name in paths
    for name in REQUIRED_RPC:
        result["rpcs"][name] = "/rpc/" + name in paths
    result["ready_for_cutover"] = (
        all(result["tables"].values()) and all(result["rpcs"].values()) and (not alias_configured or source_alias_consistent)
    )
    result["reason"] = "READY" if result["ready_for_cutover"] else "MIGRATIONS_REQUIRED"
    return result


if __name__ == "__main__":
    try:
        output = probe()
    except Exception as exc:  # noqa: BLE001 - sanitized terminal boundary
        output = {"schema": SCHEMA, "reason": "PROBE_EXCEPTION",
                  "error_code": type(exc).__name__, "ready_for_cutover": False}
    print("UOS_RI_ACTIVE_SUPABASE=" + json.dumps(output, separators=(",", ":")), flush=True)
