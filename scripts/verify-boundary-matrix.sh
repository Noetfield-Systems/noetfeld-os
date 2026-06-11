#!/usr/bin/env bash
# Dual-brand boundary matrix — govern-first handoff lines present.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MATRIX="${ROOT}/docs/spec/trustfield-noetfield-conflict-matrix.md"

echo "=== verify-boundary-matrix ==="

if [[ ! -f "$MATRIX" ]]; then
  echo "FAIL missing $MATRIX" >&2
  exit 1
fi

fail=0
for needle in \
  "Noetfield may implement" \
  "govern" \
  "handoff" \
  "Public line" \
  "Coordinated narrative"; do
  if grep -qi "$needle" "$MATRIX"; then
    echo "OK   contains: $needle"
  else
    echo "FAIL missing: $needle" >&2
    fail=1
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-boundary-matrix passed."
  exit 0
fi
exit 1
