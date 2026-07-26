/**
 * My Life Compass — 商品紹介動画用の操作イメージ自動撮影スクリプト
 * =================================================================
 * Playwright を実行するだけで、画面操作 → 動画（WebM）保存まで完了します。
 * テストではなく「素材づくり」が目的なので、テンポは速さより自然さを優先します。
 *
 * 使い方（詳細は README を参照）:
 *   1. Streamlit モックを起動:   streamlit run app.py
 *   2. 縦型を撮る:               npm run video           （= portrait）
 *      横型を撮る:               npm run video:landscape
 *
 * 環境変数で切り替え:
 *   MLC_ORIENTATION = portrait | landscape   （既定: portrait）
 *   MLC_BASE_URL    = http://localhost:8501/  （既定）
 *   MLC_PACE        = 1.0                      （待機時間の倍率。大きいほどゆっくり）
 *   MLC_HEADED      = 1                        （ブラウザを表示して撮る。既定は非表示）
 *
 * 保存先:  playwright-videos/my-life-compass_<orientation>.webm
 */
import { chromium } from '@playwright/test';
import { mkdirSync, rmSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// ---------------------------------------------------------------------------
// 設定
// ---------------------------------------------------------------------------
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// 向きは CLI 引数（例: node scripts/record-demo.mjs landscape）を最優先し、
// 次に環境変数 MLC_ORIENTATION、既定は portrait。
const CLI_ORIENTATION = process.argv.slice(2)
  .find((a) => ['portrait', 'landscape'].includes(a.toLowerCase()));
const ORIENTATION = (CLI_ORIENTATION || process.env.MLC_ORIENTATION || 'portrait')
  .toLowerCase();
const BASE_URL = process.env.MLC_BASE_URL || 'http://localhost:8501/';
const PACE = Number(process.env.MLC_PACE || '1');
const HEADED = process.env.MLC_HEADED === '1';

// 縦型（Instagramリール / X / note 向け）と横型（YouTube等）の viewport。
const SIZES = {
  portrait: { width: 1080, height: 1920 },
  landscape: { width: 1920, height: 1080 },
};
const SIZE = SIZES[ORIENTATION] || SIZES.portrait;

const OUT_DIR = path.join(ROOT, 'playwright-videos');
const TMP_DIR = path.join(OUT_DIR, '.tmp');
const OUT_FILE = path.join(OUT_DIR, `my-life-compass_${ORIENTATION}.webm`);

// 待機時間（ミリ秒）。PACE 倍率をかけて調整する。
const T = {
  hold: 2000,      // 各画面の基本停止（約2秒）
  holdLong: 3000,  // 最後の Dashboard など、長めの停止（約3秒）
  settle: 700,     // 画面遷移直後の落ち着き待ち
  beforeClick: 450,// クリック直前の“ため”
  afterClick: 900, // クリック後、次操作までの間
};
const ms = (n) => Math.round(n * PACE);
const sleep = (n) => new Promise((r) => setTimeout(r, ms(n)));

// ---------------------------------------------------------------------------
// 疑似マウスカーソル（撮影用）。
// 実際の操作らしく見せるため、body に小さな丸を描き、mousemove に追従させる。
// Streamlit の再描画で body 直下の要素は消えないため、addInitScript で一度仕込めば
// セッション中ずっと残る。クリックは pointer-events:none で邪魔しない。
// ---------------------------------------------------------------------------
const CURSOR_SCRIPT = `
(() => {
  // iframe（option_menu 等の Streamlit コンポーネント）では何もしない。
  // カバー/カーソルはトップページのみ。iframe に入れると reveal が届かず
  // ナビが白カバーで隠れてしまう。
  if (window.top !== window.self) return;

  // --- 読み込み途中（Streamlit のスケルトン）を映さないための白カバー ---
  // 真っ白なカバーを最前面へ置き続け（body 生成後・再描画後も 100ms 間隔で再設置）、
  // 完全描画後に reveal で静かにフェードアウトする。これで“ローディングの見せ物”を防ぐ。
  let mlcRevealed = false;
  const ensureCover = () => {
    if (mlcRevealed || !document.body) return;
    let cv = document.getElementById('mlc-load-cover');
    if (!cv) {
      cv = document.createElement('div');
      cv.id = 'mlc-load-cover';
      cv.style.cssText = [
        'position:fixed', 'inset:0', 'background:#ffffff',
        'z-index:2147483646', 'pointer-events:none',
        'opacity:1', 'transition:opacity .6s ease',
        'display:flex', 'align-items:center', 'justify-content:center',
      ].join(';');
      // 白い待ち時間をブランドのタイトルカードに変える（ローディングの隠しも兼ねる）。
      cv.innerHTML =
        '<div style="text-align:center;font-family:sans-serif;' +
        'animation:mlcFadeIn 1.1s ease both;">' +
        '<div style="font-size:64px;line-height:1;margin-bottom:18px;">🧭</div>' +
        '<div style="font-size:34px;font-weight:800;color:#5B7DB1;' +
        'letter-spacing:.5px;">My Life Compass</div>' +
        '<div style="font-size:18px;color:#6b7078;margin-top:12px;">' +
        '自分らしい人生を、一歩ずつ形に。</div></div>';
      if (!document.getElementById('mlc-cover-kf')) {
        const st = document.createElement('style');
        st.id = 'mlc-cover-kf';
        st.textContent =
          '@keyframes mlcFadeIn{from{opacity:0;transform:translateY(8px)}' +
          'to{opacity:1;transform:none}}';
        document.head && document.head.appendChild(st);
      }
      document.body.appendChild(cv);
    }
  };
  window.__mlcRevealApp = () => {
    mlcRevealed = true;
    const cv = document.getElementById('mlc-load-cover');
    if (!cv) return;
    cv.style.opacity = '0';
    setTimeout(() => cv.remove(), 700);
  };
  const coverIv = setInterval(() => {
    if (mlcRevealed) { clearInterval(coverIv); return; }
    ensureCover();
  }, 100);
  ensureCover();

  if (window.__mlcCursorInstalled) return;
  window.__mlcCursorInstalled = true;
  const ensure = () => {
    let c = document.getElementById('mlc-demo-cursor');
    if (!c) {
      c = document.createElement('div');
      c.id = 'mlc-demo-cursor';
      c.style.cssText = [
        'position:fixed', 'top:0', 'left:0', 'width:22px', 'height:22px',
        'margin:-11px 0 0 -11px', 'border-radius:50%',
        'background:rgba(91,125,177,0.35)',
        'border:2px solid rgba(91,125,177,0.9)',
        'box-shadow:0 2px 10px rgba(0,0,0,0.25)',
        'pointer-events:none', 'z-index:2147483647',
        'transition:transform .08s ease-out', 'transform:translate(-50px,-50px)',
      ].join(';');
      document.body.appendChild(c);
    }
    return c;
  };
  const move = (x, y) => {
    const c = ensure();
    c.style.transform = 'translate(' + x + 'px,' + y + 'px)';
  };
  document.addEventListener('mousemove', (e) => move(e.clientX, e.clientY), true);
  document.addEventListener('mousedown', () => {
    const c = ensure();
    c.style.background = 'rgba(91,125,177,0.65)';
    setTimeout(() => (c.style.background = 'rgba(91,125,177,0.35)'), 180);
  }, true);
  // 再描画に備えて存在保証
  new MutationObserver(() => ensure()).observe(document.body, { childList: true });
  ensure();
})();
`;

// ---------------------------------------------------------------------------
// 汎用ヘルパー
// ---------------------------------------------------------------------------
function log(msg) {
  // eslint-disable-next-line no-console
  console.log(`[record-demo] ${msg}`);
}

/** Streamlit の再実行（右上のランニング表示）が落ち着くのを待つ。失敗しても無視。 */
async function waitStreamlitIdle(page) {
  try {
    await page.locator('[data-testid="stStatusWidget"]')
      .waitFor({ state: 'hidden', timeout: 8000 });
  } catch { /* 表示されない環境もあるので無視 */ }
}

/** スケルトン（読み込みプレースホルダ）が消えるまで待つ。 */
async function waitNoSkeleton(page, timeout = 15000) {
  const deadline = Date.now() + timeout;
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const n = await page.locator('[data-testid="stSkeleton"]').count().catch(() => 0);
    if (n === 0) return;
    if (Date.now() > deadline) return;
    await new Promise((r) => setTimeout(r, 250));
  }
}

/** 要素を画面中央へなめらかにスクロールして収める。 */
async function bringIntoView(locator) {
  try {
    await locator.evaluate((el) =>
      el.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' }));
  } catch { /* iframe 内などで失敗しても続行 */ }
}

/** カーソルを要素中心へなめらかに移動 → 少し“ため”てからクリック。 */
async function smoothClick(page, locator, { label = '' } = {}) {
  await locator.first().waitFor({ state: 'visible', timeout: 15000 });
  await bringIntoView(locator.first());
  await sleep(300);
  const box = await locator.first().boundingBox();
  if (box) {
    const x = box.x + box.width / 2;
    const y = box.y + box.height / 2;
    await page.mouse.move(x, y, { steps: 24 });
    await sleep(T.beforeClick);
  }
  await locator.first().click({ timeout: 15000 });
  if (label) log(`click: ${label}`);
  await waitStreamlitIdle(page);
  await sleep(T.afterClick);
}

/** サイドバーの option_menu（iframe）内のナビリンク。
 *  リンクには Bootstrap アイコンの字形が含まれ role=link の名前一致が効かないため、
 *  安定する .nav-link + テキスト一致で特定する。 */
function navLink(page, name) {
  return page
    .frameLocator('iframe[title="streamlit_option_menu.option_menu"]')
    .locator('.nav-link', { hasText: name });
}

/** 指定ページへ遷移し、目印テキストが出るまで待って落ち着かせる。 */
async function goToPage(page, name, readyLocator) {
  await smoothClick(page, navLink(page, name), { label: `nav → ${name}` });
  await readyLocator.first().waitFor({ state: 'visible', timeout: 20000 });
  await waitStreamlitIdle(page);
  await sleep(T.settle);
}

// ---------------------------------------------------------------------------
// メイン
// ---------------------------------------------------------------------------
async function main() {
  log(`orientation=${ORIENTATION} size=${SIZE.width}x${SIZE.height} pace=${PACE}`);
  log(`base=${BASE_URL}`);

  // 出力先を用意（前回の一時ファイルは掃除）。
  rmSync(TMP_DIR, { recursive: true, force: true });
  mkdirSync(TMP_DIR, { recursive: true });
  mkdirSync(OUT_DIR, { recursive: true });

  const browser = await chromium.launch({
    headless: !HEADED,
    args: ['--force-color-profile=srgb', '--hide-scrollbars'],
  });

  // 事前ウォームアップ：本番録画でローディングを映さないよう、別ページで一度読み込む。
  const warm = await browser.newContext({ viewport: SIZE });
  try {
    const wp = await warm.newPage();
    await wp.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 60000 });
    await wp.waitForTimeout(3500);
  } catch (e) {
    log(`warmup skipped: ${e.message}`);
  } finally {
    await warm.close();
  }

  // 録画用コンテキスト。動画サイズ＝viewport で等倍・くっきり。
  const context = await browser.newContext({
    viewport: SIZE,
    deviceScaleFactor: 1,
    recordVideo: { dir: TMP_DIR, size: SIZE },
    reducedMotion: 'no-preference',
  });
  await context.addInitScript(CURSOR_SCRIPT);
  const page = await context.newPage();

  try {
    // クリーンな白画面から開始（読み込み途中を見せない導入）。白カバーの裏で読み込む。
    await sleep(600);

    // === 1. トップ画面を表示 ===
    log('scenario 1: open top');
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 60000 });
    // Dashboard の主要素が完全に出るまで待つ（固定 sleep に頼りすぎない）。
    await page.getByText('今日の一歩', { exact: false }).first()
      .waitFor({ state: 'visible', timeout: 30000 });
    await navLink(page, 'Dashboard').first()
      .waitFor({ state: 'visible', timeout: 20000 });
    await waitNoSkeleton(page);      // スケルトンが消えるまで待つ
    await waitStreamlitIdle(page);
    await sleep(1500);               // タイトルカード（ブランド）を読める間だけ見せる
    // 完全描画できたので、白カバーを静かにフェードアウトして本編を見せる。
    await page.evaluate(() => window.__mlcRevealApp && window.__mlcRevealApp());
    await sleep(T.settle);
    await sleep(T.hold); // 最初の画面を2秒表示

    // === 2. Dashboard 全体を見せる（今日の一歩・Compassカード・現在地）===
    log('scenario 2: dashboard overview');
    await page.getByText('今目指している未来', { exact: false }).first()
      .waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
    await sleep(T.hold); // 内容を認識できる時間

    // === 3. Compass を開く ===
    log('scenario 3: open Compass');
    await goToPage(page, 'Compass',
      page.getByRole('button', { name: /一緒に目指したい未来を整理する/ }));
    await sleep(T.hold);

    // === 4. Compass の詳細（価値観・目指したい未来・理由）を見せる ===
    // 先頭カードの「⋯」→「編集する」で、タイトル・説明・実現したい理由・目安の期間・
    // 価値観タグがそろった編集（詳細）画面を見せる。見せ終えたら「やめる」で閉じ、
    // カードは3枚のまま保つ（データを壊さない）。
    log('scenario 4: compass detail');
    try {
      await smoothClick(page, page.getByRole('button', { name: '⋯' }),
        { label: 'compass card ⋯' });
      await sleep(500);
      await smoothClick(page, page.getByRole('button', { name: '編集する' }),
        { label: '編集する' });
      await page.getByText('Compassを編集する', { exact: false }).first()
        .waitFor({ state: 'visible', timeout: 10000 });
      await sleep(T.hold);
      await smoothClick(page, page.getByRole('button', { name: 'やめる' }),
        { label: 'やめる' });
    } catch (e) {
      log(`scenario 4 fallback: ${e.message}`);
    }
    await sleep(T.settle);

    // === 5. AI チャット（壁打ち）を開く → 質問を入力 ===
    // Compass は3枚（上限）で新規整理チャットは押せないため、Compass カードの
    // 「道筋をつくる」から Route へ入り、そこで常時使える AI 壁打ち（対話でつくる）を開く。
    // これは Compass→Route への自然な導線でもあり、データも壊さない。
    log('scenario 5: open AI chat (Route dialogue)');
    await smoothClick(page, page.getByRole('button', { name: '道筋をつくる' }),
      { label: '道筋をつくる → Route' });
    const routeChatBtn = page.getByRole('button', { name: /道筋を一緒につくる（対話でつくる）/ });
    await routeChatBtn.first().waitFor({ state: 'visible', timeout: 20000 });
    await sleep(T.settle);
    await sleep(T.hold);
    await smoothClick(page, routeChatBtn, { label: 'open AI chat' });
    // チャットパネル（質問1）が出るまで待つ。
    await page.getByText('質問 1', { exact: false }).first()
      .waitFor({ state: 'visible', timeout: 15000 });
    await sleep(T.settle);
    try {
      // 最初の質問（期間）は選択式。1つ選んで、自由入力できる次の質問へ進める。
      await smoothClick(page, page.getByRole('button', { name: '3年', exact: true }),
        { label: 'choose 3年' });
      const box = page.getByRole('textbox', { name: /あなたの言葉で/ });
      await box.first().waitFor({ state: 'visible', timeout: 10000 });
      await bringIntoView(box.first());
      await sleep(400);
      await box.first().click();
      await sleep(300);
      await box.first().pressSequentially(
        '今の仕事を続けるべきか、転職するべきか迷っています',
        { delay: ms(55) });
      // 入力された状態を見せる（送信はしない）。
      await sleep(T.hold);
    } catch (e) {
      log(`scenario 5 input fallback: ${e.message}`);
      await sleep(T.hold);
    }
    // チャットを閉じて Route（道筋）を表に出す。
    await smoothClick(page, page.getByRole('button', { name: /✕ 閉じる/ }),
      { label: 'close chat' }).catch(() => {});
    await sleep(T.settle);

    // === 6. Route を見せる（Compass が具体的な道筋＝タイムラインへ）===
    log('scenario 6: show Route timeline');
    try {
      // 壁打ちで道筋が作られ、縦タイムラインが表示される。詳細を1つ開いて見せる。
      await page.getByText('この期間の詳細を見る', { exact: false }).first()
        .waitFor({ state: 'visible', timeout: 15000 });
      await sleep(T.hold);
      await smoothClick(page,
        page.getByText('この期間の詳細を見る', { exact: false }).first(),
        { label: 'route detail' });
      await sleep(T.hold);
    } catch (e) {
      log(`scenario 6 fallback: ${e.message}`);
      await sleep(T.hold);
    }

    // === 7. Journey を開く（今日の一歩・具体的な行動）===
    log('scenario 7: open Journey');
    await goToPage(page, 'Journey',
      page.getByRole('button', { name: 'できた' }));
    await sleep(T.hold);

    // === 8. Dashboard へ戻って終了 ===
    log('scenario 8: back to Dashboard');
    await goToPage(page, 'Dashboard',
      page.getByText('今日の一歩', { exact: false }));
    await sleep(T.holdLong); // 全体を3秒表示して終了

    log('scenario finished');
  } finally {
    // 動画はコンテキスト close 時に確定する。
    const video = page.video();
    await context.close();
    if (video) {
      try {
        rmSync(OUT_FILE, { force: true });
        await video.saveAs(OUT_FILE);
        log(`saved video: ${OUT_FILE}`);
      } catch (e) {
        // saveAs が使えない場合は生成ファイルを探して案内。
        const files = readdirSync(TMP_DIR).filter((f) => f.endsWith('.webm'));
        log(`saveAs failed (${e.message}). raw files: ${files.join(', ')}`);
      }
    }
    await browser.close();
    rmSync(TMP_DIR, { recursive: true, force: true });
  }
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error('[record-demo] FAILED:', err);
  process.exit(1);
});
