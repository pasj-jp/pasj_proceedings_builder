# Proceedings site (Hugo)

`data/abstracts.json` から目次、アブストラクト、著者索引を生成するHugoサイトです。
PDF本体は含めず、pasj.jp上の公開PDFへ絶対URLでリンクします。
`data/proceedings_list.json` の `start_page` が数値の講演だけがPDFリンクになります。

## ローカル確認

```bash
python3 scripts/import_abstracts.py
hugo server
```

本番ビルドは `python3 scripts/import_abstracts.py && hugo --minify` です。

公開前に `hugo.toml` の次の2項目を実際のURLへ変更してください。

- `baseURL`: GitHub PagesのURL
- `params.pdfBaseURL`: pasj.jpに配置した `PDF` ディレクトリのURL

`legacy-output/` は旧Pythonジェネレーターによる生成結果の比較用スナップショットで、
Hugoの公開物には入りません。移行確認後に別途アーカイブできます。
