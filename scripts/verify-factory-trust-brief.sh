#!/usr/bin/env bash
# verify-factory-trust-brief.sh — Trust Brief / M&A factory live checks
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

YAML="$ROOT/packages/schemas/factories/trust_brief_diligence_v1.yaml"
[[ -f "$YAML" ]] || fail "missing trust_brief_diligence_v1.yaml"

python3 -c "
import json, yaml
from pathlib import Path
root = Path('$ROOT')
meta = yaml.safe_load((root / 'packages/schemas/factories/trust_brief_diligence_v1.yaml').read_text())['metadata']
assert meta['id'] == 'trust_brief_diligence_v1'
assert meta['status'] == 'live'
assert meta.get('alias') == 'M&A Factory'
cat = json.loads((root / 'governance/FACTORY_CATALOG.json').read_text())
entry = next(f for f in cat['factories'] if f['id'] == 'trust_brief_diligence_v1')
assert entry['status'] == 'live'
assert entry.get('route')
nodes = yaml.safe_load((root / 'packages/schemas/factories/trust_brief_diligence_v1.yaml').read_text())['spec']['nodes']
assert len(nodes) == 8
" || fail "trust brief factory spec or catalog invalid"

ok "trust_brief_diligence_v1 YAML and catalog live"

grep -q "trust_brief_diligence_v1" services/governance/noetfield_governance/api.py || fail "API missing trust brief factory"
grep -q "TrustBriefDiligenceRuntime" services/governance/noetfield_governance/api.py || fail "API missing trust brief runtime"
grep -q '"/catalog/platform"' services/governance/noetfield_governance/api.py || fail "API missing /catalog/platform"
[[ -f platform/factories/index.html ]] || fail "missing platform/factories/index.html"

ok "API and platform console present"

PYTHONPATH=packages/types:packages/config:packages/sdk:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance:services/factories:services/trust-brief:services/legal-review:services/aml-trace \
  python3 -c "from noetfield_trust_brief import TrustBriefDiligenceRuntime; from noetfield_factories import TrustBriefFactoryRunner" \
  || fail "trust brief packages import failed"

ok "trust brief packages import"

echo ""
echo "verify-factory-trust-brief: all checks passed"
