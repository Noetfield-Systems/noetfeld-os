#!/usr/bin/env python3
"""Verify Railway noos-loop-runner — health+git_sha, auth reject, one tick."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_vault_paths_v1 import noos_loop_secret  # noqa: E402

PROOF = ROOT / "receipts/proof/noos-railway-loop-runner-v1.json"
DEFAULT_URL = "https://noos-loop-runner-production.up.railway.app"
DEFAULT_EVENT = "noos_orchestrator_cross_repo_tick"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_secret() -> str:
    for key in ("NOOS_LOOP_SECRET", "LOOP_RUNNER_SECRET"):
        if os.environ.get(key):
            return os.environ[key].strip()
    secret = noos_loop_secret()
    if secret:
        return secret
    railway = Path.home() / ".railway/bin/railway"
    service = os.environ.get("RAILWAY_LOOP_RUNNER_SERVICE", "noos-loop-runner")
    if railway.is_file():
        try:
            proc = subprocess.run(
                [str(railway), "variables", "--service", service, "--json"],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout)
                for key in ("NOOS_LOOP_SECRET", "LOOP_RUNNER_SECRET"):
                    val = str(data.get(key) or "").strip()
                    if val:
                        return val
        except (OSError, json.JSONDecodeError, subprocess.TimeoutExpired):
            pass
    return ""


def http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict | None = None,
    timeout: int = 120,
) -> tuple[int, dict | str]:
    data = None
    hdrs = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw


def verify(*, base_url: str, secret: str, event_type: str) -> dict:
    base = base_url.rstrip("/")
    row: dict = {
        "schema": "noos-railway-loop-runner-verify-v1",
        "at": utc_now(),
        "service": "noos-loop-runner",
        "railway_url": base,
        "ok": False,
    }

    status, health = http_json(f"{base}/health")
    health_ok = (
        status == 200
        and isinstance(health, dict)
        and health.get("ok") is True
        and health.get("service") == "noos-loop-runner"
        and bool(health.get("git_sha"))
        and health.get("git_sha") != "unknown"
    )
    row["health"] = {"ok": health_ok, "status": status, "body": health}

    status_no, reject = http_json(f"{base}/loop", method="POST", body={"event_type": event_type})
    row["auth_reject_missing"] = {
        "ok": status_no == 401 and isinstance(reject, dict) and reject.get("error") == "missing_loop_secret",
        "status": status_no,
        "body": reject,
    }

    status_bad, bad = http_json(
        f"{base}/loop",
        method="POST",
        headers={"X-NOOS-Loop-Secret": "bad-secret-on-purpose"},
        body={"event_type": event_type},
    )
    row["auth_reject_bad"] = {
        "ok": status_bad == 403 and isinstance(bad, dict) and bad.get("error") == "invalid_loop_secret",
        "status": status_bad,
        "body": bad,
    }

    if not secret:
        row["blocker"] = "NOOS_LOOP_SECRET not set locally"
        row["tick"] = {"ok": False, "skipped": True}
        return row

    status_ok, tick = http_json(
        f"{base}/loop",
        method="POST",
        headers={"X-NOOS-Loop-Secret": secret},
        body={"event_type": event_type, "source": "verify-railway-v1"},
        timeout=300,
    )
    tick_ok = status_ok == 200 and isinstance(tick, dict) and tick.get("ok") is True
    row["tick"] = {
        "ok": tick_ok,
        "status": status_ok,
        "body": tick if isinstance(tick, dict) else {"raw": str(tick)[:400]},
    }

    row["ok"] = (
        row["health"]["ok"]
        and row["auth_reject_missing"]["ok"]
        and row["auth_reject_bad"]["ok"]
        and row["tick"]["ok"]
    )
    row["report_line"] = (
        f"railway_loop_runner · health={'ok' if row['health']['ok'] else 'fail'} "
        f"auth={'ok' if row['auth_reject_missing']['ok'] and row['auth_reject_bad']['ok'] else 'fail'} "
        f"tick={'ok' if row['tick']['ok'] else 'fail'}"
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=os.environ.get("LOOP_RUNNER_URL", DEFAULT_URL))
    ap.add_argument("--secret", default="")
    ap.add_argument("--event-type", default=DEFAULT_EVENT)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    secret = args.secret or load_secret()
    row = verify(base_url=args.url, secret=secret, event_type=args.event_type)
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
