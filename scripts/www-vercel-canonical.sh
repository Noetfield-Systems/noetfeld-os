#!/usr/bin/env bash
# Canonical Noetfield www on Vercel — single project, no duplicates.
# Source this from deploy/heal scripts; do not fork per agent.
set -euo pipefail

export NF_VERCEL_SCOPE="${NF_VERCEL_SCOPE:-noetfield-systems}"
export NF_VERCEL_PROJECT="${NF_VERCEL_PROJECT:-www}"
export NF_WWW_CANONICAL_URL="${NF_WWW_CANONICAL_URL:-https://www.noetfield.com}"
export NF_WWW_LIVE_DOMAIN="${NF_WWW_LIVE_DOMAIN:-www.noetfield.com}"
# Legacy slugs to remove if they reappear (duplicate CLI deploys)
export NF_WWW_DEPLOY_URL="${NF_WWW_DEPLOY_URL:-https://project-gc7lm.vercel.app}"
export NF_INTAKE_ENV_KEYS="RESEND_API_KEY INTAKE_EMAIL_FROM INTAKE_EMAIL_TO INTAKE_AUTO_ACK_ENABLED"
export NF_SECRETS_VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
