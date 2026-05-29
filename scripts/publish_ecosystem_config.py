#!/usr/bin/env python3
"""Write assets/noetfield-ecosystem.json from deploy env (no secrets)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "noetfield-ecosystem.json"


def main() -> int:
    username = os.environ.get("TELEGRAM_BOT_USERNAME", "").strip().lstrip("@")
    chat_base = os.environ.get("PUBLIC_CHAT_API_BASE", "").strip().rstrip("/")
    intake = os.environ.get("CANONICAL_INTAKE_EMAIL", "operations@noetfield.com").strip()

    if OUT.exists():
        current = json.loads(OUT.read_text(encoding="utf-8"))
    else:
        current = {}

    payload = {
        "version": "1",
        "intake_email": intake or current.get("intake_email", "operations@noetfield.com"),
        "intake_url": current.get("intake_url", "https://www.noetfield.com/trust-brief/intake/"),
        "chat_api_base": chat_base or current.get("chat_api_base", "https://platform.noetfield.com"),
        "telegram_bot_username": username or current.get("telegram_bot_username", ""),
        "channels": {
            "website_chat": True,
            "telegram": bool(username),
            "email": True,
        },
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Wrote", OUT)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
