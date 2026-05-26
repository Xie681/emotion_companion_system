import pandas as pd
import streamlit as st

from modules.auth import current_user, persist_batch_result, render_auth_panel
from modules.batch_analyzer import analyze_dataframe
from modules.ui import apply_calm_theme, render_bili_topbar
from modules.visualization import create_wordcloud_image, emotion_bar_chart, emotion_pie_chart


st.set_page_config(page_title="CSV 批量分析", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("CSV批量分析")
render_auth_panel()
st.title("CSV 批量情感分析")
st.markdown('<div class="gentle-note">上传评论、问卷或反馈数据，选择文本列后即可批量标注情绪。</div>', unsafe_allow_html=True)
if not current_user():
    st.info("登录后，CSV 分析结果会自动保存到当前账号。")

uploaded_csv = st.file_uploader("上传 CSV 文件", type=["csv"])

if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    st.subheader("原始数据预览")
    st.dataframe(df.head(20), use_container_width=True)

    text_column = st.selectbox("选择文本列", df.columns)
    if st.button("开始批量分析"):
        with st.spinner("正在分析 CSV..."):
            result_df = analyze_dataframe(df, text_column)
            st.session_state.batch_result_df = result_df
            st.session_state.batch_text_column = text_column
            persist_batch_result(result_df, text_column)

if "batch_result_df" in st.session_state:
    result_df = st.session_state.batch_result_df
    text_column = st.session_state.get("batch_text_column", result_df.columns[0])

    st.subheader("筛选结果")
    emotions = ["全部"] + sorted(result_df["emotion_label"].unique().tolist())
    selected_emotion = st.selectbox("按情绪筛选", emotions)
    keyword = st.text_input("关键词搜索")

    filtered = result_df.copy()
    if selected_emotion != "全部":
        filtered = filtered[filtered["emotion_label"] == selected_emotion]
    if keyword:
        filtered = filtered[filtered[text_column].astype(str).str.contains(keyword, na=False)]

    filtered = filtered.sort_values("emotion_score", ascending=False)
    st.dataframe(filtered, use_container_width=True)

    csv_bytes = filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("导出筛选结果 CSV", csv_bytes, "emotion_results.csv", "text/csv")

    if not filtered.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(emotion_pie_chart(filtered), use_container_width=True)
        with col2:
            st.plotly_chart(emotion_bar_chart(filtered), use_container_width=True)

        st.subheader("关键词词云")
        image = create_wordcloud_image(filtered[text_column].astype(str).tolist())
        if image:
            st.image(image)
            st.download_button("导出词云 PNG", image.getvalue(), "wordcloud.png", "image/png")
        else:
            st.info("当前筛选结果没有足够文本生成词云。")
    else:
        st.warning("当前筛选条件下没有结果。")
