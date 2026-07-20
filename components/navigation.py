"""サイドナビゲーション。streamlit-option-menu で My Life Compass らしい見た目にする。

Vision は今回のモックでは表示しない（ファイル・データは残す）。
Compassカードから Route へ移動するようなプログラム遷移は、
session_state.nav_override を manual_select で反映して実現する。

サイドバーは VS Code / Cursor のように開閉できる。
- 開いた状態：ロゴ + メニュー名つきのナビ（option_menu）
- 閉じた状態：幅を細くし、アイコン中心のコンパクト表示
開閉しても現在ページの選択状態は保たれ、メイン画面のレイアウトは崩れない。
"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu

# (表示ラベル, Bootstrap Icon 名, 閉じた状態のアイコン絵文字)
NAV_ITEMS = [
    ("Dashboard", "house",          "🏠"),
    ("Compass",   "compass",        "🧭"),
    ("Route",     "signpost-2",     "🗺️"),
    ("Journey",   "person-walking", "🚶"),
    ("Reflect",   "journal-text",   "📖"),
    ("Update",    "arrow-repeat",   "🔄"),
    ("Settings",  "gear",           "⚙️"),
]


def _apply_nav_override(labels):
    """プログラム遷移（Compass → Route など）を現在ページへ反映する。

    返り値: option_menu の manual_select に渡すインデックス（無ければ None）。
    """
    ss = st.session_state
    manual = None
    override = ss.get("nav_override")
    if override in labels:
        ss.current_page = override
        manual = labels.index(override)
    ss.nav_override = None
    return manual


def _render_open(labels, icons, manual):
    """開いた状態：ロゴ + メニュー名つきナビ + 補足。"""
    ss = st.session_state

    st.markdown(
        """
        <div class="mlc-brand">
          <div class="mlc-logo">🧭 My Life Compass</div>
          <div class="mlc-tagline">自分らしい人生を、一歩ずつ形に。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    default_idx = labels.index(ss.current_page)
    kwargs = {}
    if manual is not None:
        kwargs["manual_select"] = manual

    selected = option_menu(
        menu_title=None,
        options=labels,
        icons=icons,
        default_index=default_idx,
        key="mlc_nav_menu",
        styles={
            "container": {"padding": "2px 0", "background-color": "#ffffff"},
            "icon": {"color": "#86a894", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px",
                "font-weight": "500",
                "color": "#3a3f45",
                "padding": "11px 14px",
                "margin": "3px 0",
                "border-radius": "12px",
                "--hover-color": "#f1f0ea",
            },
            "nav-link-selected": {
                "background-color": "#eaf0f8",
                "color": "#5b7db1",
                "font-weight": "700",
            },
        },
        **kwargs,
    )

    # ユーザーがナビをクリックした場合は現在ページを更新
    if manual is None and selected in labels and selected != ss.current_page:
        ss.current_page = selected

    st.markdown(
        """
        <div class="mlc-sidebar-note">
          焦らなくて大丈夫です。<br>
          今日できることを、一緒に少しずつ整理していきましょう。
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_collapsed():
    """閉じた状態：ロゴを小さく、アイコンボタンだけを縦に並べる。"""
    ss = st.session_state
    # このマーカーがあるとき、CSS でサイドバー幅を細くする
    st.markdown('<div class="mlc-sb-collapsed"></div>', unsafe_allow_html=True)
    st.markdown('<div class="mlc-brand-mini">🧭</div>', unsafe_allow_html=True)

    for label, _icon, emoji in NAV_ITEMS:
        is_current = (label == ss.current_page)
        if st.button(emoji, key=f"mlc_sb_icon_{label}",
                     type="primary" if is_current else "secondary",
                     use_container_width=True,
                     help=label):
            ss.current_page = label
            st.rerun()


def _inject_mobile_nav():
    """スマホ幅（≤768px）でサイドバーを開閉するハンバーガー/背景/JSを注入する。

    st.markdown ではスクリプトが実行されないため components.html（iframe）から
    親ドキュメント（window.parent.document）を操作する。

    対象要素（実際のクラス名）:
      - サイドバー本体 : section[data-testid="stSidebar"]（＝独自ナビの入れ物）
      - トグルボタン   : .mlc-mobile-hamburger（自前で生成、id=mlc-mobile-hamburger）
      - オーバーレイ   : .mlc-sb-backdrop（自前で生成、id=mlc-sb-backdrop）
      - 開状態フラグ   : body.mlc-sb-open（CSS メディアクエリで見た目を切替）

    Streamlit は再描画で DOM を作り直すため、DOMContentLoaded だけに頼らず
    MutationObserver で「対象要素が生成された後」に毎回イベントを保証し、
    dataset フラグでイベントの二重登録を防ぐ。ネイティブの折りたたみ
    コントロール（左上の「≫」）はバージョン差でCSSだけでは消せないことが
    あるため JS でも確実に隠す。PC 幅では CSS 側で全て無効化される。
    """
    components.html(
        """
        <script>
        (function () {
          const win = window.parent;
          const doc = win.document;
          if (!doc || !doc.body) return;

          const HAM_ID = "mlc-mobile-hamburger";
          const BD_ID  = "mlc-sb-backdrop";
          const OPEN   = "mlc-sb-open";
          const SB_SEL = 'section[data-testid="stSidebar"]';

          const sidebarEl = () => doc.querySelector(SB_SEL);
          const isOpen = () => doc.body.classList.contains(OPEN);

          function syncAria(state) {
            const btn = doc.getElementById(HAM_ID);
            if (btn) btn.setAttribute("aria-expanded", state ? "true" : "false");
          }
          function open()   { doc.body.classList.add(OPEN);    syncAria(true);  }
          function close()  { doc.body.classList.remove(OPEN); syncAria(false); }
          function toggle() { isOpen() ? close() : open(); }

          // --- トグルボタン（無ければ生成、消えたら再生成、二重登録は防ぐ） ---
          function ensureHamburger() {
            let btn = doc.getElementById(HAM_ID);
            if (!btn) {
              btn = doc.createElement("button");
              btn.id = HAM_ID;
              btn.className = "mlc-mobile-hamburger";
              btn.type = "button";
              btn.setAttribute("aria-label", "メニュー");
              btn.setAttribute("aria-expanded", isOpen() ? "true" : "false");
              btn.textContent = "\\u2630";  // ☰
              doc.body.appendChild(btn);
            } else if (btn.parentNode !== doc.body) {
              doc.body.appendChild(btn);   // 別要素配下に移されていたら戻す
            }
            if (!btn.dataset.mlcBound) {   // イベント二重登録防止
              btn.dataset.mlcBound = "1";
              btn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                toggle();
              });
            }
          }

          // --- オーバーレイ（サイドバー外タップで閉じる用） ---
          function ensureBackdrop() {
            let bd = doc.getElementById(BD_ID);
            if (!bd) {
              bd = doc.createElement("div");
              bd.id = BD_ID;
              bd.className = "mlc-sb-backdrop";
              doc.body.appendChild(bd);
            } else if (bd.parentNode !== doc.body) {
              doc.body.appendChild(bd);
            }
            if (!bd.dataset.mlcBound) {
              bd.dataset.mlcBound = "1";
              bd.addEventListener("click", function (e) {
                e.stopPropagation();
                close();
              });
            }
          }

          // --- Streamlit ネイティブの折りたたみ「≫」を確実に隠す ---
          function hideNativeControls() {
            const sels = [
              '[data-testid="stSidebarCollapseButton"]',
              '[data-testid="stSidebarCollapsedControl"]',
              '[data-testid="collapsedControl"]',
            ];
            sels.forEach(function (s) {
              doc.querySelectorAll(s).forEach(function (el) {
                el.style.display = "none";
              });
            });
          }

          function ensureAll() {
            ensureHamburger();
            ensureBackdrop();
            hideNativeControls();
          }

          // --- 閉じる系の委譲処理は親 window に一度だけ登録 ---
          if (!win.__mlcMobileNavBound) {
            win.__mlcMobileNavBound = true;

            // 外タップ / メニュー項目タップで閉じる（capture で先取り）
            doc.addEventListener("click", function (e) {
              if (!isOpen()) return;
              const ham = doc.getElementById(HAM_ID);
              if (ham && ham.contains(e.target)) return;  // トグルは専用ハンドラ
              const sb = sidebarEl();
              if (sb && sb.contains(e.target)) {
                // メニュー項目（リンク/ボタン等）を押したら少し待って閉じる
                if (e.target.closest(
                      'a, button, .nav-link, [role="link"], [role="option"], label')) {
                  setTimeout(close, 180);
                }
                return;  // サイドバー内のその他は閉じない
              }
              close();   // サイドバー外タップ → 閉じる
            }, true);

            // Esc で閉じる
            doc.addEventListener("keydown", function (e) {
              if (e.key === "Escape" && isOpen()) close();
            });

            // PC 幅に戻ったら開状態をリセット
            win.addEventListener("resize", function () {
              if (win.innerWidth > 768) close();
            });
          }

          // 初期化 + 再描画のたびに要素とイベントを保証（rAF でデバウンス）
          ensureAll();
          if (!win.__mlcMobileNavObserver) {
            let scheduled = false;
            const obs = new MutationObserver(function () {
              if (scheduled) return;
              scheduled = true;
              win.requestAnimationFrame(function () {
                scheduled = false;
                ensureAll();
              });
            });
            obs.observe(doc.body, { childList: true, subtree: true });
            win.__mlcMobileNavObserver = obs;
          }
        })();
        </script>
        """,
        height=0,
    )


def sidebar_nav() -> str:
    """サイドバーを描画し、選択されたページ名を返す。

    現在ページは session_state.current_page に保持する。開閉状態は
    session_state.sidebar_open で保持し、再実行でも失われない。
    """
    ss = st.session_state
    ss.setdefault("current_page", "Dashboard")
    ss.setdefault("sidebar_open", True)

    labels = [name for name, _, _ in NAV_ITEMS]
    icons = [icon for _, icon, _ in NAV_ITEMS]

    manual = _apply_nav_override(labels)

    with st.sidebar:
        # 左上の開閉ボタン（常に一番上に表示）
        toggle_label = "«  メニューをたたむ" if ss.sidebar_open else "☰"
        if st.button(toggle_label, key="mlc_sb_toggle", use_container_width=True):
            ss.sidebar_open = not ss.sidebar_open
            st.rerun()

        if ss.sidebar_open:
            _render_open(labels, icons, manual)
        else:
            _render_collapsed()

    # スマホ幅でのサイドバー開閉（ハンバーガー/背景/JS）を注入
    _inject_mobile_nav()

    return ss.current_page
