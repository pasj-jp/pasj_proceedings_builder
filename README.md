# Proceedings site (Hugo)

年度別の `data/proceedings_<年>.json` から目次、個別演題ページ、
著者索引を生成するHugoサイトです。アブストラクトは個別演題ページに掲載します。トップページには横断検索・最新巻・年度一覧を表示し、2025年度は
`/2025/` 以下に生成されます。
PDF本体は含めず、pasj.jp上の公開PDFへ絶対URLでリンクします。
各講演の `start_page` と `pdf_path` が設定されている講演だけが
PDFリンクになります。

トップページの年度一覧には、誌名「日本加速器学会年会プロシーディングス」と
`ISSN 2761-0004 (Online)` を表示します。誌名は `hugo.toml` の `title`、
ISSNは `[params]` の `issn` で管理します。

## ローカル確認

CI で指定している Hugo 0.170.1 を使用し、リポジトリ直下で実行します。
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

## 横断検索と画面構成

検索ページは `/search/` です。検索語 `q` をクエリ文字列に保持し、検索結果の共有・再読み込みに対応します。
同じタブの論文詳細からは直前の検索条件に戻れます（sessionStorage が利用可能な場合）。
JavaScript を無効にしても年度目次・著者索引・個別論文・PDF リンクは閲覧できます。

Hugo Content Adapter が既存 JSON から論文ページを生成し、論文の Params に
元レコードを保持します。`layouts/partials/search-index.html` がこれらのページから
検索索引を自動生成します。検索専用のメタデータを手作業で管理する必要はありません。

- `/index.json`: 年度と索引 URL の小さなマニフェスト。
- `/<年>/index.json`: その年度の論文索引。HTML と同じページ情報から生成。
- `static/js/search-core.js`: NFKC 正規化・大文字小文字の統一・空白区切りの AND 検索。
- `static/js/search.js`: 索引の取得、検索語の保持、結果表示。全年度の索引を取得し、
  取得済み索引は同じページ内でキャッシュ。

タイトル（日英）、著者（日英）、所属、アブストラクト、キーワード（存在する場合）、
講演番号、開催年度が検索対象です。50 件ずつ結果を追加して DOM の肥大化を抑えます。
現行 13 年度・4,545 件では索引合計約 14.7 MB、各年度約 0.93〜1.24 MB
（全年度 gzip 圧縮時の参考値は約 3.6 MB）。実際の転送圧縮はホスティングに依存します。
全年度検索は全索引をブラウザのメモリに保持します。大幅に件数が増える場合は再計測してください。
ネットワークエラー時は再検索で再取得できます。

年度・形式・分野の絞り込みは設けず、全年度をキーワードで検索します。
検索結果の発表形式表示には `presentation_type`、なければ `確定発表形式2` を使用します。
会議の回数・開催地は元データにないため推測して表示しません。
任意の年度設定 `edition` / `location` がある場合は年度カードに表示します。
翻訳ページがないため言語切替は設けていません。

## SEO と公開日

個別論文の URL、年度内の掲載順、PDF のパスと公開条件は維持しています。
タイトル・著者・所属・アブストラクトは初期 HTML に含まれ、JavaScript に依存しません。
各ページに canonical と description、論文に Highwire citation メタタグを出力します。
サイトマップと robots.txt は Hugo が生成します。

Scholar 用公開日は `disclosure` の最初の年月日（公開日）から取得し、開催年度や
更新日を公開日として扱いません。例えば 2013 年巻の公開日は 2014/06/12 です。
任意の `publicationDate`（`YYYY/MM/DD`）が年度設定にあれば優先します。
公開日が得られない場合は日付タグを省略します。PDF タグも実際に公開対象の論文だけに出力します。

## 検証

新しいパッケージや CDN 依存は追加していません。画面はローカル CSS と ES Modules で構成し、
モダンブラウザを対象とします。テストのみ Python 3 と Node.js（現行 LTS 推奨）を使用します。
GitHub Actions では本番ビルド後、配置前に以下の検証を実行します。

```bash
hugo --minify
python3 tests/verify_site.py
node tests/search.test.mjs
```

Python の検証は全論文の HTML、canonical、日付・著者・PDF の citation タグ、
元データとの PDF URL 一致、検索索引、サイトマップ、内部 HTML リンクを確認します。
Node.js の検証は実索引で日英検索・著者・所属・講演番号・全角文字・AND 検索・
年度横断・空の検索語・旧絞り込み条件が無視されること・該当なしを確認します。
外部 PDF の HTTP 到達性、Google/Scholar による実際の収録、ブラウザでの画面表示は
これらの自動検証に含まれません。公開前にデスクトップ・タブレット・モバイルで
ホーム、検索、論文詳細、キーボード操作を確認してください。
