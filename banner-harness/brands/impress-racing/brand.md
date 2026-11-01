# Impress Racing — ブランド

正典：リポジトリ直下の `README.md`（デザインコンセプト節）と `assets/shared.css`（`:root` の色トークン）。
このファイルは正典から一方向に写したもの。正典が変わったら `tools/sync_brand.py` で差分を確認し、ここを直す。
ここを先に直して正典を後追いさせない。

## コンセプト

**STILL RACING.** — 重厚な黒ベース × ピンク（マゼンタ系レッド）アクセント。
エディトリアル誌風のレイアウトに、レーシング由来のスピード感を足す。

## 色

| トークン | 値 | 用途 |
| --- | --- | --- |
| `--ink` | `#0a0a0a` | 地（写真の下地・ベタ面）、紙の上の文字 |
| `--paper` | `#f5f4ef` | 明るい地、黒地の上の文字の代わりに使ってもよい |
| `--paper-2` | `#ebe9e2` | 明るい地の二段目 |
| `--rouge` | `#ff1d4c` | アクセント。キッカー・CTA・細罫・番号。**面積は全体の1割まで** |
| `--rouge-deep` | `#c81038` | rouge の押下・影 |
| `--gold` | `#c8a96a` | 予備。勝利・表彰の告知に限る |

白文字（`#ffffff`）は写真の上・黒地の上で使う。不透明度を下げた白（0.6〜0.7）は補足のみ。

## 書体

| 役割 | 書体 | 備考 |
| --- | --- | --- |
| 和文見出し・選手名 | Noto Serif JP 700/900 | |
| 和文本文・補足 | Noto Sans JP 400/500/700 | |
| 欧文の大見出し・数字（日付・ゼッケン） | Anton | 大文字。字間 0.02〜0.05em |
| キャプション・キッカー・CTA | Bebas Neue | 大文字。字間 0.2〜0.32em |

読み込みは Google Fonts：
`https://fonts.googleapis.com/css2?family=Anton&family=Bebas+Neue&family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@400;700;900&display=swap`

## 言葉（表記）

- シリーズ名：`SUPER FORMULA`（**SF公式ロゴは使用不可。テキスト表記のみ**）／ `FIA-F4`
- 選手名：`チャーリー・ブルツ`（`CHARLIE WURZ`）／ `池島 実紅`（`MIKU IKEJIMA`）。「ブルツ」以外の表記（ヴルツ等）は使わない
- チーム：`TEAM GOH`（SF）／ `TGM Grand Prix`（F4）
- ゼッケン：`#53`（両選手とも）
- 主語：`IMP × RACING`、`Impress International`
- 日付：`11.20 – 11.22` のようにドット区切り、範囲は en dash

## 素材

| ファイル | 中身 | 使える地 |
| --- | --- | --- |
| `assets/team_goh.png` | TEAM GOH ロゴ（白抜き・縦長） | 黒地・暗い写真 |
| `assets/tgm_light.png` | TGM Grand Prix ロゴ（明色） | 黒地・暗い写真 |
| `assets/tgm_dark.png` | TGM Grand Prix ロゴ（暗色） | 明るい地 |

写真はサイト側のものを相対参照で使う（コピーしない）：
- SF：`sf/images/wurz_*.jpg`（例：`wurz_low_angle.jpg` ピットアウトのローアングル、`wurz_race_panning.jpg` 流し撮り、`wurz_front_53.jpg` 正面）
- F4：`f4/images/ikejima_*.jpg`（例：`ikejima_fuji_mountain.jpg` 富士山バック、`ikejima_race_battle.jpg` バトル）
