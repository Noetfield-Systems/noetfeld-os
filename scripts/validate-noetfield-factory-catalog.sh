#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0
fail() { echo "FAIL: $*" >&2; FAIL=1; }

[[ -f os/plan-library/noetfield-factory-catalog/REGISTRY.json ]] || fail "missing REGISTRY"
[[ -f os/plan-library/noetfield-factory-catalog/specs/noetfield-governance-factory-v1.json ]] || fail "missing spec"
[[ -f scripts/emit-governance-receipt.py ]] || fail "missing emit script"
[[ -f factory/index.html ]] || fail "missing /factory/"
[[ -f os/plan-library/FACTORY_CAMPUS_BLUEPRINT_LOCKED_v1.md ]] || fail "missing blueprint"

python3 - <<'PY' || fail "schema"
import json
from pathlib import Path
reg = json.loads(Path("os/plan-library/noetfield-factory-catalog/REGISTRY.json").read_text())
spec = json.loads(Path("os/plan-library/noetfield-factory-catalog/specs/noetfield-governance-factory-v1.json").read_text())
assert reg["schema"] == "noetfield-factory-catalog-v1"
assert spec["demo_seconds"] == 30
assert spec["governance"]["delivery_mode"] == "mock_only"
print("OK: noetfield catalog schema")
PY

[[ "$FAIL" -eq 0 ]] || exit 1
echo "OK: validate-noetfield-factory-catalog"
