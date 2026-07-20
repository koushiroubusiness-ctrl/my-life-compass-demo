"""Compass — 目指したい未来を最大3つ整理する。

壁打ちボタンで右側にチャットパネルが開き、回答に応じて
左側の「Compass候補」がリアルタイムに変わる。候補は最大3枚まで
Compassカードとして一覧へ追加できる。
"""
import streamlit as st

from components.layout import page_header, section_label
from components.chat_panel import render_chat_panel
from components.compass_card import render_compass_card, render_candidate_card
from services import mock_ai_service as ai
from services.state import go_to
from data.mock_data import COMPASS_HEADER, COMPASS_QUESTIONS, USER

MAX_COMPASS = 3
_TONES = ["main", "sub", "accent"]


# ---------------------------------------------------------
# 状態操作
# ---------------------------------------------------------
def _open_chat():
    ss = st.session_state
    ss.compass_chat_open = True
    ss.compass_q_index = 0
    ss.compass_answers = {}
    ss.compass_cand_override = {}


def _close_chat():
    st.session_state.compass_chat_open = False


def _set_index(v):
    st.session_state.compass_q_index = v


def _set_answer(akey, value):
    st.session_state.compass_answers[akey] = value


def _total_compass():
    ss = st.session_state
    return len(ss.compass_cards) + len(ss.get("compass_held", []))


def _delete_compass(cid):
    """Compassを完全に削除する（保留とは別の操作）。関連Routeなども片付ける。"""
    ss = st.session_state
    ss.compass_cards = [c for c in ss.compass_cards if c["id"] != cid]
    ss.routes.pop(cid, None)
    ss.route_answers.pop(cid, None)
    ss.route_open_axes.pop(cid, None)
    ss.route_hidden_axes.pop(cid, None)
    if ss.get("selected_compass_id") == cid:
        ss.selected_compass_id = ss.compass_cards[0]["id"] if ss.compass_cards else None
    if ss.get("compass_editing") == cid:
        ss.compass_editing = None
    ss.compass_confirm_delete = None


def _add_candidate(cand):
    ss = st.session_state
    if _total_compass() >= MAX_COMPASS:
        return
    new_id = f"c{ss.compass_next_id}"
    ss.compass_next_id += 1
    tone = _TONES[len(ss.compass_cards) % len(_TONES)]
    ss.compass_cards.append({
        "id": new_id,
        "title": cand["title"],
        "desc": cand["desc"],
        "reason": cand.get("reason", ""),
        "period": cand.get("period") or "まだ決めていない",
        "tags": list(cand.get("tags", [])),
        "tone": tone,
        "route_done": False,
    })
    _close_chat()
    ss.compass_answers = {}
    ss.compass_q_index = 0
    ss.compass_cand_override = {}


# ---------------------------------------------------------
# 左側：候補 + アクション
# ---------------------------------------------------------
def _render_candidate_area():
    ss = st.session_state
    answers = ss.compass_answers

    if not ai.has_enough_for_candidate(answers):
        st.markdown(
            '<div class="mlc-soft-note">右側の質問にいくつか答えると、'
            'ここに「今の話から見えてきたCompass候補」が表示されます。</div>',
            unsafe_allow_html=True,
        )
        return

    cand = ai.build_compass_candidate(answers)
    override = ss.get("compass_cand_override", {})
    cand.update({k: v for k, v in override.items() if v})

    render_candidate_card(cand)

    # 修正フォーム
    if ss.get("compass_cand_editing"):
        with st.form("cand_edit_form"):
            t = st.text_input("タイトル", value=cand["title"])
            d = st.text_area("目指したい状態の説明", value=cand["desc"], height=70)
            r = st.text_input("実現したい理由", value=cand.get("reason", ""))
            tags = st.text_input("価値観タグ（/ 区切り）", value=" / ".join(cand.get("tags", [])))
            if st.form_submit_button("この内容で更新", type="primary"):
                ss.compass_cand_override = {
                    "title": t, "desc": d, "reason": r,
                    "tags": [x.strip() for x in tags.split("/") if x.strip()],
                }
                ss.compass_cand_editing = False
                st.rerun()
        return

    can_add = _total_compass() < MAX_COMPASS
    b1, b2 = st.columns(2)
    with b1:
        if st.button("この内容に近い", use_container_width=True):
            st.toast("いいですね。もう少し話すと、さらに具体的になります。")
    with b2:
        if st.button("少し修正する", use_container_width=True):
            ss.compass_cand_editing = True
            st.rerun()

    b3, b4 = st.columns(2)
    with b3:
        if st.button("もう少し話す", use_container_width=True):
            st.toast("右側の質問を続けましょう。")
    with b4:
        if st.button("Compassに追加する", type="primary",
                     disabled=not can_add, use_container_width=True):
            _add_candidate(cand)
            st.rerun()

    if not can_add:
        st.markdown(f'<div class="mlc-soft-note">{COMPASS_HEADER["max_note"]}</div>',
                    unsafe_allow_html=True)


# ---------------------------------------------------------
# 左側：Compassカード一覧
# ---------------------------------------------------------
def _render_held_area():
    """保留中のCompassを再表示できるようにする（完全削除ではない）。"""
    ss = st.session_state
    held = ss.get("compass_held", [])
    if not held:
        return
    with st.popover(f"保留中（{len(held)}件）", use_container_width=False):
        st.markdown('<div class="mlc-pop-label">保留中のCompass</div>',
                    unsafe_allow_html=True)
        for c in held:
            st.markdown(f'<div class="mlc-pop-text">{c["title"]}</div>',
                        unsafe_allow_html=True)
            if st.button("再表示する", key=f"restore_{c['id']}", use_container_width=True):
                ss.compass_held = [x for x in held if x["id"] != c["id"]]
                ss.compass_cards.append(c)
                st.rerun()


def _render_card_list(compact=False):
    ss = st.session_state
    cards = ss.compass_cards

    section_label(COMPASS_HEADER["list_label"])
    _render_held_area()

    if not cards:
        st.markdown(f'<div class="mlc-soft-note">{COMPASS_HEADER["empty_note"]}</div>',
                    unsafe_allow_html=True)
        return

    n = 1 if compact else min(len(cards), 3)
    cols = st.columns(n)
    for i, card in enumerate(cards):
        with cols[i % n]:
            if ss.get("compass_confirm_delete") == card["id"]:
                _render_delete_confirm(card)
            elif ss.get("compass_editing") == card["id"]:
                _render_card_editor(card)
            else:
                action = render_compass_card(card, key=f"cc_{card['id']}")
                if action == "route":
                    ss.selected_compass_id = card["id"]
                    go_to("Route")
                    st.rerun()
                elif action == "edit":
                    ss.compass_editing = card["id"]
                    st.rerun()
                elif action == "hold":
                    ss.compass_held = ss.get("compass_held", []) + [card]
                    ss.compass_cards = [c for c in cards if c["id"] != card["id"]]
                    st.rerun()
                elif action == "delete":
                    ss.compass_confirm_delete = card["id"]
                    st.rerun()


def _render_delete_confirm(card):
    """完全削除の確認（保留とは別の操作であることを穏やかに伝える）。"""
    ss = st.session_state
    st.markdown(
        f'<div class="mlc-card tone-{card.get("tone", "main")}">'
        f'<div class="mlc-danger-note">このCompassを削除しますか？</div>'
        f'<div class="mlc-cc-title">{card["title"]}</div>'
        f'<div class="mlc-soft-note">完全に削除されます。'
        f'あとで見返したいときは「保留」を選んでください。</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("キャンセル", key=f"del_cancel_{card['id']}",
                     use_container_width=True):
            ss.compass_confirm_delete = None
            st.rerun()
    with c2:
        if st.button("削除する", key=f"del_ok_{card['id']}",
                     type="primary", use_container_width=True):
            _delete_compass(card["id"])
            st.rerun()


def _render_card_editor(card):
    ss = st.session_state
    with st.form(f"edit_{card['id']}"):
        st.markdown('<div class="mlc-cc-label">Compassを編集する</div>', unsafe_allow_html=True)
        t = st.text_input("タイトル", value=card["title"])
        d = st.text_area("説明", value=card["desc"], height=70)
        r = st.text_input("実現したい理由", value=card.get("reason", ""))
        p = st.text_input("目安の期間", value=card.get("period", ""))
        tags = st.text_input("価値観タグ（/ 区切り）", value=" / ".join(card.get("tags", [])))
        c1, c2 = st.columns(2)
        with c1:
            if st.form_submit_button("この内容で保存する", type="primary"):
                card.update({
                    "title": t, "desc": d, "reason": r, "period": p,
                    "tags": [x.strip() for x in tags.split("/") if x.strip()],
                })
                ss.compass_editing = None
                st.rerun()
        with c2:
            if st.form_submit_button("やめる"):
                ss.compass_editing = None
                st.rerun()

    # フォーム外の操作：Routeを見る / 保留する / 削除する
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("Routeを見る", key=f"edit_route_{card['id']}",
                     use_container_width=True):
            ss.selected_compass_id = card["id"]
            ss.compass_editing = None
            go_to("Route")
            st.rerun()
    with a2:
        if st.button("保留する", key=f"edit_hold_{card['id']}",
                     use_container_width=True):
            ss.compass_held = ss.get("compass_held", []) + [card]
            ss.compass_cards = [c for c in ss.compass_cards if c["id"] != card["id"]]
            ss.compass_editing = None
            st.rerun()
    with a3:
        if st.button("削除する", key=f"edit_delete_{card['id']}",
                     use_container_width=True):
            ss.compass_confirm_delete = card["id"]
            ss.compass_editing = None
            st.rerun()


# ---------------------------------------------------------
# エントリ
# ---------------------------------------------------------
def render():
    ss = st.session_state
    ss.setdefault("compass_cand_override", {})
    ss.setdefault("compass_cand_editing", False)
    ss.setdefault("compass_editing", None)
    ss.setdefault("compass_confirm_delete", None)
    ss.setdefault("compass_held", [])

    page_header(
        "Compass",
        "人生の目的地を整理する場所です。答えを決めるのではなく、今の気持ちに近い未来を言葉にします。",
        USER["initial"],
    )

    st.markdown(f'<div class="mlc-page-lead">{COMPASS_HEADER["title"]}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="mlc-soft-note">{COMPASS_HEADER["desc"]}</div>',
                unsafe_allow_html=True)

    if ss.compass_chat_open:
        # メインは全幅（CSSでパネル分だけ右に余白）。チャットは右側の固定パネルへ。
        section_label("今、整理しているCompass候補")
        _render_candidate_area()
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        _render_card_list(compact=True)

        chat_holder = st.columns(1)[0]
        with chat_holder:
            akeys = list(range(len(COMPASS_QUESTIONS)))
            render_chat_panel(
                title="一緒に目指したい未来を整理する",
                subtitle="いくつかの問いに答えると、左側にCompass候補が形になっていきます。",
                questions=COMPASS_QUESTIONS,
                q_index=ss.compass_q_index,
                answers=ss.compass_answers,
                akeys=akeys,
                key_prefix="compass",
                set_index=_set_index,
                set_answer=_set_answer,
                close=_close_chat,
            )
    else:
        can_add = _total_compass() < MAX_COMPASS
        if st.button("＋ 一緒に目指したい未来を整理する", type="primary",
                     disabled=not can_add):
            _open_chat()
            st.rerun()
        if not can_add:
            st.markdown(f'<div class="mlc-soft-note">{COMPASS_HEADER["max_note"]}</div>',
                        unsafe_allow_html=True)
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        _render_card_list(compact=False)
