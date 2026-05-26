import pandas as pd

from modules.batch_analyzer import analyze_dataframe
from modules.emotion_analyzer import EmotionAnalyzer
from modules.reply_generator import generate_reply
from modules.report_generator import build_chat_report


def test_emotion_analyzer_detects_anxiety():
    result = EmotionAnalyzer().analyze("我最近压力很大，真的很焦虑")
    assert result.label == "焦虑"
    assert result.score > 0.5


def test_reply_generator_returns_text():
    reply = generate_reply("我很难过", "悲伤")
    assert isinstance(reply, str)
    assert reply


def test_batch_analyzer_adds_columns():
    df = pd.DataFrame({"text": ["今天很开心", "我压力很大"]})
    result = analyze_dataframe(df, "text")
    assert "emotion_label" in result.columns
    assert "comfort_reply" in result.columns
    assert len(result) == 2


def test_report_generator():
    report = build_chat_report(
        [
            {
                "text": "我压力很大",
                "emotion": "焦虑",
                "score": 0.9,
                "polarity": "negative",
            }
        ]
    )
    assert "情感分析报告" in report
    assert "焦虑" in report
