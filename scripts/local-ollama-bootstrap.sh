#!/usr/bin/env bash
# Bootstrap local Ollama per LOCKED PLAN:
# docs/strategy/local-ollama-agent-runtime-blueprint.md
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${HOME}/.ollama/env"
PLAN="${ROOT}/docs/strategy/local-ollama-agent-runtime-blueprint.md"

echo "== Noetfield local Ollama bootstrap =="
echo "Plan: ${PLAN}"
echo ""

ARCH="$(uname -m)"
if [[ "${ARCH}" != "arm64" ]]; then
  echo "WARN: Locked plan targets Apple Silicon (M5 Pro 48GB). Detected: ${ARCH}"
  echo "      You can still install Ollama; thermals/RAM tables may not apply."
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama not found."
  if [[ "$(uname -s)" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
    echo "Installing via Homebrew: brew install ollama"
    brew install ollama
  else
    echo "Install manually: https://ollama.com/download/mac"
    echo "  or: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
  fi
fi

echo "Ollama version: $(ollama --version 2>/dev/null || echo unknown)"

mkdir -p "${HOME}/.ollama"
if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${ROOT}/docs/strategy/ollama.env.example" "${ENV_FILE}"
  echo "Wrote ${ENV_FILE}"
else
  echo "Exists ${ENV_FILE} (not overwritten)"
fi

# shellcheck disable=SC1090
set -a
source "${ENV_FILE}" 2>/dev/null || true
set +a

if [[ "$(uname -s)" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
  brew services start ollama 2>/dev/null || ollama serve &
else
  ollama serve &
fi

sleep 2
curl -sf "http://127.0.0.1:11434/api/version" >/dev/null && echo "API: OK" || echo "API: start ollama serve"

echo "Pulling locked default model: qwen3:14b"
ollama pull qwen3:14b

echo ""
echo "Locked defaults:"
echo "  Model:      qwen3:14b"
echo "  Keep alive: ${OLLAMA_KEEP_ALIVE:-5m}"
echo "  Context:    ${OLLAMA_NUM_CTX:-2048}"
echo "  Parallel:   ${OLLAMA_NUM_PARALLEL:-1}"
echo "  GPU layers: ${OLLAMA_NUM_GPU:-20}"
echo ""
echo "Test:  ollama run qwen3:14b"
echo "Stop:  ollama stop  (or wait for keep-alive unload)"
echo "Done."
