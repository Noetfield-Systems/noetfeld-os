"""One-shot NOOS UOS-RI boot proof cannot bypass existing HMAC or create a parallel runtime."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _server():
    target = ROOT / "ops/railway/noos-loop-runner/server.py"
    spec = importlib.util.spec_from_file_location("noos_runner_uos_ri_test", target)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_opt_in_only_and_no_network(monkeypatch, capsys):
    monkeypatch.delenv("NOOS_UOS_RI_ONE_SHOT_RUN_ID", raising=False)
    _server()._run_uos_ri_one_shot()
    assert "UOS_RI_RAILWAY_COMMISSION" not in capsys.readouterr().out


def test_one_fixed_budget_and_sanitized_log(monkeypatch, capsys):
    import noos_uos_ri_commission_v1 as uos
    submitted = []
    monkeypatch.setenv("NOOS_UOS_RI_ONE_SHOT_RUN_ID", "staging-technical-commission-01")
    def fake_commission(packet, *, max_observations, poll_seconds):
        submitted.append((packet, max_observations, poll_seconds))
        return {"status": "TERMINAL_UNVERIFIED_OR_FAILED",
                "runtime_job_id": "rj_" + "a" * 32,
                "provider_execution_verified": False,
                "raw_secret": "must-not-be-logged"}
    monkeypatch.setattr(uos, "commission", fake_commission)
    _server()._run_uos_ri_one_shot()
    assert len(submitted) == 1
    packet, checks, interval = submitted[0]
    assert packet["budget_usd"] == 0.25
    assert packet["idempotency_key"] == "uos-ri-noos-staging-technical-commission-01"
    assert packet["recipe_id"] == "vendor-decision-brief"
    assert checks == 90 and interval == 2
    output = capsys.readouterr().out
    assert "must-not-be-logged" not in output
    row = json.loads(output.split("UOS_RI_RAILWAY_COMMISSION=", 1)[1])
    assert row["status"] == "TERMINAL_UNVERIFIED_OR_FAILED"
    assert row["runtime_job_id"].startswith("rj_")
