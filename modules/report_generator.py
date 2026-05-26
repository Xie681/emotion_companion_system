from datetime import datetime
from typing import List

import pandas as pd

from .text_utils import top_keywords


def build_chat_report(records: List[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not records:
        return f"# 情感分析报告\n\n生成时间：{now}\n\n暂无对话记录。"

    df = pd.DataFrame(records)
    main_emotion = df["emotion"].mode().iloc[0]
    avg_score = round(float(df["score"].mean()), 2)
    negative_ratio = round(float((df["polarity"] == "negative").mean()) * 100, 1)
    keywords = top_keywords(df["text"].astype(str).tolist(), limit=10)
    keyword_text = "、".join([word for word, _ in keywords]) or "暂无明显关键词"

    representative = df.sort_values("score", ascending=False).head(3)["text"].tolist()
    representative_text = "\n".join([f"- {text}" for text in representative])

    suggestions = {
        "积极": "继续记录积极事件，保持当前节奏。",
        "中性": "可以进一步表达具体事件，帮助系统更准确理解状态。",
        "悲伤": "允许自己慢下来，尝试联系可信任的人获得陪伴。",
        "焦虑": "把压力拆成小步骤，先处理最紧急、最可控的一项。",
        "愤怒": "先让情绪降温，再决定沟通方式，避免冲动表达造成二次伤害。",
        "消极": "从一个小目标开始恢复掌控感，必要时寻求现实支持。",
    }

    return f"""# 情感分析报告

## 1. 基本信息

- 生成时间：{now}
- 对话轮数：{len(records)}

## 2. 总体情绪判断

- 主要情绪：{main_emotion}
- 平均置信度：{avg_score}
- 负面情绪占比：{negative_ratio}%

## 3. 高频关键词

{keyword_text}

## 4. 代表性语句

{representative_text}

## 5. 系统建议

{suggestions.get(main_emotion, suggestions["中性"])}

## 6. 温馨提示

本系统仅提供情绪分析和陪伴建议，不能替代专业心理咨询、诊断或治疗。"""
