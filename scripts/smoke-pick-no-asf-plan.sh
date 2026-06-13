#!/usr/bin/env bash
# Smoke: pick-no-asf-plan returns one nf-XXXX line and exits 0.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
out="$(python3 scripts/pick-noetfield-no-asf-plan.py --tier T0 --limit 1)"
echo "$out"
echo "$out" | grep -qE '^nf-[0-9]{4}\t'
echo "smoke-pick-no-asf-plan PASS"
