"""Deadman Telegram lane — block @Gateway_A and generic env leaks."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_noos_deadman_telegram_lane_v1 as lane  # noqa: E402


def test_forbidden_list_includes_gateway_a() -> None:
    cfg = lane.load_lane()
    names = {lane.normalize_username(x) for x in cfg.get("forbidden_bot_usernames") or []}
    assert "gateway_a" in names


def test_send_alerts_enabled_for_dedicated_noos_bot() -> None:
    cfg = lane.load_lane()
    assert cfg.get("send_alerts") is True
    assert lane.normalize_username(cfg.get("allowed_bot_username")) == "noos_cycle_bot"


def test_verify_fails_without_token() -> None:
    row = lane.verify(token="", chat_id="")
    assert row["ok"] is False
