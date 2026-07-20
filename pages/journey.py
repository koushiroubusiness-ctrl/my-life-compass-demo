"""Journey — 今日の一歩。Routeで選んだ最初の一歩を、責めずに扱う。

Todo管理にしない。期限超過・未達・遅延などの表現は使わない。今日の一歩は最大3件。
"""
import streamlit as st

from components.layout import page_header, section_label
from components.ai_message import ai_message
from data.mock_data import JOURNEY_HEADER, STEP_STATUS_LABELS, USER

_STATUS_TONE = {"none": "", "done": "done", "partial": "partial", "skip": "skip"}


def _render_step(i, step):
    ss = st.session_state
    status = step.get("status", "none")
    from_txt = step.get("from", "")
    from_html = f'<span class="mlc-js-from">{from_txt}</span>' if from_txt else ""
    badge = STEP_STATUS_LABELS.get(status, "")
    badge_html = (f'<span class="mlc-js-badge {_STATUS_TONE[status]}">{badge}</span>'
                  if status != "none" else "")

    st.markdown(
        f"""
        <div class="mlc-js-step {_STATUS_TONE[status]}">
          <div class="mlc-js-text">{step["text"]}</div>
          <div class="mlc-js-meta">{from_html}{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 状態変更ボタン
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("できた", key=f"js_done_{i}", use_container_width=True):
            step["status"] = "done"; st.rerun()
    with c2:
        if st.button("少しできた", key=f"js_part_{i}", use_container_width=True):
            step["status"] = "partial"; st.rerun()
    with c3:
        if st.button("今日は見送る", key=f"js_skip_{i}", use_container_width=True):
            step["status"] = "skip"; st.rerun()
    with c4:
        if st.button("別の一歩に変える", key=f"js_edit_{i}", use_container_width=True):
            ss.setdefault("journey_editing", None)
            ss.journey_editing = i if ss.get("journey_editing") != i else None
            st.rerun()

    if ss.get("journey_editing") == i:
        new_text = st.text_input("新しい一歩", value=step["text"], key=f"js_newtext_{i}")
        if st.button("この一歩にする", key=f"js_save_{i}", type="primary"):
            step["text"] = new_text
            step["status"] = "none"
            ss.journey_editing = None
            st.rerun()


def render():
    ss = st.session_state

    page_header(
        "Journey",
        "今日の一歩へつなげる。増やしすぎず、続けられる量だけ。",
        USER["initial"],
    )

    st.markdown(f'<div class="mlc-page-lead">{JOURNEY_HEADER["title"]}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="mlc-soft-note">{JOURNEY_HEADER["intro"]}</div>',
                unsafe_allow_html=True)

    for i, step in enumerate(ss.journey_today[:3]):
        _render_step(i, step)
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    week = ss.get("journey_week", [])
    if week:
        section_label("今週の一歩")
        for it in week:
            st.markdown(
                f'<div class="mlc-step"><div class="mark"></div><div class="txt">{it}</div></div>',
                unsafe_allow_html=True,
            )

    ai_message("AIからの小さな提案",
               "やれない日があっても大丈夫です。戻ってきたら、また一歩から始めましょう。")
