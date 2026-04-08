#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install poetry
poetry install

echo "Development environment ready. Activate with: source .venv/bin/activate" 
