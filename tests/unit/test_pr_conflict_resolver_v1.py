"""PR conflict resolver machine gate unit tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ssot_schema() -> None:
    data = json.loads((ROOT / "data/nf-pr-conflict-resolver-v1.json").read_text(encoding="utf-8"))
    assert data["schema"] == "nf-pr-conflict-resolver-v1"
    assert len(data["file_classes"]) >= 4


def test_classify_ordinary_code() -> None:
    out = subprocess.run(
        [
            "python3",
            "scripts/nf_pr_conflict_classify_v1.py",
            "--json",
            "scripts/verify_pr_conflict_resolver_v1.py",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(out.stdout)
    assert payload["classifications"]["scripts/verify_pr_conflict_resolver_v1.py"] == "ordinary_code"


def test_verify_gate_passes() -> None:
    out = subprocess.run(
        ["python3", "scripts/verify_pr_conflict_resolver_v1.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0, out.stderr
