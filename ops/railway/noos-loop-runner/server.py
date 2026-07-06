#!/usr/bin/env python3
"""Railway loop runner — HTTP execution plane for CF cron dispatches (no GHA)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_loop_liveness_v1 import upsert_loop_liveness  # noqa: E402

PORT = int(os.environ.get("PORT", "8080"))
SECRET = (os.environ.get("LOOP_RUNNER_SECRET") or "").strip()
FACTORY_EVENT = "noos_factory_autorun_tick"
_locks: dict[str, threading.Lock] = {}
_started_at = time.time()
_ready = False


def _lock_for(event_type: str) -> threading.Lock:
    if event_type not in _locks:
        _locks[event_type] = threading.Lock()
    return _locks[event_type]


def _base_env(*, event_type: str, source: str, run_id: str) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("GITHUB_EVENT_NAME", "http_loop")
    env.setdefault("DISPATCH_SOURCE", source)
    env.setdefault("GITHUB_RUN_ID", run_id)
    env.setdefault("GITHUB_WORKFLOW", "railway-noos-loop-runner")
    env.setdefault("NOOS_LOOP_EVENT_TYPE", event_type)
    return env


def run_loop(event_type: str, *, source: str, run_id: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "scripts/noos_loop_runner_v1.py", "--event-type", event_type, "--json"],
        cwd=ROOT,
        env=_base_env(event_type=event_type, source=source, run_id=run_id),
        capture_output=True,
        text=True,
        check=False,
        timeout=900,
    )
    payload: dict[str, Any] | None = None
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = None
    return {
        "handler": "loop",
        "event_type": event_type,
        "exit_code": proc.returncode,
        "ok": proc.returncode == 0 and (payload or {}).get("ok", proc.returncode == 0),
        "cycle": payload,
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def run_factory(*, source: str, run_id: str) -> dict[str, Any]:
    env = _base_env(event_type=FACTORY_EVENT, source=source, run_id=run_id)
    steps: list[dict[str, Any]] = []
    for name, cmd in (
        ("enqueue_cloud_inbox", [sys.executable, "scripts/enqueue_noos_cloud_inbox_v1.py"]),
        ("factory_once", [sys.executable, "scripts/run_noetfield_factory_loop_v1.py", "--once"]),
    ):
        proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, check=False, timeout=900)
        steps.append(
            {
                "name": name,
                "exit_code": proc.returncode,
                "ok": proc.returncode == 0,
                "stderr_tail": (proc.stderr or "")[-300:],
            }
        )
    ok = all(s["ok"] for s in steps)
    result: dict[str, Any] = {"handler": "factory", "event_type": FACTORY_EVENT, "ok": ok, "steps": steps}
    if ok:
        result["liveness_upsert"] = upsert_loop_liveness(
            loop_id="factory_autorun",
            event_type=FACTORY_EVENT,
            interval_minutes=10,
            last_cycle_status="COMPLETE",
            host="railway:noos-loop-runner",
        )
    return result


def execute(event_type: str, *, source: str) -> dict[str, Any]:
    run_id = f"railway-{uuid.uuid4().hex[:12]}"
    lock = _lock_for(event_type)
    if not lock.acquire(blocking=False):
        return {"ok": False, "event_type": event_type, "error": "already_running", "run_id": run_id}
    try:
        if event_type == FACTORY_EVENT:
            return {**run_factory(source=source, run_id=run_id), "run_id": run_id}
        return {**run_loop(event_type, source=source, run_id=run_id), "run_id": run_id}
    finally:
        lock.release()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def _auth_ok(self) -> bool:
        if not SECRET:
            return True
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {SECRET}"

    def _json(self, code: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(200 if _ready else 503, {"ok": _ready, "service": "noos-loop-runner", "uptime_sec": int(time.time() - _started_at)})
            return
        if self.path == "/ready":
            self._json(200, {"ok": True, "ready": True})
            return
        self._json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/loop":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        if not self._auth_ok():
            self._json(401, {"ok": False, "error": "unauthorized"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "error": "invalid_json"})
            return
        event_type = str(body.get("event_type") or "").strip()
        if not event_type:
            self._json(400, {"ok": False, "error": "event_type_required"})
            return
        source = str(body.get("source") or "cf-cron")
        result = execute(event_type, source=source)
        executed = "error" not in result or result.get("error") != "already_running"
        if result.get("error") == "already_running":
            self._json(409, result)
            return
        self._json(200, result)


def main() -> None:
    global _ready
    _ready = True
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
