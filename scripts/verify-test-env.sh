#!/usr/bin/env bash
# Offline-friendly defaults for governance pytest bundles (no Postgres/Docker required).
export RUNTIME_EVENT_STORE="${RUNTIME_EVENT_STORE:-memory}"
export INTAKE_PERSISTENCE="${INTAKE_PERSISTENCE:-memory}"
export REDIS_SESSIONS_ENABLED="${REDIS_SESSIONS_ENABLED:-false}"
