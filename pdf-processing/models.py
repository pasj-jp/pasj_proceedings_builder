"""Shared data structures and abstract.json loading."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Paper:
    index: int
    talk_id: str
    session: str
    date: str
    time: str
    room: str
    title_ja: str
    title_en: str
    authors_ja_html: str
    authors_en_html: str
    authors_en: str
    abstract_ja_html: str


@dataclass
class ProcessResult:
    paper: Paper
    start_page: int | None
    source_pdf: Path | None
    output_pdf: Path | None
    slide_pdf: Path | None
    pages: int
    message: str = ""


def strip_html(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value or "", flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = value.replace("○", "")
    return re.sub(r"\s+", " ", value).strip()


def safe_inline_html(value: str) -> str:
    """Escape arbitrary HTML while preserving the inline tags used in abstracts."""

    allowed = {"sup", "sub", "i", "em", "b", "strong", "br"}
    placeholders: list[str] = []

    def keep(match: re.Match[str]) -> str:
        tag = match.group(0)
        name = re.sub(r"^</?\s*([a-zA-Z0-9]+).*$", r"\1", tag).lower()
        if name not in allowed:
            return tag
        token = f"@@HTML{len(placeholders)}@@"
        closing = "/" if tag.startswith("</") else ""
        placeholders.append("<br>" if name == "br" else f"<{closing}{name}>")
        return token

    protected = re.sub(r"</?\s*[a-zA-Z0-9]+(?:\s+[^>]*)?/?>", keep, value or "")
    escaped = html.escape(protected, quote=False)
    for i, tag in enumerate(placeholders):
        escaped = escaped.replace(f"@@HTML{i}@@", tag)
    return escaped


def load_papers(path: Path) -> list[Paper]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")

    papers: list[Paper] = []
    for index, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"{path}: item {index} is not an object")

        talk_id = str(record.get("talk_id") or record.get("講演番号") or "").strip()
        if not talk_id:
            continue

        papers.append(
            Paper(
                index=index,
                talk_id=talk_id,
                session=str(record.get("session") or "").strip(),
                date=str(record.get("date") or "").strip(),
                time=str(record.get("time") or "").strip(),
                room=str(record.get("room") or "").strip(),
                title_ja=str(record.get("title_ja") or "").strip(),
                title_en=str(record.get("title_en") or "").strip(),
                authors_ja_html=safe_inline_html(str(record.get("author_text_html") or "")),
                authors_en_html=safe_inline_html(str(record.get("著者情報（英語）") or "")),
                authors_en=strip_html(str(record.get("著者情報（英語）") or "")),
                abstract_ja_html=safe_inline_html(str(record.get("abstract_ja") or "")),
            )
        )
    return papers


def load_year_config(path: Path, year: int) -> dict[str, str]:
    """Load and validate the PDF header settings for one proceedings year."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")

    config = data.get(str(year))
    if not isinstance(config, dict):
        available = ", ".join(sorted(data)) or "none"
        raise ValueError(
            f"year {year} is not configured in {path} (available: {available})"
        )

    required = ("volume", "header1", "header2")
    missing = [key for key in required if not str(config.get(key) or "").strip()]
    if missing:
        raise ValueError(
            f"{path}: year {year} is missing required values: {', '.join(missing)}"
        )
    return {key: str(config[key]).strip() for key in required}
