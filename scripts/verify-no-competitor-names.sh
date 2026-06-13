#!/usr/bin/env bash
# Fail if third-party vendor names appear anywhere in the repo (buyer-safe surfaces).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Company / product names — not Microsoft, government, or TrustField (invoicing entity).
PATTERN='Veridra|Audital|Credo AI|Holistic AI|OneTrust|Vanta|Drata|Inforcer|Cloudiway|AvePoint|Securiti|ADJUDON|Trinitite|Monitaur|Forrester|Gartner|Kwick|MindBridge|ServiceNow|Splunk|Archer|Shopify'

GREP_INCLUDE=(--include='*.md' --include='*.py' --include='*.sh' --include='*.html' --include='*.css' --include='*.json' --include='*.txt' --include='*.yaml' --include='*.yml')

should_skip() {
  local path="$1"
  [[ "$path" == *"/.git/"* ]] && return 0
  [[ "$path" == *"/node_modules/"* ]] && return 0
  [[ "$path" == *"/.next/"* ]] && return 0
  [[ "$path" == *"/.venv/"* ]] && return 0
  [[ "$path" == *"/dist/"* ]] && return 0
  [[ "$path" == *"/__pycache__/"* ]] && return 0
  [[ "$path" == *"verify-no-competitor-names.sh" ]] && return 0
  [[ "$path" == *"verify-ui-e2e.sh" ]] && return 0
  [[ "$path" == *"/docs/SOURCE_OF_TRUTH/"* ]] && return 0
  [[ "$path" == *"/L2-knowledge/"* ]] && return 0
  [[ "$path" == *"/Noetfield-All-Documents/"* ]] && return 0
  [[ "$path" == *"/ops/private/"* ]] && return 0
  [[ "$path" == *"scripts/generate-market-success-1000-roadmap.py" ]] && return 0
  [[ "$path" == *"scripts/market_success_1000_data.py" ]] && return 0
  [[ "$path" == *"scripts/verify-market-roadmap.sh" ]] && return 0
  [[ "$path" == *"/tests/"* ]] && return 0
  [[ "$path" == *"scripts/sync_l2_knowledge.py" ]] && return 0
  [[ "$path" == *"scripts/generate_batch_"* ]] && return 0
  return 1
}

scan_repo() {
  local matches=""
  local line path
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    path="${line%%:*}"
    if should_skip "$path"; then
      continue
    fi
    matches+="${line}"$'\n'
  done < <(grep -rE -i -n "${GREP_INCLUDE[@]}" "$PATTERN" . 2>/dev/null || true)

  if [[ -n "${matches//[$'\n']/}" ]]; then
    printf '%s' "$matches" >&2
    echo "FAIL verify-no-competitor-names: vendor name in repo" >&2
    return 1
  fi
  echo "OK   verify-no-competitor-names: full repo clean"
}

scan_repo || exit 1
echo "verify-no-competitor-names PASS"
