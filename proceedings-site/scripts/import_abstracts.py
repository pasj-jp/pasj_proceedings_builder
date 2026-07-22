#!/usr/bin/env python3
"""Create Hugo content pages for every configured proceedings year."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
content_root = ROOT / "content"
content_root.mkdir(parents=True, exist_ok=True)
configured_years = set()
paper_count = 0

for config_path in sorted((ROOT / "data" / "years").glob("*.json")):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    year = str(config.get("year") or config_path.stem)
    configured_years.add(year)
    data_path = ROOT / "data" / "proceedings" / year / "abstracts.json"
    records = json.loads(data_path.read_text(encoding="utf-8"))
    year_root = content_root / year
    papers_root = year_root / "papers"
    papers_root.mkdir(parents=True, exist_ok=True)

    pages = {
        year_root / "_index.md": {"title": config["title"], "layout": "year", "year": year},
        year_root / "abstracts.md": {"title": "プロシーディングス目次（アブストラクト付き）", "layout": "abstracts", "year": year},
        year_root / "authors.md": {"title": "Author Index", "layout": "authors", "year": year},
    }
    for target, front_matter in pages.items():
        target.write_text("---\n" + json.dumps(front_matter, ensure_ascii=False, indent=2) + "\n---\n", encoding="utf-8")

    expected = set()
    for position, record in enumerate(records, 1):
        talk_id = str(record.get("talk_id") or "").strip()
        if not talk_id:
            continue
        target = papers_root / f"{talk_id}.md"
        expected.add(target.name)
        front_matter = {"title": talk_id, "talk_id": talk_id, "position": position, "layout": "paper", "year": year}
        target.write_text("---\n" + json.dumps(front_matter, ensure_ascii=False, indent=2) + "\n---\n", encoding="utf-8")
        paper_count += 1
    for target in papers_root.glob("*.md"):
        if target.name not in expected:
            target.unlink()

for path in content_root.iterdir():
    if path.is_dir() and path.name.isdigit() and path.name not in configured_years:
        shutil.rmtree(path)

print(f"prepared {paper_count} paper pages for {len(configured_years)} year(s)")
