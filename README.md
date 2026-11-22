# Proceedings site (Hugo)

年度別の `data/proceedings_<年>.json` から目次、アブストラクト、
著者索引を生成するHugoサイトです。トップページは年度一覧になり、2025年度は
`/2025/` 以下に生成されます。
PDF本体は含めず、pasj.jp上の公開PDFへ絶対URLでリンクします。
各講演の `start_page` と `pdf_path` が設定されている講演だけが
PDFリンクになります。

トップページの年度一覧には、誌名「日本加速器学会年会プロシーディングス」と
`ISSN 2761-0004 (Online)` を表示します。誌名は `hugo.toml` の `title`、
ISSNは `[params]` の `issn` で管理します。

## ローカル確認

CI と同じ Hugo 0.155.1 を使用し、リポジトリ直下で実行します。
Python や前処理は不要です。PDF 加工はこのプロジェクトの対象外です。

```bash
hugo server
```

ブラウザで http://localhost:1313/ を開いて確認できます。

本番ビルドは `hugo --minify` です。`hugo.toml` の `baseURL` に設定した
`https://proceedings.pasj.jp/` を使用します。`hugo server` は自動的に
`http://localhost:1313/` を使用するため、設定の書き換えは不要です。

公開前に次の設定を確認してください。

- GitHub Pages の Custom domain: `proceedings.pasj.jp`（DNS 設定も必要）
- `data/proceedings_2025.json` の `pdfBaseURL`: pasj.jpに配置したPDFディレクトリのURL

## 翌年度の追加

例えば2026年度は次の1ファイルを追加します。

```text
data/proceedings_2026.json
```

`data/proceedings_2025.json` を複製して年度、タイトル、PDF URL、公開日を変更し、
`records` を2026年度の講演データに置き換えます。
その後に `hugo` を実行すると、トップページに
2026年度が追加され、サイトは `/2026/` 以下に生成されます。

## 構成

| パス | 用途 |
|---|---|
| `hugo.toml` | サイト URL・誌名・ISSN の設定 |
| `content/_content.gotmpl` | JSON データからページを生成する Hugo Content adapter |
| `data/proceedings_<年>.json` | 年度設定と講演・著者・アブストラクト・PDF 公開状況を統合した年度別データ |
| `layouts/` | HTML テンプレート |
| `static/` | CSS などの静的ファイル |

生成先は `public/` です。GitHub Actions も Hugo のみでビルドして GitHub Pages へ配置します。
GitHub Pages のビルドでも `hugo.toml` の本番 URL を使用します。
JSON は `data/proceedings_<年>.json` という名前にし、ファイル名の年度と、その中の `year` を揃えてください。

## 講演データ

`data/proceedings_<年>.json` は、年度設定と講演データをまとめたオブジェクトです。

```json
{
  "year": "2026",
  "title": "PASJ2026 Proceedings",
  "pdfBaseURL": "https://www.pasj.jp/web_publish/pasj2026/proceedings/PDF",
  "disclosure": "公開日を記入",
  "copyrightNotice": "著作権表示を記入",
  "records": []
}
```

`records` は、1講演を1オブジェクトとする配列です。
講演情報・著者・アブストラクトと、次の PDF 情報を同じオブジェクトに保存します。

- `talk_id`: 年度内で一意の講演番号
- `start_page`: 公開 PDF の開始ページ番号（正の整数）。PDF がない場合は `null`
- `pdf_path`: 年度設定の `pdfBaseURL` からの相対パス（例: `WEPO/WEPO703.pdf`）。先頭の `/` は付けず、PDF がない場合は `null`
- `index`: 従来の PDF 一覧の順序番号。情報がない場合は `null`

目次の表示順は配列の順序です。`index` では並べ替えません。
PDF リンクは `{pdfBaseURL}/{pdf_path}` で生成します。年度や講演によって
ディレクトリ構成・ファイル名が変わる場合は `pdf_path` に実際のパスを指定してください。
`talk_id` からパスを推測する処理はありません。
講演を追加する際も、このファイルだけを更新すれば各ページに反映されます。

著者名・所属は `coauthors` 配列の `last_name`、`first_name`、`affiliation` から表示します。
`role` が「登壇者」で始まる著者には ○ を付け、所属が複数ある場合は番号で対応付けます。
`coauthors` が空の場合は講演レコード直下の氏名・所属を使用します。
`author_text_html` は使用しません。英語の著者情報は `著者情報（英語）` があれば表示します。
