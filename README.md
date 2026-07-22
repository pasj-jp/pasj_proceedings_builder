# PASJ proceedings builder

既存の一体型処理を、デプロイ先と責務が異なる2プロジェクトへ分離しています。

| ディレクトリ | 役割 | 配置先 |
|---|---|---|
| `pdf-processing/` | 投稿PDFの加工、通しページ情報の生成 | pasj.jp |
| `proceedings-site/` | `abstracts.json` からHugoで静的HTMLを生成 | GitHub Pages |

HTMLからPDFへは年度設定の `pdfBaseURL` を基準にした絶対URLでリンクします。
このためGitHub Pagesの成果物にPDFをコピーする必要はありません。

HTMLサイトは年度別構成で、トップページの下に `/2025/`, `/2026/` のように
各年度のプロシーディングスが増えていきます。PDFの基底URLなどの年度設定は
`proceedings-site/data/years/<年>.json` で管理します。

詳しい実行方法は各ディレクトリのREADMEを参照してください。
