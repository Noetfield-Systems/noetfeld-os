#!/usr/bin/env bash
# verify-nf-mono-nerve-wire.sh — ecosystem nerve wire (Noetfield + TrustField + SourceA defer)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-nf-mono-nerve-wire ==="

for f in \
  data/nf_mono_nerve_wiring_v1.json \
  scripts/nf_mono_nerve_v1.py \
  scripts/nf_assert_implement_allowed.sh; do
  [[ -f "$f" ]] || { echo "FAIL missing $f" >&2; fail=1; continue; }
  echo "OK   $f"
done

python3 scripts/nf_mono_nerve_v1.py --json >/dev/null || fail=1
echo "OK   nf_mono_nerve assess"

[[ -f "$HOME/.sina/nf-mono-nerve-v1.json" ]] || { echo "FAIL missing nf-mono-nerve receipt" >&2; fail=1; }
[[ -f "$HOME/.sina/ecosystem-live-nerve-v1.json" ]] || { echo "FAIL missing ecosystem-live-nerve receipt" >&2; fail=1; }
[[ -f "$HOME/.sina/commercial-email-send-defer-receipt-v1.json" ]] || { echo "FAIL missing defer receipt" >&2; fail=1; }
[[ -f "$HOME/.sina/noetfield-operations-inbox-active-v1.json" ]] || { echo "FAIL missing operations inbox receipt" >&2; fail=1; }
echo "OK   ~/.sina mono receipts"

python3 - <<'PY' || exit 1
import json
from pathlib import Path

sina = Path.home() / ".sina"
eco = json.loads((sina / "ecosystem-live-nerve-v1.json").read_text())
assert eco.get("ok"), "ecosystem nerve not ok"
assert eco.get("email_send_defer_line"), "missing email_send_defer_line"
assert eco["planes"]["noetfield"]["ok"], "noetfield plane not ok"
print("OK   ecosystem-live-nerve:", eco.get("email_send_defer_line"))
PY

if [[ -f "$HOME/Desktop/TrustField Technologies/scripts/tf_fleet_live_wire_v1.py" ]]; then
  python3 "$HOME/Desktop/TrustField Technologies/scripts/tf_fleet_live_wire_v1.py" --json --no-refresh >/dev/null || fail=1
  echo "OK   trustfield fleet wire"
else
  echo "WARN trustfield fleet script missing (skip cross-plane)"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-nf-mono-nerve-wire: PASS"
else
  echo ""
  echo "verify-nf-mono-nerve-wire: FAIL"
  exit 1
fi
