# ⚠️ このフォルダは現行の本番ビルドではありません（2026-08-19 時点）

`build.py` / `master.html` は初期の生成パイプラインですが、**本番HTMLと乖離しています**。
実行すると `dist/` に古い設計のページが出力されるため、**そのまま本番へ反映しないでください。**

乖離している主な点:

| 箇所 | source/master.html | 本番（meta/・hp/・lis/） |
|---|---|---|
| `<title>` | AOHARUインターン｜キャリアは、体験で磨かれる。 | 大学1・2年生特化の長期インターン紹介｜AOHARUインターン |
| アセットパス | `/lp/assets/…`（旧GitHub Pages） | `/assets/…`（intern.worcry.com） |
| OGP画像 | aoharu-intern.github.io | intern.worcry.com |
| フォント読込 | 同期読込 | preload で非同期化（描画ブロック回避） |
| y1 / y2 ページ | master からの見出し差し替えで生成する前提 | **別レイアウト（`.v-y1` / `.yhero`）に作り替え済み。build.py では生成できない** |
| 2026-08-19 のCV改修 | 未反映 | 反映済み |

`build.py` の `TITLE_SRC` / `H1_SRC` 定数も現行タイトルと一致しないため、
学年別見出しの差し替えは今のままでは動作しません。

## 方針
現状、本番の12ページは個別に手編集されています。
再びテンプレート運用に戻す場合は、`meta/index.html` を新しい master として作り直し、
`build.py` の以下を更新してください。

- `TITLE_SRC` / `H1_SRC` を現行の値に
- y1 / y2 は別レイアウトのため、生成対象から外すか別テンプレート化
- `relativize_links` が期待する `href="y1.html"` 形式（本番は `href="y1/"`）
