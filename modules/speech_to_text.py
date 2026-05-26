from pathlib import Path
from typing import Union


def transcribe_audio(audio_path: Union[str, Path]) -> str:
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"音频文件不存在：{audio_path}")

    try:
        from faster_whisper import WhisperModel

        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _info = model.transcribe(str(audio_path), language="zh")
        return "".join(segment.text for segment in segments).strip()
    except ImportError:
        pass

    try:
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(str(audio_path), language="zh")
        return str(result.get("text", "")).strip()
    except ImportError as exc:
        raise RuntimeError(
            "未安装语音识别依赖。请安装 faster-whisper 或 openai-whisper 后再使用音视频转写。"
        ) from exc
