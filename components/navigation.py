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
    親ドキュメント（window.parent.document）を操作する。開閉は body の
    .mlc-sb-open クラスで制御し、CSS メディアクエリ側で見た目を切り替える。
    PC 幅ではハンバーガー/背景は CSS で非表示になり、挙動は変わらない。
    """
    components.html(
        """
        <script>
        (function () {
          const doc = window.parent.document;
          const body = doc.body;
          const HAM_ID = "mlc-mobile-hamburger";
          const BD_ID = "mlc-sb-backdrop";
          const OPEN = "mlc-sb-open";

          const close = () => body.classList.remove(OPEN);
          const toggle = () => body.classList.toggle(OPEN);

          // ハンバーガー / 背景を（無ければ）一度だけ作る
          if (!doc.getElementById(HAM_ID)) {
            const btn = doc.createElement("button");
            btn.id = HAM_ID;
            btn.className = "mlc-mobile-hamburger";
            btn.setAttribute("aria-label", "メニューを開く");
            btn.type = "button";
            btn.textContent = "\\u2630";  // ☰
            btn.addEventListener("click", function (e) {
              e.stopPropagation();
              toggle();
            });
            body.appendChild(btn);
          }
          if (!doc.getElementById(BD_ID)) {
            const bd = doc.createElement("div");
            bd.id = BD_ID;
            bd.className = "mlc-sb-backdrop";
            bd.addEventListener("click", close);
            body.appendChild(bd);
          }

          // 閉じる系のクリック処理は親ドキュメントに一度だけ委譲登録する
          if (!window.parent.__mlcMobileNavBound) {
            window.parent.__mlcMobileNavBound = true;
            doc.addEventListener("click", function (e) {
              if (!body.classList.contains(OPEN)) return;
              const ham = doc.getElementById(HAM_ID);
              if (ham && ham.contains(e.target)) return;   // トグルは専用ハンドラ
              const sb = doc.querySelector('section[data-testid="stSidebar"]');
              if (sb && sb.contains(e.target)) {
                // メニュー項目（リンク/ボタン）を押したら少し待って閉じる
                if (e.target.closest('a, .nav-link, button, [role="link"]')) {
                  setTimeout(close, 200);
                }
                return;   // サイドバー内のその他は閉じない
              }
              // サイドバー外をタップ → 閉じる
              close();
            }, true);
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
