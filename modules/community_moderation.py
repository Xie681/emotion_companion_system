from typing import Dict, List

from .emotion_analyzer import EmotionAnalyzer


RISK_HINTS = {
    "高": ["自杀", "不想活", "结束生命", "伤害自己", "活不下去", "想死", "想消失"],
    "中": ["撑不住", "绝望", "没人懂", "崩溃", "睡不好", "失眠", "痛苦"],
}

TAG_KEYWORDS = {
    "压力": ["压力", "学习", "考试", "作业", "来不及", "任务"],
    "焦虑": ["焦虑", "担心", "害怕", "紧张", "不安", "慌"],
    "疲惫": ["累", "疲惫", "困", "睡不好", "失眠", "没精神"],
    "孤独": ["孤独", "没人懂", "一个人", "不想和别人说话"],
    "难过": ["难过", "伤心", "委屈", "低落", "哭"],
    "需要陪伴": ["陪", "安慰", "鼓励", "抱抱", "撑不住"],
    "开心": ["开心", "高兴", "快乐", "顺利", "幸运"],
}

ANONYMOUS_NAMES = ["树洞用户", "小太阳用户", "月光用户", "云朵用户", "风铃用户"]


def _risk_level(text: str) -> Dict[str, str]:
    for level, hints in RISK_HINTS.items():
        matched = [hint for hint in hints if hint in text]
        if matched:
            return {"risk_level": level, "risk_reason": f"命中风险表达：{', '.join(matched[:3])}"}
    return {"risk_level": "低", "risk_reason": "未命中明显高风险表达。"}


def _tags(text: str, fallback: str) -> List[str]:
    tags = [tag for tag, keywords in TAG_KEYWORDS.items() if any(keyword in text for keyword in keywords)]
    if fallback not in ("中性", "积极") and fallback not in tags:
        tags.append(fallback)
    return tags[:4] or ["日常"]


def analyze_community_post(title: str, content: str, selected_emotion: str, username_seed: str = "") -> Dict[str, object]:
    text = f"{title}\n{content}"
    result = EmotionAnalyzer().analyze(text)
    risk = _risk_level(text)
    possible = _tags(text, selected_emotion or result.label)
    tendency = "积极" if result.polarity == "positive" else "消极" if result.polarity == "negative" else "中性"
    seed = sum(ord(char) for char in (username_seed + title + content))
    anonymous_name = f"{ANONYMOUS_NAMES[seed % len(ANONYMOUS_NAMES)]}{seed % 1000:03d}"
    return {
        "emotion_label": result.label,
        "emotion_score": result.score,
        "emotion_tendency": tendency,
        "possible_emotions": possible,
        "tags": [f"#{tag}" for tag in possible],
        "risk_level": risk["risk_level"],
        "risk_reason": risk["risk_reason"],
        "anonymous_name": anonymous_name,
    }


def generate_community_reply(analysis: Dict[str, object]) -> str:
    risk_level = analysis.get("risk_level")
    if risk_level == "高":
        return (
            "我注意到你现在可能非常痛苦。如果你正处于危险中，请尽快联系身边可信任的人，"
            "或拨打当地紧急求助电话。你不需要一个人扛着。"
        )

    emotion = analysis.get("emotion_label", "中性")
    templates = {
        "积极": "能看到你记录下这个时刻真好。愿这份轻松和亮一点的感受，成为你之后继续往前走的小证据。",
        "焦虑": "听起来你被很多事情压住了。可以先慢慢呼吸一下，把最紧急的一件事挑出来，拆成今天能完成的一小步。",
        "悲伤": "听起来这段感受真的不轻。你愿意说出来已经很不容易了，先允许自己慢一点，也可以找可信任的人陪你待一会儿。",
        "愤怒": "你会生气一定有原因。先给情绪一点降温的时间，再整理自己真正想表达的需求，会更保护你自己。",
        "消极": "听起来你已经消耗了很多力气。先不要用这一段低谷定义自己，从一个很小、确定能完成的动作开始就好。",
        "中性": "谢谢你把这些写下来。可以继续把最在意的部分说清楚一点，社区里的人会尽量用温和的方式回应你。",
    }
    return templates.get(str(emotion), templates["中性"])
