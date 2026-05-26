from datetime import datetime

import streamlit as st

from modules.auth import current_user, persist_chat_records, render_auth_panel
from modules.emotion_analyzer import EmotionAnalyzer
from modules.reply_generator import generate_reply
from modules.ui import apply_calm_theme, render_bili_topbar, render_confidence_card


st.set_page_config(page_title="情绪分析", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("情绪分析")
render_auth_panel()

st.title("情绪分析")
st.markdown('<div class="gentle-note">输入一段文本，系统会给出情绪识别结果、解释和建议内容。</div>', unsafe_allow_html=True)

text = st.text_area("输入文本", height=150, placeholder="例如：我最近压力很大，感觉事情都做不好。")

if st.button("开始分析") and text.strip():
    analyzer = EmotionAnalyzer()
    result = analyzer.analyze(text)
    suggestion = generate_reply(text, result.label, st.session_state.get("chat_records", []))

    st.subheader("情绪识别结果")
    col1, col2 = st.columns(2)
    col1.metric("情绪标签", result.label)
    col2.markdown(render_confidence_card(result.score), unsafe_allow_html=True)

    st.subheader("情绪解释")
    st.markdown(f'<div class="soft-panel">{result.reason}</div>', unsafe_allow_html=True)

    st.subheader("建议内容")
    st.markdown(f'<div class="gentle-note">{suggestion}</div>', unsafe_allow_html=True)

    if current_user():
        records = st.session_state.get("chat_records", [])
        records.append(
            {
                "text": text,
                "emotion": result.label,
                "score": result.score,
                "polarity": result.polarity,
                "reason": result.reason,
                "reply": suggestion,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        st.session_state.chat_records = records
        persist_chat_records(records)
        st.success("已保存到情绪记录。")
