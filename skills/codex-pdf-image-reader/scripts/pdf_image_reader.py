#!/usr/bin/env python3
"""Build a compact text-plus-image reading pack for a PDF."""

from __future__ import annotations

import argparse
import html
import importlib.metadata
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ANCHOR_RE = re.compile(
    r"\b(fig(?:ure)?\.?|table|algorithm|architecture|framework|pipeline|diagram|chart|curve|plot|ablation|equation|formula|screenshot)\b"
    r"|[图表算法架构框架流程曲线公式]",
    re.IGNORECASE,
)
CAPTION_RE = re.compile(r"^\s*(fig(?:ure)?\.?|table|algorithm|图|表)\s*[\dIVXivx一二三四五六七八九十]", re.IGNORECASE)


@dataclass
class PageInfo:
    page: int
    chars: int
    score: int
    anchors: list[str]
    text_preview: str


def import_fitz():
    try:
        import fitz  # type: ignore
    except ImportError:
        print(
            "Missing dependency: PyMuPDF. Install with: python3 -m pip install PyMuPDF pypdf pdfplumber Pillow",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return fitz


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def safe_stem(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", path.stem).strip("._-")
    return (stem or "pdf")[:90]


def parse_pages(spec: str, page_count: int) -> list[int]:
    pages: set[int] = set()
    for raw_part in spec.split(","):
        part = raw_part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            if start > end:
                raise ValueError(f"Invalid page range: {part}")
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    bad = [p for p in pages if p < 1 or p > page_count]
    if bad:
        raise ValueError(f"Page(s) outside 1-{page_count}: {bad}")
    return sorted(pages)


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def extract_anchors(text: str, limit: int = 12) -> list[str]:
    anchors: list[str] = []
    for line in text.splitlines():
        clean = normalize_line(line)
        if not clean:
            continue
        if ANCHOR_RE.search(clean) or CAPTION_RE.search(clean):
            anchors.append(clean[:240])
        if len(anchors) >= limit:
            break
    return anchors


def page_score(page_index: int, text: str, anchors: list[str]) -> int:
    score = 0
    if page_index == 0:
        score += 5
    score += min(len(anchors), 10) * 3
    lowered = text.lower()
    for term in ("architecture", "framework", "pipeline", "result", "experiment", "ablation", "simulation", "diagram"):
        if term in lowered:
            score += 2
    for term in ("架构", "框架", "流程", "实验", "仿真", "结果", "曲线"):
        if term in text:
            score += 2
    return score


def text_preview(text: str, max_chars: int = 700) -> str:
    clean = normalize_line(text)
    return clean[:max_chars]


def collect_page_text(doc) -> tuple[list[PageInfo], list[str]]:
    infos: list[PageInfo] = []
    texts: list[str] = []
    for index in range(doc.page_count):
        page = doc.load_page(index)
        text = page.get_text("text") or ""
        anchors = extract_anchors(text)
        infos.append(
            PageInfo(
                page=index + 1,
                chars=len(text),
                score=page_score(index, text, anchors),
                anchors=anchors,
                text_preview=text_preview(text),
            )
        )
        texts.append(text)
    return infos, texts


def choose_pages(infos: list[PageInfo], max_pages: int) -> list[int]:
    if not infos:
        return []
    ranked = sorted(infos, key=lambda p: (p.score, p.chars), reverse=True)
    chosen = {1}
    for info in ranked:
        if info.score <= 0 and len(chosen) >= 1:
            continue
        chosen.add(info.page)
        if len(chosen) >= max_pages:
            break
    return sorted(chosen)


def save_pages_jsonl(path: Path, infos: list[PageInfo], texts: list[str]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for info, text in zip(infos, texts):
            row = {
                "page": info.page,
                "chars": info.chars,
                "score": info.score,
                "anchors": info.anchors,
                "text": text,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def render_page(doc, page_num: int, pages_dir: Path, dpi: int, image_format: str, quality: int) -> dict:
    fitz = import_fitz()
    page = doc.load_page(page_num - 1)
    matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=matrix, alpha=False)

    ext = "jpg" if image_format.lower() in {"jpg", "jpeg"} else "png"
    out_path = pages_dir / f"page_{page_num:03d}_{dpi}dpi.{ext}"

    if ext == "jpg":
        try:
            from PIL import Image

            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            image.save(out_path, format="JPEG", quality=quality, optimize=True)
        except ImportError:
            out_path = pages_dir / f"page_{page_num:03d}_{dpi}dpi.png"
            pix.save(str(out_path))
    else:
        pix.save(str(out_path))

    return {
        "page": page_num,
        "path": str(out_path),
        "relative_path": str(out_path.relative_to(pages_dir.parent)),
        "width": pix.width,
        "height": pix.height,
        "bytes": out_path.stat().st_size,
    }


def write_report(
    report_path: Path,
    pdf_path: Path,
    page_count: int,
    selected_pages: list[int],
    page_infos: list[PageInfo],
    rendered: list[dict],
    output_dir: Path,
    dpi: int,
) -> None:
    info_by_page = {info.page: info for info in page_infos}
    total_bytes = sum(item["bytes"] for item in rendered)
    lines = [
        "# PDF Image Reading Pack",
        "",
        f"- Source PDF: `{pdf_path}`",
        f"- Page count: `{page_count}`",
        f"- Output directory: `{output_dir}`",
        f"- Selected visual pages: `{', '.join(map(str, selected_pages))}`",
        f"- Rendered image total: `{total_bytes}` bytes",
        f"- DPI: `{dpi}`",
        "",
        "## Agent Next Steps",
        "",
        "1. Read `text/pages.jsonl` for the text layer.",
        "2. Inspect the rendered page images below for diagrams, tables, charts, screenshots, equations, and qualitative examples.",
        "3. Label claims as `text-checked`, `visual-checked`, `inferred`, or `TODO visual verification`.",
        "4. Avoid exact curve or table-value claims unless the values are legible or confirmed in text.",
        "",
        "## Rendered Pages",
        "",
    ]
    rendered_by_page = {item["page"]: item for item in rendered}
    for page_num in selected_pages:
        item = rendered_by_page.get(page_num)
        info = info_by_page.get(page_num)
        lines.append(f"### PDF p.{page_num}")
        lines.append("")
        if item:
            lines.append(f"- Image: `{item['path']}`")
            lines.append(f"- Dimensions: `{item['width']} x {item['height']}`")
            lines.append(f"- Size: `{item['bytes']}` bytes")
        if info:
            lines.append(f"- Text chars: `{info.chars}`")
            if info.anchors:
                lines.append("- Anchors:")
                for anchor in info.anchors[:8]:
                    lines.append(f"  - {anchor}")
            else:
                lines.append("- Anchors: none detected")
            if info.text_preview:
                lines.append("")
                lines.append("Text preview:")
                lines.append("")
                lines.append("```text")
                lines.append(info.text_preview)
                lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Temporary File Note",
            "",
            "If this pack was written under `/private/tmp`, report whether the rendered images were retained, deleted, or moved to the active project's temporary trash/archive path.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def write_html(
    html_path: Path,
    pdf_path: Path,
    selected_pages: list[int],
    page_infos: list[PageInfo],
    rendered: list[dict],
) -> None:
    info_by_page = {info.page: info for info in page_infos}
    rendered_by_page = {item["page"]: item for item in rendered}
    sections: list[str] = []
    for page_num in selected_pages:
        item = rendered_by_page.get(page_num)
        info = info_by_page.get(page_num)
        anchors = ""
        if info and info.anchors:
            anchors = "<ul>" + "".join(f"<li>{html.escape(a)}</li>" for a in info.anchors[:10]) + "</ul>"
        preview = html.escape(info.text_preview if info else "")
        image = ""
        if item:
            image = f'<img src="{html.escape(item["relative_path"])}" alt="PDF page {page_num}">'
        sections.append(
            f"""
            <section>
              <h2>PDF p.{page_num}</h2>
              {image}
              <h3>Anchors</h3>
              {anchors or "<p>No anchors detected.</p>"}
              <h3>Text Preview</h3>
              <pre>{preview}</pre>
            </section>
            """
        )
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PDF Image Reading Pack</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111827; background: #f8fafc; }}
    header {{ padding: 24px 32px; background: #111827; color: white; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    section {{ margin: 0 0 28px; padding: 20px; background: white; border: 1px solid #e5e7eb; border-radius: 8px; }}
    img {{ display: block; max-width: 100%; height: auto; border: 1px solid #d1d5db; background: white; }}
    pre {{ white-space: pre-wrap; background: #f3f4f6; padding: 12px; border-radius: 6px; overflow-wrap: anywhere; }}
    h1, h2, h3 {{ letter-spacing: 0; }}
  </style>
</head>
<body>
  <header>
    <h1>PDF Image Reading Pack</h1>
    <p>{html.escape(str(pdf_path))}</p>
  </header>
  <main>
    {''.join(sections)}
  </main>
</body>
</html>
"""
    html_path.write_text(doc, encoding="utf-8")


def build_manifest(
    pdf_path: Path,
    output_dir: Path,
    page_count: int,
    selected_pages: list[int],
    page_infos: list[PageInfo],
    rendered: list[dict],
    dpi: int,
    image_format: str,
) -> dict:
    info_by_page = {info.page: info for info in page_infos}
    return {
        "source_pdf": str(pdf_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output_dir),
        "page_count": page_count,
        "selected_pages": selected_pages,
        "renderer": "PyMuPDF",
        "dpi": dpi,
        "image_format": image_format,
        "dependencies": {
            "PyMuPDF": package_version("PyMuPDF"),
            "pypdf": package_version("pypdf"),
            "pdfplumber": package_version("pdfplumber"),
            "Pillow": package_version("Pillow"),
        },
        "pages": [
            {
                "page": item["page"],
                "image_path": item["path"],
                "relative_image_path": item["relative_path"],
                "width": item["width"],
                "height": item["height"],
                "bytes": item["bytes"],
                "text_chars": info_by_page[item["page"]].chars if item["page"] in info_by_page else None,
                "anchors": info_by_page[item["page"]].anchors if item["page"] in info_by_page else [],
            }
            for item in rendered
        ],
        "total_image_bytes": sum(item["bytes"] for item in rendered),
        "evidence_policy": [
            "Captions route pages; rendered images provide visual evidence.",
            "Use text-checked and visual-checked labels separately.",
            "Do not render full PDFs by default.",
        ],
    }


def default_output_dir(pdf_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("/private/tmp/codex_pdf_image_reader") / f"{safe_stem(pdf_path)}_{timestamp}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a text-plus-image PDF reading pack for Codex.")
    parser.add_argument("pdf", help="Path to the PDF file.")
    parser.add_argument("--pages", help="1-indexed pages or ranges to render, e.g. 1,3,9-11.")
    parser.add_argument("--output-dir", help="Output directory. Defaults to /private/tmp/codex_pdf_image_reader/<pdf>_<timestamp>.")
    parser.add_argument("--max-visual-pages", type=int, default=8, help="Maximum pages to auto-select when --pages is omitted.")
    parser.add_argument("--dpi", type=int, default=144, help="Render DPI for selected pages.")
    parser.add_argument("--format", choices=["jpg", "png"], default="jpg", help="Rendered image format.")
    parser.add_argument("--quality", type=int, default=82, help="JPEG quality when --format jpg.")
    args = parser.parse_args(argv)

    fitz = import_fitz()
    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else default_output_dir(pdf_path)
    pages_dir = output_dir / "pages"
    text_dir = output_dir / "text"
    pages_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    try:
        page_infos, texts = collect_page_text(doc)
        if args.pages:
            selected_pages = parse_pages(args.pages, doc.page_count)
        else:
            selected_pages = choose_pages(page_infos, max(1, args.max_visual_pages))

        save_pages_jsonl(text_dir / "pages.jsonl", page_infos, texts)
        rendered = [render_page(doc, page_num, pages_dir, args.dpi, args.format, args.quality) for page_num in selected_pages]

        write_report(output_dir / "report.md", pdf_path, doc.page_count, selected_pages, page_infos, rendered, output_dir, args.dpi)
        write_html(output_dir / "review.html", pdf_path, selected_pages, page_infos, rendered)
        manifest = build_manifest(pdf_path, output_dir, doc.page_count, selected_pages, page_infos, rendered, args.dpi, args.format)
        (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    finally:
        doc.close()

    print(json.dumps({"output_dir": str(output_dir), "report": str(output_dir / "report.md"), "manifest": str(output_dir / "manifest.json")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
