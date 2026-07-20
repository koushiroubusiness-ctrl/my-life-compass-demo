"""レイアウト共通処理: ページ設定・CSS読み込み・ページヘッダー。"""
from pathlib import Path
import streamlit as st

# プロジェクトルート（このファイルの2つ上）
ROOT = Path(__file__).resolve().parent.parent
CSS_PATH = ROOT / "assets" / "styles.css"


def setup_page():
    """st.set_page_config は最初に一度だけ呼ぶ。"""
    st.set_page_config(
        page_title="My Life Compass",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def load_css():
    """assets/styles.css を読み込んで適用する。"""
    if CSS_PATH.exists():
        css = CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str, user_initial: str = "康"):
    """上部のページヘッダー: ページ名・短い説明・ユーザーアイコン。"""
    st.markdown(
        f"""
        <div class="mlc-header">
          <div>
            <p class="mlc-title">{title}</p>
            <p class="mlc-subtitle">{subtitle}</p>
          </div>
          <div class="mlc-avatar">{user_initial}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str, note: str = ""):
    """中見出し（余白を保った小見出し）。"""
    html = f'<div class="mlc-section-label">{text}</div>'
    if note:
        html += f'<div class="mlc-soft-note">{note}</div>'
    st.markdown(html, unsafe_allow_html=True)
