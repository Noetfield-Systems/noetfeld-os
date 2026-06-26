#!/usr/bin/env bash
# prove-nf-factory-spine.sh — wrapper for CI/Makefile
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/prove-nf-factory-spine-v1.py "$@"
