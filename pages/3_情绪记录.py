from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.auth import current_user, load_user_profile, render_auth_panel
from modules.ui import apply_calm_theme, render_bili_topbar


st.set_page_config(page_title="情绪记录", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("情绪记录")
render_auth_panel()

st.title("情绪记录")
st.markdown('<div class="gentle-note">集中查看历史输入内容、识别出的情绪、AI 回复摘要和时间，并用图表观察变化。</div>', unsafe_allow_html=True)

username = current_user()
if not username:
    st.info("请先登录，登录后这里会展示你的个人情绪记录。")
    st.stop()

records = load_user_profile(username).get("chat_records", [])
if not records:
    st.info("暂无情绪记录。请先在情绪分析或 AI 陪伴聊天页面输入内容。")
    st.stop()

df = pd.DataFrame(records)

st.subheader("历史记录表")
rows = []
for record in reversed(records):
    reply = str(record.get("reply", ""))
    rows.append(
        {
            "时间": record.get("created_at", "未记录时间"),
            "历史输入内容": record.get("text", ""),
            "识别出的情绪": record.get("emotion", "未知"),
            "AI回复摘要": reply[:60] + ("..." if len(reply) > 60 else ""),
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.subheader("情绪分类统计")
polarity_map = {"positive": "积极", "neutral": "中性", "negative": "消极"}
df["情绪倾向"] = df.get("polarity", pd.Series(["neutral"] * len(df))).map(polarity_map).fillna("中性")
counts = df["情绪倾向"].value_counts().reset_index()
counts.columns = ["情绪倾向", "数量"]
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.pie(counts, names="情绪倾向", values="数量", hole=0.38), use_container_width=True)
with col2:
    label_counts = df["emotion"].value_counts().reset_index()
    label_counts.columns = ["情绪标签", "数量"]
    st.plotly_chart(px.bar(label_counts, x="情绪标签", y="数量"), use_container_width=True)

st.subheader("情绪趋势图")
recent_df = df.tail(7).copy()
recent_df["轮次"] = range(max(1, len(df) - len(recent_df) + 1), len(df) + 1)
recent_df["置信度"] = recent_df["score"]
recent_df["情绪类型"] = recent_df["emotion"]
st.plotly_chart(px.line(recent_df, x="轮次", y="置信度", color="情绪类型", markers=True), use_container_width=True)

st.subheader("每日情绪趋势")
trend_df = df.copy()
if "created_at" not in trend_df.columns:
    trend_df["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
trend_df["日期"] = pd.to_datetime(trend_df["created_at"], errors="coerce").dt.date
trend_df["日期"] = trend_df["日期"].fillna(datetime.now().date())
daily_df = trend_df.groupby(["日期", "emotion"]).size().reset_index(name="次数")
st.plotly_chart(px.bar(daily_df, x="日期", y="次数", color="emotion", barmode="group"), use_container_width=True)
