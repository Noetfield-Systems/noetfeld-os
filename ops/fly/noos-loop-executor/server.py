#!/usr/bin/env python3
"""Fly Option B — one HTTP request → one bounded NOOS loop tick (no daemon/cron)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_loop_liveness_v1 import upsert_loop_liveness  # noqa: E402

RECEIPT_DIR = ROOT / ".noos-runtime/fly-executor/receipts"
PORT = int(os.environ.get("PORT", "8080"))
SECRET = (os.environ.get("NOOS_LOOP_SECRET") or "").strip()
DEFAULT_EVENT = (os.environ.get("NOOS_LOOP_DEFAULT_EVENT") or "noos_orchestrator_cross_repo_tick").strip()
FACTORY_EVENT = "noos_factory_autorun_tick"
LOOP_TIMEOUT_SEC = int(os.environ.get("NOOS_LOOP_TIMEOUT_SEC", "900"))
_started_at = time.time()
_ready = False
_lock = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _base_env(*, event_type: str, source: str, run_id: str) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("GITHUB_EVENT_NAME", "http_loop")
    env.setdefault("DISPATCH_SOURCE", source)
    env.setdefault("GITHUB_RUN_ID", run_id)
    env.setdefault("GITHUB_WORKFLOW", "fly-noos-loop-executor")
    env.setdefault("NOOS_LOOP_EVENT_TYPE", event_type)
    env.setdefault("NOOS_CLOUD_LOOP", "1")
    env.setdefault("FLY_APP", os.environ.get("FLY_APP") or "noos-loop-executor")
    return env


def write_receipt(run_id: str, payload: dict[str, Any]) -> str:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPT_DIR / f"{run_id}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT))


def run_one_tick(event_type: str, *, source: str, run_id: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "scripts/noos_loop_runner_v1.py", "--event-type", event_type, "--json"],
        cwd=ROOT,
        env=_base_env(event_type=event_type, source=source, run_id=run_id),
        capture_output=True,
        text=True,
        check=False,
        timeout=LOOP_TIMEOUT_SEC,
    )
    cycle: dict[str, Any] | None = None
    if proc.stdout.strip():
        try:
            cycle = json.loads(proc.stdout)
        except json.JSONDecodeError:
            cycle = None
    ok = proc.returncode == 0 and (cycle or {}).get("status") == "ok"
    return {
        "schema": "noos-fly-loop-executor-tick-v1",
        "run_id": run_id,
        "at": utc_now(),
        "handler": "loop",
        "event_type": event_type,
        "source": source,
        "exit_code": proc.returncode,
        "ok": ok,
        "cycle": cycle,
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def run_factory(*, source: str, run_id: str) -> dict[str, Any]:
    env = _base_env(event_type=FACTORY_EVENT, source=source, run_id=run_id)
    steps: list[dict[str, Any]] = []
    for name, cmd in (
        ("enqueue_cloud_inbox", [sys.executable, "scripts/enqueue_noos_cloud_inbox_v1.py"]),
        ("factory_once", [sys.executable, "scripts/run_noetfield_factory_loop_v1.py", "--once"]),
    ):
        proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, check=False, timeout=LOOP_TIMEOUT_SEC)
        steps.append(
            {
                "name": name,
                "exit_code": proc.returncode,
                "ok": proc.returncode == 0,
                "stderr_tail": (proc.stderr or "")[-300:],
            }
        )
    ok = all(s["ok"] for s in steps)
    cloud = os.environ.get("NOOS_CLOUD_LOOP") == "1"
    liveness_ok = ok or (cloud and any(s.get("ok") for s in steps))
    result: dict[str, Any] = {
        "schema": "noos-fly-loop-executor-tick-v1",
        "run_id": run_id,
        "at": utc_now(),
        "handler": "factory",
        "event_type": FACTORY_EVENT,
        "source": source,
        "ok": ok,
        "steps": steps,
    }
    if liveness_ok:
        result["liveness_upsert"] = upsert_loop_liveness(
            loop_id="factory_autorun",
            event_type=FACTORY_EVENT,
            interval_minutes=10,
            last_cycle_status="COMPLETE" if ok else "DEGRADED",
            host="fly:noos-loop-executor",
        )
    return result


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def _json(self, code: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _check_secret(self) -> tuple[bool, int, str]:
        if not SECRET:
            return False, 503, "secret_not_configured"
        header = (self.headers.get("X-NOOS-Loop-Secret") or "").strip()
        if not header:
            return False, 401, "missing_loop_secret"
        if header != SECRET:
            return False, 403, "invalid_loop_secret"
        return True, 0, ""

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        self._json(
            200 if _ready else 503,
            {
                "ok": _ready,
                "schema": "noos-fly-loop-executor-health-v1",
                "service": "noos-loop-executor",
                "uptime_sec": int(time.time() - _started_at),
                "execution_mode": "one_shot_http",
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/loop":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        ok_auth, code, reason = self._check_secret()
        if not ok_auth:
            self._json(code, {"ok": False, "error": reason})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "error": "invalid_json"})
            return
        event_type = str(body.get("event_type") or DEFAULT_EVENT).strip()
        if not event_type:
            self._json(400, {"ok": False, "error": "event_type_required"})
            return
        if not _lock.acquire(blocking=False):
            self._json(409, {"ok": False, "error": "already_running"})
            return
        run_id = f"fly-{uuid.uuid4().hex[:12]}"
        try:
            if event_type == FACTORY_EVENT or str(body.get("handler") or "") == "factory":
                result = run_factory(source=str(body.get("source") or "fly-http"), run_id=run_id)
            else:
                result = run_one_tick(event_type, source=str(body.get("source") or "fly-http"), run_id=run_id)
            result["receipt_path"] = write_receipt(run_id, result)
            self._json(200 if result.get("ok") else 502, result)
        finally:
            _lock.release()


def main() -> None:
    global _ready
    if not SECRET:
        print("WARN: NOOS_LOOP_SECRET unset — POST /loop will return 503", file=sys.stderr)
    _ready = True
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
