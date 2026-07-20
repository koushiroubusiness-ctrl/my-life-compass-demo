"""Settings — 信頼と管理。プロフィール・AIの理解・AI Memory・連携・プライバシー。"""
import streamlit as st

from components.layout import page_header, section_label
from components.cards import card, list_card, text_card
from data.mock_data import SETTINGS, USER


def render():
    page_header(
        "Settings",
        "信頼と管理。あなたの情報と、AIが理解している内容をいつでも確認できます。",
        USER["initial"],
    )

    # プロフィール
    p = SETTINGS["profile"]
    section_label("プロフィール")
    text_card(
        "👤 プロフィール",
        f'<b>{p["name"]}</b>　<span style="color:#6b7078">（{p["state"]} / {p["since"]}）</span>',
        tone="main",
        note=p["note"],
    )

    # AIが理解しているあなた / AI Memory
    col1, col2 = st.columns(2)
    with col1:
        list_card("🧭 AIが理解しているあなた", SETTINGS["ai_understanding"], tone="sub")
    with col2:
        mem_items = [f'{m["item"]}　<span style="color:#9aa0a8">（{m["when"]}）</span>'
                     for m in SETTINGS["ai_memory"]]
        list_card("🤖 AI Memory（覚えていること）", mem_items, tone="main")

    # データ連携
    section_label("データ連携", "モックのため、いずれも未接続です。")
    cols = st.columns(3)
    for col, ig in zip(cols, SETTINGS["integrations"]):
        with col:
            card(
                label=f'🔗 {ig["name"]}',
                body_html=f'<span class="mlc-chip">{ig["status"]}</span>',
            )

    # プライバシー
    list_card("🔒 プライバシー", SETTINGS["privacy"], tone="sub")

    # データの修正・削除（モックのため動作はしない）
    section_label("データの修正・削除", "AIが覚えている内容は、いつでも確認・修正・削除できます。")
    col_a, col_b, _ = st.columns([1, 1, 2])
    with col_a:
        st.button("覚えている内容を修正する")
    with col_b:
        st.button("データを削除する")
