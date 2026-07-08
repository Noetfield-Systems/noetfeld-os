#!/usr/bin/env python3
"""Validate deadman Telegram lane — NEVER Gateway_A / NF Probe / generic TELEGRAM_* env."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/noos-deadman-config-v1.json"

FORBIDDEN_ENV_KEYS = (
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "GATEWAY_TELEGRAM_BOT_TOKEN",
    "GATEWAY_TELEGRAM_CHAT_ID",
    "NF_PROBE_TELEGRAM_BOT_TOKEN",
    "NF_PROBE_TELEGRAM_CHAT_ID",
    "SIGNAL_FACTORY_TELEGRAM_BOT_TOKEN",
    "SIGNAL_FACTORY_TELEGRAM_CHAT_ID",
)


def load_lane() -> dict[str, Any]:
    doc = json.loads(CONFIG.read_text(encoding="utf-8"))
    return doc.get("telegram_lane") or {}


def get_me(token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token.strip()}/getMe",
        headers={"User-Agent": "noos-deadman-telegram-lane-v1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": exc.read().decode("utf-8", errors="replace")[:200]}


def normalize_username(value: str) -> str:
    return str(value or "").strip().lower().lstrip("@")


def verify(*, token: str | None = None, chat_id: str | None = None) -> dict[str, Any]:
    lane = load_lane()
    forbidden = {normalize_username(x) for x in lane.get("forbidden_bot_usernames") or []}
    allowed = normalize_username(str(lane.get("allowed_bot_username") or ""))
    token = (token or os.environ.get("DEADMAN_TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (chat_id or os.environ.get("DEADMAN_TELEGRAM_CHAT_ID") or "").strip()

    leaked = [k for k in FORBIDDEN_ENV_KEYS if os.environ.get(k)]
    row: dict[str, Any] = {
        "schema": "noos-deadman-telegram-lane-v1",
        "send_alerts": lane.get("send_alerts"),
        "forbidden_bot_usernames": sorted(forbidden),
        "allowed_bot_username": allowed or None,
        "token_present": bool(token),
        "chat_id_present": bool(chat_id),
        "forbidden_env_leaks": leaked,
        "ok": True,
    }

    if leaked:
        row["ok"] = False
        row["error"] = "forbidden_generic_telegram_env_in_shell"
        return row

    if not token:
        row["ok"] = False
        row["error"] = "DEADMAN_TELEGRAM_BOT_TOKEN_missing"
        return row

    me = get_me(token)
    row["getMe"] = me
    if not me.get("ok"):
        row["ok"] = False
        row["error"] = "getMe_failed"
        return row

    username = normalize_username((me.get("result") or {}).get("username") or "")
    row["bot_username"] = username

    if username in forbidden:
        row["ok"] = False
        row["error"] = "forbidden_bot_username"
        row["blocked_bot"] = username
        return row

    if allowed and username != allowed:
        row["ok"] = False
        row["error"] = "bot_username_mismatch"
        row["expected"] = allowed
        return row

    if lane.get("send_alerts") is not True:
        row["send_alerts_enabled"] = False
        row["note"] = "Lane valid but send_alerts=false — worker will not message any chat"

    if not chat_id:
        row["ok"] = False
        row["error"] = "DEADMAN_TELEGRAM_CHAT_ID_missing"

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-forbidden", action="store_true")
    args = ap.parse_args()

    row = verify()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if row.get("ok"):
            print(f"deadman_telegram_lane · ok bot=@{row.get('bot_username')} send_alerts={row.get('send_alerts')}")
        else:
            print(f"deadman_telegram_lane · BLOCKED · {row.get('error')}")
    if args.fail_on_forbidden and not row.get("ok"):
        return 1
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
