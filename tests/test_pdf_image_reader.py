from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


pytest.importorskip("fitz")


def test_pdf_image_reader_builds_pack(tmp_path: Path) -> None:
    import fitz

    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Sample Paper\nThis page introduces the framework.")
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Fig. 1. Architecture diagram of the system pipeline.")
    page2.draw_rect(fitz.Rect(72, 120, 260, 220), color=(0, 0, 0), width=2)
    doc.save(pdf_path)
    doc.close()

    out_dir = tmp_path / "pack"
    script = Path(__file__).resolve().parents[1] / "skills" / "codex-pdf-image-reader" / "scripts" / "pdf_image_reader.py"
    result = subprocess.run(
        [sys.executable, str(script), str(pdf_path), "--output-dir", str(out_dir), "--max-visual-pages", "2"],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert Path(payload["report"]).exists()
    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "review.html").exists()
    assert (out_dir / "text" / "pages.jsonl").exists()

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["page_count"] == 2
    assert 1 in manifest["selected_pages"]
    assert 2 in manifest["selected_pages"]
    assert manifest["total_image_bytes"] > 0
