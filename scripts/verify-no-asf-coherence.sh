#!/usr/bin/env bash
# Meta-verify: GTM_NEXT vs SHIP_NOW vs manifests; R-011; OPEN_PRS truth; canonical paths.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-no-asf-coherence ==="

# R-011 + locked agentic law on disk
for f in \
  docs/ops/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md \
  .cursor/skills/SKILL-008-agentic-commercial-boundary.md; do
  if [[ -f "$f" ]]; then
    echo "OK   exists $f"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

if grep -q 'R-011' .cursor/agent-memory/MEMORY_LOCKED.yaml 2>/dev/null; then
  echo "OK   R-011 in MEMORY_LOCKED.yaml"
else
  echo "FAIL MEMORY_LOCKED.yaml missing R-011" >&2
  fail=1
fi

# GTM_NEXT and QUICK_PICK alignment
if [[ -f docs/ops/plans/no-asf/GTM_NEXT.md ]] && [[ -f docs/ops/plans/no-asf/QUICK_PICK.md ]]; then
  if grep -q 'GTM_NEXT' docs/ops/plans/no-asf/QUICK_PICK.md; then
    echo "OK   QUICK_PICK references GTM_NEXT"
  else
    echo "FAIL QUICK_PICK missing GTM_NEXT reference" >&2
    fail=1
  fi
  if grep -qE 'no open|Agentic only|ship-design-partner-outreach-026|^1\. \*\*ship-' docs/ops/plans/no-asf/QUICK_PICK.md; then
    echo "OK   QUICK_PICK GTM_NEXT inline (picks, empty queue, or agentic pointer)"
  else
    echo "FAIL QUICK_PICK missing GTM_NEXT inline content" >&2
    fail=1
  fi
  if grep -q 'Agentic only' docs/ops/plans/no-asf/GTM_NEXT.md && grep -q 'ship-design-partner-outreach-026' docs/ops/plans/no-asf/GTM_NEXT.md; then
    echo "OK   GTM_NEXT 026 in agentic section"
  else
    echo "FAIL GTM_NEXT missing agentic 026 section" >&2
    fail=1
  fi
  if grep -q '1000/1000' docs/ops/plans/no-asf/GTM_NEXT.md; then
    echo "OK   GTM_NEXT documents 1000/1000 semantics"
  else
    echo "FAIL GTM_NEXT missing 1000/1000 semantics" >&2
    fail=1
  fi
else
  echo "FAIL missing GTM_NEXT or QUICK_PICK" >&2
  fail=1
fi

if grep -q 'GTM_NEXT' os/SHIP_NOW.md 2>/dev/null; then
  echo "OK   SHIP_NOW references GTM_NEXT"
else
  echo "FAIL SHIP_NOW missing GTM_NEXT reference" >&2
  fail=1
fi

# GTM_PRIORITY agentic fence banner
if grep -q 'agentic only' docs/ops/plans/PROMPT_PACK_LOCKED/GTM_PRIORITY_100.md 2>/dev/null; then
  echo "OK   GTM_PRIORITY_100 agentic fence banner"
else
  echo "FAIL GTM_PRIORITY_100 missing agentic fence banner" >&2
  fail=1
fi

# plan.json done ids should appear in ENGINEERING_DONE_MANIFEST
manifest="docs/ops/plans/PROMPT_PACK_LOCKED/ENGINEERING_DONE_MANIFEST.md"
if [[ -f "$manifest" ]] && command -v python3 >/dev/null 2>&1; then
  missing="$(python3 - <<'PY'
import json, pathlib
root = pathlib.Path(".")
data = json.loads((root / "os/plan.json").read_text())
manifest = (root / "docs/ops/plans/PROMPT_PACK_LOCKED/ENGINEERING_DONE_MANIFEST.md").read_text()
missing = []
for t in data.get("next_tasks", []):
    if t.get("status") == "done":
        tid = t.get("id", "")
        if tid.startswith("ship-") and tid not in manifest:
            missing.append(tid)
print("\n".join(missing))
PY
)"
  if [[ -z "$missing" ]]; then
    echo "OK   plan.json ship-* done ids in ENGINEERING_DONE_MANIFEST"
  else
    echo "FAIL plan.json done ids missing from manifest:" >&2
    echo "$missing" >&2
    fail=1
  fi
fi

# OPEN_PRS.md must not falsely claim closed stale PRs
if [[ -f docs/ops/plans/no-asf/OPEN_PRS.md ]]; then
  if grep -q 'open until founder closes' docs/ops/plans/no-asf/OPEN_PRS.md; then
    echo "OK   OPEN_PRS documents stale PR status honestly"
  elif grep -q 'closed 2026-06-10' docs/ops/plans/no-asf/OPEN_PRS.md; then
    echo "FAIL OPEN_PRS falsely claims stale PRs closed" >&2
    fail=1
  else
    echo "OK   OPEN_PRS present"
  fi
fi

# No docs/reference/ in buyer-facing HTML or copilot markdown
stale_paths="$(rg -l 'docs/reference/' copilot/ governance-console/ index.html trust-ledger/ docs/copilot/ 2>/dev/null || true)"
if [[ -z "$stale_paths" ]]; then
  echo "OK   buyer paths use docs/references/ (no singular drift)"
else
  echo "FAIL docs/reference/ in buyer-facing paths:" >&2
  echo "$stale_paths" >&2
  fail=1
fi

# cursor-reply SHA freshness (warn if reply cites old pre-merge base)
reply="reports/cursor-reply-latest.txt"
if [[ -f "$reply" ]]; then
  head_sha="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
  if grep -q "$head_sha" "$reply" 2>/dev/null; then
    echo "OK   cursor-reply cites current HEAD ($head_sha)"
  elif grep -q '76a5c6a\|post-audit\|PR #39 merged' "$reply" 2>/dev/null; then
    echo "OK   cursor-reply post-merge truth"
  else
    echo "WARN cursor-reply may be stale vs HEAD $head_sha — refresh after closeout"
  fi
fi

# PR warnings (non-fatal)
if command -v gh >/dev/null 2>&1; then
  stale_prs="$(gh pr list --state open --json number,headRefName --jq '.[] | select(.headRefName | test("trustfield-scope|governance-console")) | .number' 2>/dev/null || true)"
  if [[ -n "$stale_prs" ]]; then
    echo "WARN stale out-of-scope PR(s) still open: $stale_prs — founder should close"
  else
    echo "OK   no open trustfield-scope/governance-console PRs"
  fi
  ship_prs="$(gh pr list --state open --json number,headRefName --jq '.[] | select(.headRefName | test("^cursor/(no-asf|10-phase|post-audit)")) | .number' 2>/dev/null || true)"
  if [[ -n "$ship_prs" ]]; then
    echo "WARN open ship PR(s): $ship_prs — merge before next iter closeout"
  else
    echo "OK   no open cursor ship PRs"
  fi
else
  echo "SKIP gh not available for PR checks"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-no-asf-coherence passed."
  exit 0
fi
exit 1
