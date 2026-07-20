"""疑似AIサービス（モック）。

外部AI / API は一切使わない。ユーザーの回答テキストに対する
簡単なキーワード判定と、あらかじめ用意したテンプレートだけで、
Compass候補・Route案・穏やかな振り返り要約を組み立てる。

主役はあくまで整理された Compass / Route / 今日の一歩。
ここは「静かな補助役」として、それらしい出力を返すだけの層。
"""
from data.mock_data import ROUTE_AXES, PERIOD_ALIAS, SAMPLE_ROUTE_C1

# ---------------------------------------------------------
# キーワード → Compass候補テンプレート
# ---------------------------------------------------------
# (キーワード群, テンプレート) の順で、最初に一致したものを採用する
_COMPASS_RULES = [
    (
        ["副業", "複業", "収入", "お金", "稼", "経済", "月50", "収入を増やしたい"],
        {
            "title": "複業で収入の柱を増やす",
            "desc": "会社だけに依存せず、自分の経験を活かした複数の収入源を持つ。",
            "reason": "何かあっても安心できる状態をつくりたいから。",
            "tags": ["安心", "自由", "挑戦"],
            "tone": "main",
        },
    ),
    (
        ["家族", "子ども", "子供", "時間", "家庭", "パートナー", "家族との時間を増やしたい"],
        {
            "title": "家族との時間を大切にできる暮らし",
            "desc": "仕事だけに時間を使わず、家族との予定や日常を大切にできる暮らしをつくる。",
            "reason": "毎日の真ん中に、大切な人との時間を置きたいから。",
            "tags": ["家族", "余白", "安心"],
            "tone": "sub",
        },
    ),
    (
        ["健康", "体調", "運動", "スポーツ", "体力", "睡眠", "健康を大切にしたい"],
        {
            "title": "健康を保ちながら挑戦を続ける",
            "desc": "無理なく体を整えながら、自分の成長を感じられる挑戦を続ける。",
            "reason": "心にも体にも余裕を持ち続けたいから。",
            "tags": ["健康", "挑戦", "成長"],
            "tone": "accent",
        },
    ),
    (
        ["自由", "働き方", "会社", "独立", "場所", "リモート", "働き方を変えたい"],
        {
            "title": "自分らしく働ける環境をつくる",
            "desc": "時間や場所にしばられず、納得できる形で働ける状態をつくる。",
            "reason": "自分のペースを大切にしながら働きたいから。",
            "tags": ["自由", "安心", "挑戦"],
            "tone": "main",
        },
    ),
    (
        ["挑戦", "学び", "成長", "スキル", "勉強", "資格", "新しいことに挑戦したい"],
        {
            "title": "新しいことに挑戦し、成長し続ける",
            "desc": "小さくてもいいので、新しい経験を重ねて自分の幅を広げる。",
            "reason": "変わり続ける自分でいたいから。",
            "tags": ["挑戦", "成長", "自由"],
            "tone": "sub",
        },
    ),
    (
        ["旅行", "趣味", "経験", "旅", "体験", "遊び"],
        {
            "title": "経験を広げる時間をつくる",
            "desc": "仕事以外にも、心が動く経験のための時間を意識してつくる。",
            "reason": "暮らしに彩りと余白を持ちたいから。",
            "tags": ["余白", "自由", "成長"],
            "tone": "accent",
        },
    ),
]

# まだ何も判定できないときの初期候補
_COMPASS_DEFAULT = {
    "title": "まだ言葉にならない、これからの未来",
    "desc": "少しずつ話しながら、目指したい未来を一緒に形にしていきましょう。",
    "reason": "",
    "tags": ["これから"],
    "tone": "main",
}


def _joined(answers: dict) -> str:
    """回答（index→text）を1つの文字列にまとめる。"""
    parts = []
    for v in answers.values():
        if isinstance(v, (list, tuple)):
            parts.extend(str(x) for x in v)
        elif v:
            parts.append(str(v))
    return " ".join(parts)


def build_compass_candidate(answers: dict) -> dict:
    """Compassの回答からCompass候補を組み立てる。

    answers: {0: "…", 1: "…", 3: "1年以内", ...}
    """
    text = _joined(answers)

    template = None
    for keywords, tmpl in _COMPASS_RULES:
        if any(k in text for k in keywords):
            template = tmpl
            break
    if template is None:
        template = _COMPASS_DEFAULT

    cand = dict(template)  # コピー
    cand["tags"] = list(template["tags"])

    # Q3(理由=index2) が入力されていれば理由を上書き
    reason = answers.get(2)
    if isinstance(reason, str) and reason.strip():
        cand["reason"] = reason.strip()

    # Q4(期間=index3) を反映
    period = answers.get(3)
    cand["period"] = period if period and period != "まだ決めていない" else "まだ決めていない"

    # Q5(今大切にしたいこと=index4) を軽くタグに反映
    keep = answers.get(4)
    if isinstance(keep, str) and keep.strip() and len(cand["tags"]) < 4:
        # 短い語だけタグ化（長文は入れない）
        word = keep.strip()
        if len(word) <= 6 and word not in cand["tags"]:
            cand["tags"].append(word)

    return cand


def has_enough_for_candidate(answers: dict) -> bool:
    """Compass候補を提示してよいか（数問答えたか）。"""
    answered = [k for k, v in answers.items() if v]
    return len(answered) >= 2


# ---------------------------------------------------------
# Route 生成
# ---------------------------------------------------------
# 汎用の軸テンプレート（Compassタイトルを差し込む）
def _generic_axis_content(when: str, title: str, wall: str, step_size: str) -> dict:
    short = title
    table = {
        "5年後": {
            "state": f"「{short}」がほぼ実現できている",
            "ach": ["無理のない形で続けられている", "自分でも変化を実感している"],
        },
        "3年後": {
            "state": f"「{short}」に大きく近づいている",
            "ach": ["続けるための仕組みができている"],
        },
        "1年後": {
            "state": "手応えを感じられる状態になっている",
            "ach": ["小さな成果が1つ形になっている", "続け方が見えている"],
        },
        "6か月後": {
            "state": "続けられるリズムができている",
            "ach": ["最初の一歩を習慣にできている"],
        },
        "3か月後": {
            "state": "最初の小さな一歩を踏み出せている",
            "ach": ["やってみて分かったことがある"],
        },
        "1か月後": {
            "state": "始める準備が整っている",
            "ach": ["最初にやることが決まっている"],
        },
        "今月": {
            "state": "何から始めるかを決める",
            "ach": ["取り組むテーマを1つに絞る"],
        },
        "今週": {
            "state": "今の自分の材料を書き出す",
            "ach": ["得意なこと・使えるものを整理する"],
        },
        "今日": {
            "state": f"{step_size or '10分'}だけ、はじめの一歩に触れてみる",
            "ach": [],
        },
    }
    base = table.get(when, {"state": f"「{short}」に近づく", "ach": []})
    return {
        "state": base["state"],
        "ach": base["ach"],
        "detail": {
            "money": "今は大きな出費は不要です",
            "skill": "今あるものから始めて大丈夫です",
            "exp": "やりながら身についていきます",
            "wall": wall or "何から始めるか",
            "suggestion": "遠くを見すぎず、次の1つに集中しましょう。",
        },
    }


def resolve_period_key(period: str) -> str:
    """『3年以内』などの表記を Route軸キー（3年 等）へ寄せる。"""
    if not period:
        return "3年"
    return PERIOD_ALIAS.get(period, "3年")


def build_route(compass: dict, answers: dict) -> dict:
    """選択中Compassと回答からRoute案（時系列）を組み立てる。

    返り値: {
      "period": "3年",
      "axes": [ {"when", "state", "ach":[...], "detail":{...}}, ... ],
      "current": str, "wall": str, "resources": [...], "step_size": str,
    }
    """
    # 期間：Routeの質問で選んでいればそれ、なければCompassの期間
    period_ans = answers.get("period")
    if period_ans in ("自分で期間を設定する", "まだ決めていない", None, ""):
        period_ans = compass.get("period")
    period_key = resolve_period_key(period_ans)

    axes_names = ROUTE_AXES.get(period_key, ROUTE_AXES["3年"])

    current = answers.get("current") or "まだ整理中です"
    wall = answers.get("wall") or ""
    resources = answers.get("resources") or []
    step_size = answers.get("step_size") or ""

    axes = []
    is_sample = compass.get("id") == "c1"
    for when in axes_names:
        if is_sample and when in SAMPLE_ROUTE_C1:
            src = SAMPLE_ROUTE_C1[when]
            axes.append({
                "when": when,
                "state": src["state"],
                "ach": list(src["ach"]),
                "detail": dict(src["detail"]),
            })
        else:
            axes.append({
                "when": when,
                **_generic_axis_content(when, compass.get("title", ""), wall, step_size),
            })

    return {
        "period": period_key,
        "axes": axes,
        "current": current,
        "wall": wall,
        "resources": resources,
        "step_size": step_size,
    }


def route_progress_text(answers: dict) -> str:
    """Route案の「今の下書き度合い」を短い文で返す（チャット中の左側表示用）。"""
    n = len([v for v in answers.values() if v])
    if n == 0:
        return "まだ何も決まっていません。ここから一緒に整理していきましょう。"
    if n <= 2:
        return "少しずつ、道筋の輪郭が見えてきました。"
    if n <= 4:
        return "期間と現在地がそろってきました。時系列がはっきりしてきています。"
    return "道筋がひととおり整いました。あとは今日の一歩を選ぶだけです。"


# ---------------------------------------------------------
# Reflect：穏やかなまとめ
# ---------------------------------------------------------
def build_reflection_summary(did: str, feeling: str, notice: str, next_try: str) -> str:
    """入力に応じて、責めない穏やかなまとめを返す。"""
    if not any([did, feeling, notice, next_try]):
        return ("まだ何も書かなくて大丈夫です。"
                "ひとことでも書けたら、それが今日の振り返りになります。")

    parts = []
    if did:
        parts.append(
            "今日はすべてを進めるのではなく、一つのことに向き合う時間をつくれました。"
        )
    else:
        parts.append("今日は、立ち止まって自分を見つめられた一日でした。")

    if notice:
        parts.append("気づいたことを言葉にできたのは、確かな前進です。")

    if next_try:
        parts.append("次に試したいことも見えています。焦らず、そのままのペースで大丈夫です。")
    else:
        parts.append("小さくても、考えるだけの状態から一歩進んでいます。")

    return "".join(parts)
