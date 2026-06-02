from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from modules.auth import render_auth_panel
from modules.emotion_analyzer import EmotionAnalyzer
from modules.interview_analyzer import extract_interview_insight
from modules.reply_generator import generate_reply
from modules.speech_to_text import transcribe_audio_isolated
from modules.ui import apply_calm_theme, render_bili_topbar, render_confidence_card
from modules.video_processor import extract_audio_from_video_isolated


MAX_MEDIA_BYTES = 50 * 1024 * 1024


st.set_page_config(page_title="音视频分析", page_icon="AV", layout="wide")
apply_calm_theme()
render_bili_topbar("音视频分析")
render_auth_panel()

st.title("音视频上传转文字与情绪分析")
st.markdown(
    '<div class="gentle-note">适合分析语音日记、访谈片段或视频反馈。上传后会先转写为文字，再进行情绪识别。</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "上传音频或视频文件",
    type=["mp3", "wav", "m4a", "aac", "flac", "ogg", "mp4", "avi", "mov", "mkv", "webm", "mpeg4"],
)

video_suffixes = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".mpeg4"}

if uploaded_file and st.button("开始转写并分析"):
    temp_path = None
    audio_path = None
    suffix = Path(uploaded_file.name).suffix.lower()
    media_bytes = uploaded_file.getbuffer()

    try:
        if len(media_bytes) > MAX_MEDIA_BYTES:
            raise RuntimeError("文件过大，请上传 50MB 以内的音频/视频，或先截取一段较短片段再分析。")

        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(media_bytes)

        with st.spinner("正在处理文件..."):
            if suffix in video_suffixes:
                audio_path = extract_audio_from_video_isolated(temp_path, temp_path.parent)
            else:
                audio_path = temp_path

            transcript = transcribe_audio_isolated(audio_path)
            if not transcript:
                st.warning("没有识别到有效语音内容。")
            else:
                analyzer = EmotionAnalyzer()
                result = analyzer.analyze(transcript)
                reply = generate_reply(transcript, result.label)
                insight = extract_interview_insight(transcript)

                st.subheader("访谈观点提炼")
                st.markdown(f'<div class="gentle-note">{insight.summary}</div>', unsafe_allow_html=True)
                if insight.viewpoints:
                    st.markdown("**主要观点**")
                    for viewpoint in insight.viewpoints:
                        st.write(f"- {viewpoint}")
                if insight.keywords:
                    st.markdown("**关键词**")
                    st.write("、".join(insight.keywords[:8]))
                if insight.evidence:
                    with st.expander("查看观点依据"):
                        for sentence in insight.evidence:
                            st.write(f"- {sentence}")

                st.subheader("转写文本")
                st.write(transcript)

                st.subheader("情绪识别结果")
                cols = st.columns(3)
                cols[0].metric("情绪标签", result.label)
                cols[1].metric("情绪倾向", result.polarity)
                cols[2].metric("命中线索", result.reason)
                st.markdown(render_confidence_card(result.score), unsafe_allow_html=True)

                st.subheader("陪伴回应")
                st.markdown(f'<div class="gentle-note">{reply}</div>', unsafe_allow_html=True)

    except Exception as exc:
        st.error(str(exc))
        st.info("建议先上传 3-10 秒的 WAV/MP3 短音频测试；如果视频失败，请先把视频转成音频再上传。")
    finally:
        for path in {temp_path, audio_path}:
            try:
                if path and path.exists() and path != temp_path:
                    path.unlink()
            except OSError:
                pass
        try:
            if temp_path and temp_path.exists():
                temp_path.unlink()
        except OSError:
            pass
