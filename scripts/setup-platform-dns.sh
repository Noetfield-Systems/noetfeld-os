#!/usr/bin/env bash
# Attach platform.noetfield.com to noetfield-systems/www (institutional bridge until full API host).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/www-vercel-canonical.sh
source "$ROOT/scripts/www-vercel-canonical.sh"

export NF_WWW_LIVE_DOMAIN="${NF_PLATFORM_LIVE_DOMAIN:-platform.noetfield.com}"
export NF_WWW_CANONICAL_URL="${NF_PLATFORM_CANONICAL_URL:-https://platform.noetfield.com}"

exec "$ROOT/scripts/setup-www-dns.sh"
