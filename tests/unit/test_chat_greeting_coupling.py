"""Chat greeting SSOT — disk, generated asset, and platform must stay coupled."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from noetfield_governance.public_chat_copy import (
    public_chat_greeting_content_hash,
    public_chat_greeting_payload,
)

ROOT = Path(__file__).resolve().parents[2]
SSOT = ROOT / "data" / "chatbot" / "public-chat-greeting.json"
ASSET = ROOT / "assets" / "nf-chat-greeting-ssot.js"
SYNC = ROOT / "scripts" / "sync_chat_greeting_asset.py"
VERIFY = ROOT / "scripts" / "verify_chat_greeting_coupling.py"


def test_public_chat_greeting_content_hash_matches_disk() -> None:
    data = json.loads(SSOT.read_text(encoding="utf-8"))
    greeting = str(data["greeting"]).strip()
    citations = [str(c).strip() for c in data["citations"]]
    expected = public_chat_greeting_content_hash(greeting=greeting, citations=citations)
    payload = public_chat_greeting_payload()
    assert payload["content_hash"] == expected


def test_generated_greeting_asset_matches_disk() -> None:
    subprocess.run([sys.executable, str(SYNC)], check=True, cwd=ROOT)
    assert ASSET.is_file()
    text = ASSET.read_text(encoding="utf-8")
    match = re.search(r"sha256=([a-f0-9]{64})", text)
    assert match, "asset missing sha256 marker"
    assert match.group(1) == public_chat_greeting_payload()["content_hash"]
    assert "window.NF_CHAT_GREETING_SSOT" in text
    assert "Ask naturally" not in text


def test_verify_chat_greeting_coupling_disk_passes() -> None:
    subprocess.run([sys.executable, str(SYNC)], check=True, cwd=ROOT)
    result = subprocess.run(
        [sys.executable, str(VERIFY)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
