#!/usr/bin/env bash
# verify-ui-build-checklist.sh — mandatory UI law gate (offline-safe)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0
echo "=== verify-ui-build-checklist (mandatory) ==="

require_file() {
  local rel="$1"
  if [[ ! -f "$rel" ]]; then
    echo "FAIL missing: $rel" >&2
    fail=1
    return
  fi
  echo "OK   $rel"
}

require_file docs/ops/UI_BUILD_CHECKLIST_LOCKED_v1.md
require_file docs/WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md
require_file .cursor/skills/SKILL-009-ui-build-checklist-mandatory.md
require_file governance/FREEMIUM_POLICY_LOCKED_v1.md

memory=".cursor/agent-memory/MEMORY_LOCKED.yaml"
if grep -q 'R-012' "$memory" && grep -q 'UI_BUILD_CHECKLIST' "$memory"; then
  echo "OK   MEMORY_LOCKED R-012 UI checklist rule"
else
  echo "FAIL MEMORY_LOCKED.yaml missing R-012 UI checklist rule" >&2
  fail=1
fi

if grep -q 'SKILL-009' scripts/verify-agent-scope.sh; then
  echo "OK   verify-agent-scope wires SKILL-009"
else
  echo "FAIL verify-agent-scope must require SKILL-009" >&2
  fail=1
fi

# Homepage markers (UI-01, UI-05)
home="index.html"
for needle in 'data-live-proof-hero' 'noetfield-live-proof.js' '02 · Prove' '03 · Try' '/copilot/trial/' '/start/'; do
  if ! grep -qF "$needle" "$home"; then
    echo "FAIL index.html missing: $needle" >&2
    fail=1
  fi
done
echo "OK   homepage UI markers"

if grep -qF 'The moment Copilot becomes auditable' "$home"; then
  echo "OK   homepage prove headline"
else
  echo "FAIL index.html missing prove headline (UI-05)" >&2
  fail=1
fi

# Trial OS (UI-02)
start="start/index.html"
for needle in 'data-trial-os-flow' 'nfTrialOs' 'noetfield-sandbox.js' '/api/sandbox/'; do
  if [[ "$needle" == '/api/sandbox/' ]]; then
    grep -qF "$needle" assets/noetfield-sandbox.js || { echo "FAIL sandbox js missing API path" >&2; fail=1; }
    continue
  fi
  if ! grep -qF "$needle" "$start"; then
    echo "FAIL start/index.html missing: $needle" >&2
    fail=1
  fi
done
echo "OK   Trial OS markers"

# Agentic demo (commercial polish)
demo="copilot/demo/index.html"
for needle in 'nf26-demoStepper' 'nf26-eventTrace' 'nf26-progressRing' 'Human-in-the-loop' 'institutional-2026.css'; do
  if ! grep -qF "$needle" "$demo"; then
    echo "FAIL copilot/demo missing: $needle" >&2
    fail=1
  fi
done
echo "OK   agentic demo markers"

# Nav parity
header="assets/partials/header.html"
for link in '/copilot/demo/' '/copilot/trial/' '/start/'; do
  if ! grep -qF "$link" "$header"; then
    echo "FAIL header missing $link" >&2
    fail=1
  fi
done
echo "OK   header nav parity"

# No invitation on public buyer pages (stable self-serve guard)
INVITE_RE='calendar hold|book a call|schedule a meeting|Schedule a demo call|suggest two times'
for page in index.html start/index.html copilot/demo/index.html copilot/trial/index.html pricing/index.html; do
  if grep -qiE "$INVITE_RE" "$page" 2>/dev/null; then
    echo "FAIL $page contains invitation/calendar CTA" >&2
    fail=1
  fi
done
echo "OK   no invitation CTAs on P0 public pages"

# gate/sales must not be primary CTA on demo/trial
for page in copilot/demo/index.html copilot/trial/index.html; do
  if grep -qF 'href="/gate/sales/"' "$page" && grep -qE 'btn primary.*gate/sales' "$page"; then
    echo "FAIL $page uses gate/sales as primary CTA" >&2
    fail=1
  fi
done
echo "OK   no gate/sales primary CTA on demo/trial"

# Freemium ladder
trial="copilot/trial/index.html"
if grep -qiF QuickScan "$trial"; then
  echo "FAIL trial page lists QuickScan as retail ladder step" >&2
  fail=1
else
  echo "OK   trial ladder aligned"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-ui-build-checklist passed."
  exit 0
fi
echo ""
echo "UI build checklist verification failed — agents must read UI_BUILD_CHECKLIST_LOCKED_v1.md" >&2
exit 1
