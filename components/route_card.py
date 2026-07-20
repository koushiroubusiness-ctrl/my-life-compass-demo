"""Routeの縦タイムライン。各期間をアコーディオンで開閉する。

初期表示は「期間名・中心となる状態・主要な達成1〜2件」だけ。
詳細を開くと、達成状態・必要な行動/お金/スキル/経験・想定される壁・
AIからの小さな提案・各種操作を表示する。
情報を常時全部見せず、静かなUIを保つ。
"""
import streamlit as st


# 近い未来ほど accent、遠いほど main（既存タイムライン配色に合わせる）
_NEAR = {"今日", "今週", "今月", "1か月後"}
_SUB = {"3か月後", "6か月後"}


def _axis_cls(when: str) -> str:
    if when in _NEAR:
        return "near"
    if when in _SUB:
        return "sub"
    return ""


def render_route_timeline(route: dict, compass_id: str, *, add_today, add_week):
    """Route案の時系列を描画する。

    add_today(text) / add_week(text): 今日 / 今週の一歩へ反映するコールバック。
    """
    ss = st.session_state
    hidden = ss.route_hidden_axes.setdefault(compass_id, set())
    open_axes = ss.route_open_axes.setdefault(compass_id, set())

    axes = [a for a in route["axes"] if a["when"] not in hidden]

    st.markdown('<div class="mlc-route-tl">', unsafe_allow_html=True)

    for a in axes:
        when = a["when"]
        cls = _axis_cls(when)
        ach = a.get("ach", [])
        ach_html = ""
        if ach:
            lis = "".join(f"<li>{x}</li>" for x in ach[:2])
            ach_html = f'<ul class="mlc-rt-ach">{lis}</ul>'

        st.markdown(
            f"""
            <div class="mlc-rt-item {cls}">
              <div class="mlc-rt-when">{when}</div>
              <div class="mlc-rt-state">{a["state"]}</div>
              {ach_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("この期間の詳細を見る"):
            d = a.get("detail", {})
            rows = [
                ("必要な行動", "、".join(ach) if ach else "—"),
                ("必要なお金", d.get("money", "—")),
                ("必要なスキル", d.get("skill", "—")),
                ("必要な経験", d.get("exp", "—")),
                ("想定される壁", d.get("wall", "—")),
            ]
            for k, v in rows:
                st.markdown(
                    f'<div class="mlc-rt-row"><span class="k">{k}</span>'
                    f'<span class="v">{v}</span></div>',
                    unsafe_allow_html=True,
                )
            if d.get("suggestion"):
                st.markdown(
                    f'<div class="mlc-rt-sugg">🧭 {d["suggestion"]}</div>',
                    unsafe_allow_html=True,
                )

            # 内容の簡単な編集（入力欄として見せる）
            st.markdown('<div class="mlc-edit-label">達成していたい状態（自由に書き換えられます）</div>',
                        unsafe_allow_html=True)
            new_state = st.text_input(
                "達成していたい状態", value=a["state"],
                key=f"rt_edit_{compass_id}_{when}",
                label_visibility="collapsed",
                placeholder="ここをタップして書き換えられます",
            )
            if new_state != a["state"]:
                a["state"] = new_state

            step_text = a["state"]
            b1, b2 = st.columns(2)
            with b1:
                if st.button("今日の一歩にする", key=f"rt_today_{compass_id}_{when}",
                             use_container_width=True):
                    add_today(step_text)
                    st.toast("今日の一歩に加えました")
            with b2:
                if st.button("今週の一歩にする", key=f"rt_week_{compass_id}_{when}",
                             use_container_width=True):
                    add_week(step_text)
                    st.toast("今週の一歩に加えました")

            full = route["axes"]
            idx = full.index(a)
            b3, b4, b5 = st.columns(3)
            with b3:
                if st.button("↑ 上へ", key=f"rt_up_{compass_id}_{when}",
                             disabled=(idx == 0), use_container_width=True):
                    full[idx - 1], full[idx] = full[idx], full[idx - 1]
                    st.rerun()
            with b4:
                if st.button("↓ 下へ", key=f"rt_down_{compass_id}_{when}",
                             disabled=(idx == len(full) - 1), use_container_width=True):
                    full[idx + 1], full[idx] = full[idx], full[idx + 1]
                    st.rerun()
            with b5:
                if st.button("今は考えない", key=f"rt_hide_{compass_id}_{when}",
                             use_container_width=True):
                    hidden.add(when)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if hidden:
        if st.button(f"「今は考えない」にした項目を戻す（{len(hidden)}件）",
                     key=f"rt_restore_{compass_id}"):
            hidden.clear()
            st.rerun()


def render_route_draft(route: dict, compass: dict, progress_text: str):
    """壁打ち中に左側へ表示するRoute案の下書き（少しずつ具体化）。"""
    resources = "、".join(route.get("resources", [])) or "—"
    wall = route.get("wall") or "—"
    near = route["axes"][-1] if route["axes"] else None
    today_hint = near["state"] if near else "—"

    st.markdown(
        f"""
        <div class="mlc-card tone-main mlc-candidate">
          <div class="mlc-cc-label">康士朗さんのRoute案</div>
          <div class="mlc-cc-title">{compass["title"]}</div>
          <div class="mlc-cc-row"><span class="k">設定した期間</span>
            <span class="v">{route["period"]}</span></div>
          <div class="mlc-cc-row"><span class="k">現在地</span>
            <span class="v">{route.get("current", "—")}</span></div>
          <div class="mlc-cc-row"><span class="k">大きな壁</span>
            <span class="v">{wall}</span></div>
          <div class="mlc-cc-row"><span class="k">使えそうなもの</span>
            <span class="v">{resources}</span></div>
          <div class="mlc-cc-row"><span class="k">仮の今日の一歩</span>
            <span class="v">{today_hint}</span></div>
          <div class="mlc-cc-progress">{progress_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
