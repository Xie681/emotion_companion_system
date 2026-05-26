from pathlib import Path
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
