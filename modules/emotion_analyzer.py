from dataclasses import dataclass
from typing import Dict, List

from .text_utils import clean_text


@dataclass(frozen=True)
class EmotionResult:
    label: str
    score: float
    polarity: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "score": self.score,
            "polarity": self.polarity,
            "reason": self.reason,
        }


EMOTION_KEYWORDS: Dict[str, List[str]] = {
    "积极": [
        "开心",
        "高兴",
        "快乐",
        "喜欢",
        "满意",
        "期待",
        "顺利",
        "舒服",
        "幸运",
        "感谢",
        "成功",
        "不错",
        "很好",
        "真棒",
        "表扬",
    ],
    "悲伤": [
        "难过",
        "伤心",
        "失落",
        "孤独",
        "哭",
        "崩溃",
        "委屈",
        "心酸",
        "绝望",
        "没人懂",
        "撑不住",
    ],
    "焦虑": [
        "压力",
        "焦虑",
        "担心",
        "害怕",
        "紧张",
        "烦",
        "失眠",
        "来不及",
        "怎么办",
        "慌",
        "不安",
        "怕",
    ],
    "愤怒": [
        "生气",
        "愤怒",
        "气死",
        "讨厌",
        "不公平",
        "火大",
        "烦死",
        "忍不了",
        "骂",
        "恨",
    ],
    "消极": [
        "没用",
        "失败",
        "做不好",
        "不想",
        "放弃",
        "累",
        "麻木",
        "痛苦",
        "糟糕",
        "完了",
        "没希望",
    ],
}

NEGATIVE_LABELS = {"悲伤", "焦虑", "愤怒", "消极"}


class EmotionAnalyzer:
    """离线规则分析器，接口稳定，后续可替换为 Hugging Face 等模型。"""

    def analyze(self, text: str) -> EmotionResult:
        text = clean_text(text)
        if not text:
            return EmotionResult("中性", 0.5, "neutral", "文本为空，无法判断明显情绪。")

        label_scores = {
            label: sum(1 for keyword in keywords if keyword in text)
            for label, keywords in EMOTION_KEYWORDS.items()
        }
        best_label, best_hits = max(label_scores.items(), key=lambda item: item[1])

        if best_hits == 0:
            return EmotionResult("中性", 0.62, "neutral", "未命中明显情绪关键词，判断为中性。")

        total_hits = sum(label_scores.values())
        score = min(0.98, 0.58 + best_hits * 0.12 + total_hits * 0.03)
        polarity = "positive" if best_label == "积极" else "negative"
        matched = [kw for kw in EMOTION_KEYWORDS[best_label] if kw in text]
        reason = f"命中关键词：{', '.join(matched[:5])}"
        return EmotionResult(best_label, round(score, 2), polarity, reason)

    def analyze_many(self, texts: List[str]) -> List[EmotionResult]:
        return [self.analyze(text) for text in texts]


def analyze_text(text: str) -> dict:
    return EmotionAnalyzer().analyze(text).to_dict()
