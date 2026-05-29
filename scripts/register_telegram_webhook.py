#!/usr/bin/env python3
"""Register Telegram webhook using environment variables (no secrets in code)."""

from __future__ import annotations

import os
import sys

from noetfield_governance.telegram_client import set_webhook, get_webhook_info


def main() -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    base = os.environ.get("TELEGRAM_WEBHOOK_BASE_URL", "").strip().rstrip("/")
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip() or None
    if not token:
        print("TELEGRAM_BOT_TOKEN is required", file=sys.stderr)
        return 1
    if not base:
        print("TELEGRAM_WEBHOOK_BASE_URL is required", file=sys.stderr)
        return 1
    url = f"{base}/api/telegram/webhook"
    result = set_webhook(token=token, webhook_url=url, secret_token=secret)
    info = get_webhook_info(token=token)
    print("setWebhook:", result)
    print("webhookInfo:", info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
