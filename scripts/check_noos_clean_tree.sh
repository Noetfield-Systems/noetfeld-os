#!/usr/bin/env bash
# Verify the NOOS repo is clean and no run-patch writer is active.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0
GENERATED=0

cd "$ROOT"

is_generated_churn() {
  local path="$1"
  case "$path" in
    docs/run_patches/execution/*|*/docs/run_patches/execution/*) return 0 ;;
    docs/run_patches/noetfield_run_patch_manifest_10100_v1.json|*/docs/run_patches/noetfield_run_patch_manifest_10100_v1.json) return 0 ;;
    receipts/proof/noos-kaizen-*|*/receipts/proof/noos-kaizen-*)
      return 0
      ;;
    receipts/proof/noos-outside-audit-*T*|*/receipts/proof/noos-outside-audit-*T*)
      return 0
      ;;
    receipts/proof/noos-worker-kernel-*T*|*/receipts/proof/noos-worker-kernel-*T*)
      return 0
      ;;
    receipts/proof/noos-tool-broker-*T*|*/receipts/proof/noos-tool-broker-*T*)
      return 0
      ;;
    receipts/proof/noos-github-schedule-a1-v1.json|*/receipts/proof/noos-github-schedule-a1-v1.json)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

active_factory="$(ps -axo command | awk '/[r]un_noetfield_factory_loop_v1.py/ { print; exit }')"
if [[ -n "$active_factory" ]]; then
  echo "FAIL: run_noetfield_factory_loop_v1.py is active and may rewrite generated receipts"
  echo "      $active_factory"
  FAIL=1
fi

status="$(git status --porcelain)"
if [[ -n "$status" ]]; then
  while IFS= read -r line; do
    path="${line:3}"
    if is_generated_churn "$path"; then
      echo "      generated runtime churn (ignored): $line"
      GENERATED=$((GENERATED + 1))
      continue
    fi
    echo "      source/doc change: $line"
    FAIL=1
  done <<< "$status"
  if [[ "$FAIL" -ne 0 ]]; then
    echo "FAIL: git working tree is dirty"
  elif [[ "$GENERATED" -gt 0 ]]; then
    echo "OK: only generated runtime receipt churn present ($GENERATED paths)"
  fi
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo "NOOS clean-tree check failed"
  exit 1
fi

echo "OK: NOOS working tree clean; no factory writer detected"
