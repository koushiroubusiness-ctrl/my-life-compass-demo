# My Life Compass — 設計・デザインノート

本ドキュメントは、現在のリポジトリ（**操作可能なフロントモック** と **ランディングページ**）の
設計とデザインシステムをまとめたものです。サービスの世界観・情報設計の詳細は
[docs/extracted_design_notes.md](./docs/extracted_design_notes.md)（元資料からの抽出）を正本とします。

---

## 1. サービスの本質

- **人生の意思決定を支援する AI パートナー**。目標と日々の行動をつなぎ、自分らしい人生の実現を伴走する。
- **これではない**：AIチャット / タスク管理 / KPI管理 / 目標管理ツール / 業務システム。
- 価値：「何をすればいいか分からない」を「今日はこれでいい」に変える。
- 感情設計：**焦りを下げ、希望を上げる**。操作後に少し呼吸が楽になる。
- 主役はユーザー自身の人生。AI は画面の中心に置かず、必要な時にだけ静かに現れる。

### 体験の骨格（5つの壁 → 5つの体験）

| 壁 | 対応する体験 |
|---|---|
| ① 現在地が分からない | Compass：いまの自分と価値観を整理する |
| ② 行き先が決まらない | Compass / Vision：目指したい未来を言語化する |
| ③ 行動へ落とし込めない | Route / Journey：今日の一歩に変換する |
| ④ 続けられない | Journey / Reflect：できたことを実感する |
| ⑤ 変化に対応できない | Update：今の自分に合わせて見直す |

---

## 2. リポジトリ構成（現状）

```
My Life Compass/
├── app.py                  # モックのエントリ（option_menu の選択で各 render を呼ぶ）
├── .streamlit/config.toml  # lightテーマ・独自ナビ（自動サイドナビは無効化）
├── assets/
│   ├── styles.css          # モック全体のカスタムCSS（デザインの中心）
│   └── lp/*.png            # 画面キャプチャ（LP・紹介用）
├── components/             # 共通UI: layout / navigation / cards / ai_message /
│                           #   compass_card / route_card / chat_panel / reflection_panel
├── pages/                  # 画面本体: dashboard / compass / route / journey /
│                           #   reflect / update / settings / vision(モックでは非表示)
├── data/mock_data.py       # 仮データ（やさしいトーンの文章込み）
├── services/               # state.py（session_state・遷移）/ mock_ai_service.py
├── docs/extracted_design_notes.md  # サービス設計の正本
├── lp/                     # ランディングページ（index.html / styles.css / script.js）
└── tests/                  # Playwright E2E の雛形
```

- 画面本体は `pages/*.py` に `render()` 関数として実装し、`app.py` が選択に応じて呼び出す。
- 共通UIは `components/` に、仮データは `data/mock_data.py` に集約する。
- Streamlit は `pages/` を置くと自動でマルチページ・ナビを出すため、`.streamlit/config.toml` で
  `showSidebarNavigation = false` にして独自の option_menu に一本化している。

---

## 3. デザインシステム

### カラートークン（`assets/styles.css` の `:root`／LP と共通）

| 役割 | 変数 | 値 |
|---|---|---|
| Base | `--mlc-base` | `#ffffff` |
| Surface（薄いアイボリー） | `--mlc-surface` | `#f7f5ef` |
| Main（落ち着いた青） | `--mlc-main` | `#5b7db1` |
| Sub（優しい緑） | `--mlc-sub` | `#86a894` |
| Accent（控えめオレンジ） | `--mlc-accent` | `#d99b63` |
| Ink / Ink-soft（本文・補足） | `--mlc-ink` / `--mlc-ink-soft` | `#3a3f45` / `#6b7078` |
| Line（薄い境界線） | `--mlc-line` | `#e9e6dd` |

- 角丸は大きめ（`--mlc-radius: 22px`）、影は非常に弱い、余白は広め。
- フォントは **Noto Sans JP**。赤（Error）は多用しない。

### UI 原則

- 一画面一役割 / 次の一歩が自然に分かる / 比較対象は他人ではなく過去の自分 / 心が疲れない提案量。
- 使うUI：大きめカード / ラインアイコン / 余白のある入力欄 / 静かなAI提案 / 1つの主要CTA。
- 避けるUI：大量のボタン / KPIダッシュボード / 複雑なグラフ / チャット全面表示 / 赤い警告の多用。
- マイクロコピーは、押し付けず・急かさず・やさしく（例：「一緒に整理しましょう」「今日はここまでで十分です」）。

---

## 4. ランディングページ（`lp/`）

- 依存ライブラリなしの **HTML / CSS / バニラ JS**。ビルド不要でそのままブラウザで開ける。
- モックの `assets/styles.css` と同一のカラートークン・カード意匠・フォントを引き継ぎ、世界観を統一。
- **位置づけ**：単一システムの紹介ではなく、「人生・キャリアの意思決定に伴走するブランド」全体を紹介する。
  最終CTAは常に **「まずは無料相談を申し込む」**。導線は 無料相談（入口）→ 単発の転職サポート → 継続伴走 の順。
- サービス構成：**無料相談**（入口／営業なし）／ **単発サポート**（転職活動中の方向け：履歴書・職務経歴書添削、面接対策・模擬面接）／
  **継続伴走プログラム**（人生全体を整理したい方向け。My Life Compass はこの継続サポート専用のプラットフォームとして紹介）。
- 構成（縦スクロール1枚）：
  1. ファーストビュー（ブランドコンセプト＋無料相談CTA）→ 2. こんなお悩み → 3. 大切にしていること（押し付けない／一緒に整理／自分で選べる）→
  4. 無料相談（入口）→ 5. 転職活動サポート（カード：履歴書添削／面接対策）→ 6. 継続伴走プログラム（My Life Compass を大きく紹介）→
  7. できること（Compass / Route / Journey / Reflect / Update）→ 8. 利用の流れ（無料相談→転職サポート→継続伴走）→
  9. よくある質問 → 10. 最後のCTA（まずは無料相談を申し込む）
- 表現上の注意：架空の口コミ・利用者の声は掲載しない。医療・心理療法・診断・治療を連想させる表現、「治す／改善する」等の断定表現は使わない。
- 画面キャプチャは `../assets/lp/*.png` を参照。画像が無い場合もレイアウトが崩れないよう、
  枠は `aspect-ratio` で高さを確保し、`script.js` が読み込み失敗時にフォールバック表示へ切り替える。
- アニメーションは控えめ（スクロールでのフェード＋わずかな浮き上がり）。
  `prefers-reduced-motion` を尊重する。PC / タブレット / スマートフォンにレスポンシブ対応。

---

## 5. 注意点（モックの制約）

- 本番の DB / 外部 API / 生成 AI 連携・ログインは未使用。データは `session_state` 上のみで、
  ブラウザ再読み込みで初期化される。
- 生成 AI の応答は `services/mock_ai_service.py` によるモック。
