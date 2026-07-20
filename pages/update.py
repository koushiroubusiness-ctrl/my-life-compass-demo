"""Update — 現在の自分に合わせて人生設計を見直す。最後はユーザーが確認する。"""
import streamlit as st

from components.layout import page_header, section_label
from components.cards import text_card, card
from components.ai_message import ai_message
from data.mock_data import UPDATE, USER


def render():
    page_header(
        "Update",
        "人生を更新する。計画から外れても大丈夫。今の自分に合う道へ整え直します。",
        USER["initial"],
    )

    section_label("今の自分に合わせて見直す", UPDATE["intro"])

    # 変化（仕事・お金・健康・家族・価値観）
    changes = UPDATE["changes"]
    for i in range(0, len(changes), 2):
        cols = st.columns(2)
        for col, c in zip(cols, changes[i:i + 2]):
            with col:
                text_card(c["label"], c["text"], tone=c["tone"])

    # AIが整理した影響範囲
    im = UPDATE["impact"]
    ai_message(im["kind"], im["text"])

    # 更新候補（AIは確定しない）
    section_label("更新候補", UPDATE["confirm_note"])
    lis = "".join(f"<li>{it}</li>" for it in UPDATE["candidates"])
    card(label="🔄 AIが用意した更新候補",
         body_html=f"<ul>{lis}</ul>", tone="accent")

    # 最後はユーザーが確認して反映する（モックのため動作はしない）
    col_a, col_b, _ = st.columns([1, 1, 2])
    with col_a:
        st.button("内容を確認する")
    with col_b:
        st.button("あとで見直す")
