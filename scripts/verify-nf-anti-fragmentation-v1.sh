#!/usr/bin/env bash
# verify-nf-anti-fragmentation-v1.sh — one title · one boot entry · inventory coverage
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-nf-anti-fragmentation-v1 ==="

INV="os/NF_SSOT_INVENTORY.json"
[[ -f "$INV" ]] || { echo "FAIL missing $INV" >&2; exit 1; }

python3 - <<'PY' || fail=1
import json, sys
from pathlib import Path
root = Path(".")
inv = json.loads((root / "os/NF_SSOT_INVENTORY.json").read_text())
boot = inv.get("boot_entries") or []
ids = [e["id"] for e in boot]
if len(ids) != len(set(ids)):
    print("FAIL duplicate boot entry ids", file=sys.stderr)
    sys.exit(1)
for e in boot:
    p = root / e["path"]
    if not p.is_file():
        print(f"FAIL missing boot path {e['path']}", file=sys.stderr)
        sys.exit(1)
print(f"OK   boot entries {len(boot)}")
PY

# exactly 4 alwaysApply core rules
count=$(grep -rl 'alwaysApply: true' .cursor/rules/nf-*.mdc .cursor/rules/noetfield-ask-before-edit.mdc 2>/dev/null | wc -l | tr -d ' ')
if [[ "$count" -eq 4 ]]; then
  echo "OK   4 alwaysApply core rules"
else
  echo "FAIL expected 4 alwaysApply core rules, got $count" >&2
  fail=1
fi

# MOVED stubs
for f in noetfield-read-order noetfield-ship-first noetfield-no-asf-plans noetfield-rule-conflict-resolution noetfield-scope noetfield-self-audit; do
  if grep -q '^# MOVED' ".cursor/rules/${f}.mdc" 2>/dev/null; then
    echo "OK   MOVED stub ${f}.mdc"
  else
    echo "FAIL missing MOVED stub ${f}.mdc" >&2
    fail=1
  fi
done

# plan.json locked_reference ids unique
python3 - <<'PY' || fail=1
import json, sys
plan = json.loads(open("os/plan.json").read())
ids = [r.get("id") for r in plan.get("locked_references") or []]
if len(ids) != len(set(ids)):
    print("FAIL duplicate locked_reference ids in plan.json", file=sys.stderr)
    sys.exit(1)
print("OK   plan.json locked_reference ids unique")
PY

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-nf-anti-fragmentation-v1: PASS"
  exit 0
fi
echo ""
echo "verify-nf-anti-fragmentation-v1: FAIL" >&2
exit 1
