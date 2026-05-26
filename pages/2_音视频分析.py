from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from modules.auth import render_auth_panel
from modules.emotion_analyzer import EmotionAnalyzer
from modules.reply_generator import generate_reply
from modules.speech_to_text import transcribe_audio
from modules.ui import apply_calm_theme, render_bili_topbar, render_confidence_card
from modules.video_processor import extract_audio_from_video


st.set_page_config(page_title="音视频分析", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("音视频分析")
render_auth_panel()
st.title("音视频上传转文字与情绪分析")
st.markdown('<div class="gentle-note">适合分析语音日记、访谈片段或视频反馈。上传后会先转写为文字，再进行情绪识别。</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "上传音频或视频文件",
    type=["mp3", "wav", "m4a", "aac", "flac", "ogg", "mp4", "avi", "mov", "mkv", "webm"],
)

if uploaded_file:
    suffix = Path(uploaded_file.name).suffix.lower()
    video_suffixes = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

    st.write(f"文件名：{uploaded_file.name}")
    if st.button("开始转写并分析"):
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(uploaded_file.getbuffer())

        try:
            with st.spinner("正在处理音视频文件..."):
                audio_path = temp_path
                if suffix in video_suffixes:
                    audio_path = extract_audio_from_video(temp_path, temp_path.parent)
                text = transcribe_audio(audio_path)
                result = EmotionAnalyzer().analyze(text)
                reply = generate_reply(text, result.label)

            st.subheader("转写文本")
            st.write(text or "未识别到有效文本")

            st.subheader("情绪分析")
            col1, col2 = st.columns(2)
            col1.metric("情绪标签", result.label)
            col2.markdown(render_confidence_card(result.score), unsafe_allow_html=True)
            st.caption(result.reason)

            st.subheader("自适应回复")
            st.write(reply)
        except Exception as exc:
            st.error(str(exc))
            st.info("如果是首次使用音视频转写，请安装 faster-whisper 或 openai-whisper，并确认 ffmpeg 可用。")
        finally:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass
