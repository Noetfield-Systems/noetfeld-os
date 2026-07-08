#!/usr/bin/env bash
# Sync nf-probe-cron EXPECTED_GIT_SHA to live platform (delegates to canonical script).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$ROOT/scripts/sync_nf_probe_expected_sha.sh"
