export const normalize = value => String(value ?? '').normalize('NFKC').toLocaleLowerCase('ja').replace(/\s+/gu, ' ').trim();
export function prepare(papers) {
  return papers.sort((a, b) => b.year.localeCompare(a.year) || a.id.localeCompare(b.id))
    .map(paper => ({ ...paper, text: normalize(paper.text) }));
}
export function matches(paper, { q = '' }) {
  return normalize(q).split(' ').filter(Boolean).every(term => paper.text.includes(term));
}
