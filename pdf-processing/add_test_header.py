#!/usr/bin/env python3
"""Add a proceedings-style header and continuous page numbers to any PDF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from models import Paper, load_year_config
from pdf_writer import process_pdf


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT_DIR = ROOT / "ttfonts" / "TimesNewRomanPSMT"
DEFAULT_CONFIG = Path(__file__).with_name("header_config.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path, help="PDF to process")
    parser.add_argument("output_pdf", type=Path, help="Destination PDF (must differ from input)")
    parser.add_argument("--start-page", type=int, default=1, help="First printed page number")
    parser.add_argument("--year", type=int, required=True, help="Proceedings configuration year")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Year configuration JSON")
    parser.add_argument("--talk-id", default="SAMPLE", help="Talk ID shown in the header")
    parser.add_argument("--title", default="", help="PDF metadata title")
    parser.add_argument("--author", default="", help="PDF metadata author")
    parser.add_argument("--font-dir", type=Path, default=DEFAULT_FONT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    input_pdf = args.input_pdf.expanduser().resolve()
    output_pdf = args.output_pdf.expanduser().resolve()
    if not input_pdf.is_file():
        print(f"ERROR: input PDF not found: {input_pdf}", file=sys.stderr)
        return 1
    if input_pdf == output_pdf:
        print("ERROR: input and output PDF must be different files", file=sys.stderr)
        return 1
    if args.start_page < 1:
        print("ERROR: --start-page must be 1 or greater", file=sys.stderr)
        return 1

    try:
        year_config = load_year_config(args.config, args.year)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    paper = Paper(
        index=1,
        talk_id=args.talk_id,
        session="",
        date="",
        time="",
        room="",
        title_ja="",
        title_en=args.title,
        authors_ja_html="",
        authors_en_html="",
        authors_en=args.author,
        abstract_ja_html="",
    )

    try:
        pages = process_pdf(
            source_pdf=input_pdf,
            output_pdf=output_pdf,
            paper=paper,
            start_page=args.start_page,
            volume=year_config["volume"],
            header1=year_config["header1"],
            header2=year_config["header2"],
            font_dir=args.font_dir,
            dry_run=False,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    last_page = args.start_page + pages - 1
    print(f"created: {output_pdf}")
    print(f"pages: {pages} (printed page numbers: {args.start_page}-{last_page})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
