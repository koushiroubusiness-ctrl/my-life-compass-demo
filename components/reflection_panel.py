"""Reflect の入力パネル。責めずに、穏やかに今日を振り返る。

達成率・未達・遅延などの表現は使わない。
"""
import streamlit as st

from services.mock_ai_service import build_reflection_summary


def render_reflection_panel():
    """振り返りの入力欄と、疑似AIによる穏やかなまとめを表示する。"""
    ss = st.session_state
    inp = ss.reflect_inputs

    col1, col2 = st.columns(2)
    with col1:
        did = st.text_area("今日できたこと", value=inp.get("did", ""),
                           key="reflect_did", height=90,
                           placeholder="小さなことでも大丈夫です")
        notice = st.text_area("気づいたこと", value=inp.get("notice", ""),
                              key="reflect_notice", height=90,
                              placeholder="ふと思ったことでかまいません")
    with col2:
        feeling = st.text_area("今の気持ち", value=inp.get("feeling", ""),
                               key="reflect_feeling", height=90,
                               placeholder="今の気分をひとことで")
        next_try = st.text_area("次に試したいこと", value=inp.get("next_try", ""),
                                key="reflect_next", height=90,
                                placeholder="無理のない範囲で")

    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        if st.button("この振り返りをまとめる", type="primary", use_container_width=True):
            ss.reflect_inputs = {"did": did, "notice": notice,
                                 "feeling": feeling, "next_try": next_try}
            ss.reflect_saved = True
            st.rerun()
    with c2:
        if st.button("入力をリセット", use_container_width=True):
            ss.reflect_inputs = {"did": "", "feeling": "", "notice": "", "next_try": ""}
            ss.reflect_saved = False
            st.rerun()

    if ss.reflect_saved:
        summary = build_reflection_summary(
            inp.get("did", ""), inp.get("feeling", ""),
            inp.get("notice", ""), inp.get("next_try", ""),
        )
        st.markdown(
            f"""
            <div class="mlc-ai">
              <div class="mlc-ai-icon">🧭</div>
              <div>
                <div class="mlc-ai-kind">AIによる穏やかな要約</div>
                <div class="mlc-ai-text">{summary}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
