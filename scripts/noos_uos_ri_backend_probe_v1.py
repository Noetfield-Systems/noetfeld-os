#!/usr/bin/env python3
"""Read-only, secret-free UOS-RI network/origin diagnostic from existing NOOS runner.

No auth secret, project hostname, IP, SQL, API payload, response body, or URL
is emitted. The original RUNWAY staging project reference is a known code pin.
This does not substitute an alternate database or bypass HMAC.
"""
from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlsplit

EXPECTED_HOST = "tkgpapowwplupyekpivy.supabase.co"
SCHEMA = "uos-ri.origin-diagnostic.v1"


def _target(name: str, url: str, *, expected_host: str = EXPECTED_HOST) -> dict[str, Any]:
    value: dict[str, Any] = {
        "target": name, "configured": bool(url), "expected_project_match": None,
        "dns_resolved": False, "dns_error": None, "dns_errno": None, "http_status": None,
        "http_error": None,
    }
    if not url:
        return value
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        if parsed.scheme != "https" or not host:
            value["http_error"] = "INVALID_URL"
            return value
        value["expected_project_match"] = host == expected_host
        socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        value["dns_resolved"] = True
    except (socket.gaierror, OSError) as exc:
        value["dns_error"] = type(exc).__name__
        if isinstance(exc, socket.gaierror) and isinstance(exc.errno, int):
            value["dns_errno"] = exc.errno
        return value
    try:
        # No credentials, body, or tenant data. 401/403 = origin responded.
        path = "/healthz" if name == "runway_gateway" else "/rest/v1/"
        request = urllib.request.Request(
            "https://" + host + path, method="GET",
            headers={"user-agent": "Noetfield-UOS-RI-origin-check/1.0"},
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            value["http_status"] = response.status
    except urllib.error.HTTPError as exc:
        value["http_status"] = exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        value["http_error"] = type(exc).__name__
    return value


def probe() -> dict[str, Any]:
    targets = [
        _target("motor_staging_expected", "https://" + EXPECTED_HOST),
        _target("supabase_root_control", "https://supabase.co"),
        _target("supabase_api_control", "https://api.supabase.com"),
        _target("noos_supabase_primary", os.environ.get("NOETFIELD_SUPABASE_URL", "")),
        _target("noos_supabase_fallback", os.environ.get("SUPABASE_URL", "")),
        _target("runway_gateway", os.environ.get("NOETFIELD_RUNWAY_API_URL", "")),
    ]
    return {"schema": SCHEMA, "mode": "READ_ONLY", "targets": targets,
            "requires_further_backend_verification": True}


if __name__ == "__main__":
    print(json.dumps(probe(), separators=(",", ":")))
