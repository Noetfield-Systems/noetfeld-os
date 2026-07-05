#!/usr/bin/env python3
"""Fly always-on inbox runner — drain inbox on interval with /health and /ready."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INTERVAL_SEC = int(os.environ.get("NOOS_INBOX_INTERVAL_SEC", "300"))
PORT = int(os.environ.get("PORT", "8080"))
_ready = False
_last_cycle_ok: bool | None = None


class HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            code = 200 if _last_cycle_ok is not False else 503
            self.send_response(code)
            self.end_headers()
            self.wfile.write(b"ok" if code == 200 else b"degraded")
            return
        if self.path == "/ready":
            code = 200 if _ready else 503
            self.send_response(code)
            self.end_headers()
            self.wfile.write(b"ready" if code == 200 else b"starting")
            return
        self.send_response(404)
        self.end_headers()


def run_inbox_cycle() -> bool:
    global _last_cycle_ok
    env = os.environ.copy()
    env.setdefault("GITHUB_EVENT_NAME", "repository_dispatch")
    env.setdefault("DISPATCH_SOURCE", "cf-cron")
    env.setdefault("GITHUB_RUN_ID", "fly-inbox-runner")
    env.setdefault("GITHUB_WORKFLOW", "fly-noos-inbox-runner")
    proc = subprocess.run(
        [sys.executable, "scripts/cloud_inbox_worker_v1.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    _last_cycle_ok = proc.returncode == 0
    return _last_cycle_ok


def worker_loop() -> None:
    global _ready
    while True:
        try:
            run_inbox_cycle()
        except Exception:  # noqa: BLE001
            _last_cycle_ok = False
        _ready = True
        time.sleep(INTERVAL_SEC)


def main() -> None:
    threading.Thread(target=worker_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", PORT), HealthHandler).serve_forever()


if __name__ == "__main__":
    main()
