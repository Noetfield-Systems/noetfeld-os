"""Unit tests for SSOT governance demo runner."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_ssot_governance_demo.py"


def test_ssot_demo_output_shape(tmp_path: Path) -> None:
    out = tmp_path / "demo_output.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(out)],
        check=True,
        cwd=ROOT,
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["demo"] == "noetfield-ssot-governance-vertical"
    assert payload["ssot_event"]["event"] == "SSOT_CHANGED"
    assert payload["ssot_event"]["invalidated_count"] == 2
    assert len(payload["re_brief_queue"]) == 2
    assert payload["evaluate_result"]["decision"] in {"allow", "review", "deny"}
    assert payload["tle_receipt"]["rid"] == payload["evaluate_result"]["rid"]
