#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHONPATH_VALUE="packages/types:packages/config:packages/sdk:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance"

echo "=== deploy-copilot-template ==="

# 1. Validate policy pack loads
PYTHONPATH="$PYTHONPATH_VALUE" python3 -c "
from noetfield_governance.policy_loader import load_policy_pack
pack = load_policy_pack('copilot-governance-v1')
assert 'copilot-governance-v1' in pack.version
print('OK  policy pack copilot-governance-v1')
"

# 2. Validate governance-as-code sample
PYTHONPATH="$PYTHONPATH_VALUE" python3 -c "
from pathlib import Path
from noetfield_governance.governance_config import load_governance_config
cfg = load_governance_config(Path('docs/spec/samples/governance-copilot-v1.yaml'))
assert cfg.policy_pack_id == 'copilot-governance-v1'
print('OK  governance-copilot-v1.yaml')
"

# 3. Run phase35 demo
make phase35-demo

# 4. Validate template registry
python3 -c "
import json
reg = json.load(open('packages/templates/REGISTRY.json'))
ids = [t['template_id'] for t in reg['templates']]
assert 'copilot-governance' in ids
print('OK  packages/templates/REGISTRY.json')
"

echo "Copilot Governance Template deploy validation PASS"
