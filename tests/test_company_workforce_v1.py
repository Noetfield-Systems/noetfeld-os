from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.validate_company_workforce_v1 import (
    REGISTRY_PATH,
    SCHEMA_PATH,
    load_json,
    validate_registry,
)


def _documents() -> tuple[dict, dict]:
    return load_json(REGISTRY_PATH), load_json(SCHEMA_PATH)


def test_company_workforce_registry_passes_schema_and_invariants() -> None:
    registry, schema = _documents()
    assert validate_registry(registry, schema) == []
    assert len(registry["roles"]) == 8


def test_duplicate_role_ids_fail() -> None:
    registry, schema = _documents()
    altered = copy.deepcopy(registry)
    altered["roles"][1]["role_id"] = altered["roles"][0]["role_id"]
    errors = validate_registry(altered, schema)
    assert any("unique" in error for error in errors)


def test_digital_role_cannot_receive_a4() -> None:
    registry, schema = _documents()
    altered = copy.deepcopy(registry)
    altered["roles"][0]["max_authority"] = "A4"
    errors = validate_registry(altered, schema)
    assert errors
    assert any("A4" in error for error in errors)


def test_unwired_role_cannot_claim_runtime_binding() -> None:
    registry, schema = _documents()
    altered = copy.deepcopy(registry)
    altered["roles"][6]["activation"]["runtime_bindings"] = [
        {"reference": "hypothetical/worker", "maturity": "existing"}
    ]
    errors = validate_registry(altered, schema)
    assert any("not_wired" in error for error in errors)


def test_mapped_role_requires_runtime_evidence_reference() -> None:
    registry, schema = _documents()
    altered = copy.deepcopy(registry)
    altered["roles"][0]["activation"]["runtime_bindings"] = []
    errors = validate_registry(altered, schema)
    assert any("runtime binding" in error for error in errors)


def test_finance_role_forbids_money_movement() -> None:
    registry, schema = _documents()
    altered = copy.deepcopy(registry)
    altered["roles"][7]["forbidden_actions"] = ["Prepare monthly summary"]
    errors = validate_registry(altered, schema)
    assert any("money movement" in error for error in errors)
