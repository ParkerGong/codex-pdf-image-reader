#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE="${REPO_ROOT}/skills/codex-pdf-image-reader"
DEST_ROOT="${CODEX_HOME:-${HOME}/.codex}/skills"
DEST="${DEST_ROOT}/codex-pdf-image-reader"

mkdir -p "${DEST_ROOT}" "${DEST}"
cp -R "${SOURCE}/." "${DEST}/"

echo "Installed codex-pdf-image-reader skill to ${DEST}"
echo "Restart Codex so the skill is discovered."
