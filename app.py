from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.auth import current_user, load_user_profile, render_auth_controls, render_auth_panel
from modules.ui import apply_calm_theme, render_bili_topbar, render_feature_cards, render_home_hero


st.set_page_config(
    page_title="情绪陪伴与情感分析系统",
    page_icon="AI",
    layout="wide",
)
apply_calm_theme()
render_bili_topbar("主页")
render_auth_panel()

render_home_hero()
render_feature_cards()

st.subheader("我的主页")

with st.container():
    st.markdown('<div class="soft-panel" style="margin-top: 1rem;">', unsafe_allow_html=True)
    render_auth_controls("home_auth", show_title=True)
    st.markdown("</div>", unsafe_allow_html=True)

username = current_user()
if username:
    profile = load_user_profile(username)
    chat_records = profile.get("chat_records", [])
    reports = profile.get("reports", [])
    batch_rows = profile.get("batch_result_rows", [])
    chat_df = pd.DataFrame(chat_records)

    st.markdown(
        (
            '<div class="record-grid">'
            f'<div class="record-card"><b>对话记录</b><span>已保存 {len(chat_records)} 轮情绪聊天。最近一次：{chat_records[-1].get("emotion", "暂无") if chat_records else "暂无"}</span></div>'
            f'<div class="record-card"><b>保存报告</b><span>已保存 {len(reports)} 份报告。可以在可视化报告页继续查看。</span></div>'
            f'<div class="record-card"><b>CSV 数据</b><span>已保存 {len(batch_rows)} 条批量分析结果。</span></div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    st.subheader("个人情绪记录")
    if chat_records:
        recent_df = chat_df.tail(7).copy()
        recent_df["轮次"] = range(max(1, len(chat_df) - len(recent_df) + 1), len(chat_df) + 1)
        recent_df["情绪类型"] = recent_df["emotion"]
        recent_df["置信度"] = recent_df["score"]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 近7次情绪变化")
            fig = px.line(recent_df, x="轮次", y="置信度", color="情绪类型", markers=True)
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("#### 积极 / 中性 / 消极占比")
            polarity_map = {"positive": "积极", "neutral": "中性", "negative": "消极"}
            pie_df = chat_df.copy()
            pie_df["情绪倾向"] = pie_df["polarity"].map(polarity_map).fillna("中性")
            counts = pie_df["情绪倾向"].value_counts().reset_index()
            counts.columns = ["情绪倾向", "数量"]
            fig = px.pie(counts, names="情绪倾向", values="数量", hole=0.38)
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 每日情绪趋势")
        trend_df = chat_df.copy()
        if "created_at" not in trend_df.columns:
            trend_df["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trend_df["日期"] = pd.to_datetime(trend_df["created_at"], errors="coerce").dt.date
        trend_df["日期"] = trend_df["日期"].fillna(datetime.now().date())
        daily_df = trend_df.groupby(["日期", "emotion"]).size().reset_index(name="次数")
        fig = px.bar(daily_df, x="日期", y="次数", color="emotion", barmode="group")
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10), xaxis_title="", yaxis_title="记录次数")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("历史对话")
        for index, record in enumerate(reversed(chat_records[-8:]), start=1):
            with st.expander(f'{index}. {record.get("emotion", "未知")} · {record.get("created_at", "未记录时间")}'):
                st.write(f'你：{record.get("text", "")}')
                st.write(f'助手：{record.get("reply", "")}')

        main_emotion = chat_df["emotion"].mode().iloc[0]
        suggestions = {
            "积极": "最近积极状态较多，可以把带来好心情的事件记录下来，作为之后恢复能量的参考。",
            "中性": "近期状态比较平稳，可以继续补充更多具体事件，让系统更准确地识别变化。",
            "悲伤": "如果低落持续出现，建议先降低自我要求，并找一个可信任的人聊聊近况。",
            "焦虑": "焦虑出现较多时，可以把任务拆成今天能完成的一小步，先恢复一点掌控感。",
            "愤怒": "愤怒状态下先暂停回应，等情绪降温后再整理自己真正想表达的诉求。",
            "消极": "如果无力感比较明显，可以从一个很小、确定能完成的动作开始，不急着一次解决全部问题。",
        }
        st.subheader("个性化建议")
        st.markdown(f'<div class="gentle-note">{suggestions.get(main_emotion, suggestions["中性"])}</div>', unsafe_allow_html=True)
    else:
        st.info("还没有个人情绪记录。去情绪聊天页发送第一句话后，这里会生成趋势图和建议。")

    if reports:
        st.subheader("最近保存的报告")
        for index, report in enumerate(reports[:3], start=1):
            with st.expander(f'{index}. {report.get("title", "报告")} · {report.get("created_at", "")}'):
                st.markdown(report.get("content", ""))
else:
    st.info("登录后，主页会显示你的聊天记录、保存报告和 CSV 分析数据。")
