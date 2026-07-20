"""Compassカード。目指したい未来を1枚のカードとして表示する。

一覧はシンプルに（タイトル・説明・タグ・期間だけ）。詳しい理由や編集・保留は
右上の「⋯」メニューにまとめ、一覧性を高く保つ。
既存の .mlc-card デザイン（大きめ角丸・薄い境界線・弱い影）を踏襲する。
"""
import streamlit as st


def _tags_html(tags):
    return "".join(f'<span class="mlc-chip">{t}</span>' for t in tags)


def render_compass_card(card: dict, key: str) -> str:
    """Compassカードを描画し、押されたボタンの action 文字列を返す。

    返り値: "route" / "edit" / "hold" / "" （何も押されなければ ""）
    一覧ではタイトル・説明・タグ・期間のみ。理由などの詳細は「⋯」内に。
    """
    tone = card.get("tone", "main")
    period = card.get("period") or "まだ決めていない"

    st.markdown(
        f"""
        <div class="mlc-card tone-{tone} mlc-compass-card">
          <div class="mlc-cc-title">{card["title"]}</div>
          <div class="mlc-cc-desc">{card["desc"]}</div>
          <div class="mlc-cc-tags">{_tags_html(card.get("tags", []))}</div>
          <div class="mlc-cc-period">目安の期間 ・ {period}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    action = ""
    route_label = "道筋を見る" if card.get("route_done") else "道筋をつくる"

    col_main, col_menu = st.columns([5, 1])
    with col_main:
        if st.button(route_label, key=f"{key}_route", type="primary",
                     use_container_width=True):
            action = "route"
    with col_menu:
        with st.popover("⋯", use_container_width=True):
            if card.get("reason"):
                st.markdown(
                    f'<div class="mlc-pop-label">実現したい理由</div>'
                    f'<div class="mlc-pop-text">{card["reason"]}</div>',
                    unsafe_allow_html=True,
                )
            if st.button("編集する", key=f"{key}_edit", use_container_width=True):
                action = "edit"
            if st.button("今回は保留する", key=f"{key}_hold", use_container_width=True):
                action = "hold"
            if st.button("削除する", key=f"{key}_delete", use_container_width=True):
                action = "delete"

    return action


def render_summary_card(card: dict, key: str) -> bool:
    """Dashboard 用のCompass要約カード（カード全体がクリックできるボタン）。

    タイトル・短い説明・目安の期間・価値観タグ・Routeの状態を、情報量を抑えて
    一覧性優先で表示する。押されたら True を返す（呼び出し側でCompass編集へ）。
    """
    tone = card.get("tone", "main")
    period = card.get("period") or "まだ決めていない"
    tags = " / ".join(card.get("tags", [])) or "—"
    route_state = "Route作成済み" if card.get("route_done") else "Route未作成"

    st.markdown(f'<div class="mlc-summary-marker {tone}"></div>', unsafe_allow_html=True)
    label = (
        f'{card["title"]}\n\n'
        f'{card["desc"]}\n\n'
        f'目安の期間 ・ {period}\n\n'
        f'{tags}\n\n'
        f'{route_state}'
    )
    return st.button(label, key=key, use_container_width=True)


def render_candidate_card(cand: dict):
    """壁打ち中に左側へ表示する「今の話から見えてきたCompass候補」。"""
    period = cand.get("period") or "まだ決めていない"
    reason = cand.get("reason") or "（これから一緒に言葉にしていきましょう）"
    st.markdown(
        f"""
        <div class="mlc-card tone-{cand.get('tone', 'main')} mlc-candidate">
          <div class="mlc-cc-label">今の話から見えてきたCompass候補</div>
          <div class="mlc-cc-title">{cand["title"]}</div>
          <div class="mlc-cc-desc">{cand["desc"]}</div>
          <div class="mlc-cc-row"><span class="k">実現したい理由</span>
            <span class="v">{reason}</span></div>
          <div class="mlc-cc-row"><span class="k">目安の期間</span>
            <span class="v">{period}</span></div>
          <div class="mlc-cc-tags">{_tags_html(cand.get("tags", []))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
