# Visual Reading Guide

Use this reference when a PDF contains figures, tables, charts, diagrams, screenshots, equations, or weak text extraction.

## Evidence Labels

- `text-checked`: Supported by extracted text from the PDF text layer.
- `visual-checked`: Supported by direct inspection of a rendered page image.
- `inferred`: A synthesis made from text and/or visual evidence, but not directly stated.
- `TODO visual verification`: A figure, table, chart, or diagram matters but has not been inspected.
- `scan-or-bad-text`: Text extraction is absent, incomplete, garbled, or OCR-dependent.

## What To Inspect

| Visual type | Inspect for | Typical mistake |
| --- | --- | --- |
| Architecture diagram | Components, arrows, data/control flow, boundaries | Treating caption text as proof of actual topology |
| Model diagram | Inputs, outputs, stages, conditionals, losses | Missing conditional branches or auxiliary modules |
| Experimental curve | Ranking, trend, crossover, convergence, uncertainty | Claiming exact values from rough visual reading |
| Table | Row/column definitions, units, bold/best values, baselines | Copying table claims without checking units |
| Screenshot/example | What is visibly shown, labels, failure cases | Overgeneralizing from one qualitative example |
| Equation/formula | Symbol binding, indices, constraints, layout | Trusting text extraction when symbols are reordered |

## Recommended Agent Sequence

1. Read `report.md` and `manifest.json`.
2. Inspect the rendered images listed under `selected_pages`.
3. For each claim, write the evidence label and PDF page number.
4. Keep exact numeric claims conservative unless values are in text, tables, or clearly legible axes.
5. If a figure-bearing page was not rendered, keep the claim as `TODO visual verification`.

## Output Pattern For Literature Notes

```markdown
## Evidence By Page

- PDF p.N: CONFIRMED text-checked: ...
- PDF p.N: CONFIRMED visual-checked: Fig. X shows ...
- PDF p.N: TODO visual verification: Fig. Y may support ..., but it was not rendered in this pass.

## Risks

- RISK: Curve-level ranking was visually checked, but exact values need table/text confirmation.
```

## Failure Modes

- If PyMuPDF cannot open the PDF, try another PDF reader or repair the PDF before making claims.
- If rendered pages are blank, wrong size, or clipped, rerender at a lower DPI or try Poppler.
- If the PDF is scanned, add an OCR step before text-first reading.
- If the paper is long, render by evidence pages, not by full-document rasterization.
