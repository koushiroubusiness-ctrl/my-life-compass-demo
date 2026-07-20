"""Reflect — 自分を責めずに振り返る。比べる相手は他人ではなく過去の自分。"""
import streamlit as st

from components.layout import page_header, section_label
from components.reflection_panel import render_reflection_panel
from data.mock_data import REFLECT_HEADER, USER


def render():
    page_header(
        "Reflect",
        "振り返る。達成率よりも、少し前へ進めた自分を実感する場所です。",
        USER["initial"],
    )

    st.markdown(f'<div class="mlc-page-lead">{REFLECT_HEADER["title"]}</div>',
                unsafe_allow_html=True)
    section_label("今日を、責めずに振り返る", REFLECT_HEADER["intro"])

    render_reflection_panel()
