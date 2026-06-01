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

PLATFORM_PREFIXES = (
    "/console",
    "/api/",
    "/openapi.json",
    "/docs",
    "/redoc",
)
NEXT_PREFIXES = (
    "/cognitive-dashboard",
    "/_next/",
    "/evaluate",
    "/audit",
    "/result/",
)


def _proxy_target(path: str) -> str | None:
    if any(path.startswith(p) for p in PLATFORM_PREFIXES):
        return PLATFORM
    if any(path.startswith(p) for p in NEXT_PREFIXES):
        return NEXT
  # Next dev: root redirect goes to cognitive-dashboard
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
            with urllib.request.urlopen(req, timeout=120) as resp:
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

    def do_GET(self) -> None:
        target = _proxy_target(self.path.split("?")[0])
        if target:
            return self._proxy(target)
        return super().do_GET()

    def do_HEAD(self) -> None:
        target = _proxy_target(self.path.split("?")[0])
        if target:
            return self._proxy(target)
        return super().do_HEAD()

    def do_POST(self) -> None:
        target = _proxy_target(self.path.split("?")[0])
        if target:
            return self._proxy(target)
        self.send_error(405)

    def do_OPTIONS(self) -> None:
        target = _proxy_target(self.path.split("?")[0])
        if target:
            return self._proxy(target)
        self.send_response(204)
        self.end_headers()


def main() -> None:
    host = "0.0.0.0"
    server = ThreadingHTTPServer((host, PUBLIC_PORT), UnifiedHandler)
    print(f"Noetfield unified dev: http://localhost:{PUBLIC_PORT}/", flush=True)
    print(f"  website:  http://localhost:{PUBLIC_PORT}/", flush=True)
    print(f"  console:  http://localhost:{PUBLIC_PORT}/console", flush=True)
    print(f"  dashboard: http://localhost:{PUBLIC_PORT}/cognitive-dashboard", flush=True)
    print("Cursor: forward ONLY port", PUBLIC_PORT, flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
