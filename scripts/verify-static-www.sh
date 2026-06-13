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

check_file "homepage pilot-first" index.html \
  'noetfield-www.css?v=39' 'nf-site-v14' 'Board-grade trust' \
  'data-live-proof-hero' 'nf-live-proof-lanes' 'nf-product-lane-strip' \
  'Governance specialist' 'agentic-specialist' 'VC diligence' \
  'Trust Brief' 'Bank Pilot' 'Explore product lanes' \
  'tamper-evident decision records' 'nfScenarioOfDay' \
  'Apply for pilot ($2k–10k)' '01 · Pilot' 'Built for regulated EU and US' \
  'Copilot Governance Pack' 'Commercial path' 'Learn in sandbox' \
  'independent of the app under audit' 'AI execution becomes auditable'

check_file "homepage wave1 journey" index.html \
  '02 · Prove' '03 · Try' '04 · Trust' '$2k–10k' 'Published tiers'

# Homepage IA compression — ≤8 top-level sections (U5 v17)
section_count="$(grep -c '<section' index.html || true)"
if [[ "$section_count" -le 8 ]]; then
  ok "homepage section count ≤8 ($section_count)"
else
  bad "homepage section count ≤8 — found $section_count sections"
fi

check_file "start sandbox page" start/index.html \
  'nf-hero-flow' 'Try in minutes' '14-day trial' '50 evaluate calls' 'Apply for pilot' \
  'data-trial-os-flow' 'noetfield-www.css?v=39'

check_file "pricing packaging page" pricing/index.html \
  'Published tiers' 'Apply for pilot ($2k–10k)' 'Milestone pricing' 'Developer access · free' \
  'noetfield-www.css?v=39' 'What regulated buyers receive from Noetfield'

check_file "pilot landing page" copilot/pilot/index.html \
  'noetfield-www.css?v=39' 'Board-grade trust' 'GTM-locked pilot success signals' \
  'interest=pilot' 'nfPilotApplyForm' 'Milestone pricing' \
  'Export assurance' 'QuickScan' 'Pilot deliverables' 'tamper-evident' \
  'Copilot Governance Pack' 'Regulated buyer map' 'Honest scope' \
  'Digital trust lane' 'Governance gaps' 'Buyer voices' 'Policy-bound workflows' \
  'noetfield-intake-core.js' 'nfPilotApplyStatus'

check_file "work with us program" work-with-us/index.html \
  'noetfield-www.css?v=39' 'Work with Noetfield' 'Connector' 'Facilitator' \
  'Co-partner' 'Apply to work with us' 'nfPartnerApplyForm' 'Apply → enable → earn' \
  'noetfield-intake-core.js' 'nfPartnerApplyStatus' 'Investor' '/investors/' \
  'nf-wwu-investor-spotlight' 'nf-wwu-lane-pill' 'noetfield-work-with-us.js'

check_file "pilot intake page" trust-brief/intake/index.html \
  'noetfield-intake-pilot-mode.js' 'intakeHeroPilot' 'Copilot Governance Pack' \
  'Submit pilot application' 'tb_pilot_band' 'intakeStickyCta' 'tbPreparePilot' \
  'What speeds pilot kickoff' 'noetfield-intake-core.js' 'notified asynchronously'

check_file "contact async intake" contact/index.html \
  'nfContactForm' 'data-nf-intake-form' 'noetfield-forms.js' 'noetfield-intake-core.js'

check_file "investors async intake" investors/index.html \
  'nfInvestorForm' 'data-nf-intake-form' 'noetfield-intake-core.js' 'Diligence vault'

check_file "investor diligence vault" investors/diligence/index.html \
  'Investor Diligence Vault' 'nfInvestorDiligenceForm' 'investor-diligence' \
  'Shadow Governance Brief' '18-item checklist' 'nf-vault-checklist' \
  'noetfield-intake-core.js'

check_file "msp end-client buyer block" msp/index.html \
  'msp-end-client' 'End client' 'Apply for pilot' '/copilot/pilot/'

check_file "status intake health" status/index.html \
  'data-intake-health-host' 'noetfield-intake-status.js' 'Intake delivery'

check_file "header investors nav" assets/partials/header.html \
  '/investors/diligence/' 'Investors'

check_file "vercel intake API" vercel.json \
  'api/public/chat'

check_file "www intake serverless" api/intake.js \
  'sendIntakeEmails' 'operations@noetfield.com'

check_file "global form wiring asset" assets/noetfield-forms.js \
  'data-nf-intake-form' 'nfSandboxForm' 'NFIntakeCore'

check_file "footer pilot-first" assets/partials/footer.html \
  'Apply for pilot ($2k–10k)' 'Copilot Governance Pack' 'tamper-evident'

check_file "header pilot nav" assets/partials/header.html \
  'Pilot · $2k–10k' '/copilot/pilot/' 'Apply for pilot ($2k–10k)'

check_file "trust center diligence theme" trust/index.html \
  'nf-trust-diligence' 'fail closed' 'Metadata-only'

check_file "investors honesty" investors/index.html \
  'do not inflate ARR' 'Governance Pack' 'tamper-evident' 'Board PDF pilots open' 'Shipped today'

check_file "copilot dual artifact" copilot/index.html \
  'nf-hero-artifacts' 'Apply for pilot' 'board-grade governance'

check_file "offerings lock" OFFERINGS_LOCKED.md \
  'Three contract offerings' 'Trust Brief' 'Copilot Governance Pack' 'Bank Pilot' \
  'Primary CTA' 'interest=pilot'

check_file "commercial SSOT" docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md \
  'OFFERINGS_LOCKED' 'Trust Brief' 'operations@noetfield.com' 'W3 economic signal'

check_file "ai-automation lane B" ai-automation/index.html \
  'Make your AI automation defensible' 'Apply for pilot' 'noetfield-www.css?v=39'

# Version coherence on primary hubs
for f in index.html trust/index.html copilot/index.html msp/index.html federal/index.html investors/index.html start/index.html pricing/index.html faq/index.html contact/index.html enterprise/index.html; do
  if [[ -f "$f" ]] && ! grep -qF 'noetfield-shell.js?v=39' "$f"; then
    bad "shell v39 on $f"
  fi
done
[[ "$fail" -eq 0 ]] && ok "shell v39 on primary hubs"

LEGACY_GTM='design-partner|Design partner|Become a design partner|Purview-only trap|Accepting design partners|Available now vs what capital accelerates'
legacy_fail=0
for f in index.html copilot/pilot/index.html investors/index.html assets/partials/header.html assets/partials/footer.html; do
  if [[ -f "$f" ]] && grep -Eiq "$LEGACY_GTM" "$f"; then
    echo "FAIL verify-static-www: legacy GTM copy in $f" >&2
    grep -Ei -n "$LEGACY_GTM" "$f" >&2 || true
    legacy_fail=1
  fi
done
[[ "$legacy_fail" -eq 0 ]] && ok "no legacy design-partner GTM on public www"

check_file "digital trust lane doc" docs/strategy/NOETFIELD_DIGITAL_TRUST_LANE_LOCKED_v1.md \
  'Digital Trust Lane' 'North star' 'Regulated buyer map' 'Honest moat' 'Learn · Add · Implement · Earn'

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

check_file "pilot automation copy" copilot/pilot/index.html \
  'Policy-bound workflows' 'Automated governance' 'nf-signal-badge--available'

check_file "procurement buyer copy" copilot/procurement/index.html \
  'Available now — capability scope' 'Apply for pilot' 'Overview'

check_file "legal pages" privacy/index.html \
  'What we collect' 'operations@noetfield.com'
check_file "legal pages terms" terms/index.html \
  'No custody or payment execution' 'operations@noetfield.com'

# Pilot-first on tier hubs — no Trust Brief as sole primary without pilot
for f in faq/index.html contact/index.html enterprise/index.html pricing/index.html; do
  if [[ -f "$f" ]] && grep -qF 'Apply for pilot' "$f"; then
    ok "pilot CTA on $f"
  else
    bad "pilot CTA on $f"
  fi
done

[[ -f vercel.json ]] && grep -qF 'docs/ops' vercel.json && ok "vercel.json blocks docs/ops" || bad "vercel.json missing docs/ops block"
[[ -f .vercelignore ]] && grep -qF 'docs/ops/' .vercelignore && ok "vercelignore excludes docs/ops" || bad "vercelignore missing docs/ops"

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "verify-static-www PASS"
