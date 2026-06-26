#!/usr/bin/env bash
# Verify every markdown file under docs/_NOOS_AGENT/ contains NOOS-AGENT-DOC.
# Steps 0011–0012 — agent vault tag enforcement.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VAULT="$ROOT/docs/_NOOS_AGENT"
TOKEN="NOOS-AGENT-DOC"
FAIL=0

if [[ ! -d "$VAULT" ]]; then
  echo "FAIL: vault missing at $VAULT"
  exit 1
fi

while IFS= read -r -d '' f; do
  if ! grep -q "$TOKEN" "$f"; then
    echo "FAIL: missing $TOKEN in $f"
    FAIL=1
  fi
done < <(find "$VAULT" -name '*.md' -print0)

if [[ "$FAIL" -ne 0 ]]; then
  echo "FAIL: untagged agent vault markdown files"
  exit 1
fi

echo "OK: all docs/_NOOS_AGENT/*.md files tagged with $TOKEN"
exit 0
