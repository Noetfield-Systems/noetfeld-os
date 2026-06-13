#!/usr/bin/env bash
# Validate MARKET_SUCCESS_1000 roadmap structure (founder-only doc).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROADMAP="${ROOT}/ops/private/MARKET_SUCCESS_1000_ROADMAP_LOCKED_v3.md"
GEN="${ROOT}/scripts/generate-market-success-1000-roadmap.py"

fail=0
ok() { echo "OK   verify-market-roadmap: $1"; }
bad() { echo "FAIL verify-market-roadmap: $1" >&2; fail=1; }

[[ -f "$ROADMAP" ]] || bad "missing $ROADMAP"
[[ -f "$GEN" ]] || bad "missing generator $GEN"

count="$(python3 - <<'PY'
import re
from pathlib import Path
text = Path("ops/private/MARKET_SUCCESS_1000_ROADMAP_LOCKED_v3.md").read_text()
# Step rows only (inside phase sections), not summary tables
chunks = text.split("## Phase ")
nums = []
for chunk in chunks[1:]:
    for m in re.finditer(r"^\| (\d+) \|", chunk, re.M):
        nums.append(int(m.group(1)))
print(len(nums))
print(min(nums) if nums else 0)
print(max(nums) if nums else 0)
print(len(set(range(1, 1001)) - set(nums)))
PY
)"
step_count="$(echo "$count" | sed -n '1p')"
min_n="$(echo "$count" | sed -n '2p')"
max_n="$(echo "$count" | sed -n '3p')"
missing_n="$(echo "$count" | sed -n '4p')"

[[ "$step_count" -eq 1000 ]] && ok "1000 step rows" || bad "expected 1000 steps, got $step_count"
[[ "$min_n" -eq 1 && "$max_n" -eq 1000 ]] && ok "steps 1–1000 contiguous" || bad "range $min_n–$max_n"
[[ "$missing_n" -eq 0 ]] && ok "no missing step numbers" || bad "$missing_n missing numbers"

grep -q "Golden rules" "$ROADMAP" && ok "golden rules section" || bad "golden rules missing"
grep -q "Golden suggestions" "$ROADMAP" && ok "golden suggestions section" || bad "golden suggestions missing"
grep -q "Ten market success models" "$ROADMAP" && ok "market models table" || bad "models table missing"
grep -q "Phase X —" "$ROADMAP" && ok "phase X present" || bad "phase X missing"
grep -q "never public www" "$ROADMAP" && ok "founder-only banner" || bad "founder-only banner missing"

for phase in I II III IV V VI VII VIII IX X; do
  grep -q "Phase ${phase} —" "$ROADMAP" && ok "phase $phase header" || bad "phase $phase header missing"
done

if [[ "$fail" -ne 0 ]]; then
  echo "Run: python3 scripts/generate-market-success-1000-roadmap.py" >&2
  exit 1
fi
echo "verify-market-roadmap PASS"
