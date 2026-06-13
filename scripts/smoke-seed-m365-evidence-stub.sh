#!/usr/bin/env bash
# Smoke: seed-m365-evidence-stub is idempotent (safe double-run).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
chmod +x scripts/seed-m365-evidence-stub.sh
./scripts/seed-m365-evidence-stub.sh
./scripts/seed-m365-evidence-stub.sh
echo "smoke-seed-m365-evidence-stub PASS"
