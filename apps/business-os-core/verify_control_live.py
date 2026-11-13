#!/usr/bin/env python3
"""Read-only smoke for the live Founder Control Plane. No credentials or writes."""
from __future__ import annotations
import json
import os
import re
import urllib.error
import urllib.request
from urllib.parse import urljoin

BASE = os.getenv("BUSINESS_OS_URL", "https://business-os-core-production.up.railway.app").rstrip("/")
HEADERS = {"User-Agent": "Noetfield-UI-Production-Read-Only-Smoke/1.0", "Accept": "*/*"}

def check(path, expected=200):
    req = urllib.request.Request(BASE + path, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=22) as res:
            status = res.status
            content_type = res.headers.get("Content-Type", "")
            body = res.read(220_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        content_type = exc.headers.get("Content-Type", "")
        body = exc.read(4000).decode("utf-8", "replace")
    assert status == expected, f"{path}: expected HTTP {expected}, received {status}"
    return content_type, body

html_type, page = check("/control")
assert "text/html" in html_type, "Control route did not return HTML"
for needle in ["Founder access key", "Company overview", "data-view=\"connect\"", "data-view=\"revenue\"", "data-view=\"workflows\"", "/control/premium.css?v=4", "/control/premium.js?v=4"]:
    assert needle in page, f"Live control document lacks {needle}"
assert re.search(r'<meta name="robots" content="noindex,nofollow"', page)
css_type, css = check("/control/premium.css?v=4")
assert "text/css" in css_type, f"Incorrect CSS content type: {css_type}"
assert "@media(max-width:780px)" in css, "Mobile responsive rules missing"
assert "body.locked .layout" in css, "Locked layout not covered"
js_type, js = check("/control/premium.js?v=4")
assert any(t in js_type for t in ["javascript", "text/plain"]), f"Incorrect JS content type: {js_type}"
assert "window.noosPremium=" in js and '"/api/control/tasks"' in js, "Real UI controller missing"
_, health_txt = check("/health")
health = json.loads(health_txt)
assert health.get("ok") is True and health.get("storage") == "ready", "Database health not ready"
_, ready_txt = check("/ready")
ready = json.loads(ready_txt)
assert ready.get("ready") is True and ready.get("worker") == "running", "Workers not ready"
check("/api/control/overview", expected=401)
check("/api/control/connect-opportunities", expected=401)
check("/api/control/tasks", expected=401)
check("/api/control/roi", expected=401)
print(json.dumps({
    "status": "PASS",
    "environment": "production",
    "checks": ["control page", "CSS", "JavaScript", "mobile responsive stylesheet",
               "service health", "worker readiness", "protected API auth (4 endpoints)"],
    "requests_mutating": 0,
    "authenticated_user_flows_tested": False,
    "claim": "Unauthenticated production surface and infrastructure smoke only"
}, ensure_ascii=False))
