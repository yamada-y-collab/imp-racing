---
name: banner-builder
description: Impress Racing（SUPER FORMULA / FIA-F4）の告知バナーを、原稿 → 生成 → 検査 → 直し → 書き出し（PNG・シート・PPTX）の順で作る。「バナーを作って」「告知画像を〇サイズで」「バナーを直して」と言われたら使う。
---

# banner-builder

道具はすべて `banner-harness/` にある。設計の考え方は `banner-harness/docs/design.md`。

## 1. 原稿にする

```bash
python3 banner-harness/tools/banner.py init <id>
```

`<id>` は英小文字とハイフン（例 `sf-finale-suzuka`）。`banner-harness/work/<id>/brief.md` を埋める。

- 依頼の文から **入れる文言**（優先度順）と **落としてはいけない語** を分けて書く。
  依頼者が明言していない語を「落としてはいけない語」に足さない。
- 日付・ラウンド・会場は推測で書かない。リポジトリ内（`index.html` の NEXT RACE、`sf/schedule.html`、`f4/schedule.html`）
  で確かめ、見つからなければ依頼者に聞く。
- サイズは banner.md「6. サイズ別の注意」から選ぶ。指定がなければ6サイズすべて。
- 原稿を依頼者に見せて確認を取ってから次へ（無人で回すときを除く）。

## 2. 生成する

```bash
python3 banner-harness/tools/banner.py generate <id>
```

`work/<id>/v1/PROMPT.md` ができる。**それを読み、その指示どおりに** `v1/<幅>x<高さ>.html` を書く。
`brand.md` と `banner.md` が規範。既存の `banner.html` は参考に読んでよいが、写さない。

## 3. 書き出して、検査を通す

```bash
python3 banner-harness/tools/banner.py export <id>
```

実測（`html2layout.mjs`）→ 検査（`check.py`）→ シート（`sheet.py`）→ PPTX（`layout2pptx.py`）。

検査は事故を見つけるためのもので、流れは止めない（error があっても書き出しは最後まで走り、所見は `out/check.json` に残る）。
無人実行や CI で止めたいときだけ `--strict`。

- `error` が残っている間は人に見せない。HTML を直して export をやり直す。
- `warn` は直すか、残す理由を一言添える。
- `out/sheet.png` を自分の目で見る（Read で画像を開く）。検査は「写真の主役に文字が乗っている」
  「組みが窮屈」のような見た目の問題を拾えない。
- **自分で見て直すのは2回まで。** それでも気になる点が残れば、直さずに所見として人に渡す
  （同じところを何度もいじって組みが崩れるのを防ぐ）。

## 4. 直す

```bash
python3 banner-harness/tools/banner.py revise <id> "ロゴをもう一回り小さく"
```

前の版を写した `v2/` と、直しを含んだ `v2/PROMPT.md` ができる。直しに関係するところだけを変え、export する。

直しが**次の依頼にも効く**もの（「チームロゴは隅に」など）なら、
`banner-harness/brands/impress-racing/banner.md` の該当節に1行で足し、`[由来：<id> の直し]` を付ける。
その場限りのもの（「今回は写真を差し替え」）は戻さない。迷ったら依頼者に聞く。

## 5. 渡す

`out/sheet.png`（一覧）、`out/<size>.png`（各サイズ）、`out/pptx/<size>.pptx`（Canva にドラッグして仕上げる用）を渡す。
所見（`out/check.json` の warn / info）を短く添える。

## 正典が変わったとき

サイトの色（`assets/shared.css`）・コンセプト（`README.md`）・ロゴ（`assets/logos/`）が変わったら：

```bash
python3 banner-harness/tools/sync_brand.py
```

差分が出たら brand.md を直し、`--write` でハッシュを更新する。
