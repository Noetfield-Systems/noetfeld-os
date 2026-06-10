#!/usr/bin/env bash
# Fail if QUICK_PICK top-5 are all already done in registry (stale picks).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUICK="${ROOT}/docs/ops/plans/no-asf/QUICK_PICK.md"
REGISTRY="${ROOT}/docs/ops/plans/registry.json"

echo "=== verify-quick-pick-fresh ==="

if [[ ! -f "$QUICK" || ! -f "$REGISTRY" ]]; then
  echo "FAIL missing QUICK_PICK or registry.json" >&2
  exit 1
fi

ids="$(python3 - <<'PY'
import re
from pathlib import Path
text = Path("docs/ops/plans/no-asf/QUICK_PICK.md").read_text(encoding="utf-8")
section = text.split("## Next 25")[1].split("## Recently")[0] if "## Next 25" in text else text
found = re.findall(r"\*\*(NF-PLAN-\d{4})\*\*", section)
print("\n".join(found[:5]))
PY
)"

done_count=0
total=0
while IFS= read -r pid; do
  [[ -z "$pid" ]] && continue
  total=$((total + 1))
  status="$(python3 -c "
import json, sys
r = json.load(open('docs/ops/plans/registry.json'))
p = next((x for x in r['plans'] if x['id'] == sys.argv[1]), None)
print(p.get('status','MISSING') if p else 'MISSING')
" "$pid")"
  echo "  $pid → $status"
  if [[ "$status" == "done" ]]; then
    done_count=$((done_count + 1))
  fi
done <<< "$ids"

if [[ "$total" -ge 5 && "$done_count" -eq "$total" ]]; then
  echo "FAIL top-5 QUICK_PICK entries are all done — run sync-prompt-pack-status.py" >&2
  exit 1
fi

python3 - <<'PY' || { echo "FAIL QUICK_PICK stale pattern duplicates" >&2; exit 1; }
import json, re
from pathlib import Path

quick = Path("docs/ops/plans/no-asf/QUICK_PICK.md").read_text(encoding="utf-8")
section = quick.split("## Next 25")[1].split("## Recently")[0]
top_ids = re.findall(r"\*\*(NF-PLAN-\d{4})\*\*", section)[:5]
registry = json.loads(Path("docs/ops/plans/registry.json").read_text(encoding="utf-8"))
by_id = {p["id"]: p for p in registry["plans"]}
p0t1_done_patterns = {
    p["pattern"]
    for p in registry["plans"]
    if p["phase"] == "P0" and p["tier"] == "T1" and p["status"] == "done"
}
stale = sum(
    1 for pid in top_ids
    if pid in by_id and by_id[pid]["pattern"] in p0t1_done_patterns
)
if stale >= 5:
    raise SystemExit(f"top-5 all repeat P0/T1 done patterns ({stale}/5)")
print(f"OK   top-5 stale-pattern check ({stale}/5 repeat P0/T1 done patterns)")
PY

echo ""
echo "verify-quick-pick-fresh passed ($done_count/$total top-5 done)."
