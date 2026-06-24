#!/usr/bin/env python3
"""Single localhost port: www + /console + /cognitive-dashboard (forward only this port in Cursor)."""

from __future__ import annotations

import os
import sys
import threading
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PORT = int(os.environ.get("NF_DEV_PUBLIC_PORT", "13080"))
PLATFORM = os.environ.get(
    "NF_DEV_PLATFORM_INTERNAL",
    f"http://127.0.0.1:{os.environ.get('NF_DEV_PLATFORM_PORT', '8001')}",
)
NEXT = os.environ.get("NF_DEV_NEXT_INTERNAL", "http://127.0.0.1:13000")
GOV_API = os.environ.get(
    "NF_DEV_GOV_API_INTERNAL",
    f"http://127.0.0.1:{os.environ.get('NF_DEV_GOV_API_PORT', '18002')}",
)

PLATFORM_PREFIXES = (
    "/console",
    "/api/",
    "/openapi.json",
    "/redoc",
)
# Static www paths under /docs/ (must not hit platform OpenAPI /docs).
STATIC_DOC_PREFIXES = (
    "/docs/api",
    "/docs/diligence",
    "/docs/spec",
    "/docs/collateral",
    "/docs/references",
)
PLATFORM_SWAGGER_EXACT = frozenset({"/docs"})
NEXT_PREFIXES = (
    "/cognitive-dashboard",
    "/workspace",
    "/_next/",
    "/result/",
)

def _is_next_trust_ledger(path: str) -> bool:
    """Next UI: dynamic TLE routes — not static www hub or sample-report HTML."""
    if path == "/trust-ledger":
        return True
    if path.startswith("/trust-ledger/new"):
        return True
    if path in ("/trust-ledger/", "/trust-ledger/index.html"):
        return False
    if path.startswith("/trust-ledger/sample-report"):
        return False
    if path.startswith("/trust-ledger/verify"):
        return False
    if path.startswith("/trust-ledger/") and not path.endswith((".html", ".yaml", ".yml", ".md")):
        return True
    return False

# Gov API (18002) JSON/binary routes — must not hit Next or static www.
_GOV_API_PREFIXES = (
    "/tle",
    "/connectors",
    "/evidence/",
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirect)


def _gov_api_route(path: str, method: str, headers: dict[str, str]) -> bool:
    """Governance-console FastAPI (18002) — must not be sent to Next for POST/API GET."""
    if path == "/health":
        return True
    if path == "/evaluate" and method == "POST":
        return True
    if path.startswith("/api/v1/sandbox"):
        return True
    if path.startswith("/audit/"):
        return True
    if path == "/audit" and method == "GET":
        accept = headers.get("Accept", headers.get("accept", "*/*"))
        if "text/html" in accept and "application/json" not in accept:
            return False
        return True
    if path in _GOV_API_PREFIXES or any(path.startswith(p) for p in _GOV_API_PREFIXES):
        return True
    return False


def _proxy_target(path: str, method: str = "GET", headers: dict[str, str] | None = None) -> str | None:
    headers = headers or {}
    if _gov_api_route(path, method, headers):
        return GOV_API
    if any(path.startswith(p) for p in STATIC_DOC_PREFIXES):
        return None
    if path in PLATFORM_SWAGGER_EXACT or path.startswith("/docs/oauth2-redirect"):
        return PLATFORM
    if any(path.startswith(p) for p in PLATFORM_PREFIXES):
        return PLATFORM
    if path in ("/evaluate", "/audit") or _is_next_trust_ledger(path):
        return NEXT
    if any(path.startswith(p) for p in NEXT_PREFIXES):
        return NEXT
    if path == "/" and os.environ.get("PROXY_ROOT_TO_NEXT") == "1":
        return NEXT
    return None


class UnifiedHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[dev-proxy] {self.address_string()} - {fmt % args}\n")

    def _proxy(self, upstream: str) -> None:
        url = upstream + self.path
        if self.path == "/":
            url = upstream + "/"
        body = None
        if self.command in ("POST", "PUT", "PATCH"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else None
        req = urllib.request.Request(
            url,
            data=body,
            method=self.command,
            headers={k: v for k, v in self.headers.items() if k.lower() != "host"},
        )
        try:
            with _NO_REDIRECT_OPENER.open(req, timeout=120) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() in ("transfer-encoding", "connection"):
                        continue
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() in ("transfer-encoding", "connection"):
                    continue
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, f"Upstream error: {e}")

    def _route(self) -> str | None:
        path = self.path.split("?")[0]
        hdrs = {k: v for k, v in self.headers.items()}
        return _proxy_target(path, self.command, hdrs)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path == "/trust-ledger":
            self.send_response(301)
            self.send_header("Location", "/trust-ledger/")
            self.end_headers()
            return
        target = self._route()
        if target:
            return self._proxy(target)
        return super().do_GET()

    def do_HEAD(self) -> None:
        target = self._route()
        if target:
            return self._proxy(target)
        return super().do_HEAD()

    def _proxy_method(self) -> None:
        target = self._route()
        if target:
            return self._proxy(target)
        if self.command == "OPTIONS":
            self.send_response(204)
            self.end_headers()
            return
        self.send_error(405)

    def do_POST(self) -> None:
        self._proxy_method()

    def do_PUT(self) -> None:
        self._proxy_method()

    def do_PATCH(self) -> None:
        self._proxy_method()

    def do_DELETE(self) -> None:
        self._proxy_method()

    def do_OPTIONS(self) -> None:
        self._proxy_method()


def main() -> None:
    host = "0.0.0.0"
    server = ThreadingHTTPServer((host, PUBLIC_PORT), UnifiedHandler)
    print(f"Noetfield unified dev: http://localhost:{PUBLIC_PORT}/", flush=True)
    print(f"  website:  http://localhost:{PUBLIC_PORT}/", flush=True)
    print(f"  console:  http://localhost:{PUBLIC_PORT}/console", flush=True)
    print(f"  dashboard: http://localhost:{PUBLIC_PORT}/cognitive-dashboard", flush=True)
    print(f"  workspace: http://localhost:{PUBLIC_PORT}/workspace", flush=True)
    print("Cursor: forward ONLY port", PUBLIC_PORT, flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
