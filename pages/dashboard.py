"""Dashboard — 「今日の一歩」と「人生の現在地」を確認する場所。

機能一覧（Compass / Route / Journey のカード）ではない。ホーム画面として、
- 今日、何をすればいいか（各Compassに紐づく今日の一歩・最大3件）
- それがどのCompassにつながっているか
- 自分が今、どんな未来を目指しているか（Compassカード一覧）
が一目で分かるようにする。

表示順： 1. 挨拶 → 2. 今日の一歩一覧 → 3. 今目指しているCompassカード一覧 → 最近の気づき
"""
import streamlit as st

from components.layout import page_header, section_label
from components.cards import text_card
from components.ai_message import ai_message
from components.compass_card import render_summary_card
from services.state import (
    get_compass_by_title, open_compass_editor, go_to,
)
from data.mock_data import DASHBOARD, COMPASS_HEADER, USER

MAX_COMPASS = 3


# ---------------------------------------------------------
# 2. 今日の一歩（各Compassに紐づく一歩を最大3件）
# ---------------------------------------------------------
def _render_today_steps():
    ss = st.session_state
    steps = ss.journey_today[:3]

    st.markdown('<div class="mlc-today-lead">今日の一歩</div>', unsafe_allow_html=True)

    if not steps:
        st.markdown(
            '<div class="mlc-soft-note">今日の一歩はまだありません。'
            'Route の道筋から、今日の一歩を選んでみましょう。</div>',
            unsafe_allow_html=True,
        )
        return

    for i, step in enumerate(steps):
        compass = get_compass_by_title(step.get("from", ""))
        col_step, col_from = st.columns([3, 2])

        with col_step:
            # 一歩テキスト（押すと、その一歩に取り組む Journey へ）
            st.markdown('<div class="mlc-today-marker"></div>', unsafe_allow_html=True)
            if st.button(step["text"], key=f"dash_step_{i}", use_container_width=True):
                go_to("Journey")
                st.rerun()

        with col_from:
            # 「→」の先に、つながるCompass名を控えめなタグ／リンク風で表示
            if compass:
                st.markdown('<div class="mlc-fromtag-marker"></div>', unsafe_allow_html=True)
                if st.button(f"→ {compass['title']}", key=f"dash_from_{i}",
                             use_container_width=True):
                    open_compass_editor(compass["id"])
                    st.rerun()
            else:
                st.markdown(
                    '<div class="mlc-today-nolink">→ 今日の自分のための一歩</div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------
# 3. 今目指しているCompassカード一覧（横並び）
# ---------------------------------------------------------
def _open_new_compass_chat():
    """Compass画面を開き、新規整理チャットを開いた状態にする。"""
    ss = st.session_state
    ss.compass_chat_open = True
    ss.compass_q_index = 0
    ss.compass_answers = {}
    ss.compass_cand_override = {}
    ss.compass_editing = None
    go_to("Compass")


def _render_compass_cards():
    ss = st.session_state
    cards = ss.compass_cards
    total = len(cards) + len(ss.get("compass_held", []))
    can_add = total < MAX_COMPASS

    # 見出し + 右上の「新しいCompassを整理する」導線
    head_l, head_r = st.columns([3, 2])
    with head_l:
        section_label(f'{USER["greeting_name"]}が、今目指している未来',
                      "カードを押すと、そのCompassの編集画面へ移動します。")
    with head_r:
        if st.button("＋ 新しいCompassを整理する", key="dash_add_top",
                     type="primary", disabled=not can_add, use_container_width=True):
            _open_new_compass_chat()
            st.rerun()

    if not cards:
        st.markdown(f'<div class="mlc-soft-note">{COMPASS_HEADER["empty_note"]}</div>',
                    unsafe_allow_html=True)
        return

    # デスクトップ3枚横並び。狭い画面では Streamlit が自動で縦に折り返す。
    cols = st.columns(3)
    for i, card in enumerate(cards):
        with cols[i % 3]:
            if render_summary_card(card, key=f"dash_cc_{card['id']}"):
                open_compass_editor(card["id"])
                st.rerun()

    # 一覧の末尾の案内（3件登録済みのときは穏やかに理由を伝える）
    if not can_add:
        st.markdown(
            '<div class="mlc-add-note">新しく追加するには、'
            '現在のCompassを保留または削除してください。</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# エントリ
# ---------------------------------------------------------
def render():
    ss = st.session_state

    page_header(
        "Dashboard",
        "今日の一歩と、今の現在地を確認する場所です。焦らず、今日の一歩へ。",
        USER["initial"],
    )

    # 1. 挨拶
    st.markdown(
        f'<div class="mlc-page-lead">{DASHBOARD["greeting"]}</div>'
        f'<p style="font-size:1.0rem;color:#6b7078;margin-bottom:22px">'
        f'{DASHBOARD["greeting_sub"]}</p>',
        unsafe_allow_html=True,
    )

    # 2. 今日の一歩一覧
    _render_today_steps()

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    # 3. 今目指しているCompassカード一覧
    _render_compass_cards()

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # 最近の気づき（Reflect の入力があれば反映）
    notice = DASHBOARD["recent_notice"]
    if ss.get("reflect_saved") and ss.reflect_inputs.get("notice"):
        notice = ss.reflect_inputs["notice"]
    text_card("💡 最近の気づき", notice, tone="sub")

    # AIからの小さな提案（静かな存在として最後に）
    ai = DASHBOARD["ai_suggestion"]
    ai_message(ai["kind"], ai["text"])
