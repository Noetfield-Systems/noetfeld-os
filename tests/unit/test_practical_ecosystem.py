"""Practical cross-channel integration — ecosystem config and chat wiring."""

from __future__ import annotations

import json
from pathlib import Path


def test_ecosystem_json_is_valid() -> None:
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / "assets" / "noetfield-ecosystem.json").read_text(encoding="utf-8"))
    assert data["intake_email"] == "operations@noetfield.com"
    assert "chat_api_base" in data
    assert data["chat_api_base"].startswith("https://")


def test_chat_js_supports_configurable_api_base() -> None:
    text = (Path(__file__).resolve().parents[2] / "assets" / "noetfield-chat.js").read_text(
        encoding="utf-8"
    )
    assert "data-api-base" in text
    assert "nf-chat-api-base" in text


def test_intake_uses_rid_format() -> None:
    text = (Path(__file__).resolve().parents[2] / "trust-brief" / "intake" / "index.html").read_text(
        encoding="utf-8"
    )
    assert 'return ("RID-"' in text
    assert "NF-" not in text.split("ridNew")[1].split("function")[0]
