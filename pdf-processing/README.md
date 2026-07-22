# PDF processing

投稿PDFにヘッダー、講演番号、通しページ番号を付加し、公開用PDF、
`pdf_page_data.txt`、`proceedings_list.json` を生成する独立プロジェクトです。
HTMLは生成しません。

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python process_proceedings_pdfs.py \
  --abstract-json ../proceedings-site/data/proceedings/2025/abstracts.json \
  --source-root /path/to/submitted/proceedings \
  --output-root /path/to/pasj.jp/proceedings/PDF \
  --volume PASJ2025
```

PDFは `<output-root>/<講演番号の先頭4文字>/<講演番号>.pdf` に出力されます。
このディレクトリをpasj.jpへ同期してください。HTMLサイトとの直接のファイル共有は
なく、公開URLの規約だけが両プロジェクト間の契約です。

`proceedings_list.json` の `start_page` は、PDFが見つからなかった講演では
`null` になります。このJSONを
`proceedings-site/data/proceedings/<年>/proceedings_list.json` として渡すと、
HugoサイトはPDFが存在する講演にだけリンクを表示します。

既存のタブ区切り一覧を変換する場合:

```bash
python convert_proceedings_list.py proceedings_list.txt proceedings_list.json
```
