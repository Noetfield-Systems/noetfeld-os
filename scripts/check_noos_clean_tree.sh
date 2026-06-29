#!/usr/bin/env bash
# Verify the NOOS repo is clean and no run-patch writer is active.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

cd "$ROOT"

if ps -axo command | while IFS= read -r command; do
  case "$command" in
    *run_noetfield_factory_loop_v1.py*)
      printf '%s\n' "$command"
      ;;
  esac
done | read -r active_factory; then
  echo "FAIL: run_noetfield_factory_loop_v1.py is active and may rewrite generated receipts"
  echo "      $active_factory"
  FAIL=1
fi

status="$(git status --porcelain)"
if [[ -n "$status" ]]; then
  echo "FAIL: git working tree is dirty"
  while IFS= read -r line; do
    case "$line" in
      *"docs/run_patches/execution/"*)
        echo "      generated run-patch churn: $line"
        ;;
      *"docs/run_patches/noetfield_run_patch_manifest_10100_v1.json"*)
        echo "      generated manifest runtime churn: $line"
        ;;
      *)
        echo "      source/doc change: $line"
        ;;
    esac
  done <<< "$status"
  FAIL=1
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "NOOS clean-tree check failed"
  exit 1
fi

echo "OK: NOOS working tree clean; no factory writer detected"
