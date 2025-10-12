#!/usr/bin/env bash
set -euo pipefail

# venv
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# pip base
python -m pip install --upgrade pip wheel setuptools

# requirements
pip install -r requirements.txt

echo "Environment ready. Activate with: source .venv/bin/activate"

