"""session_state の初期化。

すべてのデータは Streamlit の session_state 上に置く。
DB・永続化はしない（リロードで初期化されて問題ない）。
"""
import copy
import streamlit as st

from data.mock_data import SAMPLE_COMPASS_CARDS, SAMPLE_TODAY_STEPS


def init_session_state():
    """初回起動時にサンプルデータを session_state へ流し込む。"""
    ss = st.session_state

    # 現在のページ（プログラム遷移用）
    ss.setdefault("nav_override", None)

    # --- Compass ---
    if "compass_cards" not in ss:
        ss.compass_cards = copy.deepcopy(SAMPLE_COMPASS_CARDS)
    ss.setdefault("compass_chat_open", False)
    ss.setdefault("compass_q_index", 0)
    ss.setdefault("compass_answers", {})   # {q_index: value}
    ss.setdefault("compass_next_id", 4)    # c4, c5... 用のカウンタ

    # --- Route ---
    ss.setdefault("selected_compass_id", None)
    ss.setdefault("route_chat_open", False)
    ss.setdefault("route_q_index", 0)
    ss.setdefault("routes", {})            # {compass_id: route_dict}
    # 各Compassごとの回答: {compass_id: {key: value}}
    ss.setdefault("route_answers", {})
    # 開いているアコーディオン: {compass_id: set(when)}
    ss.setdefault("route_open_axes", {})
    # 「今は考えない」項目: {compass_id: set(when)}
    ss.setdefault("route_hidden_axes", {})

    # --- Journey ---
    if "journey_today" not in ss:
        ss.journey_today = copy.deepcopy(SAMPLE_TODAY_STEPS)

    # --- Reflect ---
    ss.setdefault("reflect_inputs", {"did": "", "feeling": "", "notice": "", "next_try": ""})
    ss.setdefault("reflect_saved", False)


def get_compass_by_id(compass_id: str):
    """ID から Compass カードを取得（なければ None）。"""
    for c in st.session_state.compass_cards:
        if c["id"] == compass_id:
            return c
    return None


def get_compass_by_title(title: str):
    """タイトルから Compass カードを取得（なければ None）。

    今日の一歩は from にCompassタイトルを持つため、そこから対象Compassを引く。
    """
    if not title:
        return None
    for c in st.session_state.compass_cards:
        if c["title"] == title:
            return c
    return None


def open_compass_editor(compass_id: str):
    """指定Compassを選択状態にし、Compass画面をその編集画面から開く。"""
    ss = st.session_state
    ss.selected_compass_id = compass_id
    ss.compass_editing = compass_id
    ss.compass_chat_open = False        # 新規整理チャットは閉じておく
    go_to("Compass")


def go_to(page: str):
    """プログラムによるページ遷移（サイドナビの選択を上書き）。"""
    st.session_state.nav_override = page
