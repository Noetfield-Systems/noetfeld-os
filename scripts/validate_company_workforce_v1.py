#!/usr/bin/env python3
"""Validate the Noetfield company workforce registry and authority invariants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "noetfield-org" / "COMPANY_WORKFORCE_REGISTRY_v1.json"
SCHEMA_PATH = ROOT / "schemas" / "noetfield-company-workforce-v1.schema.json"
EXPECTED_ROLE_IDS = {f"N-{number:02d}" for number in range(1, 9)}
DIGITAL_MAX_AUTHORITY = "A3"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Required file not found: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def validate_registry(registry: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Return all schema and cross-field invariant violations."""
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = [
        f"{'/'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
        for error in validator.iter_errors(registry)
    ]
    if errors:
        return sorted(errors)

    role_ids = [role["role_id"] for role in registry["roles"]]
    if len(role_ids) != len(set(role_ids)):
        errors.append("roles: role_id values must be unique")
    if set(role_ids) != EXPECTED_ROLE_IDS:
        errors.append(
            "roles: expected exactly N-01 through N-08; "
            f"found {', '.join(sorted(role_ids))}"
        )

    if registry["authority_model"]["digital_worker_maximum"] != DIGITAL_MAX_AUTHORITY:
        errors.append("authority_model: digital worker maximum must remain A3")

    for role in registry["roles"]:
        role_id = role["role_id"]
        if role["max_authority"] == "A4":
            errors.append(f"{role_id}: digital roles cannot hold A4")
        if not role["human_approval_required_for"]:
            errors.append(f"{role_id}: high-impact actions must have human approval gates")
        if role["activation"]["status"] == "mapped_existing" and not role["activation"]["runtime_bindings"]:
            errors.append(f"{role_id}: mapped_existing requires at least one runtime binding")
        if role["activation"]["status"] == "not_wired" and role["activation"]["runtime_bindings"]:
            errors.append(f"{role_id}: not_wired roles cannot claim runtime bindings")
        for binding in role["activation"]["runtime_bindings"]:
            if binding["maturity"] == "not_connected" and role["activation"]["status"] == "mapped_existing":
                errors.append(
                    f"{role_id}: mapped_existing cannot contain a not_connected runtime binding"
                )

    required_human_gates = [
        "External sends, public publishing, contracts, legal filings, money movement, "
        "production deployment, protected-branch merge, and policy or verifier changes "
        "require human approval."
    ]
    # The canonical registry expresses these controls across global rules and role-level gates.
    rules = " ".join(registry["authority_model"]["rules"]).lower()
    for token in ("human approval", "delegation", "a4", "fail"):
        if token not in rules:
            errors.append(f"authority_model.rules: missing required invariant token '{token}'")

    if registry["founder"]["principal_id"] != "H-001":
        errors.append("founder: principal_id must remain H-001")
    if registry["founder"]["worker_type"] != "human":
        errors.append("founder: Founder must remain a human principal")

    # No autonomous role may silently grant public or financial powers.
    for role in registry["roles"]:
        forbidden = " ".join(role["forbidden_actions"]).lower()
        required = " ".join(role["human_approval_required_for"]).lower()
        if "send" in " ".join(role["autonomous_actions"]).lower() and "send" not in required:
            errors.append(f"{role['role_id']}: autonomous send capability lacks a matching human gate")
        if role["role_id"] == "N-08" and not any(
            word in forbidden for word in ("transfer", "money", "bank")
        ):
            errors.append("N-08: finance role must explicitly forbid money movement")

    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    try:
        registry = load_json(REGISTRY_PATH)
        schema = load_json(SCHEMA_PATH)
        errors = validate_registry(registry, schema)
    except (ValueError, TypeError) as exc:
        errors = [str(exc)]

    result = {
        "schema": "noetfield-company-workforce-validation-v1",
        "ok": not errors,
        "registry": str(REGISTRY_PATH.relative_to(ROOT)),
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "role_count": len(registry.get("roles", [])) if "registry" in locals() else 0,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    elif errors:
        print("COMPANY WORKFORCE VALIDATION: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"COMPANY WORKFORCE VALIDATION: PASS ({result['role_count']} roles)")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
