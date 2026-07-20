"""AIの見せ方: フルスクリーンチャットにせず、小さな提案カードとして静かに表示する。"""
import streamlit as st


def ai_message(kind: str, text: str):
    """AIからの提案・問い・整理結果を、小さなカードとして表示する。

    kind: 「AIからの提案」「AIからの問い」「AIによる穏やかな要約」など。
    """
    st.markdown(
        f"""
        <div class="mlc-ai">
          <div class="mlc-ai-icon">🧭</div>
          <div>
            <div class="mlc-ai-kind">{kind}</div>
            <div class="mlc-ai-text">{text}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
