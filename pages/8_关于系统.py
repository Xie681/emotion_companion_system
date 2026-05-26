import streamlit as st

from modules.auth import render_auth_panel
from modules.ui import apply_calm_theme, render_bili_topbar


st.set_page_config(page_title="关于系统", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("关于系统")
render_auth_panel()

st.title("关于系统")

st.subheader("项目背景")
st.markdown(
    """
    <div class="soft-panel">
      随着学习、工作和生活压力增加，用户常常需要一个低压力、可持续的情绪表达空间。
      本项目希望通过自然语言处理和可视化技术，把情绪倾诉、AI 陪伴、历史记录和社区互助整合成一个轻量平台。
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("技术框架")
st.markdown(
    """
    <div class="soft-panel">
      <ul>
        <li>前端框架：Streamlit</li>
        <li>情绪识别：本地规则词典与关键词匹配，可扩展 Hugging Face 中文情绪模型</li>
        <li>AI 回复：本地模板兜底，可接入通义千问 API</li>
        <li>音视频处理：预留 Whisper / faster-whisper 转写能力</li>
        <li>数据可视化：Plotly、词云与表格展示</li>
        <li>数据存储：本地 JSON 文件保存用户资料、聊天记录、报告和社区内容</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("功能说明")
st.markdown(
    """
    <div class="soft-panel">
      <ul>
        <li>情绪分析：输入文本，展示识别结果、解释和建议内容。</li>
        <li>AI 陪伴聊天：以对话方式持续交流，保存聊天记录。</li>
        <li>情绪记录：查看历史记录表、情绪分类统计和趋势图。</li>
        <li>可视化报告：生成聊天和 CSV 分析报告。</li>
        <li>情绪社区：支持匿名倾诉、AI 风险识别、AI 温和回应、同伴支持和管理员审核。</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("注意事项")
st.markdown(
    """
    <div class="gentle-note">
      本系统仅用于课程展示、情绪记录和辅助分析，不能替代专业心理咨询、医学诊断或治疗。
      如果出现持续强烈痛苦、自伤想法或紧急风险，请及时联系可信任的人、学校老师、专业机构或当地紧急服务。
    </div>
    """,
    unsafe_allow_html=True,
)
