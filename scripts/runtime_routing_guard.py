#!/usr/bin/env python3
"""Runtime routing guard utility.

Usage: called by runtime (worker/kernel) before allowing external LLM/provider calls.
Returns JSON on stdout with keys: allowed (bool), reason (str), blocked_by (optional).

This utility reads data/cost_policy_machine.json to enforce allowlist and banlist.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data/cost_policy_machine.json"


def load_policy():
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def validate(provider: str | None, model: str | None) -> dict:
    p = load_policy()
    provider = (provider or "").strip()
    model = (model or "").strip()

    if not provider and not model:
        return {"allowed": True, "reason": "no_model_no_provider"}

    # explicit bans
    banned_providers = set(p.get("forbidden_providers", []))
    banned_models = set(p.get("forbidden_models", []))
    allowed_models = set(p.get("allowed_default_models", []))

    # provider check
    if provider and provider in banned_providers:
        return {"allowed": False, "reason": f"forbidden_provider:{provider}", "blocked_by": "policy"}

    # model check
    if model and model in banned_models:
        return {"allowed": False, "reason": f"forbidden_model:{model}", "blocked_by": "policy"}

    # unknown model -> block if fail_closed_on_unknown_model
    if model and model not in allowed_models and model.lower() not in ("none", "null"):
        if p.get("fail_closed_on_unknown_model"):
            return {"allowed": False, "reason": f"unknown_model_blocked:{model}", "blocked_by": "policy"}

    # everything else allowed
    return {"allowed": True, "reason": "allowed_by_policy"}


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default=None)
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    out = validate(provider=args.provider, model=args.model)
    print(json.dumps(out))
    return 0 if out.get("allowed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
