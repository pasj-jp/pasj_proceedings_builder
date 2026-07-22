# PASJ proceedings builder

既存の一体型処理を、デプロイ先と責務が異なる2プロジェクトへ分離しています。

| ディレクトリ | 役割 | 配置先 |
|---|---|---|
| `pdf-processing/` | 投稿PDFの加工、通しページ情報の生成 | pasj.jp |
| `proceedings-site/` | `abstracts.json` からHugoで静的HTMLを生成 | GitHub Pages |

HTMLからPDFへは `proceedings-site/hugo.toml` の `params.pdfBaseURL` を基準にした
絶対URLでリンクします。このためGitHub Pagesの成果物にPDFをコピーする必要はありません。

詳しい実行方法は各ディレクトリのREADMEを参照してください。
