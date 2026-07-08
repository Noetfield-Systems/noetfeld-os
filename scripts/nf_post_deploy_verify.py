#!/usr/bin/env python3
"""Post-deploy live verify — confirm production matches expected git SHA; alert founder on Telegram."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAULT = Path.home() / ".sina" / "secrets.env"
PLATFORM_BASE = "https://platform.noetfield.com"
WWW_BASE = "https://www.noetfield.com"
USER_AGENT = "noetfield-post-deploy-verify/1.0"
PIN_FILE = ROOT / "data" / "nf-platform-deploy-pin-v1.json"


def read_vault(key: str) -> str:
    if not VAULT.is_file():
        return ""
    for line in VAULT.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"')
    return ""


def fetch_json(url: str) -> dict[str, object]:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def platform_expected_sha() -> str:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "read_nf_platform_expected_sha.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    if PIN_FILE.is_file():
        try:
            doc = json.loads(PIN_FILE.read_text(encoding="utf-8"))
            sha = str(doc.get("git_sha") or "").strip()
            if sha:
                return sha
        except json.JSONDecodeError:
            pass
    return ""


def expected_sha(value: str | None, *, surface: str) -> str:
    if value and value.strip():
        return value.strip()
    if surface in ("platform", "both"):
        pinned = platform_expected_sha()
        if pinned:
            return pinned
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def verify_platform(sha: str) -> list[str]:
    failures: list[str] = []
    try:
        body = fetch_json(f"{PLATFORM_BASE}/api/public/chat/health")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return [f"platform health unreachable: {exc}"]
    live = str(body.get("git_sha") or "")
    if not live:
        failures.append("platform health missing git_sha")
    elif not live.startswith(sha[:12]) and live != sha:
        failures.append(f"platform git_sha={live[:12]} expected={sha[:12]}")
    return failures


def verify_www(www_base: str) -> list[str]:
    failures: list[str] = []
    try:
        health = fetch_json(f"{www_base.rstrip('/')}/api/health")
        if health.get("service") != "noetfield-www":
            failures.append(f"www health unexpected payload from {www_base}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        failures.append(f"www health unreachable at {www_base}: {exc}")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "verify_chat_greeting_coupling.py"),
            "--live",
            "--www-base",
            www_base,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        failures.append(detail[-1] if detail else "www greeting coupling failed")
    return failures


def send_telegram_alert(*, title: str, lines: list[str]) -> bool:
    token = read_vault("TELEGRAM_NOETFIELD_OPS_BOT_TOKEN")
    chat_id = read_vault("TELEGRAM_OPS_CHAT_ID")
    if not token or not chat_id:
        print(
            "WARN: TELEGRAM_NOETFIELD_OPS_BOT_TOKEN or TELEGRAM_OPS_CHAT_ID missing in ~/.sina/secrets.env",
            file=sys.stderr,
        )
        return False
    text = f"<b>{title}</b>\n" + "\n".join(lines)
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text[:4096],
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return bool(body.get("ok"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"WARN: telegram alert failed: {exc}", file=sys.stderr)
        return False


def verify_intake_e2e(*, www_base: str, platform_base: str, surface: str) -> list[str]:
    # Canonical production path is www /api/intake (Pages → platform), even for platform deploy checks.
    intake_url = f"{www_base.rstrip('/')}/api/intake"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "nf_intake_e2e.py"),
            "--intake-url",
            intake_url,
            "--platform-base",
            platform_base.rstrip("/"),
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        line = detail[-1] if detail else "intake e2e failed"
        return [line]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-sha", default="")
    parser.add_argument("--surface", choices=("www", "platform", "both"), default="both")
    parser.add_argument("--deploy-failed", default="", help="Set when deploy command failed before verify")
    parser.add_argument("--www-base", default=WWW_BASE, help="WWW base URL for live checks")
    parser.add_argument("--platform-base", default=PLATFORM_BASE, help="Platform base URL for intake status polling")
    parser.add_argument(
        "--skip-intake-e2e",
        action="store_true",
        help="Skip intake Telegram+DB E2E check",
    )
    args = parser.parse_args()

    sha = expected_sha(args.expected_sha or None, surface=args.surface)
    failures: list[str] = []

    if args.deploy_failed:
        failures.append(f"deploy failed: {args.deploy_failed}")

    if args.surface in ("platform", "both"):
        failures.extend(verify_platform(sha))
    if args.surface in ("www", "both"):
        failures.extend(verify_www(args.www_base))

    if not failures and not args.skip_intake_e2e and not args.deploy_failed:
        failures.extend(
            verify_intake_e2e(
                www_base=args.www_base,
                platform_base=args.platform_base,
                surface=args.surface,
            )
        )

    if failures:
        title = "Noetfield deploy check FAIL"
        lines = [f"expected_sha: {sha[:12]}", f"surface: {args.surface}", f"www_base: {args.www_base}", *failures]
        for item in failures:
            print(f"FAIL {item}", file=sys.stderr)
        send_telegram_alert(title=title, lines=lines)
        return 1

    print(f"nf_post_deploy_verify: PASS sha={sha[:12]} surface={args.surface} www={args.www_base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
