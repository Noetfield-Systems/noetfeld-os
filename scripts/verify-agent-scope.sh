#!/usr/bin/env bash
# Agent scope self-audit — fails if tracked files bleed TrustField implementation or private paths.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-agent-scope ==="

# 1) Forbidden paths must not be tracked
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  echo "FAIL tracked forbidden path: $f" >&2
  fail=1
done < <(git ls-files 2>/dev/null | grep -E '(^ops/private/|^docs/internal/)' || true)

# 2) Required self-audit files
for f in \
  docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md \
  docs/ops/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md \
  .cursor/agent-memory/MEMORY_LOCKED.yaml \
  .cursor/incidents/REGISTRY.md \
  .cursor/skills/SKILL-001-scope-gate-before-work.md \
  .cursor/skills/SKILL-008-agentic-commercial-boundary.md; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

if ! grep -q '^version:' .cursor/agent-memory/MEMORY_LOCKED.yaml 2>/dev/null; then
  echo "FAIL MEMORY_LOCKED.yaml missing version" >&2
  fail=1
else
  echo "OK   memory version locked"
fi

if grep -q 'R-011' .cursor/agent-memory/MEMORY_LOCKED.yaml 2>/dev/null; then
  echo "OK   R-011 agentic commercial law locked"
else
  echo "FAIL MEMORY_LOCKED.yaml missing R-011" >&2
  fail=1
fi

# 3) Scan git-tracked files only — product/www must not implement TrustField
is_allowlisted() {
  local f="$1"
  [[ "$f" == .cursor/rules/* ]] && return 0
  [[ "$f" == .cursor/incidents/* ]] && return 0
  [[ "$f" == .cursor/agent-memory/* ]] && return 0
  [[ "$f" == .cursor/skills/* ]] && return 0
  [[ "$f" == .cursor/reports/* ]] && return 0
  [[ "$f" == docs/ops/AGENT_SELF_AUDIT* ]] && return 0
  [[ "$f" == docs/spec/trustfield-noetfield-conflict-matrix.md ]] && return 0
  [[ "$f" == PROJECT_BOUNDARIES_LOCKED.md ]] && return 0
  [[ "$f" == scripts/verify-agent-scope.sh ]] && return 0
  [[ "$f" == .cursor/AGENT_TRACKING.md ]] && return 0
  return 1
}

# Implementation bleed patterns (not negation docs)
# Links to trustfield.ca or TrustField implementation artifacts only (not boundary copy naming TrustField as separate entity)
BLEED_PATTERNS='trustfield\.ca|canonical.*trustfield\.ca|VENDOR_DILIGENCE_PACK|web/lib/company-copy|deploy TrustField|TrustField Vercel|UPG-003|UPG-004|UPG-011'

product_files=()
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  is_allowlisted "$f" && continue
  case "$f" in
    governance-console/*|index.html|copilot/*|partners/*|assets/*|*.html|Makefile) product_files+=("$f") ;;
  esac
done < <(git ls-files 2>/dev/null)

if [[ ${#product_files[@]} -gt 0 ]]; then
  hits="$(rg -n -i "$BLEED_PATTERNS" "${product_files[@]}" 2>/dev/null || true)"
  if [[ -n "$hits" ]]; then
    echo "FAIL product/www TrustField implementation bleed:" >&2
    echo "$hits" >&2
    fail=1
  else
    echo "OK   product/www scope clean (${#product_files[@]} files)"
  fi
else
  echo "OK   product/www scope (no product files tracked)"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-agent-scope passed."
  exit 0
fi
echo ""
echo "Fix scope bleed before commit. See docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md" >&2
exit 1
