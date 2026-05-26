from io import BytesIO
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud

from .text_utils import top_keywords


def emotion_pie_chart(df: pd.DataFrame):
    counts = df["emotion_label"].value_counts().reset_index()
    counts.columns = ["emotion_label", "count"]
    return px.pie(counts, names="emotion_label", values="count", title="情绪分布")


def emotion_bar_chart(df: pd.DataFrame):
    counts = df["emotion_label"].value_counts().reset_index()
    counts.columns = ["emotion_label", "count"]
    return px.bar(counts, x="emotion_label", y="count", title="各类情绪数量")


def emotion_trend_chart(records: List[dict]):
    if not records:
        return None
    df = pd.DataFrame(records)
    df["round"] = range(1, len(df) + 1)
    return px.line(df, x="round", y="score", color="emotion", markers=True, title="对话情绪置信度趋势")


def _resolve_font_path() -> Optional[str]:
    candidates = [
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def create_wordcloud_image(texts: List[str]) -> Optional[BytesIO]:
    keywords = dict(top_keywords(texts, limit=80))
    if not keywords:
        return None
    wordcloud = WordCloud(
        font_path=_resolve_font_path(),
        width=900,
        height=420,
        background_color="white",
        colormap="Set2",
    ).generate_from_frequencies(keywords)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    image = BytesIO()
    fig.savefig(image, format="png", bbox_inches="tight", dpi=160)
    plt.close(fig)
    image.seek(0)
    return image
