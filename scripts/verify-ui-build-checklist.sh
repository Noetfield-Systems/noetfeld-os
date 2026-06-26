#!/usr/bin/env bash
# verify-ui-build-checklist.sh — mandatory UI/www/form guard (fail-closed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

ok() { echo "OK   verify-ui-buildlist: $*"; }
bad() { echo "FAIL verify-ui-checklist: $*" >&2; fail=1; }

echo "=== verify-ui-build-checklist ==="

# 0 — LOCK docs present
for f in \
  docs/www/NF_UI_BUILD_CHECKLIST_LOCKED_v1.md \
  docs/www/NF_WWW_LANGUAGE_LAYERS_LOCKED_v1.md \
  docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md; do
  [[ -f "$f" ]] && ok "lock doc $f" || bad "missing $f"
done

# 1 — Agent rule wired
if [[ -f .cursor/rules/nf-ui-checklist-mandatory.mdc ]] \
  && grep -q 'alwaysApply: true' .cursor/rules/nf-ui-checklist-mandatory.mdc; then
  ok "cursor rule nf-ui-checklist-mandatory.mdc"
else
  bad "missing or inactive nf-ui-checklist-mandatory.mdc"
fi

# 2 — No founder ops partial on disk
if [[ -f assets/partials/copilot-gtm-ops-links.html ]] \
  && grep -qE 'STAGING_DEMO|DEMO_REHEARSAL|gtm-ops-runbooks' assets/partials/copilot-gtm-ops-links.html; then
  bad "copilot-gtm-ops-links.html still has founder runbooks — use buyer-proof-links"
else
  ok "no founder gtm-ops partial leak"
fi

# 3 — Static www + language layers
chmod +x scripts/verify-static-www.sh
./scripts/verify-static-www.sh || fail=1

# 4 — Invitation / design-partner ban (extended surfaces)
INVITE_PATTERN='design partner|design-partner|Accepting design partners|Become a design partner|You.?re invited|Invitation to'
invite_fail=0
for f in index.html start/index.html pricing/index.html copilot/pilot/index.html \
  investors/index.html templates/index.html work-with-us/index.html \
  assets/partials/header.html assets/partials/footer.html; do
  if [[ -f "$f" ]] && grep -Eiq "$INVITE_PATTERN" "$f"; then
    echo "FAIL verify-ui-checklist: invitation copy in $f" >&2
    grep -Ei -n "$INVITE_PATTERN" "$f" >&2 || true
    invite_fail=1
  fi
done
[[ "$invite_fail" -eq 0 ]] && ok "no invitation copy on public www" || fail=1

# 5 — Buyer proof links on copilot surfaces (not founder runbooks)
for path in copilot/index.html copilot/pilot/index.html copilot/demo/index.html; do
  if [[ -f "$path" ]] && grep -qF 'buyer-proof-links' "$path" \
    && grep -qF 'Proof and diligence' "$path" \
    && ! grep -qF 'gtm-ops-runbooks' "$path"; then
    ok "$path buyer-proof section"
  else
    bad "$path missing buyer-proof or still has gtm-ops-runbooks"
  fi
done

# 6 — Unit tests
python3 -m pytest tests/unit/test_public_gtm_alignment.py tests/unit/test_public_simplification.py -q || fail=1
ok "public GTM + simplification unit tests"

if [[ "$fail" -ne 0 ]]; then
  echo "Run: python3 scripts/rebuild-www-v6.py && bash scripts/verify-ui-build-checklist.sh" >&2
  exit 1
fi
echo "verify-ui-build-checklist PASS"
