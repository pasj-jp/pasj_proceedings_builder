import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { prepare, matches, normalize } from '../static/js/search-core.js';
const volumes = JSON.parse(await readFile('public/index.json', 'utf8'));
const papers = prepare((await Promise.all(volumes.map(async volume => JSON.parse(await readFile(`public${volume.url}`, 'utf8'))))).flat());
const sourceCounts = await Promise.all(volumes.map(async volume => {
  const source = JSON.parse(await readFile(`data/proceedings_${volume.year}.json`, 'utf8'));
  return source.records.filter(paper => paper.talk_id?.trim()).length;
}));
assert.equal(papers.length, sourceCounts.reduce((sum, count) => sum + count, 0));
assert.equal(normalize('ＡＴＦ　Beam'), 'atf beam');
for (const q of ['加速器', 'accelerator', 'ATF', '久保', 'Kiyoshi Kubo', '高エネ研', 'SAOTP1']) {
  assert(papers.some(paper => matches(paper, { q })), q);
}
const both = papers.filter(paper => matches(paper, { q: 'beam accelerator' }));
assert(both.length > 0);
assert(both.every(paper => paper.text.includes('beam') && paper.text.includes('accelerator')));
assert(new Set(papers.filter(paper => matches(paper, { q: 'accelerator' })).map(paper => paper.year)).size > 1);
assert.equal(papers.filter(paper => matches(paper, {})).length, papers.length);
// Old filter parameters must not restrict the simplified keyword search.
assert.deepEqual(
  papers.filter(paper => matches(paper, { q: '加速器', year: '2013', type: 'obsolete', topic: 'obsolete' })),
  papers.filter(paper => matches(paper, { q: '加速器' }))
);
assert(!papers.some(paper => matches(paper, { q: 'no-such-paper-zzxy123' })));
assert(papers.some(paper => matches(paper, { q: 'ＡＴＦ' })));
assert(papers.every(paper => paper.url.includes('/papers/')));
console.log('PASS: Japanese/English, author/affiliation/ID, NFKC, AND, cross-year, empty results');
