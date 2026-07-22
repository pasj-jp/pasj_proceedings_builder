#!/usr/bin/env python3
"""Create lightweight Hugo content pages from data/abstracts.json."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / "data" / "abstracts.json").read_text(encoding="utf-8"))
out = ROOT / "content" / "papers"
out.mkdir(parents=True, exist_ok=True)

expected = set()
for position, record in enumerate(records, 1):
    talk_id = str(record.get("talk_id") or "").strip()
    if not talk_id:
        continue
    target = out / f"{talk_id}.md"
    expected.add(target.name)
    front_matter = {
        "title": talk_id,
        "talk_id": talk_id,
        "position": position,
        "layout": "paper",
    }
    target.write_text("---\n" + json.dumps(front_matter, ensure_ascii=False, indent=2) + "\n---\n", encoding="utf-8")

for target in out.glob("*.md"):
    if target.name not in expected:
        target.unlink()

print(f"prepared {len(expected)} paper pages")

