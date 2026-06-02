#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${SKILL_DIR}/../.." && pwd)"
DEFAULT_VENV="${CODEX_HOME:-${HOME}/.codex}/venvs/codex-pdf-image-reader"

PYTHON_BIN=""

if [[ -n "${CODEX_PDF_IMAGE_READER_PYTHON:-}" ]]; then
  PYTHON_BIN="${CODEX_PDF_IMAGE_READER_PYTHON}"
elif [[ -n "${CODEX_PDF_IMAGE_READER_VENV:-}" && -x "${CODEX_PDF_IMAGE_READER_VENV}/bin/python" ]]; then
  PYTHON_BIN="${CODEX_PDF_IMAGE_READER_VENV}/bin/python"
elif [[ -x "${DEFAULT_VENV}/bin/python" ]]; then
  PYTHON_BIN="${DEFAULT_VENV}/bin/python"
elif [[ -x "${PWD}/.venv/bin/python" ]]; then
  PYTHON_BIN="${PWD}/.venv/bin/python"
elif [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
else
  PYTHON_BIN="$(command -v python3 || true)"
fi

if [[ -z "${PYTHON_BIN}" || ! -x "${PYTHON_BIN}" ]]; then
  echo "No usable Python found. Install Python 3.10+ first." >&2
  exit 2
fi

if ! "${PYTHON_BIN}" -c "import fitz" >/dev/null 2>&1; then
  echo "Missing PyMuPDF for ${PYTHON_BIN}." >&2
  echo "Run once: ${SCRIPT_DIR}/bootstrap_runtime.sh" >&2
  echo "Or set CODEX_PDF_IMAGE_READER_PYTHON to a Python with PyMuPDF installed." >&2
  exit 2
fi

exec "${PYTHON_BIN}" "${SCRIPT_DIR}/pdf_image_reader.py" "$@"
