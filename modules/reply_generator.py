from typing import Dict, List, Optional, Tuple

from .qwen_client import call_qwen


REPLY_TEMPLATES: Dict[str, List[str]] = {
    "积极": [
        "太好了，真的替你开心。能把拖了很久的任务完成，本身就很不容易，这说明你一直在努力往前走。现在这份轻松感很值得被好好感受一下。",
        "听到你说轻松了一点，我也跟着松了一口气。你做到了一个之前卡住很久的任务，这很棒，也很值得夸一夸自己。",
        "这是一件值得认真肯定的事。哪怕只是轻松了一点，也说明你已经从压力里往外走了一步。今天可以允许自己稍微休息一下。",
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
POSITIVE_PROGRESS_HINTS = [
    "完成",
    "终于",
    "轻松",
    "放松",
    "搞定",
    "做完",
    "顺利",
    "成功",
    "进步",
    "松了一口气",
]
CONTEXTUAL_REPLIES: Dict[str, List[str]] = {
    "exam_anxiety": [
        "明天考试会紧张很正常，说明你很在乎这件事。今晚先别再无限加码了，可以把最容易拿分的部分过一遍，再准备好证件和文具，让自己带着一点确定感去睡。",
        "你担心发挥不好，其实也是在提醒自己想认真对待。现在最有用的不是继续吓自己，而是做一个很小的收尾：列出3个最可能考到的点，各看5分钟就停。",
    ],
    "rain_low": [
        "下雨天确实容易把人往低处带，你能说出来已经很好了。今天不用强迫自己立刻振作，可以先做一件很轻的事，比如喝点热水、开一盏灯，给自己一点暖的信号。",
        "这种低落不一定需要马上找到原因。你可以先把今天的目标放小一点：洗个脸、整理一下桌面，或者听一首不太吵的歌，让身体先慢慢回来。",
    ],
    "pressure_overload": [
        "你现在像是被压力一下子压住了，不是你不行。我们先别处理全部事情，只挑一件最急的小任务，写下第一步，哪怕只做5分钟，也是在把局面往回拿。",
        "听起来你已经撑了一阵子了。先把脑子里的事情倒出来，分成“今天必须做”和“可以明天做”，你不需要同时扛住所有事。",
    ],
    "social_withdrawal": [
        "不想社交的时候，可能是你真的有点累了。你不用马上逼自己和很多人联系，可以只选一个安全的人，发一句很短的话：我最近有点累，晚点再聊。",
        "想躲起来并不代表你不好相处，很多时候只是能量不够了。今天可以先把社交要求降到最低，给自己留一点恢复的空间。",
    ],
    "positive_progress": [
        "这真的值得夸你。拖了很久的任务能完成，说明你不是做不到，而是一直在找回节奏。现在这份轻松感很珍贵，今天可以允许自己好好喘口气。",
        "太好了，你把一件卡了很久的事推进了，这不是小事。请认真给自己记一笔：你是有能力完成事情的，只是之前太累了。",
    ],
}


def has_crisis_risk(text: str) -> bool:
    return any(hint in str(text or "") for hint in CRISIS_HINTS)


def has_positive_progress(text: str) -> bool:
    return any(hint in str(text or "") for hint in POSITIVE_PROGRESS_HINTS)


def _detect_context(text: str) -> Optional[str]:
    text = str(text or "")
    if has_positive_progress(text):
        return "positive_progress"
    if any(word in text for word in ["考试", "考研", "测验", "挂科", "发挥不好"]):
        return "exam_anxiety"
    if any(word in text for word in ["下雨", "阴天", "天气不好"]) and any(word in text for word in ["低落", "提不起精神", "没精神", "难受"]):
        return "rain_low"
    if any(word in text for word in ["压力", "压得", "事情很多", "忙不过来", "来不及"]):
        return "pressure_overload"
    if any(word in text for word in ["不想社交", "不想和别人说话", "不想见人", "不想聊天"]):
        return "social_withdrawal"
    return None


def _is_too_similar(candidate: str, history: Optional[List[dict]]) -> bool:
    if not history:
        return False
    previous_replies = [str(item.get("reply", "")) for item in history[-4:]]
    candidate_prefix = candidate[:16]
    return any(candidate_prefix and candidate_prefix in reply for reply in previous_replies)


def _choose_reply(candidates: List[str], history: Optional[List[dict]]) -> str:
    for candidate in candidates:
        if not _is_too_similar(candidate, history):
            return candidate
    return candidates[0]


def _fallback_reply(text: str, emotion_label: str, history: Optional[List[dict]] = None) -> str:
    context = _detect_context(text)
    if context:
        return _choose_reply(CONTEXTUAL_REPLIES[context], history)
    templates = REPLY_TEMPLATES.get(emotion_label, REPLY_TEMPLATES["中性"])
    return _choose_reply(templates, history)


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
                "如果用户说完成了任务、轻松了一点、终于做完了、取得进展，先真诚夸赞和肯定，"
                "不要把这种表达当成普通中性情绪，也不要急着追问原因。"
                "避免重复上一轮已经说过的安慰句；每次回应都要结合用户这句话里的具体场景，"
                "给出一个真正能做的小动作。"
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
    reply, _source = generate_reply_with_source(text, emotion_label, history)
    return reply


def generate_reply_with_source(text: str, emotion_label: str, history: Optional[List[dict]] = None) -> Tuple[str, str]:
    if has_crisis_risk(text):
        return (
            "我很在意你刚才说的内容。如果你现在有伤害自己的冲动，请立刻联系身边可信任的人，"
            "或拨打当地紧急电话寻求帮助。你不需要一个人扛着。"
        ), "安全规则"

    if has_positive_progress(text) and emotion_label in {"中性", "积极"}:
        emotion_label = "积极"

    try:
        return generate_qwen_reply(text, emotion_label, history), "大模型API"
    except Exception:
        return _fallback_reply(text, emotion_label, history), "本地模板"
