# 商品紹介動画の素材づくり（Playwright 自動撮影）

My Life Compass のモック画面を Playwright で自動操作し、Apple の商品紹介動画のような
「操作イメージ動画」の素材（WebM）を、実行するだけで生成します。テストではなく素材づくりが目的で、
速さより自然な見え方を優先しています。

## 何が起きるか（操作シナリオ）

1. トップ（Dashboard）を表示 … ブランドのタイトルカード → 本編へフェードイン
2. Dashboard 全体（今日の一歩／Compassカード／現在地）を見せる
3. サイドナビから **Compass** を開く
4. Compassカードの「⋯ →編集する」で詳細（価値観・目指したい未来・理由・期間）を見せる
5. Compassカードの「道筋をつくる」で Route へ入り、**AIチャット（対話でつくる）** を開いて
   「今の仕事を続けるべきか、転職するべきか迷っています」と入力（送信はしない）
6. **Route**（Compass が具体的な道筋＝タイムラインへ）を見せ、期間の詳細を開く
7. **Journey**（今日の一歩・具体的な行動）を見せる
8. **Dashboard** へ戻って全体を約3秒表示して終了

各画面切り替え後に 1.5〜3秒の待機を入れ、クリック前後にも“ため”を入れています。
疑似マウスカーソル（青い丸）が動くので、人の操作らしく見えます。

## 前提

- Python 側モックが起動していること：`streamlit run app.py`（既定 http://localhost:8501/ ）
- Node の依存はインストール済み（`@playwright/test` と Chromium・ffmpeg）。
  もし未取得なら `npm install` と `npx playwright install chromium` を実行。

## 実行コマンド

```bash
# 縦型（Instagramリール / X / note 向け・1080x1920）※既定
npm run video
# または
npm run video:portrait

# 横型（YouTube 等・1920x1080）
npm run video:landscape
```

内部的には `node scripts/record-demo.mjs [portrait|landscape]` を呼びます。

### 環境変数での微調整（任意）

| 変数 | 既定 | 説明 |
| --- | --- | --- |
| `MLC_ORIENTATION` | `portrait` | `portrait` / `landscape`（CLI 引数が優先） |
| `MLC_BASE_URL` | `http://localhost:8501/` | モックの URL |
| `MLC_PACE` | `1` | 待機時間の倍率。`1.3` でゆっくり、`0.8` で速め |
| `MLC_HEADED` | （未設定） | `1` でブラウザを表示しながら撮影 |

例：`MLC_PACE=1.3 node scripts/record-demo.mjs portrait`

## 動画の保存先

```
playwright-videos/my-life-compass_portrait.webm    # 縦型
playwright-videos/my-life-compass_landscape.webm   # 横型
```

形式は WebM（VP8）。実行のたびに同じ名前で上書きされます（`.gitignore` 済み）。

## 手順（起動 → 動画作成）

```bash
# 1. モックを起動（別ターミナルで起動したままにする）
streamlit run app.py

# 2. 縦型を撮影
npm run video

# 3. 横型も撮る場合
npm run video:landscape

# 4. 生成物を確認
#    playwright-videos/my-life-compass_portrait.webm など
```

## きれいに撮るための工夫（実装メモ）

- **ブラウザ上部バーは映らない**：ヘッドレス Chromium で撮るためツールバー等は写りません。
- **読み込み途中を映さない**：描画完了までブランドのタイトルカード（白背景）で覆い、
  スケルトンが消えてから静かにフェードアウトします。
- **表示完了を待つ**：固定 `sleep` だけに頼らず、各画面固有の要素（テキスト・ボタン）の
  表示待ちと、Streamlit のスケルトン消失待ちを併用します。
- **壊れにくい要素特定**：Streamlit が付与する安定クラス（`.st-key-*`）、ボタンの表示名、
  サイドナビ（`option_menu` は iframe）の `.nav-link` テキストで特定しています。
- **不自然なスクロールを避ける**：必要な要素だけを中央へ smooth スクロールします。
- **エラーで止まりにくい**：詳細操作は try/catch で包み、失敗しても撮影を続行します。
- **再現性**：毎回ブラウザ更新で session_state が初期化されるため、同じ操作・同じ見え方になります。
- **データを壊さない**：Compass は3枚（上限）のままにするため、AIチャットは Route 側の
  「対話でつくる」を使います（新規整理チャットは上限で押せないため）。

## 縦型で余白が気になる場合

モック本体はデスクトップ表示（サイドバー＋本文）を基準にしているため、縦型（1080x1920）では
本文の下に余白が出ます。埋もれずに読める範囲であれば素材として問題ありませんが、より画面を
埋めたい場合は **横型（1920x1080）** の利用や、書き出し後の編集ソフトでのトリミングを推奨します。
