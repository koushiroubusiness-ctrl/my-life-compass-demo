"""右側に開く共通チャットパネル（Compass / Route 共通）。

- フルスクリーンにしない。あくまで左側を主役にする補助パネル。
- 大量の会話履歴を縦に積まない（直近1〜3件だけ表示、それ以前は折りたたむ）。
- 外部AIは使わない。質問は固定リスト、回答は session_state。

呼び出し側は「質問リスト・現在の質問番号・回答dict・各種setter」を渡すだけ。
状態の更新は setter 経由で session_state を書き換え、パネル内で st.rerun() する。
"""
import streamlit as st


def _history_block(questions, answers, akeys, q_index):
    """これまでの回答（直近3件を表示、それ以前は折りたたみ）。"""
    answered = []
    for i in range(min(q_index, len(questions))):
        akey = akeys[i]
        val = answers.get(akey)
        if val in (None, "", []):
            continue
        if isinstance(val, (list, tuple)):
            val = "、".join(val)
        answered.append((questions[i]["q"], val))

    if not answered:
        return

    recent = answered[-3:]
    older = answered[:-3]

    if older:
        with st.expander(f"これまでの内容を見る（{len(older)}件）"):
            for q, a in older:
                st.markdown(
                    f'<div class="mlc-chat-hist"><div class="q">{q}</div>'
                    f'<div class="a">{a}</div></div>',
                    unsafe_allow_html=True,
                )

    for q, a in recent:
        st.markdown(
            f'<div class="mlc-chat-hist"><div class="q">{q}</div>'
            f'<div class="a">{a}</div></div>',
            unsafe_allow_html=True,
        )


def render_chat_panel(*, title, subtitle, questions, q_index, answers, akeys,
                      key_prefix, set_index, set_answer, close):
    """チャットパネルを1カラム内に描画する。

    questions: [{"q","choices","free"/"multi","help"}]
    q_index:   現在の質問番号（len(questions) 以上なら「ひととおり完了」）
    answers:   {akey: value}
    akeys:     questions と同じ長さの、各質問の回答キー
    set_index(new_index): 質問番号を更新
    set_answer(akey, value): 回答を保存
    close(): パネルを閉じる
    """
    total = len(questions)
    finished = q_index >= total

    # CSS の :has() で親カラムをパネル化するためのマーカー
    st.markdown('<div class="mlc-chat-marker"></div>', unsafe_allow_html=True)

    # 上部（パネル上部に固定されるヘッダー）
    st.markdown(
        f"""
        <div class="mlc-chat-head">
          <div class="mlc-chat-title">{title}</div>
          <div class="mlc-chat-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 閉じるボタン（常に上部に見える）
    if st.button("✕ 閉じる", key=f"{key_prefix}_close_top", use_container_width=True):
        close()
        st.rerun()

    # これまでの回答（直近のみ）
    _history_block(questions, answers, akeys, q_index)

    if finished:
        st.markdown(
            '<div class="mlc-chat-q">ここまで話してくれてありがとうございます。'
            '左側にまとまった内容を確認してみてください。</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("前へ戻る", key=f"{key_prefix}_back_fin", use_container_width=True):
                set_index(max(0, q_index - 1))
                st.rerun()
        with c2:
            if st.button("チャットを閉じる", key=f"{key_prefix}_close_fin", use_container_width=True):
                close()
                st.rerun()
        return

    q = questions[q_index]
    akey = akeys[q_index]
    prev_val = answers.get(akey)

    # 現在の質問
    st.markdown(
        f'<div class="mlc-chat-qnum">質問 {q_index + 1} / {total}</div>'
        f'<div class="mlc-chat-q">{q["q"]}</div>',
        unsafe_allow_html=True,
    )
    if q.get("help"):
        st.markdown(f'<div class="mlc-chat-help">{q["help"]}</div>', unsafe_allow_html=True)

    # --- 入力欄（複数選択 / 自由入力） ---
    multi = q.get("multi", False)
    allow_free = q.get("free", False) or (not q["choices"] and not multi)

    if multi:
        st.markdown('<div class="mlc-chat-help">あてはまるものを選んでください</div>',
                    unsafe_allow_html=True)
        current = prev_val if isinstance(prev_val, list) else []
        checked = []
        for j, choice in enumerate(q["choices"]):
            ck = st.checkbox(choice, value=(choice in current),
                             key=f"{key_prefix}_q{q_index}_ck{j}")
            if ck:
                checked.append(choice)
        if st.button("次へ", key=f"{key_prefix}_multi_next",
                     type="primary", use_container_width=True):
            set_answer(akey, checked)
            set_index(q_index + 1)
            st.rerun()

    else:
        free_val = ""
        if allow_free:
            default = prev_val if isinstance(prev_val, str) else ""
            free_val = st.text_area(
                "あなたの言葉で（任意）",
                value=default,
                key=f"{key_prefix}_q{q_index}_free",
                height=80,
                label_visibility="collapsed",
                placeholder="ここに入力できます（選択肢だけでも大丈夫です）",
            )

        # 選択肢ボタン（縦に並べる）
        for j, choice in enumerate(q["choices"]):
            if st.button(choice, key=f"{key_prefix}_q{q_index}_ch{j}",
                         use_container_width=True):
                set_answer(akey, choice)
                set_index(q_index + 1)
                st.rerun()

        # 自由入力を確定して次へ
        if allow_free:
            if st.button("この内容で次へ", key=f"{key_prefix}_free_next",
                         type="primary", use_container_width=True):
                set_answer(akey, free_val.strip())
                set_index(q_index + 1)
                st.rerun()

    # --- フッター操作 ---
    st.markdown('<div class="mlc-chat-foot"></div>', unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        if st.button("前へ戻る", key=f"{key_prefix}_prev",
                     disabled=(q_index == 0), use_container_width=True):
            set_index(max(0, q_index - 1))
            st.rerun()
    with f2:
        if st.button("今は分からない", key=f"{key_prefix}_skip", use_container_width=True):
            set_answer(akey, "")
            set_index(q_index + 1)
            st.rerun()

    if st.button("チャットを閉じる", key=f"{key_prefix}_close", use_container_width=True):
        close()
        st.rerun()
