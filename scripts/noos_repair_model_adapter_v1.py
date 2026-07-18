#!/usr/bin/env python3
"""NOOS repair model adapter v1 (NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §8).

Provider-neutral repair proposer. Two strategies, both recorded identically:

  * ``deterministic-local`` — the offline, test-verified mutation-search engine
    (noos_repair_engine_v1). Honest, real, and NOT a hosted model.
  * a hosted OpenAI-compatible provider (DeepSeek / Kimi/Moonshot / any
    OPENAI_BASE_URL-compatible endpoint) — used only when a provider API key is
    present in the environment. The call is real (urllib), low-temperature,
    schema-validated, bounded by a per-call timeout and retries.

Every model call records: provider, model, purpose, input_hash, output_hash,
token counts (when available), measured/estimated cost, latency, timeout, retry
count, schema-validation result. Model output is an UNTRUSTED proposal — only
tests prove the repair (the runner re-runs them).

No provider secret exists in any sanctioned environment today, so the runner uses
``deterministic-local``. The hosted path is complete and the exact secret-injection
action is documented in docs/product; it is never faked.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_repair_engine_v1 as engine  # noqa: E402

# Provider env-var contract (values NEVER read into logs/receipts).
# github_models is the SANCTIONED default: it uses the GitHub Actions GITHUB_TOKEN
# (permissions: models: read) — no separate provider secret required. It is
# OpenAI-compatible, so it reuses _hosted().
PROVIDER_ENV = {
    "github_models": {"key": "GITHUB_TOKEN", "base": os.environ.get("GITHUB_MODELS_BASE", "https://models.github.ai/inference"), "model": os.environ.get("GITHUB_MODELS_MODEL", "openai/gpt-4o-mini")},
    "deepseek": {"key": "DEEPSEEK_API_KEY", "base": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "moonshot": {"key": "MOONSHOT_API_KEY", "base": "https://api.moonshot.cn/v1", "model": "moonshot-v1-8k"},
    "openai_compatible": {"key": "OPENAI_API_KEY", "base": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"), "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini")},
}
# github_models first — the sanctioned zero-extra-secret path.
DEFAULT_PROVIDER_ORDER = ["github_models", "deepseek", "moonshot", "openai_compatible"]


def _hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def configured_provider() -> str | None:
    """Return the first provider whose API key env var is set, else None."""
    for name in DEFAULT_PROVIDER_ORDER:
        if os.environ.get(PROVIDER_ENV[name]["key"]):
            return name
    return None


def _new_model_call(provider: str, model: str, purpose: str) -> dict[str, Any]:
    return {
        "provider": provider, "model": model, "purpose": purpose,
        "input_hash": None, "output_hash": None,
        "prompt_tokens": None, "completion_tokens": None,
        "cost_usd": None, "latency_ms": None, "timeout_s": None,
        "retries": 0, "schema_valid": None, "ok": False,
    }


def propose_repair(
    *,
    repo_dir: Path,
    test_cmd: list[str],
    allowed_files: list[str],
    failure_output: str,
    recipe: dict[str, Any],
    prefer: str = "auto",
    timeout: int = 120,
) -> dict[str, Any]:
    """Produce a VERIFIED repair proposal + a model-call record.

    ``prefer`` = 'auto' (hosted if key else deterministic), 'deterministic-local',
    or a provider name. Returns {ok, strategy, patch, file, tests_before,
    tests_after, model_call}."""
    provider = None
    if prefer in PROVIDER_ENV:
        provider = prefer if os.environ.get(PROVIDER_ENV[prefer]["key"]) else None
    elif prefer == "auto":
        provider = configured_provider()

    if provider is None:
        return _deterministic(repo_dir, test_cmd, allowed_files, recipe, timeout)
    hosted = _hosted(provider, repo_dir, test_cmd, allowed_files, failure_output, recipe, timeout)
    if hosted.get("ok"):
        return hosted
    # DETERMINISTIC FALLBACK: the hosted provider was unavailable (e.g. a CI
    # GITHUB_TOKEN without models:read -> 403), returned an invalid/forbidden
    # proposal, or its patch failed the tests. The deterministic-local engine is a
    # valid fallback candidate generator (never described as a hosted AI call).
    # Both model-call records are preserved for the receipt.
    if prefer in PROVIDER_ENV:
        # An explicit provider was requested; still fall back so a repair can land.
        pass
    fb = _deterministic(repo_dir, test_cmd, allowed_files, recipe, timeout)
    fb["hosted_attempt"] = {"provider": provider, "reason": hosted.get("reason"), "model_call": hosted.get("model_call")}
    fb["fell_back_from_hosted"] = True
    return fb


def _deterministic(repo_dir, test_cmd, allowed_files, recipe, timeout) -> dict[str, Any]:
    mc = _new_model_call("deterministic-local", "fault-localized-mutation-search", "repair_proposal")
    t0 = time.monotonic()
    max_c = 200
    res = engine.propose_and_verify_repair(
        repo_dir=repo_dir, test_cmd=test_cmd, allowed_files=allowed_files,
        max_candidates=max_c, timeout=timeout,
    )
    mc.update({
        "latency_ms": int((time.monotonic() - t0) * 1000),
        "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0,
        "schema_valid": True, "ok": bool(res.get("repaired")),
        "candidates_tried": res.get("candidates_tried"),
    })
    return {
        "ok": bool(res.get("repaired")),
        "strategy": "deterministic-local",
        "patch": res.get("patch"),
        "file": res.get("file"),
        "tests_before": res.get("tests_before"),
        "tests_after": res.get("tests_after"),
        "reason": res.get("reason"),
        "model_call": mc,
    }


_REPAIR_SCHEMA_HINT = (
    'Return ONLY JSON: {"file": "<relative path within allowed paths>", '
    '"new_content": "<complete corrected file content>"}. No prose.'
)


def _hosted(provider, repo_dir, test_cmd, allowed_files, failure_output, recipe, timeout) -> dict[str, Any]:
    cfg = PROVIDER_ENV[provider]
    model = cfg["model"]
    mc = _new_model_call(provider, model, "repair_proposal")
    per_call_timeout = int(recipe.get("limits", {}).get("per_model_call_timeout_seconds", 60))
    mc["timeout_s"] = per_call_timeout

    # Build a bounded prompt from the failure + the first allowed source file.
    target_rel = allowed_files[0]
    target = (repo_dir / target_rel)
    source = target.read_text(encoding="utf-8")[:8000] if target.is_file() else ""
    user = (
        f"A test/lint command failed. Fix the bug in the source file WITHOUT changing tests.\n"
        f"Failure output:\n{failure_output[:3000]}\n\n"
        f"File `{target_rel}`:\n```\n{source}\n```\n{_REPAIR_SCHEMA_HINT}"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise software-repair engine. Output strict JSON only."},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "max_tokens": 1500,
        "response_format": {"type": "json_object"},
    }
    mc["input_hash"] = _hash(payload)
    key = os.environ[cfg["key"]]  # value used only for the Authorization header
    max_retries = 2
    t0 = time.monotonic()
    text = None
    for attempt in range(max_retries + 1):
        mc["retries"] = attempt
        try:
            req = urllib.request.Request(
                f"{cfg['base']}/chat/completions",
                data=json.dumps(payload).encode(),
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=per_call_timeout) as resp:
                body = json.loads(resp.read().decode())
            text = body["choices"][0]["message"]["content"]
            usage = body.get("usage", {})
            mc["prompt_tokens"] = usage.get("prompt_tokens")
            mc["completion_tokens"] = usage.get("completion_tokens")
            break
        except Exception as exc:  # network/provider error -> bounded retry
            mc["error"] = str(exc)[:200]
            if attempt == max_retries:
                mc["latency_ms"] = int((time.monotonic() - t0) * 1000)
                return {"ok": False, "strategy": f"hosted:{provider}", "reason": "provider_call_failed", "model_call": mc}
    mc["latency_ms"] = int((time.monotonic() - t0) * 1000)

    # Validate the structured response, apply, and VERIFY with real tests.
    try:
        proposal = json.loads(text)
        assert isinstance(proposal.get("file"), str) and isinstance(proposal.get("new_content"), str)
        mc["schema_valid"] = True
    except (json.JSONDecodeError, AssertionError):
        mc["schema_valid"] = False
        return {"ok": False, "strategy": f"hosted:{provider}", "reason": "schema_invalid", "model_call": mc}
    mc["output_hash"] = _hash(proposal)

    rel = proposal["file"]
    if rel not in allowed_files:
        return {"ok": False, "strategy": f"hosted:{provider}", "reason": "proposed_forbidden_path", "model_call": mc}
    before = engine.run_tests(repo_dir, test_cmd, timeout=timeout)
    ok, after = engine._try_candidate(repo_dir, (repo_dir / rel).resolve(), proposal["new_content"], test_cmd, timeout)
    mc["ok"] = ok
    patch = engine._unified_diff(repo_dir, (repo_dir / rel).resolve(),
                                 (repo_dir / rel).read_text(encoding="utf-8"), proposal["new_content"]) if ok else None
    # cost estimate (rough, provider-published rates vary; recorded as estimate)
    if mc["prompt_tokens"] and mc["completion_tokens"]:
        mc["cost_usd"] = round((mc["prompt_tokens"] * 0.14 + mc["completion_tokens"] * 0.28) / 1_000_000, 6)
    return {
        "ok": ok, "strategy": f"hosted:{provider}", "patch": patch,
        "file": rel if ok else None, "tests_before": before, "tests_after": after if ok else None,
        "reason": None if ok else "model_patch_failed_tests", "model_call": mc,
    }


def secret_injection_action() -> dict[str, Any]:
    """The exact action a founder runs to enable a real hosted model."""
    return {
        "why": "No model-provider secret exists in any sanctioned environment; the hosted path is complete but idle.",
        "exact_action": "gh secret set DEEPSEEK_API_KEY --repo Noetfield-Systems/noetfeld-OS   # (or MOONSHOT_API_KEY / OPENAI_API_KEY)",
        "then": "the software_repair_ci workflow / runner auto-selects the hosted provider (configured_provider()).",
        "no_value_here": "This tool never stores or prints a key value.",
    }


if __name__ == "__main__":
    print(json.dumps({"configured_provider": configured_provider(), "secret_injection": secret_injection_action()}, indent=2))
