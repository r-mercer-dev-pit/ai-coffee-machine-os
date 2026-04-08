#!/usr/bin/env bash
set -euo pipefail

# Activate venv if present
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export HIL_RUN=0
uvicorn rmer_ai_coffee.connectivity.rest_api:app --host 0.0.0.0 --port 8000 --reload
