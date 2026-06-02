---
name: codex-pdf-image-reader
description: Read PDFs with both extracted text and selected rendered page images. Use when Codex needs figure-aware, table-aware, chart-aware, screenshot-aware, or diagram-aware PDF understanding for literature review, paper reading, technical reports, theses, architecture diagrams, experimental plots, equations, scanned/poor text PDFs, or any task where plain text extraction is not enough.
---

# Codex PDF Image Reader

## Overview

Use this skill to build a compact "reading pack" from a PDF: extracted text, selected page images, a Markdown report, an HTML gallery, and a JSON manifest. The goal is to let Codex reason over PDFs with visual evidence instead of treating figures, tables, charts, and model diagrams as invisible.

## Quick Start

Run the bundled runner on the PDF. Resolve `scripts/run_pdf_image_reader.sh` relative to this `SKILL.md`. Prefer a temporary output directory unless the user asks for durable artifacts.

```bash
scripts/run_pdf_image_reader.sh path/to/paper.pdf
```

For claim-bearing figures, provide explicit pages:

```bash
scripts/run_pdf_image_reader.sh path/to/paper.pdf --pages 1,3,9-11 --dpi 144
```

## Runtime Policy

Prefer a persistent Codex runtime instead of creating a new temporary virtual environment for every PDF. The default persistent runtime is:

```text
${CODEX_HOME:-$HOME/.codex}/venvs/codex-pdf-image-reader
```

If dependencies are missing and the user permits dependency installation, run once:

```bash
scripts/bootstrap_runtime.sh
```

The runner also honors `CODEX_PDF_IMAGE_READER_PYTHON` and `CODEX_PDF_IMAGE_READER_VENV`. Use a temporary venv only for one-off validation or when a persistent user-level environment is not allowed.

## Workflow

1. **Extract text first.** Use text to identify title, abstract, methods, conclusions, captions, equations, tables, figure anchors, and candidate evidence pages.
2. **Classify visual need.** Mark the PDF `text-ok`, `visual-needed`, or `scan-or-bad-text`.
3. **Render selectively.** Render only evidence-bearing pages, usually 3-8 pages per paper. Do not rasterize a whole paper by default.
4. **Inspect images.** Use available vision tools or local image inspection on rendered pages, especially diagrams, tables, plots, screenshots, and formula-heavy pages.
5. **Separate evidence status.** Distinguish `text-checked`, `visual-checked`, `inferred`, and `TODO visual verification`.
6. **Record temporary files.** Report output paths and size. Clean or archive temporary images according to the active project rules.

## Reading Pack Outputs

The script writes:

- `report.md`: agent-facing reading plan with selected page image paths.
- `review.html`: browser-friendly gallery pairing rendered pages with text snippets and anchors.
- `manifest.json`: machine-readable source path, page count, selected pages, output files, dimensions, byte sizes, and dependency versions.
- `text/pages.jsonl`: per-page extracted text for text-first reading.
- `pages/page_###_###dpi.jpg`: selected rendered pages.

## Page Selection

Use explicit `--pages` whenever the user or text extraction identifies important pages. Otherwise, let the script rank pages using anchors such as:

- `Fig.`, `Figure`, `Table`, `Algorithm`, `architecture`, `framework`, `pipeline`, `curve`, `ablation`, `diagram`
- Chinese anchors such as `图`, `表`, `算法`, `架构`, `框架`, `流程`, `曲线`, `公式`

Keep rendered pages bounded with `--max-visual-pages`. Raise it only when the PDF is figure-dense and the user needs deeper review.

## Visual Reading Rules

- Captions are routing hints, not visual evidence.
- Do not claim exact curve values unless the numeric values are visible in text/table or have been carefully read from the rendered figure.
- For architecture and model diagrams, describe components, arrows, inputs/outputs, and what the diagram proves.
- For tables, extract the row/column meaning and flag any values that require manual verification.
- For screenshots or examples, distinguish what is visibly shown from what the paper claims in prose.
- For scanned or garbled PDFs, state that OCR or manual review is still required.

For a more detailed checklist, read `references/visual-reading-guide.md`.

## Temporary File Discipline

Default output goes under `/private/tmp/codex_pdf_image_reader/`. If the active project has stricter temporary-file rules, follow those rules. Always report:

- output directory;
- rendered page count;
- total image size;
- whether images were deleted, retained, or moved to a temporary trash/archive path.

Do not leave important evidence only in chat. When the user needs a durable literature note, write or update the requested local artifact with page numbers and evidence status.
