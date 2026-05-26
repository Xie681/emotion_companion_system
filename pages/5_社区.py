from html import escape

import streamlit as st

from modules.auth import add_community_post, current_user, load_community_posts, render_auth_panel, rerun_app
from modules.ui import apply_calm_theme, render_bili_topbar


st.set_page_config(page_title="社区", page_icon="AI", layout="wide")
apply_calm_theme()
render_bili_topbar("社区")
render_auth_panel()

st.title("社区")
st.markdown('<div class="gentle-note">像动态广场一样记录此刻状态，也可以看看别人如何表达和调节情绪。</div>', unsafe_allow_html=True)

if not current_user():
    st.info("登录后发布内容会显示你的用户名；未登录时会以匿名用户发布。")

with st.form("community_post_form", clear_on_submit=True):
    content = st.text_area("发布动态", height=120, placeholder="写下今天的一个情绪瞬间，或者分享一个让自己好一点的小办法。")
    emotion = st.selectbox("情绪标签", ["日常", "开心", "焦虑", "低落", "愤怒", "求助", "经验分享"])
    submitted = st.form_submit_button("发布")

if submitted:
    if content.strip():
        add_community_post(content.strip(), emotion)
        st.success("已发布到社区。")
        rerun_app()
    else:
        st.warning("先写一点内容再发布。")

posts = load_community_posts()
st.subheader("社区动态")

if not posts:
    st.info("社区还没有动态，来发布第一条吧。")
else:
    for post in posts:
        st.markdown(
            (
                '<div class="community-post">'
                f'<b>{escape(post.get("username", "匿名用户"))}</b>'
                f'<div class="community-meta">{escape(post.get("emotion", "日常"))} · {escape(post.get("created_at", ""))}</div>'
                f'<p style="margin: .55rem 0 0; white-space: pre-wrap;">{escape(post.get("content", ""))}</p>'
                "</div>"
            ),
            unsafe_allow_html=True,
        )
