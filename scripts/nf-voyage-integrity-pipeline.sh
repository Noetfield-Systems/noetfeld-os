#!/usr/bin/env bash
# nf-voyage-integrity-pipeline.sh — anti-drift queue alignment
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/nf_voyage_integrity_v1.py --json "$@"
