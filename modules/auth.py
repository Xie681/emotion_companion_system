import base64
import hashlib
import json
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pandas as pd
import streamlit as st


DATA_DIR = Path("data")
USER_STORE = DATA_DIR / "users.json"
USER_DATA_DIR = DATA_DIR / "user_data"
COMMUNITY_STORE = DATA_DIR / "community_posts.json"


def _ensure_storage() -> None:
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not USER_STORE.exists():
        USER_STORE.write_text("{}", encoding="utf-8")
    if not COMMUNITY_STORE.exists():
        COMMUNITY_STORE.write_text("[]", encoding="utf-8")


def _load_users() -> Dict[str, Dict[str, str]]:
    _ensure_storage()
    return json.loads(USER_STORE.read_text(encoding="utf-8") or "{}")


def _save_users(users: Dict[str, Dict[str, str]]) -> None:
    _ensure_storage()
    USER_STORE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def _hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120000)
    return {"salt": salt, "password_hash": digest.hex()}


def _verify_password(password: str, user: Dict[str, str]) -> bool:
    password_hash = _hash_password(password, user["salt"])["password_hash"]
    return secrets.compare_digest(password_hash, user["password_hash"])


def _safe_username(username: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]", "_", username.strip())
    return cleaned[:40] or "user"


def _user_dir(username: str) -> Path:
    return USER_DATA_DIR / _safe_username(username)


def _user_json_path(username: str) -> Path:
    return _user_dir(username) / "profile.json"


def _avatar_path(username: str, suffix: str) -> Path:
    return _user_dir(username) / f"avatar{suffix}"


def current_user() -> Optional[str]:
    return st.session_state.get("current_user")


def current_actor_id() -> str:
    username = current_user()
    if username:
        return f"user:{username}"
    if "anonymous_actor_id" not in st.session_state:
        st.session_state.anonymous_actor_id = f"anon:{uuid4().hex}"
    return st.session_state.anonymous_actor_id


def rerun_app() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def load_user_profile(username: str) -> Dict[str, Any]:
    path = _user_json_path(username)
    if not path.exists():
        return {"chat_records": [], "reports": [], "batch_text_column": None}
    return json.loads(path.read_text(encoding="utf-8") or "{}")


def save_user_profile(username: str, profile: Dict[str, Any]) -> None:
    user_dir = _user_dir(username)
    user_dir.mkdir(parents=True, exist_ok=True)
    _user_json_path(username).write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")


def sync_session_from_user(username: str) -> None:
    profile = load_user_profile(username)
    st.session_state.chat_records = profile.get("chat_records", [])
    st.session_state.saved_reports = profile.get("reports", [])
    st.session_state.user_profile = profile
    st.session_state.batch_text_column = profile.get("batch_text_column")
    batch_rows = profile.get("batch_result_rows")
    if batch_rows:
        st.session_state.batch_result_df = pd.DataFrame(batch_rows)


def persist_chat_records(records: List[dict]) -> None:
    username = current_user()
    if not username:
        return
    profile = load_user_profile(username)
    profile["chat_records"] = records
    save_user_profile(username, profile)


def archive_current_chat(title: str = "") -> bool:
    username = current_user()
    if not username:
        return False
    profile = load_user_profile(username)
    records = profile.get("chat_records", [])
    if not records:
        return False
    sessions = profile.get("chat_sessions", [])
    first_text = str(records[0].get("text", ""))
    sessions.insert(
        0,
        {
            "id": uuid4().hex,
            "title": title.strip() or first_text[:24] or "新的聊天",
            "created_at": records[0].get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "records": records,
        },
    )
    profile["chat_sessions"] = sessions[:50]
    profile["chat_records"] = []
    save_user_profile(username, profile)
    st.session_state.chat_records = []
    return True


def list_chat_sessions() -> List[dict]:
    username = current_user()
    if not username:
        return []
    profile = load_user_profile(username)
    sessions = []
    current_records = profile.get("chat_records", [])
    if current_records:
        first_text = str(current_records[0].get("text", ""))
        sessions.append(
            {
                "id": "current",
                "title": first_text[:24] or "当前聊天",
                "updated_at": current_records[-1].get("created_at", ""),
                "records": current_records,
                "is_current": True,
            }
        )
    for session in profile.get("chat_sessions", []):
        sessions.append({**session, "is_current": False})
    return sessions


def restore_chat_session(session_id: str) -> bool:
    username = current_user()
    if not username:
        return False
    profile = load_user_profile(username)
    if session_id == "current":
        st.session_state.chat_records = profile.get("chat_records", [])
        return True

    selected_session = None
    remaining_sessions = []
    for session in profile.get("chat_sessions", []):
        if session.get("id") == session_id:
            selected_session = session
        else:
            remaining_sessions.append(session)
    if not selected_session:
        return False

    current_records = profile.get("chat_records", [])
    if current_records:
        first_text = str(current_records[0].get("text", ""))
        remaining_sessions.insert(
            0,
            {
                "id": uuid4().hex,
                "title": first_text[:24] or "上一段聊天",
                "created_at": current_records[0].get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "records": current_records,
            },
        )

    profile["chat_records"] = selected_session.get("records", [])
    profile["chat_sessions"] = remaining_sessions[:50]
    save_user_profile(username, profile)
    st.session_state.chat_records = profile["chat_records"]
    return True


def search_chat_records(keyword: str) -> List[dict]:
    username = current_user()
    if not username or not keyword.strip():
        return []
    profile = load_user_profile(username)
    keyword = keyword.strip()
    results = []
    sources = [{"title": "当前聊天", "records": profile.get("chat_records", [])}]
    sources.extend(profile.get("chat_sessions", []))
    for source in sources:
        for record in source.get("records", []):
            text = str(record.get("text", ""))
            reply = str(record.get("reply", ""))
            if keyword in text or keyword in reply or keyword in str(record.get("emotion", "")):
                results.append(
                    {
                        "会话": source.get("title", "历史会话"),
                        "时间": record.get("created_at", ""),
                        "情绪": record.get("emotion", ""),
                        "用户输入": text,
                        "AI回复": reply,
                    }
                )
    return results


def persist_batch_result(result_df: pd.DataFrame, text_column: str) -> None:
    username = current_user()
    if not username:
        return
    profile = load_user_profile(username)
    profile["batch_result_rows"] = result_df.to_dict(orient="records")
    profile["batch_text_column"] = text_column
    save_user_profile(username, profile)


def persist_report(title: str, content: str) -> None:
    username = current_user()
    if not username:
        return
    profile = load_user_profile(username)
    reports = profile.get("reports", [])
    reports.insert(
        0,
        {
            "title": title,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    profile["reports"] = reports[:20]
    save_user_profile(username, profile)
    st.session_state.saved_reports = profile["reports"]


def display_name(username: Optional[str] = None) -> str:
    username = username or current_user()
    if not username:
        return "未登录用户"
    profile = load_user_profile(username)
    return profile.get("nickname") or username


def render_avatar(profile: Dict[str, Any], size: int = 88) -> None:
    avatar_path = profile.get("avatar_path")
    if not avatar_path or not Path(avatar_path).exists():
        st.markdown(
            f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:linear-gradient(135deg,#bfd9c7,#b8d7df);display:flex;align-items:center;justify-content:center;color:#31413b;font-weight:800;">用户</div>',
            unsafe_allow_html=True,
        )
        return

    path = Path(avatar_path)
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    pos_x = int(profile.get("avatar_position_x", 50))
    pos_y = int(profile.get("avatar_position_y", 50))
    st.markdown(
        (
            f'<img src="data:{mime};base64,{encoded}" '
            f'style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;'
            f'object-position:{pos_x}% {pos_y}%;border:3px solid rgba(255,252,245,.95);'
            f'box-shadow:0 8px 18px rgba(92,118,105,.18);" alt="用户头像">'
        ),
        unsafe_allow_html=True,
    )


def save_user_display_profile(
    nickname: str,
    avatar_file: Optional[Any] = None,
    avatar_position_x: int = 50,
    avatar_position_y: int = 50,
    assistant_name: str = "",
) -> None:
    username = current_user()
    if not username:
        return
    profile = load_user_profile(username)
    if nickname.strip():
        profile["nickname"] = nickname.strip()
    if assistant_name.strip():
        profile["assistant_name"] = assistant_name.strip()
    profile["avatar_position_x"] = avatar_position_x
    profile["avatar_position_y"] = avatar_position_y

    if avatar_file is not None:
        suffix = Path(avatar_file.name).suffix.lower() or ".png"
        avatar_path = _avatar_path(username, suffix)
        _user_dir(username).mkdir(parents=True, exist_ok=True)
        avatar_path.write_bytes(avatar_file.getbuffer())
        profile["avatar_path"] = str(avatar_path)

    save_user_profile(username, profile)
    st.session_state.user_profile = profile


def load_community_posts() -> List[dict]:
    _ensure_storage()
    return json.loads(COMMUNITY_STORE.read_text(encoding="utf-8") or "[]")


def assistant_name(username: Optional[str] = None) -> str:
    username = username or current_user()
    if not username:
        return st.session_state.get("assistant_name", "情绪陪伴助手")
    profile = load_user_profile(username)
    return profile.get("assistant_name") or st.session_state.get("assistant_name", "情绪陪伴助手")


def update_assistant_name(name: str) -> None:
    clean_name = name.strip() or "情绪陪伴助手"
    st.session_state.assistant_name = clean_name
    username = current_user()
    if username:
        profile = load_user_profile(username)
        profile["assistant_name"] = clean_name
        save_user_profile(username, profile)
        st.session_state.user_profile = profile


def _save_community_posts(posts: List[dict]) -> None:
    _ensure_storage()
    COMMUNITY_STORE.write_text(json.dumps(posts[:100], ensure_ascii=False, indent=2), encoding="utf-8")


def add_community_post(
    title: str,
    content: str,
    section: str,
    emotion: str,
    is_anonymous: bool,
    analysis: Dict[str, Any],
    ai_reply: str,
) -> None:
    username = current_user() or "匿名用户"
    post_display_name = analysis.get("anonymous_name") if is_anonymous else display_name(username)
    posts = load_community_posts()
    posts.insert(
        0,
        {
            "id": uuid4().hex,
            "username": username,
            "display_name": post_display_name or "匿名用户",
            "title": title,
            "section": section,
            "emotion": emotion,
            "ai_tags": analysis.get("tags", []),
            "emotion_tendency": analysis.get("emotion_tendency", "中性"),
            "possible_emotions": analysis.get("possible_emotions", []),
            "risk_level": analysis.get("risk_level", "低"),
            "risk_reason": analysis.get("risk_reason", ""),
            "ai_reply": ai_reply,
            "content": content,
            "is_anonymous": is_anonymous,
            "status": "待审核" if analysis.get("risk_level") == "高" else "已发布",
            "supports": {"拥抱": 0, "陪伴": 0, "鼓励": 0},
            "supporters": {"拥抱": [], "陪伴": [], "鼓励": []},
            "comments": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    _save_community_posts(posts)


def update_community_support(post_id: str, support_type: str, actor_id: Optional[str] = None) -> bool:
    actor_id = actor_id or current_actor_id()
    posts = load_community_posts()
    changed = False
    for post in posts:
        if post.get("id") == post_id:
            supports = post.setdefault("supports", {"拥抱": 0, "陪伴": 0, "鼓励": 0})
            supporters = post.setdefault("supporters", {"拥抱": [], "陪伴": [], "鼓励": []})
            support_user_list = supporters.setdefault(support_type, [])
            if actor_id in support_user_list:
                break
            support_user_list.append(actor_id)
            supports[support_type] = int(supports.get(support_type, 0)) + 1
            changed = True
            break
    _save_community_posts(posts)
    return changed


def add_community_comment(post_id: str, content: str, quick_reply: str = "") -> None:
    username = current_user() or "匿名用户"
    posts = load_community_posts()
    for post in posts:
        if post.get("id") == post_id:
            comments = post.setdefault("comments", [])
            comments.append(
                {
                    "username": username,
                    "content": content or quick_reply,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            break
    _save_community_posts(posts)


def set_community_status(post_id: str, status: str) -> None:
    posts = load_community_posts()
    for post in posts:
        if post.get("id") == post_id:
            post["status"] = status
            break
    _save_community_posts(posts)


def render_auth_controls(key_prefix: str = "auth", show_title: bool = True) -> None:
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if show_title:
        st.markdown("### 用户")

    username = current_user()
    if username:
        profile = load_user_profile(username)
        render_avatar(profile, size=88)
        st.success(f"当前用户：{display_name(username)}")
        with st.expander("编辑个人资料"):
            nickname = st.text_input("修改昵称", value=profile.get("nickname", username), key=f"{key_prefix}_nickname")
            custom_assistant_name = st.text_input(
                "AI助手命名",
                value=profile.get("assistant_name", "情绪陪伴助手"),
                key=f"{key_prefix}_assistant_name",
            )
            avatar_file = st.file_uploader("上传头像", type=["png", "jpg", "jpeg"], key=f"{key_prefix}_avatar")
            st.caption("头像会以圆形展示。拖动下面两个滑块，可以调整图片在圆形里的水平和垂直位置。")
            avatar_position_x = st.slider(
                "头像水平对齐",
                min_value=0,
                max_value=100,
                value=int(profile.get("avatar_position_x", 50)),
                key=f"{key_prefix}_avatar_x",
            )
            avatar_position_y = st.slider(
                "头像垂直对齐",
                min_value=0,
                max_value=100,
                value=int(profile.get("avatar_position_y", 50)),
                key=f"{key_prefix}_avatar_y",
            )
            if st.button("保存资料", key=f"{key_prefix}_save_profile"):
                save_user_display_profile(
                    nickname,
                    avatar_file,
                    avatar_position_x,
                    avatar_position_y,
                    custom_assistant_name,
                )
                st.success("个人资料已保存。")
                rerun_app()
        if st.button("退出登录", key=f"{key_prefix}_logout"):
            st.session_state.current_user = None
            st.session_state.chat_records = []
            st.session_state.saved_reports = []
            st.session_state.pop("batch_result_df", None)
            st.session_state.pop("batch_text_column", None)
            rerun_app()
        return

    mode = st.radio("账号操作", ["登录", "注册"], horizontal=True, key=f"{key_prefix}_mode")
    input_username = st.text_input("用户名", key=f"{key_prefix}_username")
    input_password = st.text_input("密码", type="password", key=f"{key_prefix}_password")

    if st.button(mode, key=f"{key_prefix}_submit"):
        if not input_username.strip() or not input_password:
            st.warning("请输入用户名和密码。")
            return

        users = _load_users()
        username_key = input_username.strip()
        if mode == "注册":
            if username_key in users:
                st.error("用户名已存在，请直接登录。")
                return
            users[username_key] = _hash_password(input_password)
            _save_users(users)
            save_user_profile(username_key, {"chat_records": [], "reports": [], "batch_text_column": None})
            st.success("注册成功，已自动登录。")
        else:
            if username_key not in users or not _verify_password(input_password, users[username_key]):
                st.error("用户名或密码不正确。")
                return

        st.session_state.current_user = username_key
        sync_session_from_user(username_key)
        rerun_app()


def render_auth_panel() -> None:
    with st.sidebar:
        render_auth_controls("sidebar_auth")
        if current_user():
            st.markdown("---")
            st.markdown("### 历史聊天")
            sessions = list_chat_sessions()
            if not sessions:
                st.caption("还没有保存的聊天。")
            for session in sessions[:12]:
                title = session.get("title") or "未命名聊天"
                prefix = "当前：" if session.get("is_current") else ""
                updated_at = session.get("updated_at") or session.get("created_at", "")
                label = f"{prefix}{title}"
                if st.button(label, key=f"sidebar_chat_{session.get('id')}", use_container_width=True):
                    restore_chat_session(session.get("id", ""))
                    rerun_app()
                if updated_at:
                    st.caption(updated_at)
