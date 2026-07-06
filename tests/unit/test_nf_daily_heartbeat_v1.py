"""Unit tests for nf_daily_heartbeat_v1 fixed-format line."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import nf_daily_heartbeat_v1 as hb  # noqa: E402


def test_daily_heartbeat_format_template_exists():
    data = json.loads((ROOT / "data" / "nf-daily-heartbeat-format-v1.json").read_text(encoding="utf-8"))
    assert data["schema_version"] == "nf-daily-heartbeat-format-v1"
    assert "NF-DAILY-HEARTBEAT v1" in data["line_template"]


def test_daily_heartbeat_line_shape():
    with patch.object(hb, "_probe_url", return_value="PASS"), patch.object(hb, "_run", return_value="PASS"):
        with patch.object(sys, "argv", ["nf_daily_heartbeat_v1.py"]):
            assert hb.main() == 0
