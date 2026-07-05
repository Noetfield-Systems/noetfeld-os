#!/usr/bin/env python3
"""Intake E2E — submit test intake, poll platform for Resend webhook delivery status."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from nf_factory_lib_v1 import iso_now, write_event, write_sina  # noqa: E402

USER_AGENT = "noetfield-intake-e2e/1.0"
SCHEMA_VERSION = "nf-intake-e2e-v1"
DEFAULT_PLATFORM_BASE = "https://platform.noetfield.com"
DEFAULT_WWW_BASE = "https://www.noetfield.com"
POLL_INTERVAL_SEC = 3.0
POLL_TIMEOUT_SEC = 120.0
TERMINAL_STATUSES = frozenset({"delivered", "bounced"})


def make_request_id() -> str:
    return f"RID-E2E-{int(time.time())}"


def fetch_json(url: str, *, method: str = "GET", body: dict[str, Any] | None = None, timeout: float = 25.0) -> tuple[int, dict[str, Any]]:
    data = None
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return int(resp.status), payload if isinstance(payload, dict) else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"detail": raw[:500]}
        return int(exc.code), payload if isinstance(payload, dict) else {"detail": raw[:500]}


def intake_health_url(base: str) -> str:
    return f"{base.rstrip('/')}/api/intake/health"


def platform_status_url(platform_base: str, request_id: str) -> str:
    query = urllib.parse.urlencode({"request_id": request_id})
    return f"{platform_base.rstrip('/')}/api/intake/status?{query}"


def skip_reason_for_target(*, intake_url: str, platform_base: str) -> str | None:
    platform_code, platform_health = fetch_json(intake_health_url(platform_base))
    if platform_code != 200:
        return f"platform_intake_health_unreachable:{platform_code}"

    if not platform_health.get("email_delivery_tracking"):
        return "email_delivery_tracking_not_configured"

    parsed = urllib.parse.urlparse(intake_url)
    target_base = f"{parsed.scheme}://{parsed.netloc}"
    if target_base.rstrip("/") == platform_base.rstrip("/"):
        if not platform_health.get("ops_email_configured"):
            return "platform_ops_email_not_configured"
        return None

    target_code, target_health = fetch_json(intake_health_url(target_base))
    if target_code != 200:
        return f"target_intake_health_unreachable:{target_code}"
    if not target_health.get("www_email_configured") and not target_health.get("ops_email_configured"):
        return "target_intake_email_not_configured"
    return None


def submit_test_intake(intake_url: str, request_id: str) -> tuple[bool, dict[str, Any]]:
    body = {
        "organization": "NF E2E Deploy Verify",
        "contact_name": "NF E2E Bot",
        "contact_email": "e2e@noetfield.com",
        "message": f"Automated post-deploy intake E2E — {iso_now()}. Ignore.",
        "request_id": request_id,
        "sku": "general",
        "vector": "contact",
        "source": "api",
        "metadata": {
            "form_id": "nf_intake_e2e",
            "topic": "e2e",
            "async": True,
        },
    }
    code, payload = fetch_json(intake_url, method="POST", body=body, timeout=30.0)
    ok = 200 <= code < 300 and bool(payload.get("intake_id") or payload.get("ok"))
    return ok, {"http_status": code, **payload}


def poll_delivery_status(
    *,
    platform_base: str,
    request_id: str,
    poll_interval: float,
    poll_timeout: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + poll_timeout
    attempts = 0
    last: dict[str, Any] = {}

    while time.monotonic() < deadline:
        attempts += 1
        code, payload = fetch_json(platform_status_url(platform_base, request_id))
        last = {"http_status": code, **payload}
        if code == 404:
            time.sleep(poll_interval)
            continue
        status = str(payload.get("email_archive_status") or "").lower()
        if status in TERMINAL_STATUSES:
            return {
                "attempts": attempts,
                "final_status": status,
                "last": last,
                "timed_out": False,
            }
        time.sleep(poll_interval)

    return {
        "attempts": attempts,
        "final_status": str(last.get("email_archive_status") or ""),
        "last": last,
        "timed_out": True,
    }


def build_receipt(
    *,
    ok: bool,
    status: str,
    request_id: str,
    intake_url: str,
    platform_base: str,
    reason: str | None,
    submit: dict[str, Any] | None,
    poll: dict[str, Any] | None,
) -> dict[str, Any]:
    intake_id = ""
    if submit:
        intake_id = str(submit.get("intake_id") or "")
    if not intake_id and poll and poll.get("last"):
        last = poll["last"]
        if isinstance(last, dict):
            intake_id = str(last.get("intake_id") or "")

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": iso_now(),
        "ok": ok,
        "status": status,
        "reason": reason,
        "request_id": request_id,
        "intake_id": intake_id or None,
        "intake_url": intake_url,
        "platform_base": platform_base,
        "platform_status_url": platform_status_url(platform_base, request_id),
        "submit": submit,
        "poll": poll,
    }


def write_receipt(receipt: dict[str, Any]) -> None:
    write_event("nf-intake-e2e-v1.json", receipt, ROOT)
    write_sina("nf-intake-e2e-v1.json", receipt)


def run_e2e(
    *,
    intake_url: str,
    platform_base: str,
    poll_interval: float,
    poll_timeout: float,
    force: bool,
) -> dict[str, Any]:
    request_id = make_request_id()

    if not force:
        skip = skip_reason_for_target(intake_url=intake_url, platform_base=platform_base)
        if skip:
            receipt = build_receipt(
                ok=True,
                status="skipped",
                request_id=request_id,
                intake_url=intake_url,
                platform_base=platform_base,
                reason=skip,
                submit=None,
                poll=None,
            )
            write_receipt(receipt)
            return receipt

    submit_ok, submit_payload = submit_test_intake(intake_url, request_id)
    if not submit_ok:
        receipt = build_receipt(
            ok=False,
            status="fail",
            request_id=request_id,
            intake_url=intake_url,
            platform_base=platform_base,
            reason="intake_submit_failed",
            submit=submit_payload,
            poll=None,
        )
        write_receipt(receipt)
        return receipt

    poll = poll_delivery_status(
        platform_base=platform_base,
        request_id=request_id,
        poll_interval=poll_interval,
        poll_timeout=poll_timeout,
    )
    final_status = str(poll.get("final_status") or "").lower()

    if final_status == "delivered":
        receipt = build_receipt(
            ok=True,
            status="pass",
            request_id=request_id,
            intake_url=intake_url,
            platform_base=platform_base,
            reason=None,
            submit=submit_payload,
            poll=poll,
        )
        write_receipt(receipt)
        return receipt

    reason = "email_archive_bounced" if final_status == "bounced" else "webhook_delivery_timeout"
    receipt = build_receipt(
        ok=False,
        status="fail",
        request_id=request_id,
        intake_url=intake_url,
        platform_base=platform_base,
        reason=reason,
        submit=submit_payload,
        poll=poll,
    )
    write_receipt(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Intake E2E — submit + poll webhook delivery status")
    parser.add_argument("--intake-url", default="", help="POST target (default: {www}/api/intake)")
    parser.add_argument("--www-base", default=DEFAULT_WWW_BASE, help="WWW base when --intake-url omitted")
    parser.add_argument("--platform-base", default=DEFAULT_PLATFORM_BASE)
    parser.add_argument("--poll-interval", type=float, default=POLL_INTERVAL_SEC)
    parser.add_argument("--poll-timeout", type=float, default=POLL_TIMEOUT_SEC)
    parser.add_argument("--force", action="store_true", help="Run even when tracking/email not configured")
    parser.add_argument("--json", action="store_true", help="Print receipt JSON to stdout")
    args = parser.parse_args()

    intake_url = (args.intake_url or "").strip() or f"{args.www_base.rstrip('/')}/api/intake"
    receipt = run_e2e(
        intake_url=intake_url,
        platform_base=args.platform_base.rstrip("/"),
        poll_interval=max(1.0, args.poll_interval),
        poll_timeout=max(10.0, args.poll_timeout),
        force=args.force,
    )

    if args.json:
        print(json.dumps(receipt, indent=2))
    elif receipt["status"] == "skipped":
        print(f"nf_intake_e2e: SKIP reason={receipt.get('reason')}")
    elif receipt["ok"]:
        print(
            "nf_intake_e2e: PASS "
            f"request_id={receipt.get('request_id')} "
            f"intake_id={receipt.get('intake_id')} "
            f"email_archive_status=delivered"
        )
    else:
        print(
            f"nf_intake_e2e: FAIL reason={receipt.get('reason')} "
            f"request_id={receipt.get('request_id')}",
            file=sys.stderr,
        )

    if receipt["status"] == "skipped":
        return 0
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
