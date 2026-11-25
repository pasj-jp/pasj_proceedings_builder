"""Validate a production Hugo build against the authoritative annual data."""
import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


class HTML(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.meta, self.links, self.canonical, self.text = {}, [], [], []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and 'name' in attrs:
            self.meta.setdefault(attrs['name'], []).append(attrs.get('content', ''))
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs['href'])

    def handle_data(self, data):
        self.text.append(data)


def plain(value):
    return unescape(re.sub(r'</?[A-Za-z][^>]*>', '', value or ''))


root = Path('public')
manifest = json.loads((root / 'index.json').read_text())
assert len(manifest) == len(list(Path('data').glob('proceedings_*.json')))
indexed = {}
for volume in manifest:
    records = json.loads((root / volume['url'].lstrip('/')).read_text())
    assert all(p['year'] == volume['year'] for p in records)
    for paper in records:
        assert paper['url'] not in indexed
        indexed[paper['url']] = paper
sitemap = (root / 'sitemap.xml').read_text()
count = pdf_count = 0
for source in Path('data').glob('proceedings_*.json'):
    config = json.loads(source.read_text())
    year = config['year']
    year_html = HTML(root / year / 'index.html')
    for paper in config['records']:
        if not paper['talk_id'].strip():
            continue
        url = f"/{year}/papers/{paper['talk_id'].lower()}/"
        page = HTML(root / url.lstrip('/') / 'index.html')
        entry = indexed[url]
        title = plain(paper.get('title_ja') or paper.get('title_en') or paper['talk_id'])
        assert page.meta['citation_title'] == [title], url
        assert ' '.join(title.split()) in ' '.join(unescape(''.join(page.text)).split()), url
        if paper.get('abstract_ja'):
            assert ' '.join(plain(paper['abstract_ja']).split()) in ' '.join(''.join(page.text).split()), url
        assert page.canonical == [f'https://proceedings.pasj.jp{url}'], url
        assert page.canonical[0] in sitemap, url
        assert url in year_html.links, url
        assert page.meta.get('description'), url
        assert not any('noindex' in v for v in page.meta.get('robots', []))
        date = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', config['disclosure'])
        if date:
            expected = f'{date[1]}/{int(date[2]):02}/{int(date[3]):02}'
            assert page.meta['citation_publication_date'] == [expected], url
        names = []
        for author in paper.get('coauthors') or [paper]:
            name = ' '.join([author.get('first_name_en', ''), author.get('last_name_en', '')]).strip()
            if not name:
                name = ' '.join([author.get('last_name', ''), author.get('first_name', '')]).strip()
            if name:
                names.append(name)
        assert page.meta.get('citation_author', []) == names, url
        if paper.get('start_page') and paper.get('pdf_path'):
            pdf = config['pdfBaseURL'].rstrip('/') + '/' + paper['pdf_path'].lstrip('/')
            assert entry['pdf'] == pdf and pdf in page.links, url
            assert page.meta['citation_pdf_url'] == [pdf], url
            assert urlparse(pdf).scheme == 'https'
            pdf_count += 1
        else:
            assert not entry['pdf'] and 'citation_pdf_url' not in page.meta, url
        count += 1
assert len(indexed) == count
# Every local anchor destination (excluding fragments) must exist in the build.
for path in root.rglob('*.html'):
    page = HTML(path)
    for link in page.links:
        parsed = urlparse(link)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = root / parsed.path.lstrip('/') if parsed.path.startswith('/') else path.parent / parsed.path
        assert target.exists(), (path, link)
assert 'Disallow: /\n' not in (root / 'robots.txt').read_text()
print(f'PASS: {count} paper URLs, static metadata, citation authors/dates, sitemap, {pdf_count} exact PDF URLs, all local HTML links; {len(manifest)} index shards')
