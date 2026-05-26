import pandas as pd

from .emotion_analyzer import EmotionAnalyzer
from .reply_generator import generate_reply


def analyze_dataframe(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    if text_column not in df.columns:
        raise ValueError(f"文本列不存在：{text_column}")

    analyzer = EmotionAnalyzer()
    rows = []
    for value in df[text_column].fillna("").astype(str):
        result = analyzer.analyze(value)
        rows.append(
            {
                "emotion_label": result.label,
                "emotion_score": result.score,
                "emotion_polarity": result.polarity,
                "emotion_reason": result.reason,
                "comfort_reply": generate_reply(value, result.label),
            }
        )

    return pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
