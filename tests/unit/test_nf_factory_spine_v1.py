"""Machine proofs for NF-GAOS W3 factory spine."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PROVE = ROOT / "scripts/prove-nf-factory-spine-v1.py"

pytestmark = pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="factory spine proofs require founder Mac live-surface receipts",
)


def test_prove_nf_factory_spine_all_pass() -> None:
    """Full proof harness must PASS (positive + negative injection)."""
    assert PROVE.is_file(), f"missing {PROVE}"
    out = subprocess.run(
        [sys.executable, str(PROVE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0, out.stdout + out.stderr
    assert "prove-nf-factory-spine-v1: PASS" in out.stdout
    proof_path = ROOT / "reports/agent-auto/events/nf-factory-spine-proof-v1.json"
    report = json.loads(proof_path.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["failed"] == 0
    assert report["proof_count"] >= 9


def test_product_now_line_in_proof_receipt() -> None:
    proof_path = ROOT / "reports/agent-auto/events/nf-factory-spine-proof-v1.json"
    if not proof_path.is_file():
        subprocess.run([sys.executable, str(PROVE)], cwd=ROOT, check=True)
    data = json.loads(proof_path.read_text(encoding="utf-8"))
    assert data.get("ok") is True
    assert data.get("product_now_line")
    names = {p["proof"] for p in data.get("proofs", [])}
    assert "stale_injection_denies" in names
    assert "founder_implement_required" in names
