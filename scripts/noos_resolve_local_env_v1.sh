#!/usr/bin/env bash
# Canonical NOOS / Noetfield platform vault paths (not SourceA).
set -euo pipefail

export NOETFIELD_PLATFORM_SECRETS="${NOETFIELD_PLATFORM_SECRETS:-$HOME/.noetfield-platform-secrets}"
export NOOS_LOCAL_ENV="${NOOS_LOCAL_ENV:-$NOETFIELD_PLATFORM_SECRETS/noos-local.env}"
export NOETFIELD_LOCAL_ENV="${NOETFIELD_LOCAL_ENV:-$NOETFIELD_PLATFORM_SECRETS/noetfield.env}"
export NOETFIELD_DB_ENV="${NOETFIELD_DB_ENV:-$NOETFIELD_PLATFORM_SECRETS/noetfield-db.env}"
