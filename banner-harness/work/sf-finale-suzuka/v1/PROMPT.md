# 生成の指示（Impress Racing）

あなたはエディトリアル誌のアートディレクターとして、Impress International のレーシング告知バナーを組む。

## 渡すもの

この後ろに、次の4つを連結して渡す（`tools/banner.py generate` が組み立てる）。

1. `brand.md` — 色・書体・言葉。ここにない色や書体は使わない
2. `banner.md` — 組み方の規範。人の直しが積み上がったもの。**矛盾したら banner.md が勝つ**
3. 原稿（`brief.md`）— 入れる文言・落としてはいけない語・サイズ
4. 前の版への直し（あれば）

型（テンプレートHTML）は渡さない。既存のバナー（リポジトリ直下 `banner.html`）は読んで構わないが、
写さずに、サイズごとに一から組むこと。横長と縦長で同じ配置を引き伸ばさない。

## 書くもの

サイズごとに1ファイル、`<出力先>/<幅>x<高さ>.html` を書く。各ファイルは次を守る。

- `<body>` の直下に `<main data-canvas>` を1つ置き、幅・高さをピクセルで固定する（`overflow: hidden`）
- 測る要素には `data-role` を付ける。検査と PPTX 書き出しはこれだけを見る
  - `data-role="text"` … 文字。**1要素1まとまり**（見出し・日付・選手名など）。中に別の `data-role` を入れない
  - `data-role="image"` … 写真（`<img>` か `background-image` の要素）
  - `data-role="logo"` … ロゴ（`<img>`）
  - `data-role="shape"` … ベタ面・罫・CTA の地など、PPTX でも図形として残したいもの
- 写真・ロゴのパスは HTML ファイルからの相対パスで書く（出力先はリポジトリ直下から4階層下：`../../../../`）
- フォントは brand.md の Google Fonts の URL を `<link>` で読む
- JavaScript は使わない。アニメーションも付けない（書き出しは静止画）

## 自分で確かめること

書き終えたら `python3 banner-harness/tools/banner.py export <id>` を走らせ、
`check.json` に `error` が残っていたら直してから人に見せる。`warn` は理由を添えて残してよい。


---

# 1. brand.md

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


---

# 2. banner.md

# バナーの組み方（規範）

人が直した内容のうち、次の依頼にも効くものをここに戻す。生成の指示文（`prompts/`）には
型（テンプレートHTML）を渡さない。渡すのはこの規範だけで、組み方は毎回サイズに合わせて考えさせる。

各項目の末尾の `[由来]` は、その規範がどこから来たかの記録。

## 1. 情報の優先順位

1. 何のレースか（シリーズ名・ラウンド・サーキット）
2. いつか（日付）
3. 誰か（選手名・チーム）
4. 行動（CTA：`VIEW SF SITE →` など）

小さいサイズ（短辺 300px 以下）では 3 の英字表記と、補足の和文を落としてよい。
**原稿の「落としてはいけない語」はどのサイズでも落とさない。** [由来：banner.html の SP 表示で英字を縮めた運用]

## 2. 地と写真

- 写真を使うときは、文字の側から黒のグラデーション（scrim）をかけ、文字の背後を暗くする。
  目安：文字側 0.85 → 反対側 0.2。[由来：banner.html `.banner__scrim`]
- 写真の主役（マシン・選手）に文字を重ねない。横長は左に文字・右に主役、縦長は上下に分ける。
- 写真がないとき・弱いときは `--ink` のベタ地に組む（VARIANT 02 の考え方）。

## 3. 文字

- 大見出し（シリーズ名・日付）は Anton。和文の見出しは Noto Serif JP。
- キッカー（`SPONSORSHIP — CATEGORY 01` のような小見出し）は Bebas Neue・rouge・左に 24px 程度の細罫。
- 文字はキャンバスの端から短辺の 5% 以上離す（安全域）。
- 最小の文字サイズは 10px（300×250 でも）。

## 4. ロゴ

- SF公式ロゴは使わない。チームロゴ（TEAM GOH / TGM Grand Prix）は使ってよい。
- チームロゴはチーム名の文字と同じ行か、右下の隅に置く。主役より目立たせない（高さは短辺の 10% まで）。
- 黒地・写真の上では `team_goh.png` / `tgm_light.png`、明るい地では `tgm_dark.png`。

## 5. CTA

- rouge の地に白の Bebas Neue。右下に置く。→ を付ける。
- 300×250 では CTA を省いてよい（バナー全体がリンクになるため）。

## 6. サイズ別の注意

| サイズ | 用途 | 注意 |
| --- | --- | --- |
| 1280×560 | imp-inc.jp トップ（16:7） | サイト掲載中の `banner.html` と並べて違和感がないこと |
| 1200×628 | OGP / X | 中央 1:1 にも主要情報が入ると X のタイムラインで切れにくい |
| 1080×1080 | Instagram フィード | |
| 1080×1350 | Instagram フィード（縦） | |
| 1080×1920 | ストーリーズ | 上 250px・下 340px は UI に隠れる。文字を置かない |
| 300×250 | ディスプレイ広告 | 情報は 1〜3 に絞る |


---

# 3. 原稿（brief.md）

---
id: sf-finale-suzuka
brand: impress-racing
sizes:
  - 1280x560
  - 1200x628
  - 1080x1080
  - 1080x1350
  - 1080x1920
  - 300x250
link: sf/index.html
---

# 原稿：sf-finale-suzuka

## 目的

SUPER FORMULA 最終戦（鈴鹿・JAF GP）の告知。imp-inc.jp トップと SNS で、
ブルツ選手の応援と SF サイトへの来訪を促す。
※ハーネスの通し確認用の見本。日付・ラウンドは sf/schedule.html より。

## 入れる文言

- SEASON FINALE
- SUPER FORMULA
- RD.11 / RD.12
- 鈴鹿サーキット
- 11.20 – 11.22
- チャーリー・ブルツ
- TEAM GOH
- #53 CHARLIE WURZ（省略可）
- JAF GRAND PRIX（省略可）
- VIEW SF SITE →（省略可）

## 落としてはいけない語

- SUPER FORMULA
- 鈴鹿
- 11.20
- チャーリー・ブルツ

## 使わない語

- ヴルツ

## 使う素材

- 写真：sf/images/wurz_low_angle.jpg（ピットアウトのローアングル。マシンは右寄り）
- ロゴ：brands/impress-racing/assets/team_goh.png

## 注意

- SF公式ロゴは使わない（テキスト表記のみ）


---

# 出力

- 出力先：`banner-harness/work/sf-finale-suzuka/v1/`（リポジトリ直下から）
- サイズ：1280x560, 1200x628, 1080x1080, 1080x1350, 1080x1920, 300x250
- 書き終えたら：`python3 banner-harness/tools/banner.py export sf-finale-suzuka`
