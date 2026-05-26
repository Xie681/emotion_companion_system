from html import escape

import streamlit as st

from modules.auth import (
    add_community_comment,
    add_community_post,
    current_user,
    load_community_posts,
    render_auth_panel,
    rerun_app,
    set_community_status,
    update_community_support,
)
from modules.community_moderation import analyze_community_post, generate_community_reply
from modules.ui import apply_calm_theme, render_bili_topbar


SECTIONS = ["树洞倾诉区", "压力互助区", "学习焦虑区", "睡眠与疲惫区", "今日开心小事", "经验分享区"]
EMOTIONS = ["焦虑", "难过", "压力", "孤独", "生气", "迷茫", "开心", "需要鼓励"]
QUICK_REPLIES = ["抱抱你", "我也有过类似感受", "你已经很努力了", "希望你今天能轻松一点"]


st.set_page_config(page_title="社区", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("社区")
render_auth_panel()

st.title("情绪陪伴社区")
st.markdown(
    '<div class="gentle-note">情绪社区提供匿名倾诉、AI 辅助识别、同伴支持和安全审核，形成“用户倾诉—AI辅助—同伴支持—安全管理”的闭环。</div>',
    unsafe_allow_html=True,
)

if not current_user():
    st.info("未登录也可以匿名浏览；登录后可发布内容、评论和保存个人身份设置。")

with st.form("community_post_form", clear_on_submit=True):
    title = st.text_input("标题", placeholder="例如：最近学习压力很大")
    content = st.text_area("正文", height=140, placeholder="写下今天的一个情绪瞬间，或分享一个让自己好一点的小办法。")
    col1, col2, col3 = st.columns(3)
    with col1:
        section = st.selectbox("情绪分区", SECTIONS)
    with col2:
        emotion = st.selectbox("情绪标签", EMOTIONS)
    with col3:
        is_anonymous = st.checkbox("匿名发布", value=True)
    submitted = st.form_submit_button("发布")

if submitted:
    if title.strip() and content.strip():
        analysis = analyze_community_post(title.strip(), content.strip(), emotion, current_user() or "")
        ai_reply = generate_community_reply(analysis)
        add_community_post(title.strip(), content.strip(), section, emotion, is_anonymous, analysis, ai_reply)
        if analysis.get("risk_level") == "高":
            st.warning("已发布到待审核列表。系统检测到高风险表达，请优先联系现实中的可信任支持。")
        else:
            st.success("已发布到社区。")
        rerun_app()
    else:
        st.warning("请填写标题和正文。")

posts = load_community_posts()

st.subheader("情绪分区")
selected_section = st.selectbox("选择分区", ["全部"] + SECTIONS)
visible_posts = [post for post in posts if selected_section == "全部" or post.get("section") == selected_section]

st.subheader("社区动态")
if not visible_posts:
    st.info("当前分区还没有动态。")

for post in visible_posts:
    status = post.get("status", "已发布")
    risk_level = post.get("risk_level", "低")
    if status == "已隐藏":
        continue

    title = post.get("title") or "情绪动态"
    display_name = post.get("display_name") or post.get("username", "匿名用户")
    tags = " ".join(post.get("ai_tags", []))
    supports = post.get("supports", {"拥抱": 0, "陪伴": 0, "鼓励": 0})
    comments = post.get("comments", [])

    st.markdown(
        (
            '<div class="community-post">'
            f'<b>{escape(title)}</b>'
            f'<div class="community-meta">{escape(display_name)} · {escape(post.get("section", "树洞倾诉区"))} · {escape(post.get("created_at", ""))}</div>'
            f'<div class="community-meta">情绪倾向：{escape(post.get("emotion_tendency", "中性"))} · 风险等级：{escape(risk_level)} · {escape(tags)}</div>'
            f'<p style="margin: .65rem 0 0; white-space: pre-wrap;">{escape(post.get("content", ""))}</p>'
            f'<div class="gentle-note" style="margin-top:.75rem;"><b>AI温和回应：</b>{escape(post.get("ai_reply", ""))}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if risk_level == "高":
        st.warning("系统检测到高风险表达：建议联系可信任的人或当地紧急服务。管理员可在下方审核。")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"🤗 拥抱 {supports.get('拥抱', 0)}", key=f"hug_{post.get('id')}"):
            update_community_support(post.get("id"), "拥抱")
            rerun_app()
    with col2:
        if st.button(f"🌙 陪伴 {supports.get('陪伴', 0)}", key=f"stay_{post.get('id')}"):
            update_community_support(post.get("id"), "陪伴")
            rerun_app()
    with col3:
        if st.button(f"🌱 鼓励 {supports.get('鼓励', 0)}", key=f"encourage_{post.get('id')}"):
            update_community_support(post.get("id"), "鼓励")
            rerun_app()

    with st.expander("评论与支持"):
        st.caption("请用温和、尊重、支持的方式回复对方。")
        quick = st.selectbox("快捷回复", [""] + QUICK_REPLIES, key=f"quick_{post.get('id')}")
        comment = st.text_input("写评论", key=f"comment_{post.get('id')}")
        if st.button("发送评论", key=f"send_comment_{post.get('id')}"):
            if comment.strip() or quick:
                add_community_comment(post.get("id"), comment.strip(), quick)
                rerun_app()
        for item in comments[-5:]:
            st.markdown(f'- **{escape(item.get("username", "匿名用户"))}**：{escape(item.get("content", ""))}')

    if current_user():
        with st.expander("管理员审核"):
            st.caption(post.get("risk_reason", ""))
            col1, col2 = st.columns(2)
            with col1:
                if st.button("标记为已发布", key=f"publish_{post.get('id')}"):
                    set_community_status(post.get("id"), "已发布")
                    rerun_app()
            with col2:
                if st.button("隐藏内容", key=f"hide_{post.get('id')}"):
                    set_community_status(post.get("id"), "已隐藏")
                    rerun_app()
