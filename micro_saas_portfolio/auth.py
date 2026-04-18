"""
auth.py — Login helpers for QuantDesk Pro.
"""

from __future__ import annotations
import streamlit as st


def _auth_configured() -> bool:
    if not hasattr(st, "user") or not hasattr(st, "login") or not hasattr(st, "logout"):
        return False
    try:
        _ = st.secrets["auth"]
        return True
    except (KeyError, FileNotFoundError, AttributeError):
        return False


def require_login() -> None:
    if not _auth_configured():
        return
    user = getattr(st, "user", {}) or {}
    if not user.get("is_logged_in", False):
        inline_login_gate(
            title="Login Required",
            message="Please sign in to access this page.",
            button_label="Continue with Google",
        )


def get_user_id() -> str | None:
    if not _auth_configured():
        return "local_dev_user"
    user = getattr(st, "user", {}) or {}
    return user.get("sub") or user.get("email")


def get_user_name() -> str:
    if not _auth_configured():
        return "Local User"
    user = getattr(st, "user", {}) or {}
    return user.get("name") or user.get("email") or "User"


def get_user_email() -> str | None:
    if not _auth_configured():
        return None
    user = getattr(st, "user", {}) or {}
    return user.get("email")


def inline_login_gate(
    title: str = "Login Required",
    message: str = "Sign in to continue.",
    button_label: str = "Continue with Google",
) -> None:
    st.markdown(f"## 🔐 {title}")
    st.markdown(message)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Sign in to continue")
        if st.button(button_label, use_container_width=True):
            st.login()
    st.stop()


def sidebar_user_widget() -> None:
    if not _auth_configured():
        return
    with st.sidebar:
        name = get_user_name()
        email = get_user_email()
        st.markdown(
            f"""
            <div style='background:linear-gradient(180deg,#0c1322 0%,#0f172a 100%);
                        border:1px solid #1e2d45; border-radius:12px;
                        padding:12px 14px; margin-bottom:12px;'>
              <div style='font-size:10px; font-weight:800; color:#7f8ea3; letter-spacing:0.14em; text-transform:uppercase;'>Active session</div>
              <div style='font-size:13px; font-weight:800; color:#e2e8f0; margin-top:6px;'>{name}</div>
              {'' if not email else f"<div style='font-size:11px; color:#64748b; margin-top:2px;'>{email}</div>"}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Log out", use_container_width=True, key="_logout_btn"):
            st.logout()

