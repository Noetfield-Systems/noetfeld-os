#!/usr/bin/env bash
# verify-factory-catalog.sh — dual registry anti-drift (tier + factory catalog)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

FACTORY_CAT="$ROOT/governance/FACTORY_CATALOG.json"
TIER_CAT="$ROOT/governance/CAPABILITY_TIER_CATALOG.json"
CATALOG_MD="$ROOT/docs/platform/CATALOG.md"

[[ -f "$FACTORY_CAT" ]] || fail "missing governance/FACTORY_CATALOG.json"
[[ -f "$TIER_CAT" ]] || fail "missing governance/CAPABILITY_TIER_CATALOG.json"
[[ -f "$CATALOG_MD" ]] || fail "missing docs/platform/CATALOG.md"

python3 -c "
import json, yaml
from pathlib import Path
root = Path('$ROOT')
factory_cat = json.loads((root / 'governance/FACTORY_CATALOG.json').read_text())
tier_cat = json.loads((root / 'governance/CAPABILITY_TIER_CATALOG.json').read_text())
allowed = set(factory_cat['allowed_gtm_skus'])
blocked = set(factory_cat['blocked_capabilities'])

live = [f for f in factory_cat['factories'] if f.get('status') == 'live']
if len(live) < 1:
    raise SystemExit('no live factories in catalog')
for f in live:
    spec = f.get('spec_path')
    if not spec or not (root / spec).is_file():
        raise SystemExit(f'live factory missing spec: {f[\"id\"]}')
    meta = yaml.safe_load((root / spec).read_text())['metadata']
    if meta.get('id') != f['id']:
        raise SystemExit(f'yaml id mismatch: {f[\"id\"]}')
    if meta.get('status') != 'live':
        raise SystemExit(f'yaml status not live: {f[\"id\"]}')
    cap = meta.get('capability', '')
    for b in blocked:
        if b in cap:
            raise SystemExit(f'live factory has blocked capability: {f[\"id\"]} {cap}')
    route = f.get('route') or ''
    if route and route.split('/')[-2] not in open(root / 'services/governance/noetfield_governance/api.py').read():
        raise SystemExit(f'api missing route for live factory: {f[\"id\"]}')

for tier in tier_cat['tiers']:
    for cap in tier['capabilities']:
        sku = cap.get('gtm_sku')
        if sku and sku not in allowed:
            raise SystemExit(f'invalid gtm_sku in tier catalog: {sku}')
        if cap.get('public_sku') and not sku:
            raise SystemExit(f'public_sku without gtm_sku: {cap[\"id\"]}')

planned_with_spec = [f for f in factory_cat['factories'] if f.get('status') == 'planned' and f.get('spec_path')]
for f in planned_with_spec:
    if not (root / f['spec_path']).is_file():
        raise SystemExit(f'planned factory missing stub yaml: {f[\"id\"]}')
" || fail "catalog JSON validation failed"

ok "FACTORY_CATALOG.json and CAPABILITY_TIER_CATALOG.json valid"

grep -q "verify-factory-catalog" Makefile || fail "Makefile missing verify-factory-catalog"
grep -q "GET /catalog/tiers" docs/LAWS/ROUTING.md || fail "ROUTING missing catalog API"
grep -q "catalog_manifests" governance/LAW_STACK.json || fail "LAW_STACK missing catalog_manifests"

ok "Makefile, ROUTING, LAW_STACK wired"

echo ""
echo "verify-factory-catalog: all checks passed"
