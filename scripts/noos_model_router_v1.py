#!/usr/bin/env python3
"""NOOS model router v1 — route task kinds to T0–T3 under budget and governance law."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "model-router.yml"

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore


def _parse_yaml(text: str) -> dict[str, Any]:
    if yaml is not None:
        return yaml.safe_load(text) or {}
    # Minimal fallback for environments without PyYAML (tests use JSON export or inline)
    raise RuntimeError("PyYAML required for model-router.yml — pip install pyyaml")


def load_router_config(path: Path | None = None) -> dict[str, Any]:
    target = path or CONFIG_PATH
    if not target.is_file():
        return {}
    text = target.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return {}


def redact_secrets(text: str, *, config: dict[str, Any] | None = None) -> tuple[str, int]:
    cfg = config or load_router_config()
    redaction = cfg.get("secret_redaction") if isinstance(cfg.get("secret_redaction"), dict) else {}
    patterns = redaction.get("patterns") if isinstance(redaction.get("patterns"), list) else []
    replacement = str(redaction.get("replacement") or "[REDACTED]")
    count = 0
    out = text
    for pat in patterns:
        out, n = re.subn(pat, replacement, out)
        count += n
    return out, count


def route_task(
    *,
    task_kind: str,
    founder_approval_token: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return tier routing decision for a task kind."""
    cfg = config or load_router_config()
    tiers = cfg.get("tiers") if isinstance(cfg.get("tiers"), dict) else {}
    routing = cfg.get("routing") if isinstance(cfg.get("routing"), dict) else {}
    kind = str(task_kind or "").strip().lower()

    matched_tier: str | None = None
    for tier_id, spec in tiers.items():
        if not isinstance(spec, dict):
            continue
        kinds = spec.get("task_kinds") if isinstance(spec.get("task_kinds"), list) else []
        if kind in {str(k).lower() for k in kinds}:
            matched_tier = str(tier_id)
            break

    tier_id = matched_tier or str(routing.get("unknown_task_kind") or routing.get("default_tier") or "T0")
    spec = tiers.get(tier_id) if isinstance(tiers.get(tier_id), dict) else {}
    requires_founder = bool(spec.get("requires_founder_approval"))

    blocked_reason: str | None = None
    if tier_id == "T3" and requires_founder:
        token = (founder_approval_token or "").strip()
        if not token:
            blocked_reason = "t3_requires_founder_approval"
        elif token != "FOUNDER_APPROVED_T3":
            blocked_reason = "invalid_founder_approval_token"

    models = spec.get("models") if isinstance(spec.get("models"), list) else []
    primary_model = models[0] if models and isinstance(models[0], dict) else {}
    providers = spec.get("providers") if isinstance(spec.get("providers"), list) else []
    provider = (
        primary_model.get("provider")
        or (providers[0] if providers else "local_shell")
    )

    return {
        "task_kind": kind,
        "tier": tier_id,
        "tier_name": spec.get("name"),
        "provider": provider,
        "model_id": primary_model.get("id"),
        "max_usd": float(spec.get("max_usd") or 0.0),
        "requires_founder_approval": requires_founder,
        "blocked": blocked_reason is not None,
        "blocker_reason": blocked_reason,
        "mode": "deterministic" if tier_id == "T0" else "llm_proposal",
    }


def estimate_cost(
    *,
    tier: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = config or load_router_config()
    tiers = cfg.get("tiers") if isinstance(cfg.get("tiers"), dict) else {}
    budget = cfg.get("budget") if isinstance(cfg.get("budget"), dict) else {}
    spec = tiers.get(tier) if isinstance(tiers.get(tier), dict) else {}
    models = spec.get("models") if isinstance(spec.get("models"), list) else []
    unit = 0.0
    if models and isinstance(models[0], dict):
        unit = float(models[0].get("unit_cost_usd_per_1k_tokens") or 0.0)
    total_tokens = tokens_in + tokens_out
    total_usd = round((total_tokens / 1000.0) * unit, 6)
    max_run = float(budget.get("max_usd_per_run") or 0.05)
    tier_max = float(spec.get("max_usd") or max_run)
    cap = min(max_run, tier_max) if tier_max > 0 else max_run
    return {
        "tier": tier,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "total_usd": total_usd,
        "max_usd_per_run": max_run,
        "tier_max_usd": tier_max,
        "within_budget": total_usd <= cap,
        "cap_usd": cap,
    }


def enforce_budget(cost_row: dict[str, Any], *, config: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = config or load_router_config()
    budget = cfg.get("budget") if isinstance(cfg.get("budget"), dict) else {}
    max_run = float(budget.get("max_usd_per_run") or 0.05)
    ok = bool(cost_row.get("within_budget", cost_row.get("total_usd", 0) <= max_run))
    return {
        "ok": ok,
        "total_usd": cost_row.get("total_usd", 0),
        "max_usd_per_run": max_run,
        "blocker_reason": None if ok else "max_cost_exceeded",
    }
