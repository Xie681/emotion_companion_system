import pandas as pd
import streamlit as st

from modules.report_generator import build_chat_report
from modules.ui import apply_calm_theme
from modules.visualization import create_wordcloud_image, emotion_bar_chart, emotion_pie_chart, emotion_trend_chart


st.set_page_config(page_title="可视化报告", page_icon="AI", layout="wide")
apply_calm_theme()
st.title("可视化报告")
st.markdown('<div class="gentle-note">把聊天和批量分析结果汇总成更容易阅读的情绪报告。</div>', unsafe_allow_html=True)

chat_records = st.session_state.get("chat_records", [])
batch_result_df = st.session_state.get("batch_result_df")
text_column = st.session_state.get("batch_text_column")

tab1, tab2 = st.tabs(["聊天报告", "CSV 分析报告"])

with tab1:
    report = build_chat_report(chat_records)
    st.markdown(report)
    st.download_button("导出聊天报告 Markdown", report, "chat_emotion_report.md")

    if chat_records:
        fig = emotion_trend_chart(chat_records)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        image = create_wordcloud_image([record["text"] for record in chat_records])
        if image:
            st.image(image)

with tab2:
    if isinstance(batch_result_df, pd.DataFrame) and not batch_result_df.empty:
        st.plotly_chart(emotion_pie_chart(batch_result_df), use_container_width=True)
        st.plotly_chart(emotion_bar_chart(batch_result_df), use_container_width=True)
        if text_column:
            image = create_wordcloud_image(batch_result_df[text_column].astype(str).tolist())
            if image:
                st.image(image)
        csv_bytes = batch_result_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("导出完整 CSV 分析结果", csv_bytes, "all_emotion_results.csv", "text/csv")
    else:
        st.info("请先在 CSV 批量分析页面上传并分析数据。")
