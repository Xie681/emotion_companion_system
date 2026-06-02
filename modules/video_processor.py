from pathlib import Path
import subprocess
import sys
from typing import Union


def extract_audio_from_video(video_path: Union[str, Path], output_dir: Union[str, Path]) -> Path:
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{video_path.stem}_audio.wav"

    try:
        from moviepy.editor import VideoFileClip
    except ImportError as exc:
        raise RuntimeError("未安装 moviepy，无法从视频中提取音频。") from exc

    clip = VideoFileClip(str(video_path))
    try:
        if clip.audio is None:
            raise RuntimeError("该视频没有可提取的音频轨道。")
        clip.audio.write_audiofile(str(audio_path), logger=None)
    finally:
        clip.close()

    return audio_path


def extract_audio_from_video_isolated(video_path: Union[str, Path], output_dir: Union[str, Path], timeout: int = 180) -> Path:
    """Extract audio in a child process so video/ffmpeg crashes do not kill Streamlit."""
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    if not video_path.exists():
        raise FileNotFoundError(f"视频文件不存在：{video_path}")

    command = [
        sys.executable,
        "-m",
        "modules.video_processor_worker",
        str(video_path),
        str(output_dir),
    ]
    result = subprocess.run(
        command,
        cwd=str(Path(__file__).resolve().parent.parent),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"视频音频提取失败，请换一个更短的视频或转为 MP3/WAV 后重试。{detail}")

    audio_path = Path(result.stdout.strip())
    if not audio_path.exists():
        raise RuntimeError("视频音频提取失败：未生成音频文件。")
    return audio_path
