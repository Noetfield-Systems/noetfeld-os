"""UPG-0159 — integration: noetfield gate PASS on clean repo (CI lane)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gate_cli_passes_json_in_clean_repo():
    proc = subprocess.run(
        [sys.executable, "-m", "noetfield_gate.cli", "gate", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    report = json.loads(proc.stdout)
    assert report["schema"] == "noetfield-gate-report-v1"
    assert report["outcome"] == "PASS"
