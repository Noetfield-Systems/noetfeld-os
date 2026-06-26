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

check_file "homepage intelligence-first" index.html \
  'noetfield-www.css?v=41' 'nf-site-v14' 'Board-grade trust' \
  'data-live-proof-hero' 'nf-live-proof-lanes' 'nf-product-lane-strip' \
  'Governance specialist' 'agentic-specialist' 'VC diligence' \
  'Trust Brief' 'Bank Pilot' 'Explore product lanes' \
  'tamper-evident decision records' 'nfScenarioOfDay' \
  'Apply for pilot ($2k–10k)' '01 · Diagnose' 'Diagnostic Sprint' \
  'Copilot Governance Pack' 'Commercial path' 'Start free sandbox' \
  'fail closed' 'Copilot becomes auditable'

check_file "homepage buyer journey" index.html \
  '02 · Build' '03 · Prove' '04 · Govern' '$2k–10k' 'Published tiers'

# Homepage IA compression — ≤8 top-level sections (U5 v17)
section_count="$(grep -c '<section' index.html || true)"
if [[ "$section_count" -le 8 ]]; then
  ok "homepage section count ≤8 ($section_count)"
else
  bad "homepage section count ≤8 — found $section_count sections"
fi

check_file "start sandbox page" start/index.html \
  'nf-hero-flow' 'Try in minutes' '14-day trial' '50 evaluate calls' 'Apply for pilot' \
  'data-trial-os-flow' 'NF_SANDBOX_NURTURE_SEQUENCE' 'noetfield-www.css?v=41'

check_file "pricing packaging page" pricing/index.html \
  'Published tiers' 'Apply for pilot ($2k–10k)' 'Milestone pricing' 'Developer access · free' \
  'noetfield-www.css?v=41' 'What regulated buyers receive from Noetfield'

check_file "pilot landing page" copilot/pilot/index.html \
  'noetfield-www.css?v=41' 'Board-grade trust' 'GTM-locked pilot success signals' \
  'interest=pilot' 'nfPilotApplyForm' 'Milestone pricing' \
  'Export assurance' 'QuickScan' 'Pilot deliverables' 'tamper-evident' \
  'Copilot Governance Pack' 'Regulated buyer map' 'Honest scope' \
  'Digital trust lane' 'Governance gaps' 'Buyer voices' 'Policy-bound workflows' \
  'noetfield-intake-core.js' 'nfPilotApplyStatus'

check_file "work with us program" work-with-us/index.html \
  'noetfield-www.css?v=41' 'Work with Noetfield' 'Connector' 'Facilitator' \
  'Co-partner' 'Apply to work with us' 'nfPartnerApplyForm' 'Apply → enable → earn' \
  'noetfield-intake-core.js' 'nfPartnerApplyStatus' 'Investor' '/investors/' \
  'nf-wwu-investor-spotlight' 'nf-wwu-lane-pill' 'noetfield-work-with-us.js'

check_file "pilot intake page" trust-brief/intake/index.html \
  'noetfield-intake-pilot-mode.js' 'intakeHeroPilot' 'Copilot Governance Pack' \
  'Submit pilot application' 'tb_pilot_band' 'intakeStickyCta' 'tbPreparePilot' \
  'we reply within one business day' 'What speeds pilot kickoff' 'noetfield-intake-core.js' 'notified asynchronously'

check_file "gate intake page" gate/intake/index.html \
  'intakeStickyCta' 'board PDF in governance meeting' 'Apply for pilot' \
  'noetfield-intake.css' 'Engagement intake'

check_file "contact async intake" contact/index.html \
  'nfContactForm' 'data-nf-intake-form' 'noetfield-forms.js' 'noetfield-intake-core.js'

check_file "investors async intake" investors/index.html \
  'nfInvestorForm' 'data-nf-intake-form' 'noetfield-intake-core.js' 'Diligence vault'

check_file "investor diligence vault" investors/diligence/index.html \
  'Investor Diligence Vault' 'nfInvestorDiligenceForm' 'investor-diligence' \
  'Shadow Governance Brief' '18-item checklist' 'nf-vault-checklist' \
  'noetfield-www.css?v=43' 'NF_INVESTOR_DILIGENCE_VAULT' \
  'noetfield-intake-core.js'

check_file "msp end-client buyer block" msp/index.html \
  'msp-end-client' 'End client' 'Apply for pilot' '/copilot/pilot/'

check_file "status intake health" status/index.html \
  'data-intake-health-host' 'noetfield-intake-status.js' 'Intake delivery' '/next/'

check_file "header institutional nav" assets/partials/header.html \
  'href="/"' '/copilot/' '/templates/' '/trust/' '/federal/' '/msp/' '/copilot/demo/' 'Pilot · $2k–10k'

check_file "footer enterprise nav" assets/partials/footer.html \
  '/investors/' '/next/' 'Diligence vault' 'Copilot Governance Pack'

check_file "templates catalog page" templates/index.html \
  'copilot-governance-v1' 'bank-pilot-v1' 'Trust Brief' \
  'Governance Runtime' 'noetfield-www.css?v=41' 'Deploy governed AI templates'

check_file "runtime landing page" runtime/index.html \
  'Policy before execution' 'REQUIRE_HUMAN_REVIEW' 'copilot-governance-v1' \
  'POST /api/v1/governance/evaluate' 'Illustrative sandbox output' 'noetfield-www.css?v=41'

check_file "federal lane page" federal/index.html \
  'Federal Governance Pack' 'NF_OSFI_E23_DILIGENCE_REFRESH' 'NF_METADATA_EVIDENCE_INDEX' \
  'AIA' 'Copilot PIN' 'noetfield-www.css?v=41'

check_file "partner banner embed" banner/index.html \
  'noindex,nofollow' 'REQUIRE_HUMAN_REVIEW' 'Illustrative — no fabricated hash' 'copilot-governance-v1'

check_file "header pilot CTA" assets/partials/header.html \
  'Pilot · $2k–10k' '/trust-brief/intake/?interest=pilot'

check_file "next steps hub" next/index.html \
  'next-buyer' 'next-investor' 'next-partner' 'next-ops' \
  'noetfield-intake-status.js' 'Apply for pilot' 'Enterprise standard'

check_file "vercel intake API" vercel.json \
  '/api/health'

check_file "www chat handler" api/public/chat/index.js \
  'www-local' 'operations@noetfield.com'

check_file "www intake serverless" api/intake.js \
  'sendIntakeEmails' 'operations@noetfield.com'

check_file "global form wiring asset" assets/noetfield-forms.js \
  'data-nf-intake-form' 'nfSandboxForm' 'NFIntakeCore'

check_file "footer pilot-first" assets/partials/footer.html \
  'Apply for pilot ($2k–10k)' 'Copilot Governance Pack' 'tamper-evident'

check_file "trust center diligence theme" trust/index.html \
  'nf-trust-diligence' 'nf-trust-doc-layout' 'fail closed' 'Metadata-only' 'Shipped'

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
  'Make your AI automation defensible' 'Apply for pilot' 'noetfield-www.css?v=41'

# Version coherence on primary hubs
for f in index.html trust/index.html copilot/index.html msp/index.html federal/index.html investors/index.html start/index.html pricing/index.html faq/index.html contact/index.html enterprise/index.html; do
  if [[ -f "$f" ]] && ! grep -qF 'noetfield-shell.js?v=41' "$f"; then
    bad "shell v41 on $f"
  fi
done
[[ "$fail" -eq 0 ]] && ok "shell v41 on primary hubs"

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
# copilot/procurement — buyer diligence surface; ops doc hrefs allowed (gtm-ops parity)
for f in index.html start/index.html privacy/index.html terms/index.html status/index.html \
  trust/index.html faq/index.html investors/index.html trust-ledger/verify/index.html; do
  if [[ -f "$f" ]] && grep -E -q "$LEAK_PATTERN" "$f"; then
    echo "FAIL verify-static-www: P0 copy leak in $f" >&2
    grep -E -n "$LEAK_PATTERN" "$f" >&2 || true
    leak_fail=1
  fi
done
[[ "$leak_fail" -eq 0 ]] && ok "no P0 copy leaks on public www" || fail=1

# Client-view language — no founder/SSOT jargon on buyer surfaces (developer demo widget exempt)
LANG_PATTERN='W3 economic signal|Lane SSOT|nurture SSOT|commercial SSOT|SourceA = motor|REGISTRY\.json|OFFERINGS_LOCKED|SSOT: <a|sell-side governance pack \(founder\)|gtm-ops-runbooks|STAGING_DEMO\.md|DEMO_REHEARSAL_CHECKLIST|design partner|design-partner|Accepting design partners|Become a design partner|613 GTM|founder never|Hub approve|RESEND_API_KEY|plan-with-no-asf|AGENT_SELF_AUDIT|docs/ops/|make nf-prove|portfolio [0-9]+/300'
lang_fail=0
for f in index.html start/index.html pricing/index.html copilot/pilot/index.html federal/index.html msp/index.html \
  investors/index.html investors/diligence/index.html gate/intake/index.html trust-brief/intake/index.html \
  status/index.html templates/index.html factory/index.html runtime/index.html copilot/index.html copilot/demo/index.html next/index.html; do
  if [[ -f "$f" ]] && grep -E -q "$LANG_PATTERN" "$f"; then
    echo "FAIL verify-static-www: founder/internal language in $f" >&2
    grep -E -n "$LANG_PATTERN" "$f" >&2 || true
    lang_fail=1
  fi
done
[[ "$lang_fail" -eq 0 ]] && ok "client-view language on public www" || fail=1

check_file "pilot automation copy" copilot/pilot/index.html \
  'Policy-bound workflows' 'Automated governance' 'nf-signal-badge--available'

check_file "procurement buyer copy" copilot/procurement/index.html \
  'Available now — capability scope' 'Apply for pilot' 'buyer-faq'

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
[[ -f vercel.json ]] && grep -qF 'docs/platform' vercel.json && ok "vercel.json blocks docs/platform" || bad "vercel.json missing docs/platform block"
[[ -f vercel.json ]] && grep -qF 'OPS_LIVE_STATUS_LOCKED.json' vercel.json && ok "vercel.json blocks OPS_LIVE" || bad "vercel.json missing OPS_LIVE block"
[[ -f vercel.json ]] && grep -qF 'OFFERINGS_LOCKED.md' vercel.json && ok "vercel.json blocks OFFERINGS_LOCKED" || bad "vercel.json missing OFFERINGS_LOCKED block"
[[ -f vercel.json ]] && ! grep -qF '"/governance"' vercel.json && ok "vercel.json keeps public /governance page" || bad "vercel.json must not 404 the public governance hub"
[[ -f .vercelignore ]] && grep -qF 'docs/ops/' .vercelignore && ok "vercelignore excludes docs/ops" || bad "vercelignore missing docs/ops"
[[ -f .vercelignore ]] && grep -qF 'docs/platform/' .vercelignore && ok "vercelignore excludes docs/platform" || bad "vercelignore missing docs/platform"
[[ -f .vercelignore ]] && grep -qF 'governance/*.json' .vercelignore && ok "vercelignore excludes governance json" || bad "vercelignore missing governance json"
[[ -f .vercelignore ]] && grep -qF 'OFFERINGS_LOCKED.md' .vercelignore && ok "vercelignore excludes OFFERINGS_LOCKED" || bad "vercelignore missing OFFERINGS_LOCKED"
[[ -f .vercelignore ]] && grep -qF 'platform/' .vercelignore && ok "vercelignore excludes platform" || bad "vercelignore missing platform"
[[ -f vercel.json ]] && grep -qF '/platform' vercel.json && ok "vercel.json blocks platform" || bad "vercel.json missing platform block"
[[ -f governance/index.html ]] && ok "public governance hub html present" || bad "missing governance/index.html"
[[ -f .vercelignore ]] && grep -qF 'docs/mockups/' .vercelignore && ok "vercelignore excludes docs/mockups" || bad "vercelignore missing docs/mockups"

# Truth mockups — ban invented product copy on public www
FAKE_PATTERN='FINTRAC|HIPAA policy pack|Factory catalog|Most deployed|\$48,?000|\$48k transfer|18 nodes|24 nodes|Governed Exchange|Audit Factory'
fake_fail=0
for f in index.html templates/index.html runtime/index.html banner/index.html copilot/index.html pricing/index.html start/index.html; do
  if [[ -f "$f" ]] && grep -Eiq "$FAKE_PATTERN" "$f"; then
    echo "FAIL verify-static-www: invented mockup copy in $f" >&2
    grep -Ei -n "$FAKE_PATTERN" "$f" >&2 || true
    fake_fail=1
  fi
done
[[ "$fake_fail" -eq 0 ]] && ok "no invented mockup copy on public www" || fail=1

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "verify-static-www PASS"
