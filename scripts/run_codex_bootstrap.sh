#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m venv "${ROOT_DIR}/.venv"
"${ROOT_DIR}/.venv/bin/python" -m pip install --upgrade pip

if [[ -f "${ROOT_DIR}/requirements.txt" ]]; then
  "${ROOT_DIR}/.venv/bin/pip" install -r "${ROOT_DIR}/requirements.txt"
fi

if [[ -f "${ROOT_DIR}/backend/requirements.txt" ]]; then
  "${ROOT_DIR}/.venv/bin/pip" install -r "${ROOT_DIR}/backend/requirements.txt"
fi

if [[ -f "${ROOT_DIR}/frontend/package.json" ]]; then
  (cd "${ROOT_DIR}/frontend" && npm install)
fi
