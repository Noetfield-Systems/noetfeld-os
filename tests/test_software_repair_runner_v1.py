"""NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §7/8/11 — repair pipeline gate.

Real end-to-end repairs of the three fixture defect classes (off-by-one,
unused-import lint, wrong-operator data defect), plus recipe policy enforcement,
idempotency, truthful failure, and forbidden-path rejection. All offline via the
deterministic-local engine (no hosted-model key needed).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_motor_state_machine_v1 as fsm  # noqa: E402
import noos_recipe_registry_v1 as registry  # noqa: E402
import noos_software_repair_runner_v1 as runner  # noqa: E402

JOBS = ROOT / "fixtures" / "repair" / "jobs"


def _job(name):
    return json.loads((JOBS / name).read_text())


# ---- recipe registry -------------------------------------------------------
def test_recipe_loads_and_rejects():
    r = registry.load_recipe("software_repair_ci_v1", version="1.0.0")
    assert r["recipe_id"] == "software_repair_ci_v1"
    with pytest.raises(registry.UnknownRecipe):
        registry.load_recipe("does_not_exist")
    with pytest.raises(registry.UnknownRecipe):
        registry.load_recipe("software_repair_ci_v1", version="9.9.9")


def test_recipe_path_and_limit_policy():
    r = registry.load_recipe("software_repair_ci_v1")
    assert registry.path_allowed(r, "src/mathutil.py")[0] is True
    assert registry.path_allowed(r, ".github/workflows/deploy.yml")[0] is False
    assert registry.path_allowed(r, "infrastructure/x.tf")[0] is False
    ok, viol = registry.within_limits(r, changed_files=99, patch_bytes=1, model_calls=1, attempts=1)
    assert ok is False and "max_changed_files" in viol


# ---- the three real repairs ------------------------------------------------
@pytest.mark.parametrize("spec,expect_class", [
    ("job1-unit-regression.json", "unit_test_regression"),
    ("job2-lint-failure.json", "lint_failure"),
    ("job3-integration-data.json", "unit_test_regression"),  # data bug surfaces as assertion
])
def test_real_repair_jobs(spec, expect_class):
    res = runner.run_repair_job(_job(spec))
    assert res["ok"] is True
    assert res["job_status"] == "repaired"
    assert res["state"] == fsm.COMPLETED
    assert res["tests_before"]["exit_code"] != 0  # really failing before
    assert res["tests_after"]["passed"] is True    # really passing after
    assert res["failure_class"] == expect_class
    assert Path(res["patch_path"]).read_text().strip()  # a non-empty real patch
    assert res["patch_hash"]


# ---- idempotency -----------------------------------------------------------
def test_idempotent_commission():
    led = fsm.MotorLedger()
    job = _job("job1-unit-regression.json")
    a = runner.run_repair_job(job, ledger=led)
    b = runner.run_repair_job(job, ledger=led)
    assert a["execution_id"] == b["execution_id"]
    assert b["job_status"] == "deduplicated"


# ---- truthful failure (no fake green) --------------------------------------
def test_unrepairable_fails_truthfully():
    job = {
        "commission_id": "SR-NEG", "recipe_id": "software_repair_ci_v1", "recipe_version": "1.0.0",
        "repository": {"kind": "local_fixture", "path": "fixtures/repair/py-unit-regression"},
        "failure": {"test_command": ["python3", "-c", "import sys; sys.exit(3)"], "allowed_files": ["src/mathutil.py"]},
    }
    res = runner.run_repair_job(job)
    assert res["ok"] is False
    assert res["state"] == fsm.FAILED
    assert res["job_status"] == "unrepaired"


def test_invalid_job_rejected():
    res = runner.run_repair_job({"commission_id": "x"})
    assert res["ok"] is False
    assert res["job_status"] == "invalid"


def test_unknown_recipe_job_rejected():
    job = _job("job1-unit-regression.json") | {"recipe_id": "nope"}
    res = runner.run_repair_job(job)
    assert res["job_status"] == "rejected_recipe"


def test_hosted_provider_failure_falls_back_to_deterministic(monkeypatch):
    """Independent-CI regression: a GITHUB_TOKEN without models:read (or any hosted
    provider failure) must fall back to the deterministic engine, not fail the job.
    Caught by GEL CI on the product PR head."""
    # Force the router to prefer a hosted provider whose call cannot succeed.
    monkeypatch.setenv("GITHUB_TOKEN", "broken_token_no_models_scope")
    monkeypatch.setenv("GITHUB_MODELS_BASE", "https://models.github.ai/inference")
    res = runner.run_repair_job(_job("job3-integration-data.json"), prefer_model="auto")
    assert res["ok"] is True
    assert res["job_status"] == "repaired"
    receipt = json.loads(Path(res["receipt_path"]).read_text())
    assert (receipt.get("repaired") or {}).get("strategy") == "deterministic-local"
