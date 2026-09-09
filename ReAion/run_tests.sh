#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
"${PYTHON:-python3}" -m unittest discover -s tests -v
"${PYTHON:-python3}" -m compileall -q .
"${PYTHON:-python3}" preflight.py
