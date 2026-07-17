#!/usr/bin/env python3
"""Motor registry validator v1.2 — fail-closed invariant enforcement.

v1.0 validated structure and one cross-field rule. v1.1 added the documented
invariants. v1.2 closes the fail-closed gaps an adversarial red-team found in
v1.1: whitespace/zero-width evidence bypassed minLength; the promotion/outcome
splits were skippable by OMITTING the sub-objects; states.evidence was never
checked at RECEIPT_COMPLETE; a trailing newline slipped past the date-time
format check and a lowercase 'z' silently defeated timestamp ordering; a
41-char production_sha passed the `$`-anchored regex. Each is now closed and
carries a regression test.

Enforced invariants
  Schema (schema/*.json, via jsonschema + strict date-time FormatChecker):
    I1  state PROVEN|FAILED           -> evidence_ref required
    I2  state BLOCKED|FAILED|DIVERGED|UNPROVEN -> reason required
    I3  every date-time strict RFC3339 (no surrounding/embedded whitespace, no trailing newline)
  Cross-file / semantic (this module):
    M   evidence_ref / reason must be MEANINGFUL (non-blank after stripping unicode + zero-width)
    R1  job.recipe_id exists;  I4 recipe_version == recipe.version
    R2  outcome PROVEN -> promotion PROVEN
    I5a promotion PROVEN -> source PROVEN & runtime PROVEN/NA; on external recipes the split is REQUIRED (not omittable)
    I5b outcome PROVEN -> observation PROVEN & attribution PROVEN; on external recipes the split is REQUIRED
    I6  external_proof_required -> recipe has an external check; verification PROVEN needs a PASS row; outcome PROVEN needs a PASS external row whose check name is recipe-declared
    I7  production_sha set iff runtime PROVEN, exact 40-hex (fullmatch); candidate_sha hex[7..40] when execution PROVEN
    I8  timestamp ordering (lowercase 'z' handled); outcome_observed >= promoted+60s for external recipes
    I9  RECEIPT_COMPLETE: dispatch/execution/verification/evidence/promotion PROVEN; authority PROVEN/NA; outcome PROVEN (never NA on external recipes); cost.metered; receipt_hash hashlike; recipe receipt.required_fields non-blank; required timestamps present+ordered
    B   cost.total_usd <= recipe budgets.cost_usd unless BLOCKED_WITH_REASON (L11)
    T   job trigger.type == recipe trigger.type
    U   job_id and idempotency_key unique across all job files
  Recipe-side (check_recipe_semantics):
    RC1 trigger.type schedule->schedule_cron, event->event_source
    RC2 failure_policy.repair_scope must not include verifier paths (L5)
    RC3 receipt.required_fields entries are non-blank dotted paths
    RC4 external_proof_required -> >=1 external check

Exit 0 = all valid. Exit 1 = any failure. Importable: validate_all(root).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import unicodedata
from datetime import datetime, timezone
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

FULL_SHA = re.compile(r"[0-9a-f]{40}")
SHORT_SHA = re.compile(r"[0-9a-fA-F]{7,40}")
HASHLIKE = re.compile(r"(sha256:)?[0-9a-fA-F]{16,}")
VERIFIER_MARKERS = ("scripts/verify_", "noetfield_gate/", "verifier", "freshness_threshold")


def _meaningful(v: Any) -> bool:
    """True if v carries at least one VISIBLE character. Category-based, not a
    denylist: after NFKC normalization, require >=1 letter or number. This
    rejects strings made only of whitespace, control (Cc), format (Cf, e.g.
    U+00AD soft hyphen / U+2061-2064 / U+200B), separator (Z*), or combining
    marks (Mn) \u2014 the whole invisible-character class, not just an enumerated
    few. A real evidence_ref/reason always contains alphanumerics."""
    if not isinstance(v, str):
        return v is not None
    return any(unicodedata.category(ch)[0] in ("L", "N") for ch in unicodedata.normalize("NFKC", v))


def _strict_dt(raw: Any) -> datetime | None:
    """Parse a strict RFC3339 date-time. Rejects surrounding/embedded
    whitespace, trailing newlines, and date-only strings (which fromisoformat
    accepts); accepts lowercase 'z' per RFC3339."""
    if not isinstance(raw, str):
        return None
    if raw != raw.strip() or any(c in raw for c in " \t\n\r"):
        return None
    if "T" not in raw and "t" not in raw:  # RFC3339 date-time requires a time component
        return None
    s = re.sub(r"[Zz]$", "+00:00", raw)
    try:
        dt = datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:  # RFC3339 date-time requires an offset (Z or +hh:mm)
        return None
    return dt


def _strict_format_checker() -> FormatChecker:
    fc = FormatChecker()

    @fc.checks("date-time", raises=(ValueError,))
    def _dt(value: Any) -> bool:  # noqa: ANN001
        if not isinstance(value, str):
            return True  # type handled by schema
        return _strict_dt(value) is not None

    return fc


def _get_path(obj: Any, dotted: str) -> Any:
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def build_validators(root: pathlib.Path) -> tuple[Draft202012Validator, Draft202012Validator]:
    recipe_schema = json.loads((root / "schema/recipe.schema.json").read_text())
    job_schema = json.loads((root / "schema/job.schema.json").read_text())
    Draft202012Validator.check_schema(recipe_schema)
    Draft202012Validator.check_schema(job_schema)
    fc = _strict_format_checker()
    return (
        Draft202012Validator(recipe_schema, format_checker=fc),
        Draft202012Validator(job_schema, format_checker=fc),
    )


def schema_errors(instance: dict[str, Any], validator: Draft202012Validator, label: str) -> list[str]:
    out = []
    for e in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        path = "/".join(str(p) for p in e.path) or "<root>"
        out.append(f"{label}: {path}: {e.message}")
    return out


def _state(container: dict[str, Any], field: str) -> str:
    return str((container.get(field) or {}).get("state") or "")


def _walk_state_fields(states: dict[str, Any]):
    """Yield (path, obj) for every state field and nested sub-state."""
    for name, obj in (states or {}).items():
        if not isinstance(obj, dict):
            continue
        yield name, obj
        for sub in ("source", "runtime", "observation", "attribution"):
            if isinstance(obj.get(sub), dict):
                yield f"{name}.{sub}", obj[sub]


def check_state_meaning(states: dict[str, Any], label: str) -> list[str]:
    """M: evidence_ref/reason must be meaningful for the states that require them."""
    f: list[str] = []
    for path, obj in _walk_state_fields(states):
        st = str(obj.get("state") or "")
        if st in {"PROVEN", "FAILED"} and not _meaningful(obj.get("evidence_ref")):
            f.append(f"{label}: states.{path}.evidence_ref is blank/whitespace/zero-width for state {st} (M/I1)")
        if st in {"BLOCKED", "FAILED", "DIVERGED", "UNPROVEN"} and not _meaningful(obj.get("reason")):
            f.append(f"{label}: states.{path}.reason is blank/whitespace/zero-width for state {st} (M/I2)")
    return f


def check_recipe_semantics(recipe: dict[str, Any], label: str) -> list[str]:
    f: list[str] = []
    trig = recipe.get("trigger") or {}
    # RC1 — "iff" both directions: required when the type matches, and
    # forbidden (dangling) when it does not.
    if trig.get("type") == "schedule" and not _meaningful(trig.get("schedule_cron")):
        f.append(f"{label}: trigger.type=schedule requires schedule_cron (RC1)")
    if trig.get("type") != "schedule" and _meaningful(trig.get("schedule_cron")):
        f.append(f"{label}: schedule_cron present but trigger.type is {trig.get('type')} (RC1)")
    if trig.get("type") == "event" and not _meaningful(trig.get("event_source")):
        f.append(f"{label}: trigger.type=event requires event_source (RC1)")
    if trig.get("type") != "event" and _meaningful(trig.get("event_source")):
        f.append(f"{label}: event_source present but trigger.type is {trig.get('type')} (RC1)")
    for scope in ((recipe.get("failure_policy") or {}).get("repair_scope") or []):
        if any(m in str(scope) for m in VERIFIER_MARKERS):
            f.append(f"{label}: failure_policy.repair_scope includes a verifier path '{scope}' (RC2/L5)")
    for rf in ((recipe.get("receipt") or {}).get("required_fields") or []):
        if not _meaningful(rf):
            f.append(f"{label}: receipt.required_fields has a blank entry (RC3)")
    ver = recipe.get("verification") or {}
    if ver.get("external_proof_required") and not [c for c in (ver.get("checks") or []) if c.get("external")]:
        f.append(f"{label}: external_proof_required but no external:true check (RC4/I6)")
    return f


def check_job_semantics(job: dict[str, Any], recipes: dict[str, dict[str, Any]], label: str) -> list[str]:
    f: list[str] = []
    states = job.get("states") or {}
    f += check_state_meaning(states, label)

    recipe = recipes.get(job.get("recipe_id"))
    if recipe is None:
        f.append(f"{label}: recipe_id {job.get('recipe_id')} not found in recipes/ (R1)")
        return f
    if str(job.get("recipe_version")) != str(recipe.get("version")):
        f.append(f"{label}: recipe_version {job.get('recipe_version')} != recipe {recipe.get('version')} (I4)")

    ext_required = bool((recipe.get("verification") or {}).get("external_proof_required"))
    promotion = states.get("promotion") or {}
    outcome = states.get("outcome") or {}
    prom_state, out_state = _state(states, "promotion"), _state(states, "outcome")
    src, rt = (promotion.get("source") or {}).get("state"), (promotion.get("runtime") or {}).get("state")
    obs, attr = (outcome.get("observation") or {}).get("state"), (outcome.get("attribution") or {}).get("state")

    # R2
    if out_state == "PROVEN" and prom_state != "PROVEN":
        f.append(f"{label}: outcome PROVEN while promotion is {prom_state or 'unset'} (R2)")

    # I5a — split required (not omittable) on external recipes
    if prom_state == "PROVEN":
        if ext_required and (promotion.get("source") is None or promotion.get("runtime") is None):
            f.append(f"{label}: promotion PROVEN on external recipe must carry source AND runtime sub-states (I5a)")
        elif src is not None or rt is not None:
            need_rt = {"PROVEN"} if ext_required else {"PROVEN", "NOT_APPLICABLE"}
            if src != "PROVEN" or rt not in need_rt:
                f.append(f"{label}: promotion PROVEN but source={src} runtime={rt} (I5a)")

    # I5b
    if out_state == "PROVEN":
        if ext_required and (outcome.get("observation") is None or outcome.get("attribution") is None):
            f.append(f"{label}: outcome PROVEN on external recipe must carry observation AND attribution sub-states (I5b)")
        elif obs is not None or attr is not None:
            if obs != "PROVEN" or attr != "PROVEN":
                f.append(f"{label}: outcome PROVEN but observation={obs} attribution={attr} (I5b)")

    # I6 — verification tied to results; external names recipe-declared
    recipe_check_names = {c.get("name") for c in ((recipe.get("verification") or {}).get("checks") or [])}
    vrs = job.get("verification_results") or []
    if _state(states, "verification") == "PROVEN":
        if not [v for v in vrs if v.get("decision") == "PASS"]:
            f.append(f"{label}: verification PROVEN but no verification_result with decision PASS (I6)")
    if ext_required and out_state == "PROVEN":
        ext_pass = [v for v in vrs if v.get("external") and v.get("decision") == "PASS"]
        if not ext_pass:
            f.append(f"{label}: outcome PROVEN but no external PASS verification_result (I6)")
        elif recipe_check_names and not any(v.get("check") in recipe_check_names for v in ext_pass):
            f.append(f"{label}: external PASS check name not declared by recipe verification.checks (I6)")

    # I7 — artifact identity
    artifacts = job.get("artifacts") or {}
    prod_sha = str(artifacts.get("production_sha") or "")
    cand_sha = str(artifacts.get("candidate_sha") or "")
    runtime_proven = rt == "PROVEN" or (rt is None and prom_state == "PROVEN")
    if prod_sha and not FULL_SHA.fullmatch(prod_sha):
        f.append(f"{label}: production_sha is not exactly 40 lowercase hex (I7)")
    if prod_sha and not runtime_proven:
        f.append(f"{label}: production_sha set but promotion runtime not PROVEN (I7)")
    if runtime_proven and not _meaningful(prod_sha):
        f.append(f"{label}: promotion runtime PROVEN but production_sha empty (I7)")
    if _state(states, "execution") == "PROVEN":
        if not _meaningful(cand_sha):
            f.append(f"{label}: execution PROVEN but candidate_sha empty (I7)")
        elif not SHORT_SHA.fullmatch(cand_sha):
            f.append(f"{label}: execution PROVEN but candidate_sha '{cand_sha}' is not 7-40 hex (I7)")

    # I8 — timestamp ordering. Enforce monotonicity over ALL present stages in
    # canonical order (not just adjacent pairs) so omitting an intermediate
    # stage cannot let created_at land after promoted_at.
    ts = job.get("timestamps") or {}
    chain = [
        ("created_at", _strict_dt(ts.get("created_at"))),
        ("executing_at", _strict_dt(ts.get("executing_at"))),
        ("verified_at", _strict_dt(ts.get("verified_at"))),
        ("promoted_at", _strict_dt(ts.get("promoted_at"))),
        ("outcome_observed_at", _strict_dt(ts.get("outcome_observed_at"))),
    ]
    present = [(n, d) for n, d in chain if d is not None]
    for (n1, d1), (n2, d2) in zip(present, present[1:]):
        if d2 < d1:
            f.append(f"{label}: {n2} < {n1} (I8)")
    created = _strict_dt(ts.get("created_at"))
    promoted = _strict_dt(ts.get("promoted_at"))
    observed = _strict_dt(ts.get("outcome_observed_at"))
    approved = _strict_dt((job.get("approval") or {}).get("approved_at"))
    if approved and promoted and promoted < approved:
        f.append(f"{label}: promoted_at < approved_at (I8)")
    if ext_required and promoted and observed and (observed - promoted).total_seconds() < 60:
        f.append(f"{label}: outcome_observed_at <60s after promoted_at on external recipe (I8)")

    # recovery causation (docs: self-healing PROVEN only by a before/after
    # external check pair — correlation is not causality). recovery PROVEN
    # requires an external PASS verification_result.
    if _state(states, "recovery") == "PROVEN":
        if not [v for v in (job.get("verification_results") or []) if v.get("external") and v.get("decision") == "PASS"]:
            f.append(f"{label}: states.recovery PROVEN but no external PASS verification_result (before/after pair) (recovery)")

    # B — budget cap (L11)
    budget = (recipe.get("budgets") or {}).get("cost_usd")
    total = (job.get("cost") or {}).get("total_usd")
    if isinstance(budget, (int, float)) and isinstance(total, (int, float)):
        if total > budget and job.get("lifecycle_status") != "BLOCKED_WITH_REASON":
            f.append(f"{label}: cost.total_usd {total} > recipe budget {budget} but not BLOCKED_WITH_REASON (B/L11)")

    # T — trigger type match
    if (job.get("trigger") or {}).get("type") != (recipe.get("trigger") or {}).get("type"):
        f.append(f"{label}: trigger.type {(job.get('trigger') or {}).get('type')} != recipe {(recipe.get('trigger') or {}).get('type')} (T)")

    # I9 — RECEIPT_COMPLETE cannot be asserted over incomplete truth
    if job.get("lifecycle_status") == "RECEIPT_COMPLETE":
        for fld in ("dispatch", "execution", "verification", "evidence"):
            if _state(states, fld) != "PROVEN":
                f.append(f"{label}: RECEIPT_COMPLETE but states.{fld} is {_state(states, fld) or 'unset'} (I9)")
        if _state(states, "authority") not in {"PROVEN", "NOT_APPLICABLE"}:
            f.append(f"{label}: RECEIPT_COMPLETE but states.authority is {_state(states, 'authority') or 'unset'} (I9)")
        if prom_state != "PROVEN":
            f.append(f"{label}: RECEIPT_COMPLETE but states.promotion is {prom_state or 'unset'} (I9)")
        if ext_required and out_state != "PROVEN":
            f.append(f"{label}: RECEIPT_COMPLETE on external recipe but states.outcome is {out_state or 'unset'} (not PROVEN) (I9)")
        if not ext_required and out_state not in {"PROVEN", "NOT_APPLICABLE"}:
            f.append(f"{label}: RECEIPT_COMPLETE but states.outcome is {out_state or 'unset'} (I9)")
        cost = job.get("cost") or {}
        if not cost.get("metered"):
            f.append(f"{label}: RECEIPT_COMPLETE but cost.metered not true (placeholder cost, I9/L11)")
        rh = job.get("receipt_hash")
        if not _meaningful(rh) or not HASHLIKE.fullmatch(str(rh)):
            f.append(f"{label}: RECEIPT_COMPLETE but receipt_hash is missing/not hash-like (I9)")
        for rf in ((recipe.get("receipt") or {}).get("required_fields") or []):
            if not _meaningful(rf) or not _meaningful(_get_path(job, rf)):
                f.append(f"{label}: RECEIPT_COMPLETE but recipe-required field '{rf}' empty/absent (I9)")
        if ext_required:
            for req_ts, name in ((created, "created_at"), (promoted, "promoted_at"), (observed, "outcome_observed_at")):
                if req_ts is None:
                    f.append(f"{label}: RECEIPT_COMPLETE on external recipe requires timestamps.{name} (I9/I8)")

    return f


def validate_all(root: pathlib.Path) -> tuple[list[str], dict[str, int]]:
    rv, jv = build_validators(root)
    failures: list[str] = []
    recipes: dict[str, dict[str, Any]] = {}

    for fp in sorted((root / "recipes").glob("*.yaml")):
        data = yaml.safe_load(fp.read_text())
        errs = schema_errors(data, rv, fp.name)
        failures += errs
        if not errs:
            failures += check_recipe_semantics(data, fp.name)
            recipes[data["recipe_id"]] = data

    seen_job_ids: dict[str, str] = {}
    seen_keys: dict[str, str] = {}
    n_jobs = 0
    for fp in sorted((root / "jobs").glob("*.json")):
        n_jobs += 1
        data = json.loads(fp.read_text())
        errs = schema_errors(data, jv, fp.name)
        failures += errs
        # U — uniqueness across files
        jid = data.get("job_id")
        if jid in seen_job_ids:
            failures.append(f"{fp.name}: duplicate job_id {jid} (also in {seen_job_ids[jid]}) (U)")
        elif jid:
            seen_job_ids[jid] = fp.name
        key = data.get("idempotency_key")
        if key and key in seen_keys:
            failures.append(f"{fp.name}: duplicate idempotency_key (also in {seen_keys[key]}) (U/L13)")
        elif key:
            seen_keys[key] = fp.name
        if not errs:
            failures += check_job_semantics(data, recipes, fp.name)

    return failures, {"recipes": len(recipes), "jobs": n_jobs}


def main() -> int:
    root = pathlib.Path(__file__).parent
    failures, counts = validate_all(root)
    print(f"recipes: {counts['recipes']}  jobs: {counts['jobs']}")
    if failures:
        print("\nFAILURES:")
        for m in failures:
            print(" -", m)
        return 1
    print("\nAll artifacts valid (v1.2 fail-closed invariants enforced).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
