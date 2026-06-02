from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from modules.batch_analyzer import analyze_dataframe
from modules.emotion_analyzer import EmotionAnalyzer
from modules.interview_analyzer import extract_interview_insight
from modules.reply_generator import generate_reply
from modules.speech_to_text import transcribe_audio_isolated
from modules.video_processor import extract_audio_from_video_isolated


app = FastAPI(
    title="情绪陪伴与情感分析 API",
    description="提供文本情绪分析、聊天回复、CSV 批量分析、音视频转写接口。",
    version="1.0.0",
)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="需要分析的文本")


class ChatRequest(BaseModel):
    text: str = Field(..., description="用户输入文本")
    history: List[dict] = Field(default_factory=list, description="可选聊天历史")


class BatchAnalyzeRequest(BaseModel):
    texts: List[str] = Field(..., description="待批量分析的文本列表")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    result = EmotionAnalyzer().analyze(request.text)
    return result.to_dict()


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    result = EmotionAnalyzer().analyze(request.text)
    reply = generate_reply(request.text, result.label)
    return {
        "text": request.text,
        "emotion": result.to_dict(),
        "reply": reply,
    }


@app.post("/batch/analyze")
def batch_analyze(request: BatchAnalyzeRequest) -> dict:
    analyzer = EmotionAnalyzer()
    rows = []
    for text in request.texts:
        result = analyzer.analyze(text)
        rows.append(
            {
                "text": text,
                "emotion": result.to_dict(),
                "reply": generate_reply(text, result.label),
            }
        )
    return {"results": rows}


@app.post("/csv/analyze")
async def analyze_csv(file: UploadFile = File(...), text_column: str = "text"):
    try:
        df = pd.read_csv(file.file)
        result_df = analyze_dataframe(df, text_column)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    csv_bytes = result_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    return StreamingResponse(
        iter([csv_bytes]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=emotion_results.csv"},
    )


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)) -> dict:
    suffix = Path(file.filename or "").suffix.lower()
    video_suffixes = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    audio_suffixes = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
    if suffix not in video_suffixes | audio_suffixes:
        raise HTTPException(status_code=400, detail="仅支持常见音频或视频文件。")

    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(await file.read())

    try:
        audio_path = temp_path
        if suffix in video_suffixes:
            audio_path = extract_audio_from_video_isolated(temp_path, temp_path.parent)
        text = transcribe_audio_isolated(audio_path)
        result = EmotionAnalyzer().analyze(text)
        insight = extract_interview_insight(text)
        return {
            "text": text,
            "emotion": result.to_dict(),
            "interview_insight": {
                "summary": insight.summary,
                "viewpoints": insight.viewpoints,
                "keywords": insight.keywords,
                "evidence": insight.evidence,
            },
            "reply": generate_reply(text, result.label),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except OSError:
            pass
