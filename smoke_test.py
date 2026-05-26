from modules.emotion_analyzer import EmotionAnalyzer
from modules.reply_generator import generate_reply
from modules.report_generator import build_chat_report
from modules.text_utils import top_keywords


def main():
    analyzer = EmotionAnalyzer()
    samples = [
        "今天收到表扬，我特别开心。",
        "最近作业太多了，我压力很大，真的很焦虑。",
        "我很生气，感觉这件事一点也不公平。",
    ]

    records = []
    for text in samples:
        result = analyzer.analyze(text)
        reply = generate_reply(text, result.label)
        records.append(
            {
                "text": text,
                "emotion": result.label,
                "score": result.score,
                "polarity": result.polarity,
            }
        )
        print(f"文本：{text}")
        print(f"情绪：{result.label} 置信度：{result.score} 原因：{result.reason}")
        print(f"回复：{reply}")
        print("-" * 40)

    print("关键词：", top_keywords(samples, limit=5))
    print(build_chat_report(records))


if __name__ == "__main__":
    main()
