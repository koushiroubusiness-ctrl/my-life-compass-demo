"""Vision — 理想の人生を描く。仕事だけでなく暮らし全体を。"""
import streamlit as st

from components.layout import page_header, section_label
from components.cards import text_card
from components.ai_message import ai_message
from data.mock_data import VISION, USER


def render():
    page_header(
        "Vision",
        "理想の人生を描く。目的地がはっきりすると、道筋も見えてきます。",
        USER["initial"],
    )

    section_label("理想の人生を描く", VISION["intro"])

    # 2列 × 3行で理想のカードを表示
    cards = VISION["cards"]
    for i in range(0, len(cards), 2):
        cols = st.columns(2)
        for col, c in zip(cols, cards[i:i + 2]):
            with col:
                text_card(c["label"], c["text"], tone=c["tone"])

    ai = VISION["ai_suggestion"]
    ai_message(ai["kind"], ai["text"])
