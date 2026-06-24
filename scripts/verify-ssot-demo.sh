#!/usr/bin/env bash
# Verify SSOT governance demo fixtures, Python runner, and demo API logic.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== verify-ssot-demo ==="

python3 scripts/run_ssot_governance_demo.py --output /tmp/nf-ssot-demo-out.json
python3 -c "
import json, sys
p = json.load(open('/tmp/nf-ssot-demo-out.json'))
assert p['demo'] == 'noetfield-ssot-governance-vertical'
assert p['ssot_event']['invalidated_count'] == 2
assert p['evaluate_result']['rid']
assert p['tle_receipt']['tle_id']
print('OK   python demo:', p['ssot_event']['invalidated_count'], 'invalidated →', p['evaluate_result']['decision'])
"

node -e "
const g = require('./api/_lib/governance-evaluate');
const ssot = g.applySsotChange({
  fromVersion: '3.1',
  toVersion: '3.2',
  pending: [
    { rid: 'RID-1', policy_version: '3.1', action: 'copilot_rollout' },
    { rid: 'RID-2', policy_version: '3.2', action: 'copilot_rollout' },
  ],
});
if (ssot.invalidated_count !== 1) process.exit(1);
const ev = g.evaluateIntent({
  actor: 'security-team',
  action: 'copilot_rollout',
  context: 'Copilot rollout to production M365 tenant — re-briefed',
  metadata: { policy_version: '3.2' },
});
if (!ev.rid || !ev.decision) process.exit(1);
console.log('OK   node governance-evaluate:', ev.decision, 'score', ev.risk_score);
"

for f in policy_v3.1.json policy_v3.2.json pending_evaluations.json; do
  test -f "demos/copilot-governance/ssot/$f" || { echo "FAIL missing $f" >&2; exit 1; }
done
echo "OK   fixtures present"

grep -q 'nfSsotDemo' copilot/demo/index.html || { echo "FAIL demo page missing nfSsotDemo" >&2; exit 1; }
grep -q 'noetfield-ssot-demo.js' copilot/demo/index.html || { echo "FAIL demo page missing script" >&2; exit 1; }
echo "OK   copilot/demo/index.html wired"

echo ""
echo "verify-ssot-demo passed."
