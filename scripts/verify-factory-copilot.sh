#!/usr/bin/env bash
# verify-factory-copilot.sh — AI factory spec, schemas, and runtime smoke
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

FACTORY_YAML="$ROOT/packages/schemas/factories/copilot_governance_readiness_v1.yaml"
INPUT_SCHEMA="$ROOT/packages/schemas/factory_io/copilot_governance_input.schema.json"
OUTPUT_SCHEMA="$ROOT/packages/schemas/factory_io/copilot_governance_output.schema.json"

[[ -f "$FACTORY_YAML" ]] || fail "missing factory YAML spec"
[[ -f "$INPUT_SCHEMA" ]] || fail "missing factory input schema"
[[ -f "$OUTPUT_SCHEMA" ]] || fail "missing factory output schema"

python3 -c "
import json, yaml
from pathlib import Path
root = Path('$ROOT')
spec = yaml.safe_load((root / 'packages/schemas/factories/copilot_governance_readiness_v1.yaml').read_text())
assert spec['metadata']['id'] == 'copilot_governance_readiness_v1'
nodes = spec['spec']['nodes']
assert 5 <= len(nodes) <= 12
for path in [
    'packages/schemas/factory_io/copilot_governance_input.schema.json',
    'packages/schemas/factory_io/copilot_governance_output.schema.json',
]:
    json.loads((root / path).read_text())
" || fail "factory YAML or JSON schemas invalid"

ok "factory YAML and JSON schemas valid"

grep -q "FACTORY_RUN_STARTED" packages/schemas/event_catalog.yaml || fail "event catalog missing FACTORY_RUN_STARTED"
grep -q "FACTORY_NODE_COMPLETED" packages/schemas/event_catalog.yaml || fail "event catalog missing FACTORY_NODE_COMPLETED"
grep -q "FACTORY_RUN_STARTED" services/events/noetfield_events/contracts.py || fail "contracts missing factory events"

ok "factory audit events registered"

grep -q "verify-factory-copilot" Makefile || fail "Makefile missing verify-factory-copilot"
grep -q "services/factories" Makefile || fail "Makefile PYTHONPATH missing factories"
grep -q "/factories/{factory_id}/run" services/governance/noetfield_governance/api.py || fail "API missing factory route"

ok "Makefile and API factory route present"

PYTHONPATH=packages/types:packages/config:packages/sdk:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance:services/factories:services/trust-brief:services/legal-review:services/aml-trace \
  python3 -c "from noetfield_factories import load_factory_spec; load_factory_spec('copilot_governance_readiness_v1')" \
  || fail "factory package import failed"

ok "factory package imports"

echo ""
echo "verify-factory-copilot: all checks passed"
