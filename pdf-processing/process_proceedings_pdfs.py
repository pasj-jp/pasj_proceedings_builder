#!/usr/bin/env python3
"""Build processed proceedings PDFs from abstract.json.

This is a CGI-free replacement candidate for pdf_editor.cgi.  It reads
new_program/abstract.json in array order, finds the newest PDF for each
talk_id, writes a proceedings header and page number on every page, and
creates pdf_page_data.txt. HTML is built independently by proceedings-site.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from models import ProcessResult, load_papers, load_year_config
from pdf_writer import (
    copy_slide,
    newest_pdf_for_talk,
    process_pdf,
    write_page_data,
    write_proceedings_list,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ABSTRACT_JSON = ROOT / "proceedings-site" / "data" / "proceedings" / "2025" / "abstracts.json"
DEFAULT_FONT_DIR = ROOT / "ttfonts" / "TimesNewRomanPSMT"
DEFAULT_CONFIG = Path(__file__).with_name("header_config.json")


def process_all(args: argparse.Namespace) -> list[ProcessResult]:
    papers = load_papers(args.abstract_json)
    year_config = load_year_config(args.config, args.year)
    results: list[ProcessResult] = []
    next_page = args.start_page

    for paper in papers:
        source_pdf = newest_pdf_for_talk(args.source_root, paper.talk_id)
        if source_pdf is None:
            results.append(
                ProcessResult(
                    paper=paper,
                    start_page=None,
                    source_pdf=None,
                    output_pdf=None,
                    slide_pdf=None,
                    pages=0,
                    message="source PDF not found",
                )
            )
            continue

        output_pdf = args.output_root / paper.talk_id[:4] / f"{paper.talk_id}.pdf"
        start_page = next_page
        pages = process_pdf(
            source_pdf=source_pdf,
            output_pdf=output_pdf,
            paper=paper,
            start_page=start_page,
            volume=year_config["volume"],
            header1=year_config["header1"],
            header2=year_config["header2"],
            font_dir=args.font_dir,
            dry_run=args.dry_run,
        )
        slide_pdf = copy_slide(args.slides_root, args.output_root, paper.talk_id, args.dry_run)
        next_page += pages
        results.append(
            ProcessResult(
                paper=paper,
                start_page=start_page,
                source_pdf=source_pdf,
                output_pdf=output_pdf,
                slide_pdf=slide_pdf,
                pages=pages,
            )
        )

    write_page_data(args.output_root / args.page_data_file, results, args.dry_run)
    write_proceedings_list(
        args.output_root / args.proceedings_list_file, results, args.dry_run
    )
    if args.list_files_dir is not None:
        write_page_data(args.list_files_dir / args.page_data_file, results, args.dry_run)
        write_proceedings_list(
            args.list_files_dir / args.proceedings_list_file, results, args.dry_run
        )

    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Process proceedings PDFs using abstracts.json order."
    )
    parser.add_argument("--abstract-json", type=Path, default=DEFAULT_ABSTRACT_JSON)
    parser.add_argument("--source-root", type=Path, required=True, help="Root of submitted proceedings PDFs.")
    parser.add_argument("--output-root", type=Path, required=True, help="Root for processed public PDFs.")
    parser.add_argument("--list-files-dir", type=Path, help="Optional list_files directory for pdf_page_data.txt.")
    parser.add_argument("--slides-root", type=Path, help="Optional root of oral slide PDFs to copy.")
    parser.add_argument("--font-dir", type=Path, default=DEFAULT_FONT_DIR)
    parser.add_argument("--year", type=int, default=2025, help="Proceedings configuration year.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Year configuration JSON.")
    parser.add_argument("--page-data-file", default="pdf_page_data.txt")
    parser.add_argument(
        "--proceedings-list-file",
        default="proceedings_list.json",
        help="JSON availability list written under output-root (and list-files-dir).",
    )
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-missing", action="store_true", help="Return success even when some source PDFs are missing.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        results = process_all(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    processed = sum(1 for result in results if result.start_page is not None)
    missing = len(results) - processed
    print(f"presentations: {len(results)}")
    print(f"processed PDFs: {processed}")
    print(f"missing PDFs: {missing}")
    for result in results:
        if result.start_page is None:
            print(f"MISS\t{result.paper.talk_id}\t{result.message}")
        else:
            print(f"OK\t{result.paper.talk_id}\tp.{result.start_page}\t{result.pages} pages\t{result.output_pdf}")
    return 0 if missing == 0 or args.allow_missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
