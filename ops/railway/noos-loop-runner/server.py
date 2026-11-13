#!/usr/bin/env python3
"""Railway loop runner — one HTTP request → one bounded NOOS loop tick."""

from __future__ import annotations

import json
import hmac
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

ROOT_CANDIDATES = [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]
ROOT = next(
    (candidate for candidate in ROOT_CANDIDATES
     if (candidate / "scripts" / "noos_loop_runner_v1.py").is_file()),
    None,
)
if ROOT is None:
    # Do not eagerly evaluate a brittle parents[n] fallback: both supported
    # Docker layouts place the copied runner at /app/server.py or below /app.
    ROOT = Path(__file__).resolve().parent
if not (ROOT / "scripts" / "noos_loop_runner_v1.py").is_file():
    raise RuntimeError(
        f"NOOS runtime root not found from {Path(__file__).resolve()}; "
        "expected scripts/noos_loop_runner_v1.py"
    )
sys.path.insert(0, str(ROOT / "scripts"))
from noos_loop_liveness_v1 import upsert_loop_liveness  # noqa: E402
from noos_incident_log_v1 import log_incident  # noqa: E402
from noos_postgres_store_v1 import (configured as pg_store_enabled, probe as pg_probe, enqueue_job, claim_job, report_job, queue_status)  # noqa: E402
from noos_github_oidc_v1 import authorize as authorize_github_oidc  # noqa: E402

RECEIPT_DIR = ROOT / ".noos-runtime/railway-loop-runner/receipts"
PORT = int(os.environ.get("PORT", "8080"))
SECRET = (os.environ.get("NOOS_LOOP_SECRET") or os.environ.get("LOOP_RUNNER_SECRET") or "").strip()
FACTORY_EVENT = "noos_factory_autorun_tick"
LOOP_TIMEOUT_SEC = int(os.environ.get("NOOS_LOOP_TIMEOUT_SEC", "900"))
_locks: dict[str, threading.Lock] = {}
_started_at = time.time()
_ready = False
_git_sha_cache: str | None = None
# Repair fix 5: _ready is set once at process start and never reflects whether
# the write path is actually alive — this is exactly why /health stayed green
# while writes silently died. These track the real thing staleness probes care
# about: did the last tick's heartbeat write actually land.
_last_liveness_ok_at: str | None = None
_last_liveness_error: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_sha() -> str:
    global _git_sha_cache
    if _git_sha_cache is not None:
        return _git_sha_cache
    # Prefer the image BUILD_SHA (true deployed code) over NOOS_GIT_SHA env,
    # which deploy scripts may update before the new image is live.
    for path in (ROOT / "BUILD_SHA", ROOT / "ops/railway/noos-loop-runner/BUILD_SHA"):
        if path.is_file():
            val = path.read_text(encoding="utf-8").strip()
            if val:
                _git_sha_cache = val[:40]
                return _git_sha_cache
    env = (os.environ.get("NOOS_GIT_SHA") or os.environ.get("RAILWAY_GIT_COMMIT_SHA") or "").strip()
    if env:
        _git_sha_cache = env[:40]
        return _git_sha_cache
    _git_sha_cache = "unknown"
    return _git_sha_cache


def write_receipt(run_id: str, payload: dict[str, Any]) -> str:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPT_DIR / f"{run_id}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT))


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
    env.setdefault("RAILWAY_ENVIRONMENT", "production")
    env.setdefault("NOOS_CLOUD_LOOP", "1")
    return env


def _tick_diagnostic(
    *,
    event_type: str,
    source: str,
    run_id: str,
    proc: subprocess.CompletedProcess[str],
    cycle: dict[str, Any] | None,
    ok: bool,
) -> dict[str, Any]:
    """Return a bounded, secret-free projection for Railway runtime logs."""
    cycle = cycle if isinstance(cycle, dict) else {}
    d2 = cycle.get("d2") if isinstance(cycle.get("d2"), dict) else {}
    floor = d2.get("floor") if isinstance(d2.get("floor"), dict) else {}
    sink = cycle.get("supabase_sink") if isinstance(cycle.get("supabase_sink"), dict) else {}
    runner_output = cycle.get("runner_output") if isinstance(cycle.get("runner_output"), dict) else {}
    steps = runner_output.get("steps") if isinstance(runner_output.get("steps"), list) else []
    failed_steps = [
        {
            "name": str(step.get("name") or "unknown")[:80],
            "exit_code": step.get("exit_code"),
            "error": str(step.get("error") or "")[:160] or None,
        }
        for step in steps
        if isinstance(step, dict) and step.get("ok") is False
    ][:8]
    liveness = cycle.get("liveness_upsert") if isinstance(cycle.get("liveness_upsert"), dict) else {}
    meta_liveness = cycle.get("meta_liveness_sync") if isinstance(cycle.get("meta_liveness_sync"), dict) else {}
    supabase_env = cycle.get("supabase_env") if isinstance(cycle.get("supabase_env"), dict) else {}
    return {
        "schema": "noos-loop-runner-diagnostic-v1",
        "run_id": run_id,
        "event_type": event_type,
        "source": source,
        "ok": ok,
        "process_exit_code": proc.returncode,
        "cycle_status": cycle.get("status"),
        "state_after": cycle.get("state_after"),
        "cycle_number": cycle.get("cycle_number"),
        "blocker_reason": str(cycle.get("blocker_reason") or "")[:240] or None,
        "d2_reason": d2.get("reason"),
        "supabase_floor_reason": floor.get("reason"),
        "supabase_floor_status": floor.get("status"),
        "supabase_env": {
            "ok": supabase_env.get("ok"),
            "has_url": supabase_env.get("has_url"),
            "has_key": supabase_env.get("has_key"),
        },
        "sink": {
            "ok": sink.get("ok"),
            "reason": sink.get("reason"),
            "status": sink.get("status"),
            "exit_code": sink.get("exit_code"),
        },
        "failed_steps": failed_steps,
        "liveness_write_ok": liveness.get("ok"),
        "liveness_error": str(liveness.get("error") or liveness.get("reason") or "")[:160] or None,
        "meta_liveness_ok": meta_liveness.get("ok"),
        "stderr_present": bool(proc.stderr and proc.stderr.strip()),
        "stdout_present": bool(proc.stdout and proc.stdout.strip()),
    }


def run_loop(event_type: str, *, source: str, run_id: str) -> dict[str, Any]:
    global _last_liveness_ok_at, _last_liveness_error
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
    # Repair fix 5: record whether the heartbeat write itself actually landed —
    # independent of whether this cycle's business logic succeeded. Meaningful
    # now that repair fix 1 makes liveness_upsert populate on every code path.
    liveness = (cycle or {}).get("liveness_upsert") or {}
    if liveness.get("ok") is True:
        _last_liveness_ok_at = utc_now()
        _last_liveness_error = None
    elif liveness:
        _last_liveness_error = str(liveness.get("error") or liveness.get("reason") or "liveness_write_failed")
    ok = proc.returncode == 0 and (cycle or {}).get("status") == "ok"
    # Keep the actual cycle failure visible in Railway logs; HTTP status alone
    # hides whether the blocker is cycle acquisition, a command, or the sink.
    diagnostic = _tick_diagnostic(
        event_type=event_type,
        source=source,
        run_id=run_id,
        proc=proc,
        cycle=cycle,
        ok=ok,
    )
    print("NOOS_TICK_DIAGNOSTIC " + json.dumps(diagnostic, separators=(",", ":"), sort_keys=True), flush=True)
    return {
        "schema": "noos-railway-loop-runner-tick-v1",
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
        "schema": "noos-railway-loop-runner-tick-v1",
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
            host="railway:noos-loop-runner",
        )
    return result


def probe_supabase() -> dict[str, Any]:
    """Probe the exact Supabase tables required by real loop execution.

    Process liveness is not motor readiness. Cycle allocation reads
    noetfield_factory_cycle_runs; loop heartbeat reads noos_loop_registry.
    The incident table is optional because migration 0019 may still be pending.
    """
    url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").strip()
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    if not url or not key:
        return {"ok": False, "reason": "supabase_not_configured"}

    import urllib.error
    import urllib.request

    base = url.rstrip("/")

    def probe_table(table: str, select: str) -> dict[str, Any]:
        req = urllib.request.Request(
            f"{base}/rest/v1/{table}?select={select}&limit=1",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return {"ok": 200 <= resp.status < 300, "status": resp.status}
        except urllib.error.HTTPError as exc:
            return {"ok": False, "status": exc.code, "reason": "http_error"}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return {"ok": False, "reason": type(exc).__name__}

    tables = {
        "noos_loop_registry": probe_table("noos_loop_registry", "loop_id"),
        "noetfield_factory_cycle_runs": probe_table("noetfield_factory_cycle_runs", "cycle_number"),
        "noos_incident_log": probe_table("noos_incident_log", "id"),
    }
    core_ok = (
        tables["noos_loop_registry"].get("ok") is True
        and tables["noetfield_factory_cycle_runs"].get("ok") is True
    )
    return {
        "ok": core_ok,
        "tables": tables,
        "incident_logging_ready": tables["noos_incident_log"].get("ok") is True,
    }


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
        if not hmac.compare_digest(header, SECRET):
            return False, 403, "invalid_loop_secret"
        return True, 0, ""

    def _check_coding_access(self, operation: str) -> tuple[bool,int,str]:
        # Existing NOOS secret is reserved for its authorized control plane.
        if self.headers.get("X-NOOS-Loop-Secret"):
            return self._check_secret()
        try:
            authorize_github_oidc(self.headers.get("Authorization") or "", operation)
            return True,0,""
        except ValueError as exc:
            return False,401,str(exc)[:90]

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/v1/coding/status":
            ok,code,reason=self._check_coding_access("status")
            if not ok:
                self._json(code,{"ok":False,"error":reason})
                return
            if not pg_store_enabled():
                self._json(503,{"ok":False,"error":"POSTGRES_BACKEND_NOT_ENABLED"})
                return
            stats=queue_status()
            self._json(200 if stats.get("ok") else 503,stats)
            return
        if self.path == "/health/deep":
            probe = pg_probe() if pg_store_enabled() else probe_supabase()
            self._json(
                200 if probe.get("ok") else 503,
                {
                    "ok": bool(probe.get("ok")),
                    "schema": "noos-railway-loop-runner-health-deep-v1",
                    "service": "noos-loop-runner",
                    "supabase_probe": probe if not pg_store_enabled() else {"ok": False, "reason": "replaced_by_pg_epoch"},
                    "storage_probe": probe,
                    "last_successful_liveness_write_at": _last_liveness_ok_at,
                    "last_liveness_error": _last_liveness_error,
                },
            )
            return
        if self.path != "/health":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        self._json(
            200 if _ready else 503,
            {
                "ok": _ready,
                "schema": "noos-railway-loop-runner-health-v1",
                "service": "noos-loop-runner",
                "git_sha": git_sha(),
                "uptime_sec": int(time.time() - _started_at),
                "execution_mode": "one_shot_http",
                # Repair fix 5: additive — /health's status code and existing
                # fields are unchanged, so verify_noos_motor_sustain_v1.py
                # (which only checks resp.status == 200) is unaffected.
                "last_successful_liveness_write_at": _last_liveness_ok_at,
                "last_liveness_error": _last_liveness_error,
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path in ("/v1/coding/queue","/v1/coding/claim","/v1/coding/report"):
            ok,code,reason=self._check_coding_access(self.path.rsplit("/",1)[-1] if not self.path.endswith("/queue") else "queue")
            if not ok:
                self._json(code,{"ok":False,"error":reason})
                return
            if not pg_store_enabled():
                self._json(503,{"ok":False,"error":"POSTGRES_BACKEND_NOT_ENABLED"})
                return
            try:
                length=int(self.headers.get("Content-Length") or 0)
                if length < 2 or length>12000:
                    raise ValueError("INVALID_PAYLOAD_SIZE")
                payload=json.loads(self.rfile.read(length))
                if not isinstance(payload,dict):
                    raise ValueError("JSON_OBJECT_REQUIRED")
                if self.path.endswith("/queue"):
                    result=enqueue_job(payload)
                elif self.path.endswith("/claim"):
                    result=claim_job(str(payload.get("repo") or ""),lease_minutes=int(payload.get("lease_minutes") or 15))
                else:
                    result=report_job(payload)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json(400,{"ok":False,"error":str(exc)[:100]})
                return
            self._json(200 if result.get("ok") else 503,result)
            return
        if self.path == "/motor-restart":
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
            recipe_id = str(body.get("recipe_id") or "").strip()
            if not recipe_id:
                self._json(400, {"ok": False, "error": "recipe_id_required"})
                return
            dry_run = bool(body.get("dry_run"))
            cmd = [sys.executable, "scripts/noos_motor_restart_v1.py", "--recipe", recipe_id, "--json"]
            if dry_run:
                cmd.append("--dry-run")
            else:
                cmd.append("--write-receipt")
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False, timeout=1800)
            payload: dict[str, Any] | None = None
            if proc.stdout.strip():
                try:
                    payload = json.loads(proc.stdout)
                except json.JSONDecodeError:
                    payload = None
            ok = proc.returncode == 0 and (payload or {}).get("ok", proc.returncode == 0)
            self._json(200 if ok else 502, {"handler": "motor-restart", "ok": ok, "recipe_id": recipe_id, "result": payload})
            return

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

        event_type = str(body.get("event_type") or "").strip()
        if not event_type:
            self._json(400, {"ok": False, "error": "event_type_required"})
            return

        source = str(body.get("source") or "railway-http")
        lock = _lock_for(event_type)
        if not lock.acquire(blocking=False):
            self._json(409, {"ok": False, "event_type": event_type, "error": "already_running"})
            return

        run_id = f"railway-{uuid.uuid4().hex[:12]}"
        try:
            try:
                if event_type == FACTORY_EVENT or str(body.get("handler") or "") == "factory":
                    result = run_factory(source=source, run_id=run_id)
                else:
                    result = run_loop(event_type, source=source, run_id=run_id)
            except Exception as exc:  # noqa: BLE001 — an unhandled exception here (e.g.
                # subprocess.TimeoutExpired past LOOP_TIMEOUT_SEC) used to propagate raw,
                # closing the connection without ever calling self._json — the client saw
                # a bare connection failure. Respond cleanly so the caller can retry on the
                # next tick. Logging is fail-open: a missing migration 0019 must
                # never make the loop handler fail a second time.
                log_incident(
                    source="railway:noos-loop-runner",
                    severity="error",
                    message="unhandled_loop_handler_exception",
                    loop_id=str(body.get("loop_id") or "") or None,
                    event_type=event_type,
                    detail={"error_type": type(exc).__name__, "error": str(exc)[:300]},
                    run_id=run_id,
                )
                self._json(
                    502,
                    {
                        "ok": False,
                        "event_type": event_type,
                        "error": "unhandled_exception",
                        "detail": str(exc)[:500],
                        "run_id": run_id,
                    },
                )
                return
            result["receipt_path"] = write_receipt(run_id, result)
            self._json(200 if result.get("ok") else 502, result)
        finally:
            lock.release()


def main() -> None:
    global _ready
    if not SECRET:
        print("WARN: NOOS_LOOP_SECRET unset — POST /loop will return 503", file=sys.stderr)
    # Ensure Supabase service env is visible before the first tick's CAS seed.
    try:
        from noos_vault_paths_v1 import load_platform_env

        for key, val in load_platform_env().items():
            if val:
                os.environ.setdefault(key, val)
    except Exception as exc:  # noqa: BLE001 — boot must not die on vault miss
        print(f"WARN: vault env load failed: {exc}", file=sys.stderr)
    _ready = True
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
