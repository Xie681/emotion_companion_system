from datetime import datetime
import hashlib
from html import escape
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import streamlit as st

from modules.auth import (
    archive_current_chat,
    assistant_name,
    current_user,
    persist_chat_records,
    persist_report,
    render_auth_panel,
    rerun_app,
    search_chat_records,
    update_assistant_name,
)
from modules.emotion_analyzer import EmotionAnalyzer
from modules.reply_generator import generate_reply_with_source
from modules.report_generator import build_chat_report
from modules.speech_to_text import transcribe_audio
from modules.ui import apply_calm_theme, confidence_hint, render_bili_topbar
from modules.visualization import emotion_trend_chart


st.set_page_config(page_title="AI陪伴聊天", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("AI陪伴聊天")
render_auth_panel()

st.title("AI陪伴聊天")
st.markdown(
    '<div class="gentle-note">像日常聊天一样发送想说的话。系统会识别情绪，并把对话保存在已登录账号中。</div>',
    unsafe_allow_html=True,
)

current_assistant_name = assistant_name()
analyzer = EmotionAnalyzer()

if "chat_records" not in st.session_state:
    st.session_state.chat_records = []

if not current_user():
    st.info("登录后可以自动保存对话和报告；未登录时仍可临时体验。")

name_col, save_name_col = st.columns([4, 1])
with name_col:
    edited_assistant_name = st.text_input(
        "AI助手命名",
        value=current_assistant_name,
        help="修改后，后续聊天和社区中的 AI 回复都会沿用这个名字。",
    )
with save_name_col:
    st.write("")
    if st.button("保存命名"):
        update_assistant_name(edited_assistant_name)
        st.success("AI助手命名已保存。")
        rerun_app()
current_assistant_name = assistant_name()


def add_chat_message(message_text: str, source: str = "text") -> None:
    message_text = message_text.strip()
    if not message_text:
        return

    result = analyzer.analyze(message_text)
    reply, reply_source = generate_reply_with_source(message_text, result.label, st.session_state.chat_records)
    st.session_state.chat_records.append(
        {
            "text": message_text,
            "emotion": result.label,
            "score": result.score,
            "polarity": result.polarity,
            "reason": result.reason,
            "reply": reply,
            "reply_source": reply_source,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
        }
    )
    persist_chat_records(st.session_state.chat_records)


def transcribe_uploaded_audio(uploaded_audio) -> str:
    suffix = Path(getattr(uploaded_audio, "name", "voice.wav")).suffix.lower() or ".wav"
    temp_path = None
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(uploaded_audio.getvalue())
        return transcribe_audio(temp_path)
    finally:
        try:
            if temp_path and temp_path.exists():
                temp_path.unlink()
        except OSError:
            pass


tool_col1, tool_col2 = st.columns(2)
with tool_col1:
    if st.button("开启新聊天"):
        if current_user():
            archived = archive_current_chat()
            st.success("已开启新聊天。" if archived else "当前没有可归档的聊天。")
        else:
            st.session_state.chat_records = []
            st.success("已开启新聊天。")
        rerun_app()
with tool_col2:
    search_keyword = st.text_input("查找聊天记录", placeholder="输入关键词、情绪或回复内容")

if current_user() and search_keyword.strip():
    search_results = search_chat_records(search_keyword)
    st.subheader("查找结果")
    if search_results:
        st.dataframe(search_results, use_container_width=True, hide_index=True)
    else:
        st.info("没有找到匹配的聊天记录。")
elif search_keyword.strip():
    st.info("登录后可以查找已保存的聊天记录。")

chat_html = ['<div class="chat-shell">']
if not st.session_state.chat_records:
    chat_html.append(
        '<div class="chat-row assistant">'
        '<div class="chat-bubble">'
        f'<div class="chat-name">{escape(current_assistant_name)}</div>'
        '<div class="chat-text">你好，我在这里。你可以先发一句现在最想说的话。</div>'
        "</div>"
        "</div>"
    )
else:
    for record in st.session_state.chat_records:
        chat_html.append(
            '<div class="chat-row user">'
            '<div class="chat-bubble">'
            '<div class="chat-name">你</div>'
            f'<div class="chat-text">{escape(record["text"])}</div>'
            "</div>"
            "</div>"
            '<div class="chat-row assistant">'
            '<div class="chat-bubble">'
            f'<div class="chat-name">{escape(current_assistant_name)}</div>'
            f'<div class="chat-text">{escape(record["reply"])}</div>'
            f'<div class="chat-meta">情绪：{escape(record["emotion"])} | {confidence_hint(record["score"])} | {escape(record["reason"])} | 回复来源：{escape(record.get("reply_source", "历史记录"))}</div>'
            '<div class="confidence-note">置信度表示系统对当前情绪标签判断的可靠程度，数值越接近 1 越可靠。</div>'
            "</div>"
            "</div>"
        )
chat_html.append("</div>")
st.markdown("\n".join(chat_html), unsafe_allow_html=True)

input_col, mic_col = st.columns([9, 2])
with input_col:
    with st.form("chat_form", clear_on_submit=True):
        user_text = st.text_input(
            "发送消息",
            placeholder="例如：我最近压力很大，感觉什么事情都做不好。",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("发送")

with mic_col:
    audio_input = getattr(st, "audio_input", None)
    if audio_input:
        uploaded_voice = audio_input("点击说话", label_visibility="collapsed", key="voice_chat_audio")
    else:
        st.markdown('<div class="mic-trigger" title="语音输入">🎙️</div>', unsafe_allow_html=True)
        uploaded_voice = st.file_uploader(
            "语音输入",
            type=["mp3", "wav", "m4a", "aac", "flac", "ogg"],
            label_visibility="collapsed",
            key="voice_chat_file",
        )

if submitted:
    if user_text.strip():
        with st.spinner("正在生成回复..."):
            add_chat_message(user_text, "text")
        rerun_app()
    else:
        st.warning("请输入文字，或点击麦克风入口说话。")

if uploaded_voice:
    voice_bytes = uploaded_voice.getvalue()
    voice_hash = hashlib.sha256(voice_bytes).hexdigest()
    if st.session_state.get("last_voice_hash") != voice_hash:
        st.session_state.last_voice_hash = voice_hash
        try:
            with st.spinner("正在识别语音并生成回复..."):
                voice_text = transcribe_uploaded_audio(uploaded_voice)
                if voice_text:
                    add_chat_message(voice_text, "voice")
                    rerun_app()
                else:
                    st.warning("没有识别到有效语音内容。")
        except Exception as exc:
            st.error(str(exc))
            st.info("如果当前版本没有浏览器录音能力，请使用麦克风旁的语音文件上传，或升级到支持 st.audio_input 的 Streamlit。")

col1, col2 = st.columns(2)
with col1:
    if st.button("清空对话"):
        st.session_state.chat_records = []
        persist_chat_records(st.session_state.chat_records)
        rerun_app()
with col2:
    report = build_chat_report(st.session_state.chat_records)
    st.download_button("导出聊天报告 Markdown", report, "chat_emotion_report.md")

if st.session_state.chat_records:
    if st.button("保存聊天报告到当前账号"):
        if current_user():
            persist_report("聊天报告", build_chat_report(st.session_state.chat_records))
            st.success("已保存到当前账号。")
        else:
            st.warning("请先登录后再保存报告。")

    st.subheader("情绪趋势")
    fig = emotion_trend_chart(st.session_state.chat_records)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("对话记录")
    st.dataframe(pd.DataFrame(st.session_state.chat_records), use_container_width=True)
