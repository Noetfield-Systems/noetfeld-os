#!/usr/bin/env bash
# verify-nf-agent-report-language.sh — machine-enforced report language law
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-nf-agent-report-language ==="

for f in \
  data/nf-agent-report-language-standard-v1.json \
  data/nf-founder-reply-glossary-v1.json \
  scripts/nf_agent_report_language_gate_v1.py \
  scripts/nf_founder_reply_loop_v1.py \
  .cursor/rules/nf-agent-report-language.mdc; do
  [[ -f "$f" ]] || { echo "FAIL missing $f" >&2; fail=1; continue; }
  echo "OK   $f"
done

python3 scripts/nf_agent_report_language_gate_v1.py --scan-text "You asked why cloud cannot see Mac work. Because nothing was on git main yet — so the cloud agent had nothing to read." --json >/dev/null || fail=1
echo "OK   gate accepts plain explanation"

python3 scripts/nf_agent_report_language_gate_v1.py --scan-text "email-defer · ON · main=5/5 · sites=RED · lift=NO" --json >/dev/null && {
  echo "FAIL gate must reject receipt-only parrot" >&2
  fail=1
} || echo "OK   gate rejects receipt parrot"

reply="reports/cursor-reply-latest.txt"
if [[ -f "$reply" ]]; then
  if python3 scripts/nf_agent_report_language_gate_v1.py --scan-file "$reply" --json >/dev/null; then
    echo "OK   cursor-reply language gate"
  else
    echo "FAIL cursor-reply violates language law — rewrite for founder understanding" >&2
    python3 scripts/nf_agent_report_language_gate_v1.py --scan-file "$reply" --json 2>/dev/null | head -20 >&2 || true
    fail=1
  fi
else
  echo "SKIP cursor-reply (no file yet)"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-nf-agent-report-language: PASS"
else
  echo ""
  echo "verify-nf-agent-report-language: FAIL"
  exit 1
fi
