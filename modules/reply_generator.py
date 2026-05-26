import random
from typing import Dict, List, Optional

from .qwen_client import call_qwen


REPLY_TEMPLATES: Dict[str, List[str]] = {
    "积极": [
        "听到你这样说，我也替你松了一口气。这样的好时刻值得被认真收起来，哪怕只是一个小小的顺利，也是在提醒你：你其实一直在往前走。",
        "感觉你现在像是终于喘上了一口气。要不要多讲一点，今天是哪一件事让你心里亮了一下？我想听。",
    ],
    "中性": [
        "嗯，我在听。你可以不用一下子说得很完整，想到哪儿就说到哪儿，我们慢慢把这团线理出来。",
        "我懂，这种感觉可能不算特别强烈，但也确实在心里占了点位置。你可以先说说，刚才那句话里最让你在意的是哪一部分？",
    ],
    "悲伤": [
        "听起来你真的有点难过，而且可能已经憋了一会儿了。先别急着把自己拉起来，能说出来已经很不容易了，我会在这里陪你慢慢讲。",
        "这件事好像挺扎心的。你现在不需要马上变好，也不用急着证明自己没事；先让自己靠一会儿，缓一缓也可以。",
    ],
    "焦虑": [
        "我能感觉到你像是被很多事情一起追着跑。先别急，我们先把呼吸放慢一点，然后只挑最眼前的一小件事看，好吗？",
        "焦虑的时候，脑子真的会把所有问题都推到你面前。你不用一次解决全部，我们可以先把它拆小，小到今天只需要迈一步。",
    ],
    "愤怒": [
        "你会生气不是没道理的，肯定是有什么地方让你觉得被冒犯、被忽视，或者很不公平。先别急着压下去，我们可以把它说清楚。",
        "这事听起来确实让人窝火。你先把火气放在这里，不用马上处理对方；我陪你先看看，你最不能接受的点到底是什么。",
    ],
    "消极": [
        "听起来你真的累了很久，像是心里的电量已经见底了。先别用现在这一刻否定自己，我们先找一个特别小、你还勉强做得到的动作开始。",
        "你现在这种无力感不是矫情，也不是你太脆弱。它值得被认真对待。今天先别逼自己太狠，如果可以，也找一个信得过的人陪你待一会儿。",
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
                "语气像一个真诚、有边界感的朋友，柔和、自然、有一点生活气，不要像客服或报告。"
                "要求：先共情，不评判；不要做医学诊断；不要夸大问题；"
                "回复控制在80到160字；可以给一个很小、可执行的下一步。"
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
