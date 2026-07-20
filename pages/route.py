"""Route — 選んだCompassを実現する道筋をつくる。

Compassごとに独立したRouteを持つ。壁打ちで期間・現在地・壁などを答えると、
期間に応じて時間軸（今日〜数年後）が変わり、縦タイムラインで表示される。
"""
import streamlit as st

from components.layout import page_header, section_label
from components.chat_panel import render_chat_panel
from components.route_card import render_route_timeline, render_route_draft
from services import mock_ai_service as ai
from services.state import get_compass_by_id, go_to
from data.mock_data import ROUTE_HEADER, ROUTE_QUESTIONS, USER

_AKEYS = [q["key"] for q in ROUTE_QUESTIONS]
_QMAP = {q["key"]: q for q in ROUTE_QUESTIONS}
_PERIODS = ["3か月", "1年", "3年", "5年"]


# ---------------------------------------------------------
# 状態操作
# ---------------------------------------------------------
def _rebuild_route(cid, compass):
    answers = st.session_state.route_answers.setdefault(cid, {})
    st.session_state.routes[cid] = ai.build_route(compass, answers)
    compass["route_done"] = True


def _open_chat(cid, compass):
    ss = st.session_state
    ss.route_chat_open = True
    ss.route_q_index = 0
    if cid not in ss.routes:
        _rebuild_route(cid, compass)


def _close_chat():
    st.session_state.route_chat_open = False


def _add_today(text):
    ss = st.session_state
    ss.journey_today = ss.journey_today[:2]  # 最大3件を保つため先頭を活かす
    ss.journey_today.insert(0, {"text": text, "status": "none",
                                "from": _current_compass_title()})
    ss.journey_today = ss.journey_today[:3]


def _add_week(text):
    ss = st.session_state
    ss.setdefault("journey_week", [])
    if text not in ss.journey_week:
        ss.journey_week.insert(0, text)
    ss.journey_week = ss.journey_week[:3]


def _current_compass_title():
    c = get_compass_by_id(st.session_state.selected_compass_id)
    return c["title"] if c else ""


# ---------------------------------------------------------
# Compass 選択（プルダウンではなくカードで選ぶ）
# ---------------------------------------------------------
def _render_compass_selector(cid):
    ss = st.session_state
    cards = ss.compass_cards
    if len(cards) <= 1:
        return
    section_label("道筋をつくるCompassを選ぶ", "カードを選ぶと、その道筋に切り替わります。")
    cols = st.columns(len(cards))
    for col, c in zip(cols, cards):
        with col:
            st.markdown('<div class="mlc-pick-marker"></div>', unsafe_allow_html=True)
            selected = (c["id"] == cid)
            label = ("✓ " if selected else "") + c["title"]
            if st.button(label, key=f"pick_{c['id']}",
                         type="primary" if selected else "secondary",
                         use_container_width=True):
                ss.selected_compass_id = c["id"]
                st.rerun()
            st.markdown(
                f'<div class="mlc-pick-tags">{" / ".join(c.get("tags", []))}</div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------
# はじめの設定フォーム（対話の前に、直接入力でも作れる）
# ---------------------------------------------------------
def _render_setup_form(cid, compass):
    ss = st.session_state
    section_label("はじめに、道筋の材料を整理しましょう",
                  "わかる範囲で大丈夫です。あとからいつでも変えられます。")

    default_period = ai.resolve_period_key(compass.get("period"))
    p_idx = _PERIODS.index(default_period) if default_period in _PERIODS else 2

    with st.form(f"route_setup_{cid}"):
        period = st.radio("① いつまでに近づきたいですか？", _PERIODS,
                          index=p_idx, horizontal=True)
        current = st.selectbox("② 今、どのくらい近づけていますか？",
                               _QMAP["current"]["choices"])
        step = st.selectbox("③ 使えそうな時間は、どのくらいですか？",
                            _QMAP["step_size"]["choices"])
        resources = st.multiselect("④ 今、使えそうなもの（スキル・経験など）は？",
                                   _QMAP["resources"]["choices"])
        wall = st.selectbox("⑤ 今、一番大きな壁は何ですか？",
                            _QMAP["wall"]["choices"])
        submitted = st.form_submit_button("Routeを作る", type="primary")

    if submitted:
        ss.route_answers[cid] = {
            "period": period, "current": current, "step_size": step,
            "resources": resources, "wall": wall,
        }
        _rebuild_route(cid, compass)
        ss.route_open_axes[cid] = set()
        ss.route_hidden_axes[cid] = set()
        st.rerun()


# ---------------------------------------------------------
# エントリ
# ---------------------------------------------------------
def render():
    ss = st.session_state

    page_header(
        "Route",
        "Compassへ向かう道筋をつくる場所です。遠い未来から今日へ、無理のない順番に。",
        USER["initial"],
    )

    # 対象Compassの決定（未選択なら先頭を既定に）
    cid = ss.selected_compass_id
    if cid is None and ss.compass_cards:
        cid = ss.compass_cards[0]["id"]
        ss.selected_compass_id = cid

    compass = get_compass_by_id(cid) if cid else None

    if compass is None:
        st.markdown(
            '<div class="mlc-soft-note">まだCompassがありません。'
            'まず Compass で「目指したい未来」を1つ整理してみましょう。</div>',
            unsafe_allow_html=True,
        )
        if st.button("Compassへ移動する", type="primary"):
            go_to("Compass")
            st.rerun()
        return

    # 選んだCompassの切り替え（プルダウンではなくカードで）
    _render_compass_selector(cid)

    # 選んだCompassの概要
    st.markdown(
        f"""
        <div class="mlc-card tone-{compass.get('tone', 'main')} mlc-chosen">
          <div class="mlc-cc-label">{ROUTE_HEADER["chosen_label"]}</div>
          <div class="mlc-cc-title">{compass["title"]}</div>
          <div class="mlc-cc-desc">{compass["desc"]}</div>
          <div class="mlc-cc-row"><span class="k">目安の期間</span>
            <span class="v">{compass.get("period", "—")}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- 対話パネルが開いている場合：メイン全幅 + 右側固定パネル ---
    if ss.route_chat_open:
        answers = ss.route_answers.setdefault(cid, {})
        draft = ai.build_route(compass, answers)
        section_label("整理中のRoute案")
        render_route_draft(draft, compass, ai.route_progress_text(answers))

        chat_holder = st.columns(1)[0]
        with chat_holder:
            def set_index(v):
                ss.route_q_index = v

            def set_answer(akey, value):
                ss.route_answers.setdefault(cid, {})[akey] = value
                _rebuild_route(cid, compass)

            render_chat_panel(
                title="道筋を一緒につくる",
                subtitle="期間と現在地をうかがいながら、今日の一歩まで一緒に整えます。",
                questions=ROUTE_QUESTIONS,
                q_index=ss.route_q_index,
                answers=ss.route_answers.setdefault(cid, {}),
                akeys=_AKEYS,
                key_prefix=f"route_{cid}",
                set_index=set_index,
                set_answer=set_answer,
                close=_close_chat,
            )
        return

    route = ss.routes.get(cid)

    # --- まだ道筋がない：まず材料を入力して作る ---
    if not route:
        _render_setup_form(cid, compass)
        st.markdown('<div class="mlc-soft-note" style="margin-top:18px">'
                    'じっくり相談しながら決めたいときは、対話でもつくれます。</div>',
                    unsafe_allow_html=True)
        if st.button("＋ 道筋を一緒につくる（対話でつくる）", type="primary"):
            _open_chat(cid, compass)
            st.rerun()
        return

    # --- 道筋がある：タイムライン表示 ---
    c1, c2 = st.columns([2, 1])
    with c1:
        cur = route.get("period", "3年")
        idx = _PERIODS.index(cur) if cur in _PERIODS else 2
        new_period = st.selectbox("期間を変える", _PERIODS, index=idx, key=f"route_period_{cid}")
    with c2:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        if st.button("この期間で作り直す", key=f"route_regen_{cid}", use_container_width=True):
            ss.route_answers.setdefault(cid, {})["period"] = new_period
            _rebuild_route(cid, compass)
            ss.route_open_axes[cid] = set()
            ss.route_hidden_axes[cid] = set()
            st.rerun()

    if st.button("対話で見直す", key=f"route_open_chat_{cid}"):
        _open_chat(cid, compass)
        st.rerun()

    section_label("康士朗さんのRoute",
                  "各期間を開くと、必要な行動やお金・スキル、今日の一歩への反映ができます。")
    render_route_timeline(route, cid, add_today=_add_today, add_week=_add_week)
