# Codex PDF Image Reader

PDFs are not just text. Codex needs the diagrams too.

Codex PDF Image Reader is a lightweight Codex skill that turns a PDF into a compact reading pack: extracted text, selected rendered page images, a Markdown report, an HTML review gallery, and a JSON manifest. It is designed for literature review, technical paper reading, thesis reading, and any workflow where figures, tables, plots, equations, screenshots, and architecture diagrams carry the real evidence.

Inspired by the open request for native Codex PDF support in [openai/codex#1797](https://github.com/openai/codex/issues/1797), this repository provides a practical bridge today: render only the pages that matter, inspect them visually, and keep text evidence separate from visual evidence.

[Quick Start](#quick-start) | [What It Does](#what-it-does) | [Install The Skill](#install-the-skill) | [Agent Search Keywords](#agent-search-keywords)

## Why This Exists

Current agent workflows often extract PDF text and silently lose the most important parts:

- system architecture figures;
- model pipeline diagrams;
- result curves and convergence plots;
- ablation tables;
- screenshot examples;
- formula layouts that text extraction scrambles.

This skill codifies a field-tested pattern: text-first reading plus selective visual verification. It does not rasterize a whole paper by default. It finds likely evidence pages, renders a small set of images, and gives Codex a disciplined way to say what is `text-checked`, what is `visual-checked`, and what still needs review.

## What It Does

| Need | Output |
| --- | --- |
| Read the PDF text layer | `text/pages.jsonl` with per-page text |
| Find likely figure/table/chart pages | automatic anchor scoring or explicit `--pages` |
| Render evidence pages | `pages/page_###_144dpi.jpg` |
| Help Codex inspect visuals | `report.md` with image paths and anchors |
| Help humans review quickly | `review.html` gallery |
| Keep runs auditable | `manifest.json` with paths, sizes, versions, and selected pages |

## Quick Start

```bash
git clone https://github.com/parkersix/codex-pdf-image-reader.git
cd codex-pdf-image-reader

python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt

python3 skills/codex-pdf-image-reader/scripts/pdf_image_reader.py path/to/paper.pdf
```

The command prints JSON containing the output directory, report path, and manifest path.

Render specific claim-bearing pages:

```bash
python3 skills/codex-pdf-image-reader/scripts/pdf_image_reader.py path/to/paper.pdf --pages 1,3,9-11 --dpi 144
```

Bound automatic rendering:

```bash
python3 skills/codex-pdf-image-reader/scripts/pdf_image_reader.py path/to/paper.pdf --max-visual-pages 6
```

## Install The Skill

Install into Codex's skill directory:

```bash
bash scripts/install.sh
```

This copies `skills/codex-pdf-image-reader` into:

```text
${CODEX_HOME:-$HOME/.codex}/skills/codex-pdf-image-reader
```

Restart Codex so the skill metadata is discovered. Then ask:

```text
Use $codex-pdf-image-reader to read this PDF with text extraction and selected visual page checks.
```

## Agent Workflow

1. Extract the PDF text layer.
2. Detect figure/table/chart/equation anchors.
3. Render only selected pages, usually 3-8 pages per paper.
4. Inspect rendered images with a vision-capable model or local image review.
5. Write conclusions with evidence labels:
   - `text-checked`
   - `visual-checked`
   - `inferred`
   - `TODO visual verification`

## Example Output

```text
/private/tmp/codex_pdf_image_reader/paper_20260602_153000/
├── manifest.json
├── report.md
├── review.html
├── pages/
│   ├── page_001_144dpi.jpg
│   ├── page_003_144dpi.jpg
│   └── page_009_144dpi.jpg
└── text/
    └── pages.jsonl
```

## Agent Search Keywords

`pdf`, `PDF image reader`, `Codex PDF`, `PDF visual verification`, `PyMuPDF`, `render PDF pages`, `extract PDF text`, `figure-aware reading`, `table-aware reading`, `chart-aware reading`, `diagram-aware reading`, `multimodal PDF`, `literature review`, `paper reading`, `thesis reading`, `architecture diagram`, `experimental curve`, `visual-checked`, `text-checked`.

## Design Principles

- Selective rendering beats full-document rasterization.
- Captions are routing hints, not visual proof.
- Visual claims need rendered page inspection.
- Temporary images should stay outside project repos unless the user asks for durable artifacts.
- Every run should leave a manifest with page numbers, sizes, and paths.

## Dependencies

Required:

- Python 3.10+
- PyMuPDF

Recommended:

- Pillow, for optimized JPEG output
- pypdf and pdfplumber, for future text/table extraction extensions

Install:

```bash
python3 -m pip install -r requirements.txt
```

## License

MIT
