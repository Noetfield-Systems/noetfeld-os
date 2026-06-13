#!/usr/bin/env bash
# Offline static www checks — no dev server required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
ok() { echo "OK   verify-static-www: $1"; }
bad() { echo "FAIL verify-static-www: $1" >&2; fail=1; }

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

check_file "homepage v18 shell" index.html \
  'noetfield-www.css?v=22' 'nf-site-v14' 'The audit trail your Copilot deployment' \
  'data-live-proof-hero' 'What legal and security reviewers need to see' \
  'nf-procurement-rail' 'Apply for pilot ($2k–10k)' 'Published tiers' \
  'Governance playground' 'Three traps before Copilot' 'One evaluate · four exports' \
  'Your peers roll out Copilot with slides' 'This is for you if' \
  'EU and US regulated institutions' 'EU AI Act Art. 12'

check_file "homepage wave1 journey" index.html \
  '01 · Pilot' '02 · Prove' '03 · Try' '04 · Trust' '$2k–10k' \
  'Lead program · $2k–10k · 90 days' 'Pilot overview'

check_file "start sandbox page" start/index.html \
  'nf-hero-flow' 'Try in minutes' '14-day trial' '50 evaluate calls' 'Sandbox mode' \
  'data-trial-os-flow'

check_file "pricing packaging page" pricing/index.html \
  'Published tiers' 'Sandbox + production' 'Developer access · free' 'noetfield-www.css?v=22' 'What you tried vs what breaks vs what Noetfield delivers'

check_file "pilot landing page" copilot/pilot/index.html \
  'noetfield-www.css?v=22' '90-day design-partner pilot' 'Pilot deliverables' \
  'interest=design-partner' 'EU AI Act Art. 12' 'QuickScan' 'Board PDF success signal'

check_file "trust center diligence theme" trust/index.html \
  'nf-trust-diligence' 'fail closed' 'Metadata-only'

check_file "investors honesty" investors/index.html \
  'do not inflate ARR' 'design partner' 'Company compliance automation'

check_file "copilot dual artifact" copilot/index.html \
  'nf-hero-artifacts' 'nf-workspace-mock' 'Copilot Control System'

check_file "offerings lock" OFFERINGS_LOCKED.md \
  'Three contract offerings' 'Trust Brief' 'Copilot Governance Pack' 'Bank Pilot' \
  'Primary CTA' 'design-partner'

check_file "commercial SSOT" docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md \
  'OFFERINGS_LOCKED' 'Trust Brief' 'operations@noetfield.com' 'W3 economic signal'

check_file "ai-automation lane B" ai-automation/index.html \
  'Make your AI automation defensible' 'Three offerings only' 'noetfield-www.css?v=22'

# Version coherence on primary hubs
for f in index.html trust/index.html copilot/index.html msp/index.html federal/index.html investors/index.html start/index.html pricing/index.html; do
  if [[ -f "$f" ]] && ! grep -qF 'noetfield-shell.js?v=22' "$f"; then
    bad "shell v22 on $f"
  fi
done
[[ "$fail" -eq 0 ]] && ok "shell v22 on primary hubs"

if [[ "$fail" -ne 0 ]]; then
  echo "Run: python3 scripts/rebuild-www-v6.py" >&2
  exit 1
fi

# No comparison / competitor framing on public www
COMP_PATTERN='not another|They configure|Complement, not compete|estate catalog|GRC catalog|GRC platforms do not|different from an AI governance|six-figure GRC'
www_fail=0
for f in index.html trust/index.html copilot/index.html copilot/sme/index.html msp/index.html \
  federal/index.html investors/index.html ai-automation/index.html faq/index.html start/index.html pricing/index.html; do
  if [[ -f "$f" ]] && grep -E -i -q "$COMP_PATTERN" "$f"; then
    echo "FAIL verify-static-www: comparison framing in $f" >&2
    grep -E -i -n "$COMP_PATTERN" "$f" >&2 || true
    www_fail=1
  fi
done
[[ "$www_fail" -eq 0 ]] && ok "no comparison framing on public www" || fail=1

# P0 — no internal / founder / agent copy on public www
LEAK_PATTERN='maintained in repo|not claimed on www|plan-with-no-asf|AGENT_SELF_AUDIT|repo-native|ASSERT→|Founder-led \+ agentic|pipeline stage [0-9]|W3 PASS|Product on disk|/docs/ops/|services/governance/README|nf-card__tag">Hub<|Shipped today — honest|execution infrastructure|API offline|what we ship|our roadmap|Fully agentic|Governance agents|IBM Plex'
leak_fail=0
for f in index.html start/index.html copilot/procurement/index.html privacy/index.html terms/index.html status/index.html \
  trust/index.html faq/index.html investors/index.html trust-ledger/verify/index.html; do
  if [[ -f "$f" ]] && grep -E -q "$LEAK_PATTERN" "$f"; then
    echo "FAIL verify-static-www: P0 copy leak in $f" >&2
    grep -E -n "$LEAK_PATTERN" "$f" >&2 || true
    leak_fail=1
  fi
done
[[ "$leak_fail" -eq 0 ]] && ok "no P0 copy leaks on public www" || fail=1

check_file "homepage automation copy" index.html \
  'Policy-bound workflows' 'Automated governance' 'nf-signal-badge--available'

check_file "procurement buyer copy" copilot/procurement/index.html \
  'Available now — capability scope' 'Governance API reference' 'Overview'

check_file "legal pages" privacy/index.html \
  'What we collect' 'operations@noetfield.com'
check_file "legal pages terms" terms/index.html \
  'No custody or payment execution' 'operations@noetfield.com'

[[ -f vercel.json ]] && grep -qF 'docs/ops' vercel.json && ok "vercel.json blocks docs/ops" || bad "vercel.json missing docs/ops block"
[[ -f .vercelignore ]] && grep -qF 'docs/ops/' .vercelignore && ok "vercelignore excludes docs/ops" || bad "vercelignore missing docs/ops"

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "verify-static-www PASS"
