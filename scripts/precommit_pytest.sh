#!/usr/bin/env bash
# Pre-commit pytest hook: reinstall the checkout into a venv outside the repo, then test the installed package.
set -euo pipefail

venv="${AIORAINPOINT_TEST_VENV:-$HOME/venvs/aiorainpoint}"
py="$venv/bin/python"
if [[ ! -x "$py" ]]; then
    echo "No test venv at $venv. Create it as CONTRIBUTING.md describes, or point AIORAINPOINT_TEST_VENV at one." >&2
    exit 1
fi

# A uv-made venv has no pip.
if command -v uv >/dev/null; then
    uv pip install -q --python "$py" --reinstall --no-deps .
else
    "$py" -m pip install -q --force-reinstall --no-deps .
fi
exec "$py" -m pytest -q --no-cov
