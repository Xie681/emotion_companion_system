# 基于 NLP 的多模态情绪陪伴与情感分析系统

这是一个课程大作业级别的增强版情感分析应用，支持文字聊天、音视频上传转文字、情绪分析、自适应安慰回复、CSV 批量分析、可视化报告和 API 接口。

## 功能

- 文字聊天：识别用户当前情绪，并生成不同语气的安慰回复。
- 音视频分析：上传音频或视频，转写为文本后进行情绪分析。
- CSV 批量分析：选择文本列，批量生成情绪标签、置信度和回复建议。
- 可视化报告：情绪分布图、趋势图、关键词词云、代表性语句和导出结果。
- API 接口：保留 `/analyze`、`/chat`、`/batch/analyze`、`/csv/analyze`、`/transcribe` 等接口。

## 运行 Streamlit 应用

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 运行 API 服务

```bash
uvicorn api:app --reload --port 8000
```

访问接口文档：

```text
http://127.0.0.1:8000/docs
```

## API 示例

```bash
curl -X POST "http://127.0.0.1:8000/analyze" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"我最近压力很大，感觉很焦虑\"}"
```

```bash
curl -X POST "http://127.0.0.1:8000/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"我觉得自己什么都做不好\"}"
```

```bash
curl -X POST "http://127.0.0.1:8000/batch/analyze" ^
  -H "Content-Type: application/json" ^
  -d "{\"texts\":[\"今天很开心\",\"最近压力很大\"]}"
```

```bash
curl -X POST "http://127.0.0.1:8000/csv/analyze?text_column=text" ^
  -F "file=@sample_comments.csv" ^
  -o emotion_results.csv
```

## 项目结构

```text
emotion_companion_app/
├── app.py
├── api.py
├── pages/
│   ├── 1_情绪聊天.py
│   ├── 2_音视频分析.py
│   ├── 3_CSV批量分析.py
│   └── 4_可视化报告.py
├── modules/
│   ├── emotion_analyzer.py
│   ├── reply_generator.py
│   ├── speech_to_text.py
│   ├── video_processor.py
│   ├── batch_analyzer.py
│   ├── report_generator.py
│   ├── visualization.py
│   └── text_utils.py
├── assets/
│   └── stopwords.txt
├── data/
│   ├── uploaded/
│   └── results/
└── tests/
```

## 说明

默认情绪识别采用本地规则词典，优点是无需联网、无需下载大模型，方便答辩演示。后续可以在 `modules/emotion_analyzer.py` 中替换为中文 RoBERTa、SnowNLP、pysentimiento 或其他模型。

音视频转写接口默认优先尝试 `faster-whisper`，其次尝试 `openai-whisper`。如果本机没有安装转写依赖，会给出明确提示，不影响文字聊天和 CSV 分析功能。

本系统只提供情绪分析和陪伴建议，不能替代专业心理咨询或医疗诊断。
