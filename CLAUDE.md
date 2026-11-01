# imp-racing

インプレスインターナショナル様のレーシングサイト（GitHub Pages で配信する静的サイト）。
サイトの構成と運用は `README.md` を参照。

## バナー制作の依頼が来たら

「バナーを作って」「告知画像を〇サイズで」などの依頼は、`.claude/skills/banner-builder/SKILL.md`
（スキル `banner-builder`）の手順に従う。道具と規範はすべて `banner-harness/` にある。

- ブランドの規範：`banner-harness/brands/impress-racing/`（`brand.md` / `banner.md`）
- 原稿のひな形：`banner-harness/templates/brief.md`
- 入口のコマンド：`python3 banner-harness/tools/banner.py --help`

人の直し（「ロゴはもっと小さく」など）で、次の依頼にも効くものは
`banner-harness/brands/impress-racing/banner.md` に書き戻す。その場限りの直しは書き戻さない。
