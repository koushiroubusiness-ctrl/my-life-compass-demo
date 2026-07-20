"""カード系の共通UI。角丸の大きなカード・薄い境界線・弱い影で統一する。"""
import streamlit as st


def card(label: str = "", body_html: str = "", tone: str = "", title: str = ""):
    """汎用カード。tone は '' / 'main' / 'sub' / 'accent'。"""
    tone_cls = f" tone-{tone}" if tone else ""
    inner = ""
    if label:
        inner += f'<div class="mlc-card-label">{label}</div>'
    if title:
        inner += f'<div class="mlc-card-title">{title}</div>'
    if body_html:
        inner += f'<div class="mlc-card-body">{body_html}</div>'
    st.markdown(f'<div class="mlc-card{tone_cls}">{inner}</div>', unsafe_allow_html=True)


def list_card(label: str, items: list[str], tone: str = ""):
    """箇条書きを持つカード。"""
    lis = "".join(f"<li>{it}</li>" for it in items)
    card(label=label, body_html=f"<ul>{lis}</ul>", tone=tone)


def text_card(label: str, text: str, tone: str = "", note: str = ""):
    """本文テキストのカード。note があれば薄い補足を添える。"""
    body = text
    if note:
        body += f'<div class="mlc-soft-note" style="margin-top:10px">{note}</div>'
    card(label=label, body_html=body, tone=tone)


def hero(label: str, text: str, sub: str = ""):
    """大きめのヒーローカード（今日の一歩など、1画面の主役）。"""
    sub_html = f'<div class="mlc-hero-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="mlc-hero">
          <div class="mlc-hero-label">{label}</div>
          <div class="mlc-hero-text">{text}</div>
          {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_row(name: str, where: str, tone: str = "main"):
    """現在地の1行（Dashboard 用）。tone: main / sub / acc。"""
    st.markdown(
        f"""
        <div class="mlc-status">
          <div class="dot {tone}"></div>
          <div class="name">{name}</div>
          <div class="where">{where}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chips(items: list[str], tone: str = ""):
    """チップ（お金・スキルなどの補助情報）。"""
    cls = f" {tone}" if tone else ""
    html = "".join(f'<span class="mlc-chip{cls}">{it}</span>' for it in items)
    st.markdown(html, unsafe_allow_html=True)


def timeline(items: list[dict]):
    """柔らかい縦タイムライン（Route 用）。

    items: [{"cls": "" | "sub" | "near", "when": str, "what": str, "meta": str}]
    """
    rows = ""
    for it in items:
        cls = it.get("cls", "")
        rows += f"""
        <div class="mlc-tl-item {cls}">
          <div class="mlc-tl-when">{it['when']}</div>
          <div class="mlc-tl-what">{it['what']}</div>
          <div class="mlc-tl-meta">{it.get('meta', '')}</div>
        </div>
        """
    st.markdown(f'<div class="mlc-timeline">{rows}</div>', unsafe_allow_html=True)
