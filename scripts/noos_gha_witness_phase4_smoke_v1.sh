#!/usr/bin/env bash
# Dispatch Phase-4 GHA sustain/audit witnesses and wait for success.
set -euo pipefail

REPO="${GITHUB_REPO:-Noetfield-Systems/noetfeld-os}"
WAIT_SEC="${WAIT_SEC:-900}"

log() { printf '[witness-phase4-smoke] %s\n' "$*"; }

if ! command -v gh >/dev/null 2>&1; then
  echo "FAIL: gh CLI required" >&2
  exit 1
fi

workflows=(
  noos-machine-audit-witness.yml
  noos-liveness-registry-witness.yml
  noos-sandbox-url-sweep-witness.yml
)

declare -a RUN_IDS=()

for wf in "${workflows[@]}"; do
  log "dispatch $wf"
  gh workflow run "$wf" --repo "$REPO" >/dev/null 2>&1 || true
  sleep 3
  run_id="$(gh run list --repo "$REPO" --workflow="$wf" --limit 1 --json databaseId --jq '.[0].databaseId')"
  log "  run_id=$run_id"
  RUN_IDS+=("$run_id")
done

fail=0
for i in "${!workflows[@]}"; do
  wf="${workflows[$i]}"
  run_id="${RUN_IDS[$i]}"
  log "wait $wf ($run_id) up to ${WAIT_SEC}s"
  if ! gh run watch "$run_id" --repo "$REPO" --exit-status --interval 15 2>/dev/null; then
    log "FAIL: $wf run $run_id"
    gh run view "$run_id" --repo "$REPO" --log-failed 2>&1 | tail -20 || true
    fail=1
  else
    log "OK: $wf"
  fi
done

if [[ "$fail" -ne 0 ]]; then
  log "witness phase4 smoke: FAIL"
  exit 1
fi

log "witness phase4 smoke: PASS (${#workflows[@]} workflows)"
exit 0
