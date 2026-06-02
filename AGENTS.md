# AGENTS.md

This repository packages `codex-pdf-image-reader`, a Codex skill for reading PDFs with both extracted text and selected rendered page images.

## First Read

When an agent starts work in this repository, read these files first:

1. `README.md` for the user-facing purpose, install flow, and examples.
2. `skills/codex-pdf-image-reader/SKILL.md` for the actual Codex skill behavior.
3. `skills/codex-pdf-image-reader/scripts/pdf_image_reader.py` before changing runtime behavior.

Keep the skill body concise. Do not add extra documentation files inside `skills/codex-pdf-image-reader/` unless they are directly used by the skill through progressive disclosure.

## Project Shape

- `skills/codex-pdf-image-reader/` is the installable Codex skill.
- `skills/codex-pdf-image-reader/scripts/pdf_image_reader.py` builds the PDF reading pack.
- `skills/codex-pdf-image-reader/scripts/run_pdf_image_reader.sh` selects the best available Python runtime and runs the reader.
- `skills/codex-pdf-image-reader/scripts/bootstrap_runtime.sh` creates or updates the persistent Codex runtime venv.
- `scripts/install.sh` copies the skill into `${CODEX_HOME:-$HOME/.codex}/skills`.
- `tests/` contains the smoke test for pack generation.

## Install Guidance

For Codex users, prefer a Codex-first instruction in docs and examples:

```text
Install the Codex skill from https://github.com/ParkerGong/codex-pdf-image-reader.
Use a persistent Codex venv for its Python dependencies.
Then use $codex-pdf-image-reader to read path/to/paper.pdf with text extraction and selected visual page checks.
```

For manual installation:

```bash
bash scripts/install.sh --with-deps
```

This installs dependencies into:

```text
${CODEX_HOME:-$HOME/.codex}/venvs/codex-pdf-image-reader
```

Do not recommend creating a fresh temporary venv for every PDF run. Temporary venvs are fine for one-off validation or isolated debugging, but the normal user and Codex path should be persistent and user-level.

## Validation

Use the lightest relevant checks for the change:

```bash
bash -n scripts/install.sh
bash -n skills/codex-pdf-image-reader/scripts/bootstrap_runtime.sh
bash -n skills/codex-pdf-image-reader/scripts/run_pdf_image_reader.sh
```

If the persistent runtime exists, validate the runner:

```bash
CODEX_PDF_IMAGE_READER_PYTHON="${CODEX_HOME:-$HOME/.codex}/venvs/codex-pdf-image-reader/bin/python" \
  skills/codex-pdf-image-reader/scripts/run_pdf_image_reader.sh --help
```

If `pytest` is available in the active Python environment:

```bash
python -m pytest -p no:cacheprovider tests
```

If the local Codex skill validator is available:

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/codex-pdf-image-reader
```

Avoid leaving `.pytest_cache/` or `__pycache__/` in the working tree after validation.

## Editing Rules

- Keep README examples Codex-first, with manual shell commands later.
- Keep runtime dependencies in `skills/codex-pdf-image-reader/requirements.txt`; the root `requirements.txt` should delegate to it.
- Prefer PyMuPDF as the default renderer.
- Do not rasterize whole PDFs by default; preserve selective rendering as the core behavior.
- Keep generated reading packs under `/private/tmp/codex_pdf_image_reader/` unless the user asks for durable artifacts.
- When changing output formats, update `manifest.json` fields and the README examples together.
