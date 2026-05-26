import streamlit as st

from modules.auth import render_auth_panel
from modules.ui import apply_calm_theme, render_bili_topbar


st.set_page_config(page_title="关于系统", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("关于系统")
render_auth_panel()

st.title("关于系统")

st.markdown(
    """
    <div class="soft-panel">
      <h3 style="margin-top:0;">系统名称</h3>
      <p>基于 NLP 的多模态情绪陪伴与情感分析系统</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="soft-panel" style="margin-top:1rem;">
      <h3 style="margin-top:0;">开发目的</h3>
      <p>
        本系统面向课程实践和情绪数据分析场景，帮助用户通过文字、音频、视频和 CSV 数据记录情绪状态，
        识别情绪变化，并获得温和、可执行的陪伴式反馈。
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="soft-panel" style="margin-top:1rem;">
      <h3 style="margin-top:0;">核心功能</h3>
      <ul>
        <li>情绪聊天：识别用户输入文本的情绪标签、置信度和关键词原因，并生成陪伴回复。</li>
        <li>音视频分析：上传音频或视频后转写文本，再完成情绪分析。</li>
        <li>CSV 批量分析：对评论、问卷、反馈等文本数据进行批量情绪标注。</li>
        <li>可视化报告：展示情绪分布、趋势图、词云和可保存的分析报告。</li>
        <li>用户主页：保存用户对话、报告和个人情绪趋势。</li>
        <li>社区：发布情绪动态，浏览社区分享。</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="soft-panel" style="margin-top:1rem;">
      <h3 style="margin-top:0;">技术路线</h3>
      <p>
        前端界面基于 Streamlit 构建；情绪识别默认采用本地规则词典和关键词匹配，便于离线运行和课堂展示；
        回复生成可接入通义千问 API；音视频转写预留 Whisper / faster-whisper 后端；图表使用 Plotly 和词云组件生成。
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="soft-panel" style="margin-top:1rem;">
      <h3 style="margin-top:0;">使用说明</h3>
      <ul>
        <li>先在侧边栏或主页登录/注册账号，以便保存个人数据。</li>
        <li>在情绪聊天页面输入一句话，即可获得情绪分析和回复。</li>
        <li>在 CSV 批量分析页面上传文件并选择文本列，可生成批量分析结果。</li>
        <li>在可视化报告页面保存报告，之后可在主页查看。</li>
        <li>新增社区动态后，需要保持本地数据文件存在，才能继续查看历史发布内容。</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="gentle-note" style="margin-top:1rem;">
      <b>注意事项：</b>本系统仅用于学习展示、情绪记录和辅助分析，不能替代专业心理咨询、医学诊断或治疗。
      如果出现持续强烈痛苦、自伤想法或紧急风险，请及时联系可信任的人、学校老师、专业机构或当地紧急服务。
    </div>
    """,
    unsafe_allow_html=True,
)
