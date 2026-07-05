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


def expected_sha(value: str | None) -> str:
    if value and value.strip():
        return value.strip()
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-sha", default="")
    parser.add_argument("--surface", choices=("www", "platform", "both"), default="both")
    parser.add_argument("--deploy-failed", default="", help="Set when deploy command failed before verify")
    parser.add_argument("--www-base", default=WWW_BASE, help="WWW base URL for live checks")
    args = parser.parse_args()

    sha = expected_sha(args.expected_sha or None)
    failures: list[str] = []

    if args.deploy_failed:
        failures.append(f"deploy failed: {args.deploy_failed}")

    if args.surface in ("platform", "both"):
        failures.extend(verify_platform(sha))
    if args.surface in ("www", "both"):
        failures.extend(verify_www(args.www_base))

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
