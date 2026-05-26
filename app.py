import streamlit as st

from modules.ui import apply_calm_theme, render_feature_cards, render_home_hero


st.set_page_config(
    page_title="情绪陪伴与情感分析系统",
    page_icon="AI",
    layout="wide",
)
apply_calm_theme()

render_home_hero()
render_feature_cards()

st.markdown(
    """
    <div class="soft-panel" style="margin-top: 1.4rem;">
      <h3 style="margin-top:0;">项目定位</h3>
      <p>
        这是一个课程大作业级别的原型系统。默认使用本地规则词典完成情绪识别，
        方便离线运行和课堂展示；后续也可以把分析器替换为 Whisper、Hugging Face
        中文情绪分类模型或大模型 API。
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info("请从左侧页面导航选择功能。")
