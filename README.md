# Impress International — Racing Page

インプレスインターナショナル様のレーシングスポンサーシップ紹介サイト。
2026年5月13日の打合せで決定した「**SF用／F4用の2サイト独立構成**」に基づく。

🏁 **Live Preview：** GitHub Pages 公開後にURLが発行されます

---

## ファイル構成

```
.
├── index.html              ルート：SF/F4 への2サイト分岐ランディング
├── banner.html             imp-inc.jp トップに設置するバナー（2パターン）
├── assets/
│   └── shared.css          SF/F4 共通スタイルシート
├── sf/                     ────────  SUPER FORMULA 独立サイト  ────────
│   ├── index.html          SFトップ（ブルツ選手フィーチャー）
│   ├── schedule.html       年間スケジュール（全7大会12戦）
│   ├── driver.html         チャーリー・ブルツ 選手 詳細
│   ├── results.html        レース結果アーカイブ
│   └── images/             画像セット
├── f4/                     ────────  FIA-F4 独立サイト  ────────
│   ├── index.html          F4トップ（池島選手フィーチャー）
│   ├── schedule.html       年間スケジュール（全7大会）
│   ├── driver.html         池島 実紅 選手 詳細（経歴2009-2025フル年表）
│   ├── results.html        レース結果アーカイブ
│   └── images/             画像セット
├── images/                 ルート画像セット
├── source-materials/       支給素材（経歴PDF・F4ワッペンデータ）
├── _archive_v1/            旧統合ハブ版（参考保存）
├── .nojekyll               GitHub Pages 設定
├── .gitignore
└── README.md
```

## ページ遷移フロー

```
[imp-inc.jp トップに banner.html を埋め込み（2バナー並列）]
     │
     ├── SF バナー ───→ racing/sf/index.html (SF独立サイト)
     │                     ├── schedule.html
     │                     ├── driver.html
     │                     └── results.html
     │
     └── F4 バナー ───→ racing/f4/index.html (F4独立サイト)
                           ├── schedule.html
                           ├── driver.html
                           └── results.html

※ 直接 racing/index.html にアクセスした場合は分岐ランディングを表示
```

---

## 打合せ決定事項の反映状況（2026.05.13）

| 項目 | 決定内容 | 反映状況 |
| --- | --- | --- |
| サイト構成 | SF用／F4用の2サイト独立 | ✅ `sf/` `f4/` で分割完了 |
| SF公式ロゴ | 使用不可 → テキスト表記のみ | ✅ 全ページテキスト表記 |
| TEAM GOH ロゴ | 使用OK | ✅ SFサイト全体で使用 |
| TGMGP ロゴ | 使用OK | ✅ F4サイト全体で使用 |
| F4ロゴ | 使用OK | ✅ F4サイトで使用 |
| バナー配置（SP） | SF上 / F4下 | ✅ `banner.html` 反映済み |
| ブルツ選手バナー素材 | 「Race Action.jpg」採用 | ✅ `wurz_race_side.jpg` 使用 |
| 次回SFレース | 5/22-24 鈴鹿 | ✅ NEXT表示 |
| 次回F4レース | 6/11-14 岡山国際 | ✅ NEXT表示 |

---

## GitHub Pages で公開する手順

### 1. GitHubに新規リポジトリを作成
- リポジトリ名（推奨）：`imp-racing`
- 公開設定：**Public**
- README・.gitignore は「追加しない」

### 2. ローカルからプッシュ
```bash
git init
git add .
git commit -m "Initial mock: SF / F4 split site"
git branch -M main
git remote add origin https://github.com/[ユーザー名]/imp-racing.git
git push -u origin main
```

### 3. GitHub Pages を有効化
1. **Settings** → **Pages**
2. **Source**：`Deploy from a branch`
3. **Branch**：`main` / `/ (root)` → **Save**
4. 数分後、`https://[ユーザー名].github.io/imp-racing/` で公開

### 4. URL例
- 分岐ランディング：`/`
- SUPER FORMULA：`/sf/`
- FIA-F4：`/f4/`
- バナーサンプル：`/banner.html`
- F4 池島選手詳細：`/f4/driver.html`

---

## デザインコンセプト

**STILL RACING.** — 重厚な黒ベース × ピンク（マゼンタ系レッド）アクセント。

- 和欧混植：Noto Serif JP（見出し）× Anton（数字・英字）× Bebas Neue（キャプション）
- エディトリアル誌風レイアウト × レーシング由来のスピード感

カラー：
- `--ink: #0a0a0a` （黒）
- `--paper: #f5f4ef` （ペーパー）
- `--rouge: #ff1d4c` （ピンク／マゼンタレッド）

---

## 運用：レース結果PDFの追加

### F4 / SF 共通の手順
1. 受領したPDFを `sf/images/results/` または `f4/images/results/` 配下にアップロード
   命名規則例：`2026-r02-okayama-ikejima.pdf`
2. 該当の `results.html` 内、対応するカテゴリーグループの `.rc--coming` を `.rc` に変更
3. `<a href="...">` にPDFパスを指定、ファイルサイズ表記を更新

### NEXTマークの移動
`schedule.html` / `results.html` で、終わったレースの `.rd__status` クラスを `is-next` → `is-done` に。次のレースを `is-coming` → `is-next` に変更。

---

## 直近の更新

### 2026.05.14 (追加素材反映)
- **「ブルツ」→「ヴルツ」**全文修正（ヴルツPDFで正式表記を確認）
- **ヴルツ選手の経歴情報を全面アップデート**：
  - 父アレクサンダー・ヴルツ（元F1ドライバー／ル・マン2度総合優勝）の血を継ぐサラブレッド
  - 2017年カート開始、フェラーリ育成プログラムにスカウト
  - 2021 伊F4ルーキー優勝 / 2022 F4UAE選手権チャンピオン / 2023 F-リージョナル・オセアニアチャンピオン
  - 2025年12月鈴鹿合同テストでTEAM GOH参加 → 2026年正式参戦
- **新規写真素材を投入**：
  - SF: オートポリス第3戦（4/25）の実戦写真6枚（コックピット越し目線、ピットアウト、流し撮り、フロント正面など）
  - F4: 富士第1戦（5/1-4）の実戦写真6枚（富士山バック走行、ヘルメットポートレート、バトルシーン、コーナリングなど）
- **TEAM GOH ロゴ**（白抜き、黒BG用）を `assets/logos/team_goh.png` に配置、SF全ページに組み込み
- **TGM Grand Prix ロゴ**（dark/light両バージョン）を `assets/logos/` に配置、F4全ページに組み込み
  - TGMロゴのマゼンタピンクアクセントがサイトテーマカラー `--rouge` と完全一致
- 画像サイズ最適化（zip全体: 152MB → 8.4MB）

### 2026.05.13 (議事録反映の大改修)
- 統合ハブ案から **SF/F4 2サイト独立構成へ全面リファクタリング**
- 2026年スケジュールを公式情報に基づき正確に反映（SF: JAFモータースポーツ / F4: Honda Racing）
- `banner.html` を議事録仕様（SF上/F4下）に再調整
- 池島選手の経歴を2009-2025フル年表として `f4/driver.html` に反映
- 共通CSSを `assets/shared.css` にファイル化

---

Medirection × Impress International / 2026.05
