import streamlit as st

from modules.auth import current_user, load_user_profile, render_auth_panel
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
username = current_user()
if username:
    profile = load_user_profile(username)
    chat_records = profile.get("chat_records", [])
    reports = profile.get("reports", [])
    batch_rows = profile.get("batch_result_rows", [])

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

    if reports:
        st.subheader("最近保存的报告")
        for index, report in enumerate(reports[:3], start=1):
            with st.expander(f'{index}. {report.get("title", "报告")} · {report.get("created_at", "")}'):
                st.markdown(report.get("content", ""))
else:
    st.info("登录后，主页会显示你的聊天记录、保存报告和 CSV 分析数据。")
