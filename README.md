# My Life Compass

**自分らしい人生を、一歩ずつ形に。**

My Life Compass は、人生に迷ったときに、自分の価値観や目指したい未来を整理し、
そこまでの道筋と今日の一歩を考えるための、人生の意思決定を支援する AI パートナーです。
タスク管理ツールや目標管理ツールではありません。

- 価値観と目指したい未来を整理する（**Compass**）
- 遠い未来から今日への道筋をつくる（**Route**）
- 心が疲れない今日の一歩に落とし込む（**Journey**）

> 価値：「何をすればいいか分からない」を「今日はこれでいい」に変える。
> 感情設計：焦りを下げ、希望を上げる。

---

## このリポジトリの中身

現在は、利用体験を確認・共有するための **操作可能なフロントモック**（Streamlit 製）と、
サービスを紹介する **ランディングページ（LP）** で構成されています。

本番のバックエンド / DB / ログイン / 外部 API / 生成 AI 連携は使わず、
モックは Python 内のモックデータと Streamlit の `session_state` だけで動きます
（ブラウザ再読み込みでデータは初期化されます）。

```
My Life Compass/
├── app.py                  # モックのエントリポイント（Streamlit）
├── .streamlit/config.toml  # テーマ・独自ナビ設定
├── assets/
│   ├── styles.css          # モックの世界観をつくるカスタムCSS
│   └── lp/                 # LP・紹介用の画面キャプチャ（png）
├── components/             # 共通UI（カード / ナビ / AI提案 など）
├── pages/                  # 各画面の render() 関数
├── data/mock_data.py       # 画面確認用の仮データ（やさしいトーンの文章込み）
├── services/               # session_state 初期化・画面遷移・モックAI
├── docs/                   # 設計ノート（元資料からの抽出まとめ）
├── lp/                     # ランディングページ（HTML / CSS / JS）
└── tests/                  # Playwright による E2E テストの雛形
```

設計の詳細・世界観は [DESIGN.md](./DESIGN.md) と
[docs/extracted_design_notes.md](./docs/extracted_design_notes.md) を参照してください。

---

## 1. モックの起動（Streamlit）

### 必要なもの
- Python 3.10 以上

### セットアップと実行

```powershell
# 1. 仮想環境の作成と有効化（Windows / PowerShell）
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. 依存パッケージのインストール
pip install -r requirements.txt

# 3. 起動
streamlit run app.py
```

ブラウザで開く画面：Dashboard / Compass / Route / Journey / Reflect / Update / Settings。

---

## 2. ランディングページ（LP）の閲覧

`lp/` フォルダに、HTML / CSS / JavaScript のみで作られた静的な LP があります。
ビルド不要で、ファイルをそのままブラウザで開けます。

```powershell
# ブラウザで直接開く
Start-Process .\lp\index.html

# もしくは簡易サーバーで配信して確認する場合
python -m http.server 8000
#   → http://localhost:8000/lp/ を開く
```

- LP は `assets/lp/` 内の画面キャプチャを使用します（画像が無くてもレイアウトは崩れません）。
- モックと同じカラー・フォント・カードデザインを引き継ぎ、世界観を統一しています。
- PC / タブレット / スマートフォンに対応したレスポンシブデザインです。

---

## デザインの世界観

- 白基調 ＋ 薄いアイボリー背景、落ち着いた青 / 優しい緑 / 控えめオレンジ。
- 大きな角丸カード、薄い境界線、非常に弱い影、十分な余白。
- 主役はユーザー自身の人生。AI は画面の中心に置かず、必要な時にだけ静かに現れる。
- マイクロコピーは、押し付けず・急かさず・やさしく（「一緒に整理しましょう」「今日はここまでで十分です」）。
