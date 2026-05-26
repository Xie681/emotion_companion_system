from html import escape
from datetime import datetime

import pandas as pd
import streamlit as st

from modules.auth import current_user, persist_chat_records, persist_report, render_auth_panel, rerun_app
from modules.emotion_analyzer import EmotionAnalyzer
from modules.reply_generator import generate_reply
from modules.report_generator import build_chat_report
from modules.ui import apply_calm_theme, confidence_hint, render_bili_topbar
from modules.visualization import emotion_trend_chart


st.set_page_config(page_title="AI陪伴聊天", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("AI陪伴聊天")
render_auth_panel()
st.title("AI陪伴聊天")
st.markdown('<div class="gentle-note">像日常聊天一样发送想说的话。系统会识别情绪，并把对话保存在已登录账号中。</div>', unsafe_allow_html=True)

if "chat_records" not in st.session_state:
    st.session_state.chat_records = []

analyzer = EmotionAnalyzer()

if not current_user():
    st.info("登录后可以自动保存对话和报告；未登录时仍可临时体验。")

chat_html = ['<div class="chat-shell">']
if not st.session_state.chat_records:
    chat_html.append(
        '<div class="chat-row assistant">'
        '<div class="chat-bubble">'
        '<div class="chat-name">情绪陪伴助手</div>'
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
            '<div class="chat-name">情绪陪伴助手</div>'
            f'<div class="chat-text">{escape(record["reply"])}</div>'
            f'<div class="chat-meta">情绪：{escape(record["emotion"])} | {confidence_hint(record["score"])} | {escape(record["reason"])}</div>'
            "</div>"
            "</div>"
        )
chat_html.append("</div>")
st.markdown("\n".join(chat_html), unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_input("发送消息", placeholder="例如：我最近压力很大，感觉什么事情都做不好。", label_visibility="collapsed")
    submitted = st.form_submit_button("发送")

if submitted and user_text.strip():
    with st.spinner("正在生成回复..."):
        result = analyzer.analyze(user_text)
        reply = generate_reply(user_text, result.label, st.session_state.chat_records)

    st.session_state.chat_records.append(
        {
            "text": user_text,
            "emotion": result.label,
            "score": result.score,
            "polarity": result.polarity,
            "reason": result.reason,
            "reply": reply,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    persist_chat_records(st.session_state.chat_records)
    rerun_app()

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
