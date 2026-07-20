"""My Life Compass — 操作可能なフロントモック（エントリポイント）。

本番システムではなく、利用体験を確認・共有するためのモック。
バックエンド / DB / ログイン / 外部API / 生成AI連携は使わず、
すべて Python 内のモックデータと Streamlit の session_state で動く。
（ブラウザ再読み込みでデータは初期化される）

起動:  streamlit run app.py
"""
from components.layout import setup_page, load_css
from components.navigation import sidebar_nav
from services.state import init_session_state

# 各画面（pages/*.py の render 関数）。Vision は今回のモックでは表示しない。
from pages import dashboard, compass, route, journey, reflect, update, settings

# ページ名 → render 関数
PAGES = {
    "Dashboard": dashboard.render,
    "Compass":   compass.render,
    "Route":     route.render,
    "Journey":   journey.render,
    "Reflect":   reflect.render,
    "Update":    update.render,
    "Settings":  settings.render,
}


def main():
    setup_page()          # set_page_config は最初に一度だけ
    load_css()            # assets/styles.css を適用
    init_session_state()  # サンプルデータを session_state へ
    selected = sidebar_nav()   # 独自サイドナビ（option_menu）で選択
    PAGES.get(selected, dashboard.render)()   # 選択された画面を描画


if __name__ == "__main__":
    main()
