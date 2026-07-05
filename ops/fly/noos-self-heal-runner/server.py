#!/usr/bin/env python3
"""Fly always-on self-heal runner — reenqueue + heartbeat with /health and /ready."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INTERVAL_SEC = int(os.environ.get("NOOS_SELF_HEAL_INTERVAL_SEC", "60"))
PORT = int(os.environ.get("PORT", "8080"))
_ready = False
_last_cycle_ok: bool | None = None


class HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/health", "/ready"):
            code = 200 if (_ready and _last_cycle_ok is not False) else 503
            self.send_response(code)
            self.end_headers()
            self.wfile.write(b"ok")
            return
        self.send_response(404)
        self.end_headers()


def run_self_heal_cycle() -> bool:
    global _last_cycle_ok
    env = os.environ.copy()
    env.setdefault("GITHUB_EVENT_NAME", "repository_dispatch")
    env.setdefault("DISPATCH_SOURCE", "cf-cron")
    steps = [
        [sys.executable, "scripts/reenqueue_blocked_upg_inbox_v1.py"],
        [sys.executable, "scripts/noos_loop_heartbeat_v1.py", "--write-receipt"],
    ]
    ok = True
    for cmd in steps:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, check=False)
        ok = ok and proc.returncode == 0
    _last_cycle_ok = ok
    return ok


def worker_loop() -> None:
    global _ready
    while True:
        try:
            run_self_heal_cycle()
        except Exception:  # noqa: BLE001
            _last_cycle_ok = False
        _ready = True
        time.sleep(INTERVAL_SEC)


def main() -> None:
    threading.Thread(target=worker_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", PORT), HealthHandler).serve_forever()


if __name__ == "__main__":
    main()
