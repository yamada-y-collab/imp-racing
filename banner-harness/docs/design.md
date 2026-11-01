# 設計・状態・引き継ぎ

図解：[`docs/index.html`](index.html)（ブラウザで開く。GitHub Pages では `/banner-harness/docs/`）

## 考え方

参考にした「banner-harness v3」の構成を、Impress Racing のサイト（このリポジトリ）向けに置き換えたもの。

1. **正典はリポジトリ。** ブランドの色・言葉・ロゴはサイト本体（`README.md`・`assets/shared.css`・`assets/logos/`）が正典で、
   `brands/impress-racing/` はそこから一方向に写したもの（`sync_brand.py` がハッシュで変化を見張る）。
2. **型は渡さない。** 生成には規範（`brand.md`・`banner.md`）だけを渡し、サイズごとに一から組ませる。
   人の直しのうち次にも効くものは `banner.md` に戻す。規範が育つほど直しが減る。
3. **中心は、ブラウザで実測した1つのデータ。** 生成した HTML をブラウザで描き、座標・色・文字・改行を測って
   `layout.json` にする。PNG・PPTX・検査はすべてそこから分ける。出口が増えても生成側は変えない。
4. **機械の検査は事故だけを見る。止めない。** 文言の欠け・はみ出し・重なり・コントラストのような「事故」だけを
   `check.py` が拾い、所見として成果物に添える。良し悪しの判断は人（デザイナー）がする。
5. **描画は自分で見て直す（2回まで）。** 検査が拾えない見た目の問題は、生成した側が `sheet.png` を見て直す。
   3回目は人に渡す。

## 流れ（今動いているもの）

```
原稿（brief.md）
  └─ banner.py generate ── PROMPT.md（指示文 + brand.md + banner.md + 原稿）
        └─ Claude Code が <幅>x<高さ>.html を書く
              └─ banner.py export
                   ├─ html2layout.mjs  … ブラウザで実測 → layout.json・PNG・地の PNG
                   ├─ check.py         … 事故の検査 → check.json
                   ├─ sheet.py         … 全サイズを1枚に → sheet.png
                   └─ layout2pptx.py   … 地の画像 + ロゴ + 編集できる文字 → PPTX（Canva にドラッグ）
  └─ banner.py revise "直し" ── 前の版を写した v2 と直しの指示文
```

## 参考構成との対応

| 参考（v3） | ここ | 状態 |
| --- | --- | --- |
| `CLAUDE.md` | リポジトリ直下の `CLAUDE.md` | ✅ |
| `.claude/skills/banner-builder/SKILL.md` | 同じ（リポジトリ直下の `.claude/`） | ✅ |
| `brands/episode-n/` | `brands/impress-racing/`（brand.md / banner.md / SOURCE.json / assets） | ✅ |
| `prompts/generate-episode-n.md` | `prompts/generate-impress-racing.md` | ✅ |
| `templates/brief.md` | 同じ | ✅ |
| `tools/banner.py`（init / generate / revise / export / status） | 同じ | ✅ |
| `tools/html2layout.mjs` | 同じ | ✅ |
| `tools/layout2pptx.py` | 同じ | ✅ |
| `tools/check.py` | 同じ | ✅ |
| `tools/sheet.py` | 同じ | ✅ |
| `tools/sync_brand.py` | 同じ | ✅ |
| `tests/check_selftest.py` | 同じ（16 ケース） | ✅ |
| `docs/` | `docs/design.md`・`docs/index.html` | ✅ |
| `tools/layout2figma.py` | — | 未着手（Figma の接続が要る） |
| `tools/layout2canva.py`（Path C） | — | 未着手（参考でも候補扱い） |
| `tools/marker.mjs` | — | 未着手（語の位置は `layout.json` に入っているので、足すならここから） |
| `hearing/` `brief_from_notion.py` `notion_writeback.py` | — | 未着手（Notion の依頼 DB が要る） |
| `slack_post.py` | — | 未着手（Slack の接続が要る） |
| `diff_versions.py` `feedback/` | — | 未着手（Canva で仕上げた版の回収が要る） |
| `ops/run_unattended.sh` `schedule/` | `banner.py generate --run`（`claude -p` で回す） | 一部 |
| `tests/pipeline_selftest.py` | — | 未着手（Notion 連携とあわせて） |
| `phase0/` | — | 対象外 |

## 決めごと

- 出力先は `banner-harness/work/<id>/v<n>/`。HTML から素材への相対パスは、写真が `../../../../`（リポジトリ直下）、
  ロゴが `../../../brands/impress-racing/assets/`。
- リポジトリに残すのは原稿・HTML・`sheet.png`・`check.json` だけ。PNG・PPTX・`layout.json` は作り直せるので
  `.gitignore` で外している（GitHub Pages に重い画像を載せないため）。
- PPTX の背景は「文字とロゴを隠して撮った地の画像」。写真・scrim・図形は1枚に焼き込まれ、
  文字（テキストボックス）とロゴ（画像）だけが Canva で動かせる。
- Chromium は `HTTPS_PROXY` を自分で読まないので、`html2layout.mjs` が渡している（Google Fonts の読み込みのため）。

## 検査の閾値

| 項目 | error | warn |
| --- | --- | --- |
| コントラスト（文字の箱の地の、悪い側から1割の画素で測る） | 3:1 未満 | 小さな文字（24px 未満、太字は 18.66px 未満）で 4.5:1 未満 |
| 縦のはみ出し | 字の大きさの半分を超える | — |
| 安全域 | — | 端から短辺の 5% 以内 |
| ストーリーズの UI 帯 | — | 1080x1920 の上 250px・下 340px |
| 最小の文字 | 10px 未満 | — |
