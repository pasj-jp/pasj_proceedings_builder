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
- `data/years/2025.json` の `pdfBaseURL`: pasj.jpに配置したPDFディレクトリのURL

## 翌年度の追加

例えば2026年度は次の3ファイルを追加します。

```text
data/years/2026.json
data/proceedings/2026/abstracts.json
data/proceedings/2026/proceedings_list.json
```

`data/years/2025.json` を複製して年度、タイトル、PDF URL、公開日を変更できます。
その後に `hugo` を実行すると、トップページに
2026年度が追加され、サイトは `/2026/` 以下に生成されます。

## 構成

| パス | 用途 |
|---|---|
| `hugo.toml` | サイト URL・誌名・ISSN の設定 |
| `content/_content.gotmpl` | JSON データからページを生成する Hugo Content adapter |
| `data/years/` | 年度別の設定 |
| `data/proceedings/` | 年度別の講演・PDF 公開状況データ |
| `layouts/` | HTML テンプレート |
| `static/` | CSS などの静的ファイル |

生成先は `public/` です。GitHub Actions も Hugo のみでビルドして GitHub Pages へ配置します。
GitHub Pages のビルドでも `hugo.toml` の本番 URL を使用します。
年度設定のファイル名と `year`、講演データのディレクトリ名は同じ年度に揃えてください。
