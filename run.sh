#!/usr/bin/env bash
export UV_PROJECT_ENVIRONMENT=/tmp/pyludusavi/.venv
export XDG_CACHE_HOME=/tmp/pyludusavi/.cache
export PYTHONPYCACHEPREFIX=/tmp/pyludusavi/__pycache__
export TMPDIR=/tmp/pyludusavi
export PATH="/tmp/pyludusavi/.venv/bin:$PATH"

echo "Using environment: /tmp/pyludusavi/.venv"
exec "$@"
