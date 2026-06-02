import streamlit as st

from modules.auth import render_auth_panel
from modules.hospital_resources import default_hospital_resources, search_hospital_resources
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

st.subheader("心理咨询资源查询")
st.markdown(
    """
    <div class="gentle-note">
      输入地区、城市或医院名称，查询部分地区第一医院/综合医院的心理咨询相关联系方式。
      若出现强烈危机或自伤风险，请优先联系身边可信任的人或当地紧急救助服务。
    </div>
    """,
    unsafe_allow_html=True,
)
resource_keyword = st.text_input(
    "搜索地区、医院、简称或别名",
    placeholder="例如：广西壮族自治区、广西医科大学第一附属医院、医科大附属医院、桂、南宁",
)
resources = search_hospital_resources(resource_keyword) if resource_keyword.strip() else default_hospital_resources(5)
if resources:
    if resource_keyword.strip():
        st.markdown(
            '<div class="resource-hint">以下联系方式用于课程系统演示和查询引导，电话、邮箱、门诊安排请以医院官网或官方公众号最新信息为准。</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="resource-hint">默认展示5条重点查询地区示例，不代表地区风险排名。需要其他地区时，请在上方输入省份、城市、简称或医院名称搜索。</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="resource-grid">', unsafe_allow_html=True)
    for item in resources:
        st.markdown(
            f"""
            <div class="resource-card">
              <b>{item["region"]} · {item["hospital"]}</b>
              <span>咨询方向：{item["department"]}</span>
              <span>电话：{item["phone"]}</span>
              <span>邮箱：{item["email"]}</span>
              <span>地址：{item["address"]}</span>
              <span>官网来源：<a href="{item["source_url"]}" target="_blank">{item["source_url"]}</a></span>
              <span>{item["notice"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("暂未找到匹配地区。可以尝试输入城市名、省份名或医院名称。")

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
