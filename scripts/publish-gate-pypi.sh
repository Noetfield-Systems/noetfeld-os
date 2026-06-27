#!/usr/bin/env bash
# Publish noetfield-gate to TestPyPI and/or production PyPI.
# Requires: PYPI_API_TOKEN and/or PYPI_TEST_API_TOKEN in ~/.sina/secrets.env
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f "$HOME/.sina/secrets.env" ]]; then
  # shellcheck disable=SC1091
  set -a
  source "$HOME/.sina/secrets.env"
  set +a
fi

python3 -m pip install -q build twine
python3 -m pytest -q tests/test_noetfield_gate.py
python3 -m build
python3 -m twine check dist/*

TARGET="${1:-all}"

publish_test() {
  if [[ -z "${PYPI_TEST_API_TOKEN:-}" ]]; then
    echo "skip TestPyPI — PYPI_TEST_API_TOKEN not set"
    return 0
  fi
  python3 -m twine upload --repository testpypi dist/* \
    -u __token__ -p "$PYPI_TEST_API_TOKEN"
  echo "TestPyPI: https://test.pypi.org/project/noetfield-gate/"
}

publish_prod() {
  if [[ -z "${PYPI_API_TOKEN:-}" ]]; then
    echo "ERROR: PYPI_API_TOKEN not set (add to ~/.sina/secrets.env)" >&2
    exit 1
  fi
  python3 -m twine upload dist/* -u __token__ -p "$PYPI_API_TOKEN"
  echo "PyPI: https://pypi.org/project/noetfield-gate/"
}

case "$TARGET" in
  test) publish_test ;;
  prod) publish_prod ;;
  all)
    publish_test
    publish_prod
    ;;
  *)
    echo "usage: $0 [test|prod|all]" >&2
    exit 2
    ;;
esac
