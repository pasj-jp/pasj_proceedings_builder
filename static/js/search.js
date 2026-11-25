import { prepare, matches } from './search-core.js';
const form = document.querySelector('#paper-search');
const status = document.querySelector('#search-status');
const results = document.querySelector('#search-results');
const more = document.querySelector('#load-more');
const fields = ['q'];
let papers = [], filtered = [], displayed = 0, ready = false, volumes = [], request = 0;
const cache = new Map();
async function loadVolume(volume) {
  if (!cache.has(volume.url)) {
    const pending = fetch(volume.url).then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    }).then(prepare).catch(error => { cache.delete(volume.url); throw error; });
    cache.set(volume.url, pending);
  }
  return cache.get(volume.url);
}
const controls = Object.fromEntries(fields.map(name => [name, form.elements.namedItem(name)]));
function restore() {
  const params = new URLSearchParams(location.search);
  for (const field of fields) controls[field].value = params.get(field) || '';
}
function element(tag, text, className) {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
}
function append() {
  const fragment = document.createDocumentFragment();
  const batch = filtered.slice(displayed, displayed + 50);
  for (const paper of batch) {
    const card = element('article', '', 'search-result');
    card.append(element('p', `${paper.year} · ${paper.id}${paper.type ? ` · ${paper.type}` : ''}`, 'result-meta'));
    const heading = element('h2', '');
    const link = element('a', paper.title);
    link.href = paper.url;
    heading.append(link);
    card.append(heading);
    if (paper.english && paper.english !== paper.title) card.append(element('p', paper.english, 'english-title'));
    if (paper.authors) card.append(element('p', paper.authors, 'result-authors'));
    if (paper.abstract) card.append(element('p', paper.abstract, 'result-abstract'));
    if (paper.pdf) {
      const pdf = element('a', 'PDFを開く ↗', 'pdf-link');
      pdf.href = paper.pdf;
      card.append(pdf);
    }
    fragment.append(card);
  }
  results.append(fragment);
  displayed += batch.length;
  more.hidden = displayed >= filtered.length;
}
async function search(updateURL = true) {
  if (!ready) return;
  const values = Object.fromEntries(fields.map(field => [field, controls[field].value]));
  if (updateURL) {
    const params = new URLSearchParams();
    for (const field of fields) if (values[field]) params.set(field, values[field]);
    history.replaceState(null, '', `${location.pathname}${params.size ? `?${params}` : ''}`);
  }
  try { sessionStorage.setItem('pasj-search', location.href); } catch { /* Optional. */ }
  const current = ++request;
  status.textContent = '検索索引を読み込んでいます…';
  more.hidden = true;
  results.replaceChildren();
  try {
    papers = (await Promise.all(volumes.map(loadVolume))).flat();
    if (current !== request) return;
  } catch {
    if (current === request) status.textContent = '検索索引を読み込めませんでした。再度検索するか、年度別一覧をご覧ください。';
    return;
  }
  filtered = papers.filter(paper => matches(paper, values));
  results.replaceChildren();
  displayed = 0;
  status.textContent = `${filtered.length.toLocaleString('ja-JP')}件の論文・講演が見つかりました`;
  if (!filtered.length) results.append(element('p', '該当する論文がありません。検索語を短くするか、別のキーワードで検索してください。', 'empty-results'));
  append();
}
restore();
form.addEventListener('submit', event => { event.preventDefault(); search(); });
window.addEventListener('popstate', () => { restore(); search(false); });
more.addEventListener('click', () => { const previous = results.children.length; append(); const link = results.children[previous]?.querySelector('h2 a'); link?.focus(); });
try {
  const response = await fetch(form.dataset.index);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  volumes = await response.json();
  restore();
  ready = true;
  search(false);
} catch {
  status.textContent = '検索索引を読み込めませんでした。ページを再読み込みするか、年度別一覧から論文をご覧ください。';
}
