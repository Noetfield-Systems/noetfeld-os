"""NF-PLAN-0105 — tle-smoke performance budget hooks."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TLE_SMOKE = ROOT / "scripts" / "tle-smoke.sh"
VERIFY = ROOT / "scripts" / "verify-tle-performance.sh"


def test_tle_smoke_has_perf_flag_and_budgets() -> None:
    text = TLE_SMOKE.read_text(encoding="utf-8")
    assert "--perf" in text
    assert "TLE_SMOKE_MAX_MS_PER_STEP" in text
    assert "TLE_SMOKE_MAX_TOTAL_MS" in text
    assert "record_perf" in text
    assert "confidence_score" in text


def test_verify_tle_performance_script_exists() -> None:
    assert VERIFY.is_file()
    text = VERIFY.read_text(encoding="utf-8")
    assert "tle-smoke.sh --api --perf" in text
