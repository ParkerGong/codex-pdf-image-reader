#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REQ_FILE="${SKILL_DIR}/requirements.txt"
VENV_DIR="${CODEX_PDF_IMAGE_READER_VENV:-${CODEX_HOME:-${HOME}/.codex}/venvs/codex-pdf-image-reader}"
PYTHON_BIN="${PYTHON:-python3}"

if [[ ! -f "${REQ_FILE}" ]]; then
  echo "requirements.txt not found next to the skill: ${REQ_FILE}" >&2
  exit 1
fi

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  mkdir -p "$(dirname "${VENV_DIR}")"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -r "${REQ_FILE}"

echo "Codex PDF Image Reader runtime ready:"
echo "${VENV_DIR}/bin/python"
