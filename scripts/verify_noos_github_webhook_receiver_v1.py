#!/usr/bin/env python3
"""Verify Event Phase 1 — GitHub webhook receiver: sign a synthetic 'push to
SourceA/main' payload, POST it to the deployed worker, confirm the worker
accepted and dispatched it, then poll noos_loop_registry to confirm the
downstream /loop call (fired via ctx.waitUntil, asynchronous relative to the
worker's own response) actually landed a fresh sourcea_observe heartbeat."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_vault_paths_v1 import supabase_creds  # noqa: E402

PROOF = ROOT / "receipts/proof/noos-github-webhook-receiver-verify-v1.json"
DEFAULT_URL = "https://noos-loop-github-events-v1.sina-kazemnezhad-ca.workers.dev"
TARGET_LOOP_ID = "sourcea_observe"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sign(secret: str, body: bytes) -> str:
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={mac}"


def post_webhook(*, base_url: str, secret: str) -> dict[str, Any]:
    payload = {
        "ref": "refs/heads/main",
        "after": "0" * 40,
        "repository": {"full_name": "Noetfield-Systems/SourceA"},
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/webhook/github",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": sign(secret, body),
            "User-Agent": "noos-github-webhook-verify-v1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body_json = json.loads(raw)
        except json.JSONDecodeError:
            body_json = {"raw": raw[:300]}
        return {"ok": False, "status": exc.code, "body": body_json}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "error": str(exc)[:300]}


def read_last_fired_at(loop_id: str) -> str | None:
    url, key = supabase_creds()
    if not url or not key:
        return None
    req = urllib.request.Request(
        f"{url.rstrip('/')}/rest/v1/noos_loop_registry?select=last_fired_at&loop_id=eq.{loop_id}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
            if rows:
                return rows[0].get("last_fired_at")
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return None
    return None


def verify(*, base_url: str, secret: str, poll_seconds: int) -> dict[str, Any]:
    before = read_last_fired_at(TARGET_LOOP_ID)
    webhook_result = post_webhook(base_url=base_url, secret=secret)
    accepted = (
        webhook_result.get("ok")
        and webhook_result.get("status") == 200
        and (webhook_result.get("body") or {}).get("action") == "dispatched"
    )

    after = before
    landed = False
    deadline = time.monotonic() + poll_seconds
    while time.monotonic() < deadline:
        after = read_last_fired_at(TARGET_LOOP_ID)
        if after and after != before:
            landed = True
            break
        time.sleep(2)

    return {
        "schema": "noos-github-webhook-receiver-verify-v1",
        "verified_at": utc_now(),
        "worker_url": base_url,
        "webhook_accepted": accepted,
        "webhook_response": webhook_result,
        "loop_id_checked": TARGET_LOOP_ID,
        "last_fired_at_before": before,
        "last_fired_at_after": after,
        "downstream_dispatch_landed": landed,
        "ok": accepted and landed,
        "report_line": f"github_webhook_receiver_verify · accepted={accepted} downstream_landed={landed}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=os.environ.get("GITHUB_EVENTS_WORKER_URL", DEFAULT_URL))
    ap.add_argument("--secret", default=os.environ.get("MOTOR_APP_WEBHOOK_SECRET", ""))
    ap.add_argument("--poll-seconds", type=int, default=30)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.secret:
        print(json.dumps({"ok": False, "error": "MOTOR_APP_WEBHOOK_SECRET not available"}), file=sys.stderr)
        return 1
    row = verify(base_url=args.url, secret=args.secret, poll_seconds=args.poll_seconds)
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
