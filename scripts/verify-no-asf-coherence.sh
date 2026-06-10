#!/usr/bin/env bash
# Meta-verify: GTM_NEXT vs SHIP_NOW vs QUICK_PICK inline; R-011 on disk; open ship PR warning.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-no-asf-coherence ==="

# R-011 + locked agentic law on disk
for f in \
  docs/ops/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md \
  .cursor/skills/SKILL-008-agentic-commercial-boundary.md; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

if grep -q 'R-011' .cursor/agent-memory/MEMORY_LOCKED.yaml 2>/dev/null; then
  echo "OK   R-011 in MEMORY_LOCKED.yaml"
else
  echo "FAIL MEMORY_LOCKED.yaml missing R-011" >&2
  fail=1
fi

# GTM_NEXT and QUICK_PICK should both point to GTM_NEXT queue when registry empty
if [[ -f docs/ops/plans/no-asf/GTM_NEXT.md ]] && [[ -f docs/ops/plans/no-asf/QUICK_PICK.md ]]; then
  if grep -q 'GTM_NEXT' docs/ops/plans/no-asf/QUICK_PICK.md; then
    echo "OK   QUICK_PICK references GTM_NEXT"
  else
    echo "FAIL QUICK_PICK missing GTM_NEXT reference" >&2
    fail=1
  fi
  if grep -q 'Agentic only' docs/ops/plans/no-asf/GTM_NEXT.md && grep -q 'ship-design-partner-outreach-026' docs/ops/plans/no-asf/GTM_NEXT.md; then
    echo "OK   GTM_NEXT 026 in agentic section"
  else
    echo "FAIL GTM_NEXT missing agentic 026 section" >&2
    fail=1
  fi
  if grep -q '1000/1000' docs/ops/plans/no-asf/GTM_NEXT.md; then
    echo "OK   GTM_NEXT documents 1000/1000 semantics"
  else
    echo "FAIL GTM_NEXT missing 1000/1000 semantics" >&2
    fail=1
  fi
else
  echo "FAIL missing GTM_NEXT or QUICK_PICK" >&2
  fail=1
fi

# SHIP_NOW should reference GTM_NEXT when registry empty
if grep -q 'GTM_NEXT' os/SHIP_NOW.md 2>/dev/null; then
  echo "OK   SHIP_NOW references GTM_NEXT"
else
  echo "FAIL SHIP_NOW missing GTM_NEXT reference" >&2
  fail=1
fi

# Warn on open ship PRs (non-fatal)
if command -v gh >/dev/null 2>&1; then
  open_prs="$(gh pr list --state open --json number,headRefName --jq '.[] | select(.headRefName | test("^cursor/(no-asf|10-phase)")) | .number' 2>/dev/null || true)"
  if [[ -n "$open_prs" ]]; then
    echo "WARN open ship PR(s): $open_prs — merge before next iter closeout"
  else
    echo "OK   no open cursor/no-asf ship PRs"
  fi
else
  echo "SKIP gh not available for open PR check"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-no-asf-coherence passed."
  exit 0
fi
exit 1
