import random
from typing import Dict, List, Optional

from .qwen_client import call_qwen


REPLY_TEMPLATES: Dict[str, List[str]] = {
    "积极": [
        "听起来这是一个很好的时刻。你可以把这份积极感受记下来，它会成为之后继续前进的小证据。",
        "能感受到你现在的状态不错。愿意继续说说是什么让你有这种感觉吗？",
    ],
    "中性": [
        "我明白了。你可以继续把事情说得更具体一点，我会陪你一起梳理。",
        "谢谢你告诉我这些。我们可以先从你最在意的部分开始聊。",
    ],
    "悲伤": [
        "听起来你现在真的有些难过。你愿意说出来已经很不容易了，我们可以慢慢把这件事理清楚。",
        "我能感受到这件事对你影响很大。先别急着责怪自己，情绪低落时更需要一点温柔的停顿。",
    ],
    "焦虑": [
        "你现在可能被很多事情压住了。先试着慢慢呼吸一下，再把最紧急的一件事挑出来处理。",
        "焦虑的时候，大脑容易把问题放大。我们可以把它拆成几个更小、更能完成的步骤。",
    ],
    "愤怒": [
        "你会生气是有原因的。先让情绪缓一缓，再决定怎么回应，会更保护你自己。",
        "这件事确实让人不舒服。我们可以先弄清楚，你最在意的是被误解、被忽视，还是觉得不公平。",
    ],
    "消极": [
        "听起来你已经累了很久。先不要用一次低谷定义自己，我们可以从一个很小的可完成动作开始。",
        "你现在的感受值得被认真对待。若这种无力感持续很久，也可以考虑找信任的人或专业人士聊聊。",
    ],
}

CRISIS_HINTS = ["自杀", "不想活", "结束生命", "伤害自己", "活不下去"]


def has_crisis_risk(text: str) -> bool:
    return any(hint in str(text or "") for hint in CRISIS_HINTS)


def _fallback_reply(emotion_label: str) -> str:
    templates = REPLY_TEMPLATES.get(emotion_label, REPLY_TEMPLATES["中性"])
    return random.choice(templates)


def generate_qwen_reply(text: str, emotion_label: str, history: Optional[List[dict]] = None) -> str:
    history = history or []
    compact_history = history[-6:]
    history_text = "\n".join(
        f"用户：{item.get('text', '')}\n系统：{item.get('reply', '')}"
        for item in compact_history
        if item.get("text") or item.get("reply")
    )

    messages = [
        {
            "role": "system",
            "content": (
                "你是一个温和、克制、可靠的中文情绪陪伴助手。"
                "请根据用户原文、情绪标签和必要的聊天历史生成回应。"
                "要求：先共情，不评判；不要做医学诊断；不要夸大问题；"
                "回复控制在80到150字；可以给一个很小、可执行的下一步。"
                "如果用户表达自伤或伤害他人的风险，建议立即联系可信任的人或当地紧急服务。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"聊天历史：\n{history_text or '暂无'}\n\n"
                f"用户原文：{text}\n"
                f"情绪标签：{emotion_label}\n\n"
                "请生成一段自然、温和、有陪伴感的中文回复。"
            ),
        },
    ]
    return call_qwen(messages, model="qwen-plus", temperature=0.7)


def generate_reply(text: str, emotion_label: str, history: Optional[List[dict]] = None) -> str:
    if has_crisis_risk(text):
        return (
            "我很在意你刚才说的内容。如果你现在有伤害自己的冲动，请立刻联系身边可信任的人，"
            "或拨打当地紧急电话寻求帮助。你不需要一个人扛着。"
        )

    try:
        return generate_qwen_reply(text, emotion_label, history)
    except Exception:
        return _fallback_reply(emotion_label)
