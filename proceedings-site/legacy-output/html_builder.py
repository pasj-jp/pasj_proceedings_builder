"""Static HTML generation for proceedings artifacts."""

from __future__ import annotations

import html
import json
from pathlib import Path

from models import Paper, ProcessResult, safe_inline_html, strip_html


PROCEEDINGS_CSS = """\
body {
  background: #fff;
  color: #111;
  font-family: Arial, Helvetica, "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  margin: 24px;
}
a { color: #0645ad; }
.page { max-width: 900px; margin: 0 auto; }
.hero { text-align: center; margin-bottom: 22px; }
.copyright { color: #b00000; max-width: 700px; margin: 16px auto; text-align: left; }
.nav { text-align: center; margin: 18px 0 28px; }
.session { background: #005080; color: #fff; font-weight: bold; padding: 5px 8px; }
.time { background: #e0f0ff; color: #005080; font-weight: bold; padding: 4px 8px; }
.paper-row td { padding: 8px 6px 14px; vertical-align: top; }
.code { width: 72px; white-space: nowrap; font-weight: bold; }
.abstract { margin-top: 12px; }
.links { margin-top: 3px; font-weight: normal; }
.toc { margin: 0 auto 28px; }
.toc td { padding: 2px 8px; }
.article table { width: 100%; border-collapse: collapse; }
.article td { padding: 6px; }
"""


def pdf_relpath(paper: Paper) -> str:
    return f"PDF/{html.escape(paper.talk_id[:4])}/{html.escape(paper.talk_id)}.pdf"


def slide_relpath(paper: Paper) -> str:
    return f"PDF/{html.escape(paper.talk_id[:4])}/{html.escape(paper.talk_id)}_oral.pdf"


def article_relpath(paper: Paper) -> str:
    return f"index/{html.escape(paper.talk_id)}.htm"


def render_title(paper: Paper) -> str:
    title_ja = html.escape(paper.title_ja)
    title_en = html.escape(paper.title_en)
    if title_ja and title_en and title_ja != title_en:
        return f"{title_ja}<br>{title_en}"
    return title_ja or title_en


def render_authors(paper: Paper) -> str:
    if paper.authors_ja_html and paper.authors_en_html and strip_html(paper.authors_ja_html) != strip_html(paper.authors_en_html):
        return f"{paper.authors_ja_html}<br>{paper.authors_en_html}"
    return paper.authors_en_html or paper.authors_ja_html


def html_head(title: str, stylesheet_href: str | None = None) -> str:
    stylesheet = f'  <link rel="stylesheet" href="{stylesheet_href}">\n' if stylesheet_href else ""
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
{stylesheet}</head>
<body>
"""


def html_tail() -> str:
    return "</body>\n</html>\n"


def render_paper_row(result: ProcessResult, with_abstract: bool) -> str:
    paper = result.paper
    pdf = pdf_relpath(paper)
    title = render_title(paper)
    authors = render_authors(paper)
    page = f"<br><b>p.{result.start_page}</b>" if result.start_page is not None else ""
    slide = f'<br><a href="{slide_relpath(paper)}" target="_blank">[Slides]</a>' if result.slide_pdf else ""
    abstract = f'<div class="abstract">{paper.abstract_ja_html}</div>' if with_abstract else ""
    return (
        '<tr class="paper-row">'
        f'<td class="code"><a href="{pdf}" target="_blank">{html.escape(paper.talk_id)}</a>{page}'
        f'<div class="links"><a href="{article_relpath(paper)}">[Abstract]</a>{slide}</div></td>'
        f'<td><a href="{pdf}" target="_blank">{title}</a><br>{authors}<br>&nbsp;{abstract}</td>'
        "</tr>\n"
    )


def session_label(paper: Paper) -> str:
    details = " ".join(part for part in (paper.date, paper.room) if part)
    return f"{paper.session}　（{details}）" if details else paper.session


def build_toc(papers: list[Paper]) -> str:
    rows: list[str] = []
    current = ""
    first_code = ""
    count = 0

    def flush() -> None:
        if not current:
            return
        rows.append(
            f'<tr><td><font color="#005080">◆</font>&nbsp;'
            f'<a href="#{html.escape(first_code)}">{html.escape(current)}</a></td>'
            f'<td nowrap align="right">&nbsp;{count}&nbsp;件</td></tr>'
        )

    for paper in papers:
        label = session_label(paper)
        if label != current:
            flush()
            current = label
            first_code = paper.talk_id
            count = 1
        else:
            count += 1
    flush()
    return '<table class="toc">\n' + "\n".join(rows) + "\n</table>\n"


def render_index(
    results: list[ProcessResult],
    title: str,
    with_abstract: bool,
    disclosure: str,
    copyright_text: str,
    css_href: str,
) -> str:
    papers = [result.paper for result in results]
    body = [
        html_head(title, css_href),
        '<div class="page">\n',
        '<div class="hero">\n',
        f"<h1>{html.escape(title)}</h1>\n",
        f'<div class="copyright">{safe_inline_html(copyright_text)}</div>\n',
        f"<p>{safe_inline_html(disclosure)}</p>\n",
    ]
    if with_abstract:
        body.append('<p>プロシーディングス目次（アブストラクト付き）</p>\n')
        body.append('<p><a href="index.html">［プロシーディングス目次（アブストラクトなし）へ］</a>&nbsp;&nbsp;<a href="author_index.htm">［著者索引ページへ］</a></p>\n')
    else:
        body.append('<p>プロシーディングス目次（アブストラクトなし）</p>\n')
        body.append('<p><a href="index_abstracts.html">［プロシーディングス目次（アブストラクト付き）へ］</a>&nbsp;&nbsp;<a href="author_index.htm">［著者索引ページへ］</a></p>\n')
    body.append("</div>\n")
    body.append(build_toc(papers))
    body.append('<table cellpadding="3" cellspacing="0">\n')

    current_session = ""
    for result in results:
        paper = result.paper
        label = session_label(paper)
        if label != current_session:
            body.append(f'<tr><td colspan="2" class="session" id="{html.escape(paper.talk_id)}">{html.escape(label)}</td></tr>\n')
            current_session = label
        body.append(f'<tr><td colspan="2" class="time">{html.escape(paper.time)}&nbsp;</td></tr>\n')
        body.append(render_paper_row(result, with_abstract))

    body.append("</table>\n</div>\n")
    body.append(html_tail())
    return "".join(body)


def render_article(result: ProcessResult, css_href: str) -> str:
    paper = result.paper
    page = f" p.{result.start_page}" if result.start_page is not None else ""
    title = f"{paper.talk_id} {page}".strip()
    return (
        html_head(title, css_href)
        + '<div class="page article">\n'
        + "<table>\n"
        + f'<tr><td class="session"><b>{html.escape(paper.talk_id)}</b>　{html.escape(paper.session)}　{html.escape(paper.date)} {html.escape(paper.room)} {html.escape(paper.time)}</td></tr>\n'
        + f'<tr><td align="center">{render_title(paper)}</td></tr>\n'
        + f'<tr><td align="center">&nbsp;<br>{render_authors(paper)}</td></tr>\n'
        + f'<tr><td align="left">&nbsp;<br><span>{paper.abstract_ja_html}</span><br>&nbsp;</td></tr>\n'
        + "</table>\n</div>\n"
        + html_tail()
    )


def render_author_index(papers: list[Paper], source_json: Path, css_href: str) -> str:
    entries: dict[tuple[str, str, str], tuple[str, list[str]]] = {}
    data = json.loads(source_json.read_text(encoding="utf-8"))
    by_talk = {paper.talk_id: paper for paper in papers}
    for record in data:
        if not isinstance(record, dict):
            continue
        talk_id = str(record.get("talk_id") or "").strip()
        if talk_id not in by_talk:
            continue
        for author in record.get("coauthors") or []:
            if not isinstance(author, dict):
                continue
            last = strip_html(str(author.get("last_name_en") or ""))
            first = strip_html(str(author.get("first_name_en") or ""))
            middle = strip_html(str(author.get("middle_name") or ""))
            given = " ".join(part for part in (first, middle) if part)
            display = f"{last}, {given}" if last and given else last or given
            if not display:
                continue
            key = (last.casefold(), given.casefold(), display.casefold())
            entries.setdefault(key, (display, []))[1].append(talk_id)

    rows = []
    for key in sorted(entries):
        display, talk_ids = entries[key]
        unique_ids = list(dict.fromkeys(talk_ids))
        links = ", ".join(f'<a href="index/{html.escape(tid)}.htm">{html.escape(tid)}</a>' for tid in unique_ids)
        rows.append(f'<tr><td>{html.escape(display)}</td><td>{links}</td></tr>')

    return (
        html_head("Author Index", css_href)
        + '<div class="page"><h1>Author Index</h1><table cellpadding="3" cellspacing="0">\n'
        + "\n".join(rows)
        + "\n</table></div>\n"
        + html_tail()
    )


def write_text(path: Path, text: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def build_web_artifact(
    artifact_root: Path | None,
    abstract_json: Path,
    results: list[ProcessResult],
    site_title: str,
    disclosure: str,
    copyright_text: str,
    dry_run: bool,
) -> None:
    if artifact_root is None:
        return

    css_name = "proceedings.css"
    write_text(artifact_root / css_name, PROCEEDINGS_CSS, dry_run)
    write_text(
        artifact_root / "index.html",
        render_index(results, site_title, False, disclosure, copyright_text, css_name),
        dry_run,
    )
    write_text(
        artifact_root / "index_abstracts.html",
        render_index(results, site_title, True, disclosure, copyright_text, css_name),
        dry_run,
    )
    for result in results:
        write_text(artifact_root / "index" / f"{result.paper.talk_id}.htm", render_article(result, f"../{css_name}"), dry_run)
    write_text(
        artifact_root / "author_index.htm",
        render_author_index([r.paper for r in results], abstract_json, css_name),
        dry_run,
    )
