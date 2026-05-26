import hashlib
import json
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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


def current_user() -> Optional[str]:
    return st.session_state.get("current_user")


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


def load_community_posts() -> List[dict]:
    _ensure_storage()
    return json.loads(COMMUNITY_STORE.read_text(encoding="utf-8") or "[]")


def add_community_post(content: str, emotion: str = "日常") -> None:
    username = current_user() or "匿名用户"
    posts = load_community_posts()
    posts.insert(
        0,
        {
            "username": username,
            "emotion": emotion,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    COMMUNITY_STORE.write_text(json.dumps(posts[:100], ensure_ascii=False, indent=2), encoding="utf-8")


def render_auth_panel() -> None:
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    with st.sidebar:
        st.markdown("### 用户")
        username = current_user()
        if username:
            st.success(f"已登录：{username}")
            if st.button("退出登录"):
                st.session_state.current_user = None
                st.session_state.chat_records = []
                st.session_state.saved_reports = []
                st.session_state.pop("batch_result_df", None)
                st.session_state.pop("batch_text_column", None)
                rerun_app()
            return

        mode = st.radio("账号操作", ["登录", "注册"], horizontal=True)
        input_username = st.text_input("用户名")
        input_password = st.text_input("密码", type="password")

        if st.button(mode):
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
