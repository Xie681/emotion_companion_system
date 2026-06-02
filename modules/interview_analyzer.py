import re
from dataclasses import dataclass
from typing import List

from modules.chinese_text import to_simplified_chinese
from modules.text_utils import top_keywords


VIEWPOINT_HINTS = [
    "认为",
    "觉得",
    "说明",
    "所以",
    "因此",
    "关键",
    "核心",
    "问题",
    "原因",
    "应该",
    "需要",
    "可以",
    "不是",
    "而是",
    "改变",
    "信号",
    "机会",
]


@dataclass
class InterviewInsight:
    summary: str
    viewpoints: List[str]
    keywords: List[str]
    evidence: List[str]


def _split_sentences(text: str) -> List[str]:
    normalized = re.sub(r"\s+", "", to_simplified_chinese(str(text or "")))
    parts = re.split(r"[。！？!?；;]+", normalized)
    return [part.strip("，,、 ") for part in parts if len(part.strip()) >= 8]


def _score_sentence(sentence: str, keywords: List[str]) -> int:
    score = 0
    score += sum(3 for hint in VIEWPOINT_HINTS if hint in sentence)
    score += sum(2 for keyword in keywords[:8] if keyword in sentence)
    if 18 <= len(sentence) <= 90:
        score += 2
    if len(sentence) > 140:
        score -= 3
    return score


def _compact_sentence(sentence: str, limit: int = 90) -> str:
    if len(sentence) <= limit:
        return sentence
    return sentence[: limit - 1].rstrip("，,、 ") + "..."


def extract_interview_insight(text: str) -> InterviewInsight:
    text = to_simplified_chinese(text)
    sentences = _split_sentences(text)
    keywords = [word for word, _count in top_keywords([text], limit=10)]

    if not sentences:
        return InterviewInsight(
            summary="暂未提取到清晰观点。",
            viewpoints=[],
            keywords=keywords,
            evidence=[],
        )

    ranked = sorted(
        sentences,
        key=lambda item: (_score_sentence(item, keywords), -sentences.index(item)),
        reverse=True,
    )
    evidence = [to_simplified_chinese(_compact_sentence(sentence)) for sentence in ranked[:3]]

    viewpoints = []
    for sentence in ranked:
        compact = to_simplified_chinese(_compact_sentence(sentence))
        if compact not in viewpoints:
            viewpoints.append(compact)
        if len(viewpoints) >= 3:
            break

    if viewpoints:
        summary = viewpoints[0]
    else:
        summary = _compact_sentence(sentences[0])

    return InterviewInsight(
        summary=to_simplified_chinese(summary),
        viewpoints=viewpoints,
        keywords=[to_simplified_chinese(keyword) for keyword in keywords],
        evidence=evidence,
    )
