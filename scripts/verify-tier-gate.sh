#!/usr/bin/env bash
# QUICK_PICK top-25 must not include Tier B/C gated plans (GTM fence).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUICK="${ROOT}/docs/ops/plans/no-asf/QUICK_PICK.md"
REGISTRY="${ROOT}/docs/ops/plans/registry.json"

echo "=== verify-tier-gate ==="

if [[ ! -f "$QUICK" || ! -f "$REGISTRY" ]]; then
  echo "FAIL missing QUICK_PICK or registry.json" >&2
  exit 1
fi

ids="$(python3 - <<'PY'
import re
from pathlib import Path
text = Path("docs/ops/plans/no-asf/QUICK_PICK.md").read_text(encoding="utf-8")
# First 25 numbered entries in Next 25 section
section = text.split("## Next 25")[1].split("## Recently")[0] if "## Next 25" in text else text
found = re.findall(r"\*\*(NF-PLAN-\d{4})\*\*", section)
print("\n".join(found[:25]))
PY
)"

fail=0
while IFS= read -r pid; do
  [[ -z "$pid" ]] && continue
  gate="$(python3 -c "
import json, sys
r = json.load(open('docs/ops/plans/registry.json'))
p = next((x for x in r['plans'] if x['id'] == sys.argv[1]), None)
print(p.get('tier_gate','none') if p else 'MISSING')
" "$pid")"
  if [[ "$gate" == "B" || "$gate" == "C" ]]; then
    echo "FAIL $pid tier_gate=$gate in QUICK_PICK top-25" >&2
    fail=1
  else
    echo "OK   $pid tier_gate=$gate"
  fi
done <<< "$ids"

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-tier-gate passed."
  exit 0
fi
exit 1
