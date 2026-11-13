"""Safe NOOS loop error categories; no upstream secrets copied to public diagnostics."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from noos_loop_runner_v1 import classify_step_failure, run_cmd


def test_upstream_auth_is_classified_without_copying_secret():
    assert classify_step_failure("", '{"error":"HTTP Error 401: Unauthorized","token":"private-secret"}') == "UPSTREAM_AUTH_401"


def test_database_tenant_error_is_classified():
    assert classify_step_failure("", "FATAL: tenant or user not found") == "DATABASE_POOLER_TENANT_INVALID"


def test_unrecognized_failure_is_constant_not_upstream_payload():
    assert classify_step_failure("", "secret=VERYPRIVATE012345 error") == "UNCLASSIFIED_NONZERO_EXIT"


def test_real_nonzero_subprocess_returns_safe_error_code():
    result = run_cmd(["python3", "-c", "import sys; sys.stderr.write('HTTP Error 403: Forbidden\\n'); sys.exit(1)"])
    assert result["ok"] is False
    assert result["exit_code"] == 1
    assert result["error"] == "UPSTREAM_PERMISSION_403"


def test_success_has_no_failure_code():
    result = run_cmd(["python3", "-c", "print('OK')"])
    assert result["ok"] is True
    assert result["error"] is None
