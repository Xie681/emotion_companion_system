import pandas as pd
import streamlit as st

from modules.emotion_analyzer import EmotionAnalyzer
from modules.reply_generator import generate_reply
from modules.report_generator import build_chat_report
from modules.ui import apply_calm_theme
from modules.visualization import emotion_trend_chart


st.set_page_config(page_title="情绪聊天", page_icon="AI", layout="wide")
apply_calm_theme()
st.title("情绪聊天")
st.markdown('<div class="gentle-note">把想说的话先放在这里。系统会识别当前情绪，并给出一段温和的回应。</div>', unsafe_allow_html=True)

if "chat_records" not in st.session_state:
    st.session_state.chat_records = []

analyzer = EmotionAnalyzer()

with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_area("请输入你想说的话", height=140, placeholder="例如：我最近压力很大，感觉什么事情都做不好。")
    submitted = st.form_submit_button("发送并分析")

if submitted and user_text.strip():
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
        }
    )

for record in st.session_state.chat_records:
    st.markdown(
        f"""
        <div class="soft-panel" style="margin-top: 1rem;">
          <b>你</b>
          <p style="margin: .45rem 0 0;">{record["text"]}</p>
        </div>
        <div class="soft-panel" style="margin-top: .65rem; background: rgba(238, 246, 241, .92);">
          <b>情绪陪伴助手</b>
          <p style="margin: .45rem 0 0;">{record["reply"]}</p>
          <p style="margin: .55rem 0 0; color: #68766f; font-size: .9rem;">
            情绪：{record["emotion"]} | 置信度：{record["score"]} | {record["reason"]}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

col1, col2 = st.columns(2)
with col1:
    if st.button("清空对话"):
        st.session_state.chat_records = []
        st.rerun()
with col2:
    report = build_chat_report(st.session_state.chat_records)
    st.download_button("导出聊天报告 Markdown", report, "chat_emotion_report.md")

if st.session_state.chat_records:
    st.subheader("情绪趋势")
    fig = emotion_trend_chart(st.session_state.chat_records)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("对话记录")
    st.dataframe(pd.DataFrame(st.session_state.chat_records), use_container_width=True)
