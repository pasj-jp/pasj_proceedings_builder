"""PDF processing helpers for proceedings artifacts."""

from __future__ import annotations

import shutil
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from models import Paper, ProcessResult

try:
    import fitz
except ImportError:  # pragma: no cover - exercised only before install
    fitz = None


JST = timezone(timedelta(hours=9))


def newest_pdf_for_talk(source_root: Path, talk_id: str) -> Path | None:
    talk_dir = source_root / talk_id[:4] / talk_id
    if not talk_dir.is_dir():
        return None

    candidates = [
        path
        for path in talk_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".pdf"
        and path.name.startswith(talk_id)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def text_width(text: str, fontname: str, fontsize: float, fontfile: Path | None = None) -> float:
    if fontfile is not None:
        font = fitz.Font(fontfile=str(fontfile))
    else:
        font = fitz.Font(fontname=fontname)
    return font.text_length(text, fontsize)


def insert_centered_text(
    page: Any,
    text: str,
    y: float,
    fontname: str,
    fontsize: float,
    color: tuple[float, float, float],
    fontfile: Path | None = None,
) -> None:
    width = text_width(text, fontname, fontsize, fontfile)
    x = (page.rect.width - width) / 2
    kwargs: dict[str, Any] = {
        "fontsize": fontsize,
        "fontname": fontname,
        "color": color,
    }
    if fontfile is not None:
        kwargs["fontfile"] = str(fontfile)
    page.insert_text(fitz.Point(x, y), text, **kwargs)


def process_pdf(
    source_pdf: Path,
    output_pdf: Path,
    paper: Paper,
    start_page: int,
    volume: str,
    header1: str,
    header2: str,
    font_dir: Path,
    dry_run: bool,
) -> int:
    if fitz is None:
        raise RuntimeError("PyMuPDF is not installed. Run: pip install -r pdf_processing/requirements.txt")

    doc = fitz.open(source_pdf)
    page_count = doc.page_count
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    italic_font = font_dir / "timesi.ttf"
    bold_font = font_dir / "timesbd.ttf"
    regular_font = font_dir / "times.ttf"
    use_files = italic_font.exists() and bold_font.exists() and regular_font.exists()

    font_italic = "TimesNewRomanItalic" if use_files else "tiit"
    font_bold = "TimesNewRomanBold" if use_files else "tibo"
    font_regular = "TimesNewRoman" if use_files else "tiro"
    italic_file = italic_font if use_files else None
    bold_file = bold_font if use_files else None
    regular_file = regular_font if use_files else None

    blue = (0, 0, 1)
    margin = 58
    paper_id = f"{volume}  {paper.talk_id}"

    for page_index, page in enumerate(doc):
        page_number = start_page + page_index

        # Match the legacy CGI's fixed media box: 595 x 791 pt.
        page.set_mediabox(fitz.Rect(0, 0, 595, 791))

        insert_centered_text(page, header1, 15, font_italic, 10, blue, italic_file)
        insert_centered_text(page, header2, 26, font_italic, 10, blue, italic_file)

        paper_id_width = text_width(paper_id, font_bold, 10.5, bold_file)
        if page_number % 2:
            x = page.rect.width - margin - paper_id_width
        else:
            x = margin
        kwargs: dict[str, Any] = {
            "fontsize": 10.5,
            "fontname": font_bold,
            "color": blue,
        }
        if bold_file is not None:
            kwargs["fontfile"] = str(bold_file)
        page.insert_text(fitz.Point(x, 37), paper_id, **kwargs)

        insert_centered_text(
            page,
            f"- {page_number} -",
            page.rect.height - 25,
            font_regular,
            10.5,
            blue,
            regular_file,
        )

    metadata = doc.metadata or {}
    now = datetime.now(JST).strftime("D:%Y%m%d%H%M%S+09'00'")
    metadata.update(
        {
            "title": paper.title_en,
            "author": paper.authors_en,
            "creationDate": now,
            "modDate": now,
        }
    )
    doc.set_metadata(metadata)

    if hasattr(doc, "set_page_labels"):
        doc.set_page_labels([{"startpage": 0, "prefix": "", "style": "D", "firstpagenum": start_page}])

    if not dry_run:
        doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
    return page_count


def copy_slide(slides_root: Path | None, output_root: Path, talk_id: str, dry_run: bool) -> Path | None:
    if slides_root is None:
        return None
    source = slides_root / talk_id[:4] / f"{talk_id}_oral.pdf"
    if not source.is_file():
        return None
    dest = output_root / talk_id[:4] / source.name
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    return dest


def write_page_data(path: Path, results: list[ProcessResult], dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for paper_index, result in enumerate(results, start=1):
            page = "" if result.start_page is None else str(result.start_page)
            handle.write(f"{paper_index}\t{result.paper.talk_id}\t{page}\n")


def write_proceedings_list(path: Path, results: list[ProcessResult], dry_run: bool) -> None:
    """Write the machine-readable contract consumed by the Hugo site."""

    if dry_run:
        return
    records = [
        {
            "index": paper_index,
            "talk_id": result.paper.talk_id,
            "start_page": result.start_page,
        }
        for paper_index, result in enumerate(results, start=1)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
