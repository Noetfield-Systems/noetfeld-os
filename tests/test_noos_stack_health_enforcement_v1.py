"""Regression tests for the NOOS stack-health enforcing gate (Mission 1).

Guards the exact false-green defect proven in run 29664359403: the enforcing
GitHub Actions job concluded ``success`` while
``scripts/noos_stack_automation_health_v1.py`` computed ``ok=false`` /
``overall_status=red``, because the workflow disabled ``pipefail`` around a
``python ... | tee`` and never propagated the real Python exit code.

These tests prove, deterministically and offline:
  * computed RED  → Python exit code != 0 (workflow now propagates → job fails)
  * computed GREEN → Python exit code == 0 (workflow passes)
  * the receipt file is always written (uploaded) regardless of RED/GREEN
  * the workflow YAML can no longer mask the health exit code
    (no ``set +o pipefail`` and no ``| tee`` on the health invocation, and an
    explicit ``exit "${rc}"`` propagation is present).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_stack_automation_health_v1 as stack  # noqa: E402

WORKFLOW = ROOT / ".github/workflows/noos-stack-health-receipt.yml"

RED_ROW = {
    "schema": "noos-stack-automation-health-v1",
    "ok": False,
    "overall_status": "red",
    "closure_token": "NOOS_STACK_AUTOMATION: red",
    "fix_queue": ["integrator_status", "autorun_critique", "trustfield_registry"],
}
GREEN_ROW = {
    "schema": "noos-stack-automation-health-v1",
    "ok": True,
    "overall_status": "green",
    "closure_token": "NOOS_STACK_AUTOMATION: green",
    "fix_queue": [],
}


def test_computed_red_exits_nonzero(monkeypatch, capsys):
    monkeypatch.setattr(stack, "rollup", lambda: dict(RED_ROW))
    monkeypatch.setattr(sys, "argv", ["prog", "--json"])
    rc = stack.main()
    assert rc == 1, "computed RED must return a non-zero exit code so the job fails"
    out = json.loads(capsys.readouterr().out)
    assert out["overall_status"] == "red"


def test_computed_green_exits_zero(monkeypatch, capsys):
    monkeypatch.setattr(stack, "rollup", lambda: dict(GREEN_ROW))
    monkeypatch.setattr(sys, "argv", ["prog", "--json"])
    rc = stack.main()
    assert rc == 0, "computed GREEN must return exit 0 so the job passes"
    capsys.readouterr()


def test_receipt_written_on_red(monkeypatch, tmp_path, capsys):
    proof = tmp_path / "noos-stack-automation-health-v1.json"
    monkeypatch.setattr(stack, "PROOF", proof)
    monkeypatch.setattr(stack, "rollup", lambda: dict(RED_ROW))
    monkeypatch.setattr(sys, "argv", ["prog", "--write-receipt", "--json"])
    rc = stack.main()
    assert rc == 1
    assert proof.is_file(), "receipt must be written (uploaded) even when RED"
    written = json.loads(proof.read_text())
    assert written["overall_status"] == "red"
    capsys.readouterr()


def test_receipt_written_on_green(monkeypatch, tmp_path, capsys):
    proof = tmp_path / "noos-stack-automation-health-v1.json"
    monkeypatch.setattr(stack, "PROOF", proof)
    monkeypatch.setattr(stack, "rollup", lambda: dict(GREEN_ROW))
    monkeypatch.setattr(sys, "argv", ["prog", "--write-receipt", "--json"])
    rc = stack.main()
    assert rc == 0
    assert proof.is_file(), "receipt must be written (uploaded) when GREEN"
    capsys.readouterr()


def test_workflow_cannot_mask_health_exit_code():
    text = WORKFLOW.read_text(encoding="utf-8")
    # The false-green pattern must not return.
    assert "set +o pipefail" not in text, "pipefail must never be disabled around the health command"
    # The health script must not be piped into tee (that masked the exit code).
    assert "noos_stack_automation_health_v1.py" in text
    for line in text.splitlines():
        if "noos_stack_automation_health_v1.py" in line:
            assert "| tee" not in line, "health script must not be piped into tee"
    # The real exit code must be captured and explicitly propagated.
    assert 'rc=$?' in text, "workflow must capture the real Python exit code"
    assert 'exit "${rc}"' in text, "workflow must propagate the health exit code to the job result"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
