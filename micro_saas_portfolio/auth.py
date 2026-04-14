"""
auth.py — Login guard and user helpers for QuantDesk Pro.

Usage in every page:
    from auth import require_login, get_user_id, get_user_name
    require_login()   # ← call at the top of every page
"""

from __future__ import annotations
import streamlit as st


def _auth_configured() -> bool:
    """Return True if [auth] section exists in secrets.toml."""
    try:
        _ = st.secrets["auth"]
        return True
    except (KeyError, FileNotFoundError):
        return False


def require_login() -> None:
    """
    Gate the current page behind login.

    - If auth is NOT configured (local dev / no secrets): shows a warning
      but lets the user through so the app still works locally.
    - If auth IS configured: enforces login and redirects to the login screen.
    """
    if not _auth_configured():
        # Dev mode — auth not set up, skip the gate
        return

    if not st.user.get("is_logged_in", False):
        st.warning("🔒 Please log in to access this page.")
        st.markdown(
            """
            <div style='text-align:center; margin-top:40px;'>
              <a href='/' style='
                background:#00d4ff; color:#000; font-weight:700;
                padding:12px 28px; border-radius:6px; text-decoration:none;
                font-size:15px; letter-spacing:0.04em;
              '>← Back to Home / Login</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()


def get_user_id() -> str | None:
    """Return the logged-in user's subject ID, or None."""
    if not _auth_configured():
        return "local_dev_user"
    return st.user.get("sub") or st.user.get("email")


def get_user_name() -> str:
    """Return a display name for the logged-in user."""
    if not _auth_configured():
        return "Local User"
    return (
        st.user.get("name")
        or st.user.get("email")
        or "User"
    )


def get_user_email() -> str | None:
    """Return the logged-in user's email."""
    if not _auth_configured():
        return None
    return st.user.get("email")


def sidebar_user_widget() -> None:
    """Render the user info + logout button in the sidebar."""
    if not _auth_configured():
        return
    with st.sidebar:
        name = get_user_name()
        email = get_user_email()
        st.markdown(
            f"""
            <div style='background:#111827; border:1px solid #1e2d45; border-radius:8px;
                        padding:10px 14px; margin-bottom:12px;'>
              <div style='font-size:13px; font-weight:700; color:#e2e8f0;'>{name}</div>
              {"" if not email else f"<div style='font-size:11px; color:#64748b;'>{email}</div>"}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Log out", use_container_width=True, key="_logout_btn"):
            st.logout()