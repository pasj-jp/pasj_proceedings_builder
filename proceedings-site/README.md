# Proceedings site (Hugo)

年度別の `data/proceedings/<年>/abstracts.json` から目次、アブストラクト、
著者索引を生成するHugoサイトです。トップページは年度一覧になり、2025年度は
`/2025/` 以下に生成されます。
PDF本体は含めず、pasj.jp上の公開PDFへ絶対URLでリンクします。
同じ年度ディレクトリの `proceedings_list.json` で `start_page` が数値の講演だけが
PDFリンクになります。

トップページの年度一覧には、誌名「日本加速器学会年会プロシーディングス」と
`ISSN 2761-0004 (Online)` を表示します。誌名は `hugo.toml` の `title`、
ISSNは `[params]` の `issn` で管理します。

## ローカル確認

```bash
python3 scripts/import_abstracts.py
hugo server
```

本番ビルドは `python3 scripts/import_abstracts.py && hugo --minify` です。

公開前に次のURLを実際の値へ変更してください。

- `hugo.toml` の `baseURL`: GitHub PagesのURL
- `data/years/2025.json` の `pdfBaseURL`: pasj.jpに配置したPDFディレクトリのURL

## 翌年度の追加

例えば2026年度は次の3ファイルを追加します。

```text
data/years/2026.json
data/proceedings/2026/abstracts.json
data/proceedings/2026/proceedings_list.json
```

`data/years/2025.json` を複製して年度、タイトル、PDF URL、公開日を変更できます。
その後に通常どおり `scripts/import_abstracts.py` とHugoを実行すると、トップページに
2026年度が追加され、サイトは `/2026/` 以下に生成されます。

`legacy-output/` は旧Pythonジェネレーターによる生成結果の比較用スナップショットで、
Hugoの公開物には入りません。移行確認後に別途アーカイブできます。
