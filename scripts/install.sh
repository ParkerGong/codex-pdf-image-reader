#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE="${REPO_ROOT}/skills/codex-pdf-image-reader"
DEST_ROOT="${CODEX_HOME:-${HOME}/.codex}/skills"
DEST="${DEST_ROOT}/codex-pdf-image-reader"
WITH_DEPS=0

usage() {
  cat <<'EOF'
Usage: bash scripts/install.sh [--with-deps]

Installs the codex-pdf-image-reader skill into ${CODEX_HOME:-$HOME/.codex}/skills.

Options:
  --with-deps  Also create/update a persistent runtime venv at
               ${CODEX_HOME:-$HOME/.codex}/venvs/codex-pdf-image-reader.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-deps)
      WITH_DEPS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "${DEST_ROOT}" "${DEST}"
cp -R "${SOURCE}/." "${DEST}/"

echo "Installed codex-pdf-image-reader skill to ${DEST}"
if [[ "${WITH_DEPS}" -eq 1 ]]; then
  "${DEST}/scripts/bootstrap_runtime.sh"
else
  echo "Optional: run '${DEST}/scripts/bootstrap_runtime.sh' once to install dependencies in a persistent Codex venv."
fi
echo "Restart Codex so the skill is discovered."
