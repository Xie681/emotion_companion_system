from pathlib import Path
from functools import lru_cache
import os
import subprocess
import sys
from typing import Union

from modules.chinese_text import to_simplified_chinese


DEFAULT_MODEL_NAME = "base"
MODEL_NAME = os.getenv("WHISPER_MODEL", DEFAULT_MODEL_NAME)
TRANSCRIBE_PROMPT = "以下是普通话日常对话或访谈片段，请使用简体中文准确转写，不要翻译，不要总结。"


@lru_cache(maxsize=1)
def _load_faster_whisper_model():
    from faster_whisper import WhisperModel

    return WhisperModel(
        MODEL_NAME,
        device="cpu",
        compute_type="int8",
        local_files_only=True,
        cpu_threads=1,
        num_workers=1,
    )


@lru_cache(maxsize=1)
def _load_openai_whisper_model():
    import whisper

    return whisper.load_model(MODEL_NAME)


def transcribe_audio(audio_path: Union[str, Path]) -> str:
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"音频文件不存在：{audio_path}")

    errors = []

    try:
        model = _load_faster_whisper_model()
        segments, _info = model.transcribe(
            str(audio_path),
            language="zh",
            task="transcribe",
            initial_prompt=TRANSCRIBE_PROMPT,
            vad_filter=True,
            beam_size=5,
            best_of=5,
            temperature=0.0,
            condition_on_previous_text=False,
        )
        return to_simplified_chinese("".join(segment.text for segment in segments).strip())
    except ImportError as exc:
        errors.append(f"faster-whisper 未安装：{exc}")
    except Exception as exc:
        errors.append(f"faster-whisper 加载或识别失败：{exc}")

    try:
        model = _load_openai_whisper_model()
        result = model.transcribe(
            str(audio_path),
            language="zh",
            task="transcribe",
            initial_prompt=TRANSCRIBE_PROMPT,
        )
        return to_simplified_chinese(str(result.get("text", "")).strip())
    except ImportError as exc:
        errors.append(f"openai-whisper 未安装：{exc}")
    except Exception as exc:
        errors.append(f"openai-whisper 加载或识别失败：{exc}")

    raise RuntimeError(
        "语音识别暂时不可用。请确认已安装 faster-whisper，并已提前下载 "
        f"Systran/faster-whisper-{MODEL_NAME} 到本地缓存。详细信息："
        + "；".join(errors)
    )


def transcribe_audio_isolated(audio_path: Union[str, Path], timeout: int = 120) -> str:
    """Run ASR in a child process so native-library crashes do not kill Streamlit."""
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"音频文件不存在：{audio_path}")

    command = [sys.executable, "-m", "modules.speech_to_text_worker", str(audio_path)]
    result = subprocess.run(
        command,
        cwd=str(Path(__file__).resolve().parent.parent),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"语音识别进程失败，请换一段更短更清晰的录音重试。{detail}")
    return to_simplified_chinese(result.stdout.strip())


def transcribe_audio_isolated_with_model(
    audio_path: Union[str, Path],
    model_name: str = DEFAULT_MODEL_NAME,
    timeout: int = 120,
) -> str:
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"音频文件不存在：{audio_path}")

    env = os.environ.copy()
    env["WHISPER_MODEL"] = model_name
    command = [sys.executable, "-m", "modules.speech_to_text_worker", str(audio_path)]
    result = subprocess.run(
        command,
        cwd=str(Path(__file__).resolve().parent.parent),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"语音识别进程失败，请换一段更短更清晰的录音重试。{detail}")
    return to_simplified_chinese(result.stdout.strip())
