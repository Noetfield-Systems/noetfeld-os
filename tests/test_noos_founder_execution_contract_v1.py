"""Founder intent is present in EVERY real NOOS -> Runway intake path."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_founder_execution_contract_v1 as policy  # noqa: E402
import noos_plan_completion_dispatch_v1 as plan  # noqa: E402
import noos_role_runway_dispatch_v1 as role  # noqa: E402


def test_shared_contract_is_specific_and_not_a_permit():
    fc = policy.FOUNDER_EXECUTION_CONTRACT
    assert fc["version"] == "2026-11-11.3"
    assert fc["risk_appetite"] == "HIGH_COMMERCIAL_MARKET_PRODUCT_SPECULATIVE_RISK_ACCEPTED"
    assert fc["drift_signal"] == "FOUNDER INTENT DRIFT"
    assert "Token/Airdrop/Referral/Quest/Season 0" in fc["directive"]
    assert fc["not_an_external_action_permit"] is True
    assert role.FOUNDER_EXECUTION_CONTRACT is fc
    assert plan.FOUNDER_EXECUTION_CONTRACT is fc


def test_plan_intake_carries_founder_goal_contract_even_offline(tmp_path, monkeypatch):
    (tmp_path / "config.json").write_text(json.dumps({
        "runtime_queue_path": "queue.json",
        "dispatch_events_path": "events.jsonl",
        "concurrency": {"default_key": "local-test", "max_inflight_per_key": 1}
    }))
    (tmp_path / "contract.json").write_text(json.dumps({
        "role_recipe_map": {"research": {
            "runway_id": "research",
            "recipe_id": "noos-research-memo",
            "recipe_version": "1.0.0"
        }}
    }))
    (tmp_path / "queue.json").write_text(json.dumps({"items": [{
        "status": "READY", "op_key": "c" * 64, "plan_id": "P1",
        "item_id": "ITEM-1", "title": "Build Web3 community referrals",
        "role": "research", "value_class": "goal_delivery",
        "acceptance_checks": ["real_users"], "repository": "example/project"
    }], "counts": {"READY": 1}}))
    monkeypatch.setattr(plan, "ROOT", tmp_path)
    monkeypatch.setattr(plan, "CONFIG", tmp_path / "config.json")
    monkeypatch.setattr(plan, "CONTRACT", tmp_path / "contract.json")
    monkeypatch.setattr(plan.runway, "preflight", lambda: {"ok": False})
    monkeypatch.setattr(plan.runway, "verify_deepseek_pin", lambda: {"ok": True})
    monkeypatch.delenv("NOOS_PLAN_COMPLETION_LIVE_INTAKE", raising=False)
    capture = {}
    def capture_ack(intake):
        capture["intake"] = intake
        return {"ok": True, "status": 202, "dry_run": True,
                "op_key": intake["idempotency_key"],
                "body": {"job_id": "rj_" + "c"*32}}
    monkeypatch.setattr(plan, "dry_run_ack", capture_ack, raising=False)
    monkeypatch.setattr(plan, "dry_run_preview",
                        lambda intake: capture.setdefault("intake", intake) or {"intake": intake},
                        raising=False)
    plan.dispatch_once(write=False, allow_dry_run=True)
    fc = capture["intake"]["input"]["goal"]["founder_execution_contract"]
    assert fc["drift_signal"] == "FOUNDER INTENT DRIFT"
    assert fc["not_an_external_action_permit"] is True
