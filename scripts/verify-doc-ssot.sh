#!/usr/bin/env bash
# Doc SSOT unification checks — fast, offline.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
ok() { echo "OK   verify-doc-ssot: $1"; }
bad() { echo "FAIL verify-doc-ssot: $1" >&2; fail=1; }

check_file() {
  local label="$1" file="$2"
  shift 2
  [[ -f "$file" ]] || { bad "$label — missing $file"; return; }
  local missing=0 needle
  for needle in "$@"; do
    if ! grep -qF "$needle" "$file"; then
      echo "     missing in $file: $needle" >&2
      missing=1
    fi
  done
  [[ "$missing" -eq 0 ]] && ok "$label" || bad "$label"
}

echo "=== verify-doc-ssot ==="

check_file "docs hub" docs/README.md \
  'DOC_UNIFIED_INDEX_LOCKED_v1.md' 'make verify-doc-ssot'

check_file "unified index" docs/DOC_UNIFIED_INDEX_LOCKED_v1.md \
  'NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md' 'docs/references/' 'pick-wise'

check_file "quick pick v14" docs/ops/plans/no-asf/QUICK_PICK.md \
  'v14 WISE' 'make pick-wise'

check_file "domain index drift refs" os/LOCKED_REFERENCE_INDEX.md \
  'DOC_UNIFIED_INDEX_LOCKED_v1.md' 'GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md'

check_file "reference redirect" docs/reference/README.md \
  '../references/README.md'

check_file "agent memory doc nav" .cursor/agent-memory/MEMORY_LOCKED.yaml \
  'doc_navigation:' 'DOC_UNIFIED_INDEX_LOCKED_v1.md' '.cursor/README.md'

check_file "cursor layer index" .cursor/README.md \
  'DOC_UNIFIED_INDEX_LOCKED_v1.md' 'SKILL-001' 'verify-doc-ssot'

check_file "sources index locked paths" os/plan-library/noetfield-1000/SOURCES_INDEX.yaml \
  'GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md' 'GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md'

check_file "read-order unified index" .cursor/rules/noetfield-read-order.mdc \
  'DOC_UNIFIED_INDEX_LOCKED_v1.md' 'pick-wise'

check_file "500 master picker" docs/ops/NOETFIELD_PROMPT_PACK_500_MASTER_LOCKED_v1.md \
  'pick-wise' 'V14_WISE'

check_file "agent memory packaging" .cursor/agent-memory/MEMORY_LOCKED.yaml \
  'packaging_v16:' 'WWW_V16_PACKAGING_PLAN_LOCKED_v1.md' '14-day trial'

check_file "v16 packaging plan" docs/WWW_V16_PACKAGING_PLAN_LOCKED_v1.md \
  'Sign up (free)' '/start/' '14 days' '50 calls' 'Agentic'

check_file "commercial inbox packaging" docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md \
  'operations@noetfield.com' 'sandbox' 'Self-serve first'

check_file "gtm copybook v16" docs/GTM_COPYBOOK.md \
  'Start free sandbox' 'Published tiers' 'Agentic'

check_file "offerings sandbox tier" OFFERINGS_LOCKED.md \
  'Developer access' '/start/' 'Three contract offerings'

check_file "north star offerings" NORTH_STAR.md \
  'OFFERINGS_LOCKED.md'

check_file "registry nf-1000 sources" os/plan-library/noetfield-1000/REGISTRY.json \
  'GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md' 'GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md'

if [[ -f ops/private/agent-reference/README.md ]]; then
  ok "private agent-reference README"
else
  echo "SKIP private agent-reference README (ops/private may be absent on cloud clone)"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-doc-ssot passed."
  exit 0
fi
echo ""
echo "Fix doc SSOT drift. Hub: docs/DOC_UNIFIED_INDEX_LOCKED_v1.md" >&2
exit 1
