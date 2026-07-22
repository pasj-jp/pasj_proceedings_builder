#!/usr/bin/env python3
"""Convert the legacy tab-separated proceedings list to JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def convert(source: Path, destination: Path) -> int:
    records = []
    for line_number, raw_line in enumerate(
        source.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        columns = raw_line.split("\t")
        if len(columns) != 3:
            raise ValueError(f"{source}:{line_number}: expected 3 tab-separated columns")
        index_text, talk_id, start_page_text = (value.strip() for value in columns)
        if not talk_id:
            raise ValueError(f"{source}:{line_number}: talk_id is empty")
        records.append(
            {
                "index": int(index_text),
                "talk_id": talk_id,
                "start_page": int(start_page_text) if start_page_text else None,
            }
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return len(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    count = convert(args.source, args.destination)
    print(f"converted {count} records to {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
