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

check_file "read-order routing card" .cursor/rules/nf-routing-card.mdc \
  'make nf-onboard' 'ROUTING_CARD.md'

check_file "500 master picker" docs/ops/NOETFIELD_PROMPT_PACK_500_MASTER_LOCKED_v1.md \
  'pick-wise' 'V14_WISE'

check_file "agent memory packaging" .cursor/agent-memory/MEMORY_LOCKED.yaml \
  'packaging_v16:' 'WWW_V16_PACKAGING_PLAN_LOCKED_v1.md' '14-day trial'

check_file "v16 packaging plan" docs/WWW_V16_PACKAGING_PLAN_LOCKED_v1.md \
  'Sign up (free)' '/start/' '14 days' '50 calls' 'Agentic'

check_file "phase15 factory prep" docs/ops/NF_FACTORY_ROUND_15_PREP_LOCKED_v1.md \
  '197/300' 'XF-P1' 'ship-sandbox-server-side-057'

check_file "phase16 factory prep" docs/ops/NF_FACTORY_ROUND_16_PREP_LOCKED_v1.md \
  '260/300' 'XF-P2' 'CA-P2' 'PL-P1' 'verify-nf-anti-staleness-max' 'PORTFOLIO_300_PHASE16_10_STEP_LOCKED_v1.md'

check_file "sandbox server-side spec" docs/start/SANDBOX_SERVER_SIDE_SESSION_SPEC_v1.md \
  '/api/v1/sandbox/sessions' 'NF_SANDBOX_API=1' 'localStorage'

check_file "commercial inbox packaging" docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md \
  'operations@noetfield.com' 'sandbox' 'Self-serve first' 'Google Workspace' 'ACTIVE' 'DEFERRED post-factory'

check_file "gtm copybook v16" docs/GTM_COPYBOOK.md \
  'Start free sandbox' 'Published tiers' 'Agentic'

check_file "offerings sandbox tier" OFFERINGS_LOCKED.md \
  'Developer access' '/start/' 'Three contract offerings'

check_file "north star offerings" NORTH_STAR.md \
  'OFFERINGS_LOCKED.md'

check_file "registry nf-1000 sources" os/plan-library/noetfield-1000/REGISTRY.json \
  'GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md' 'GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md'

check_file "nf-gaos w0 spine" docs/ops/NF_GAOS_W0_LOCKED_v1.md \
  'make nf-onboard' 'nf_session_gate_run_v1.py' 'ROUTING_CARD.md'

check_file "routing card boot" ROUTING_CARD.md \
  'make nf-onboard' 'nf_mono_nerve_v1.py' 'email_send_defer_line' 'nf_assert_implement_allowed.sh'

check_file "sandbox funnel metrics 061" docs/copilot/SANDBOX_FUNNEL_METRICS_SPEC_v1.md \
  'S0' 'S1' 'S2' 'S3' 'S4' 'S5' 'session_id'

check_file "copilot intake hub report 062" docs/copilot/INTAKE_COPILOT_GOVERNANCE_HUB_REPORT_v1.md \
  'vector=copilot-governance' 'INTAKE REPORT' 'copilot-governance'

check_file "anti-staleness maximum" docs/ops/NF_ANTI_STALENESS_MAXIMUM_FIX_SET_LOCKED_v1.md \
  'make nf-onboard' 'nf_anti_staleness_max' 'email_send_defer_line' 'Three email gates'

check_file "nf-gaos w3 factory spine" docs/ops/NF_GAOS_W3_FACTORY_SPINE_LOCKED_v1.md \
  'make verify-nf-gaos-w3' 'prove-nf-factory-spine' 'nf_mono_nerve_v1.py' 'email_send_defer_line'

check_file "platform entity split index" docs/platform/NF_PLATFORM_ENTITY_SPLIT_INDEX_v1.md \
  'pf-0266' 'pf-0275' 'PL-P1' 'separate_brand_law'

check_file "living system charter v3" docs/platform/NF_LIVING_SYSTEM_CHARTER_DRAFT_v3.md \
  'status: draft' 'visibility: internal-agent-only' 'not_www: true' \
  'NF_PLATFORM_ENTITY_SPLIT_INDEX_v1.md' 'Sense' 'Remember' 'Reflex' 'Speak' \
  'Goal A' '260/300' 'separate_brand_law' 'campus factory metric' \
  'www_email_configured' 'DEFERRED' 'sites=GREEN' 'make nf-onboard' 'never public www'

if [[ -x scripts/verify-nf-gaos-w3.sh ]]; then
  ./scripts/verify-nf-gaos-w3.sh && ok "nf-gaos-w3 prove bundle"
else
  bad "nf-gaos-w3 verify script missing"
fi

if [[ -x scripts/verify-nf-gaos-w0.sh ]]; then
  ./scripts/verify-nf-gaos-w0.sh && ok "nf-gaos-w0 verify bundle"
else
  bad "nf-gaos-w0 verify script missing"
fi

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
