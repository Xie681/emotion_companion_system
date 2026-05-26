import streamlit as st

from modules.auth import render_auth_panel
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

st.subheader("系统简介")
st.markdown(
    """
    <div class="soft-panel">
      本系统面向有情绪倾诉、压力释放和情感分析需求的用户，提供文本情绪分析、AI 陪伴聊天、
      情绪记录可视化、社区互助和报告导出能力，帮助用户形成持续记录、理解和调节情绪的闭环。
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("功能入口卡片")
render_feature_cards()

st.subheader("使用流程说明")
st.markdown(
    """
    <div class="record-grid">
      <div class="record-card"><b>1. 登录账号</b><span>注册或登录后，系统会保存你的对话、情绪记录和报告。</span></div>
      <div class="record-card"><b>2. 输入内容</b><span>在情绪分析或 AI 陪伴聊天页面输入当前想表达的内容。</span></div>
      <div class="record-card"><b>3. 查看结果</b><span>系统展示情绪标签、置信度、解释和温和建议。</span></div>
      <div class="record-card"><b>4. 追踪变化</b><span>在情绪记录页面查看历史记录、分类统计和趋势图。</span></div>
      <div class="record-card"><b>5. 生成报告</b><span>在可视化报告页面导出或保存分析报告。</span></div>
      <div class="record-card"><b>6. 社区互助</b><span>在社区匿名倾诉，获得 AI 回应和同伴支持。</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)
