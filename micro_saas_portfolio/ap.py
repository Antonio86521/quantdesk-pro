"""
ap_Pro.py — upgraded QuantDesk Pro home page.

Drop-in replacement for the current Streamlit home page.
Designed to be resilient even if a few optional helper functions differ slightly.
"""

import streamlit as st
import pandas as pd

from utils import apply_theme

# Optional helpers from your project
try:
    from utils import terminal_ribbon
except Exception:
    terminal_ribbon = None

try:
    from auth import (
        _auth_configured,
        get_user_name,
        get_user_email,
        get_user_id,
        sidebar_user_widget,
    )
except Exception:
    _auth_configured = None
    get_user_name = None
    get_user_email = None
    get_user_id = None
    sidebar_user_widget = None

try:
    from database import create_profile_if_needed
except Exception:
    create_profile_if_needed = None


# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()

is_logged_in = bool(getattr(st.user, "is_logged_in", False))

# ──────────────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────────────
def safe_call(fn, default=None):
    try:
        if callable(fn):
            return fn()
    except Exception:
        return default
    return default


def inject_home_css():
    st.markdown(
        """
        <style>
        :root {
            --bg: #0a0e1a;
            --surface: #0f172a;
            --surface-2: #111827;
            --border: #1f2d45;
            --text: #e5eefb;
            --muted: #7f8ea3;
            --accent: #35c2ff;
            --accent2: #7c3aed;
            --green: #00e676;
            --red: #ff4d6d;
            --yellow: #ffd166;
        }

        .home-wrap { padding-top: 0.2rem; }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 28px 28px 24px 28px;
            background:
                radial-gradient(circle at top right, rgba(53,194,255,0.12), transparent 26%),
                radial-gradient(circle at bottom left, rgba(124,58,237,0.12), transparent 22%),
                linear-gradient(180deg, #0b1220 0%, #0d1526 100%);
            box-shadow: 0 10px 35px rgba(0,0,0,0.28);
        }

        .hero-title {
            font-size: 42px;
            font-weight: 900;
            line-height: 1.0;
            letter-spacing: -0.03em;
            color: var(--text);
            margin-bottom: 8px;
        }

        .hero-subtitle {
            color: var(--muted);
            font-size: 15px;
            line-height: 1.7;
            max-width: 820px;
            margin-bottom: 18px;
        }

        .brand-accent { color: var(--accent); }
        .brand-accent2 { color: #a78bfa; }

        .pill-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin: 12px 0 20px 0;
        }

        .pill {
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 6px 11px;
            font-size: 11px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text);
            background: rgba(255,255,255,0.02);
            font-weight: 800;
        }

        .grid-note {
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 15px 16px;
            background: linear-gradient(180deg, #0c1322 0%, #0f172a 100%);
            height: 100%;
        }

        .grid-note-label {
            color: var(--muted);
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .grid-note-value {
            color: var(--text);
            font-size: 22px;
            font-weight: 900;
            margin-bottom: 4px;
        }

        .grid-note-desc {
            color: var(--muted);
            font-size: 12px;
            line-height: 1.6;
        }

        .section-title {
            color: var(--text);
            font-size: 14px;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            font-weight: 900;
            margin: 6px 0 12px 0;
        }

        .card {
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px 16px 14px 16px;
            background: linear-gradient(180deg, #0c1322 0%, #0f172a 100%);
            min-height: 170px;
        }

        .card-title {
            color: var(--text);
            font-size: 16px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .card-subtitle {
            color: var(--muted);
            font-size: 12px;
            line-height: 1.6;
            margin-bottom: 12px;
        }

        .bullet {
            color: var(--muted);
            font-size: 12px;
            line-height: 1.8;
            margin: 0;
            padding-left: 18px;
        }

        .status-box {
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px;
            background: linear-gradient(180deg, #0b1220 0%, #0e1627 100%);
        }

        .status-title {
            color: var(--text);
            font-size: 15px;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .status-text {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.7;
        }

        .tiny {
            color: var(--muted);
            font-size: 11px;
        }

        .stButton > button {
            border-radius: 12px !important;
            font-weight: 800 !important;
            border: 1px solid var(--border) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(user_name: str | None):
    name_part = ""
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">
                Quant<span class="brand-accent">Desk</span> <span class="brand-accent2">Pro</span>{name_part}
            </div>
            <div class="hero-subtitle">
                Multi-asset analytics for portfolio monitoring, macro tracking, derivatives workflows,
                volatility analysis, risk attribution, and scenario testing — all in one terminal-style workspace.
            </div>
            <div class="pill-row">
                <div class="pill">Portfolio Analytics</div>
                <div class="pill">Macro Monitor</div>
                <div class="pill">Risk & Attribution</div>
                <div class="pill">Derivatives</div>
                <div class="pill">Vol Surface</div>
                <div class="pill">Monte Carlo</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_stats():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            """
            <div class="grid-note">
              <div class="grid-note-label">Workspace</div>
              <div class="grid-note-value">Multi-Page</div>
              <div class="grid-note-desc">Dedicated tools for portfolio, macro, derivatives, vol surface, and simulation workflows.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="grid-note">
              <div class="grid-note-label">Data Stack</div>
              <div class="grid-note-value">Hybrid</div>
              <div class="grid-note-desc">Yahoo Finance with Alpha Vantage fallback for stronger reliability across pages.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="grid-note">
              <div class="grid-note-label">Use Cases</div>
              <div class="grid-note-value">6 Core</div>
              <div class="grid-note-desc">Monitoring, screening, risk, options, macro, and simulation in a single interface.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            """
            <div class="grid-note">
              <div class="grid-note-label">Mode</div>
              <div class="grid-note-value">Research</div>
              <div class="grid-note-desc">Built for learning, presenting projects, and demonstrating real finance workflow skills.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_feature_cards():
    st.markdown('<div class="section-title">Core Modules</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="card">
              <div class="card-title">Portfolio Analytics</div>
              <div class="card-subtitle">Track performance, P&amp;L, risk-adjusted returns, technicals, and benchmark-relative metrics.</div>
              <ul class="bullet">
                <li>Performance and attribution</li>
                <li>VaR, CVaR, drawdown, alpha, beta</li>
                <li>Technicals and news integration</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="card">
              <div class="card-title">Macro & Risk</div>
              <div class="card-subtitle">Monitor rates, FX, commodities, equities, crypto, and cross-asset regime conditions.</div>
              <ul class="bullet">
                <li>FX heatmap and inflation proxy</li>
                <li>Rate trend and curve logic</li>
                <li>Cross-asset correlation and baskets</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="card">
              <div class="card-title">Derivatives Lab</div>
              <div class="card-subtitle">Price options, inspect chains, analyze smiles and surfaces, and test structured payoffs.</div>
              <ul class="bullet">
                <li>Black-Scholes, binomial, Monte Carlo</li>
                <li>Volatility surface and term structure</li>
                <li>Strategy payoff visualizations</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_quick_actions():
    st.markdown('<div class="section-title">Quick Start</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="status-box">
              <div class="status-title">Start with Portfolio</div>
              <div class="status-text">Input a few tickers, shares, and buy prices to generate a clean performance and risk view.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="status-box">
              <div class="status-title">Check Macro Conditions</div>
              <div class="status-text">Use the Macro page to scan rates, FX, commodities, equities, and inflation-sensitive assets.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="status-box">
              <div class="status-title">Run an Options Workflow</div>
              <div class="status-text">Open Derivatives or Vol Surface to test pricing logic, smiles, and live chain structure.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_user_panel(user_name: str | None, user_email: str | None, user_id: str | None):
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown('<div class="section-title">Session</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="status-box">
              <div class="status-title">Logged in</div>
              <div class="status-text">
                <strong>User:</strong> {user_name or "Unknown"}<br>
                <strong>Email:</strong> {user_email or "Unknown"}<br>
                <strong>User ID:</strong> {user_id or "Unavailable"}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="section-title">Build Notes</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="status-box">
              <div class="status-title">Future upgrades</div>
              <div class="status-text">
                1. Saved user portfolios<br>
                2. Pro dashboard / landing page cards<br>
                3. Better onboarding text<br>
                4. Public deployment + custom domain
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_not_logged_in():
    st.markdown(
        """
        <div class="status-box" style="margin-top:18px;">
          <div class="status-title">Authentication required</div>
          <div class="status-text">
            Your app is configured to use authentication, but no active session was detected.
            Use the sign-in flow in the app sidebar or your configured provider.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main page
# ──────────────────────────────────────────────────────────────────────────────
inject_home_css()

if callable(terminal_ribbon):
    try:
        terminal_ribbon("QUANTDESK PRO · MULTI-ASSET ANALYTICS WORKSPACE")
    except Exception:
        pass

user_name = safe_call(get_user_name, None)
user_email = safe_call(get_user_email, None)
user_id = safe_call(get_user_id, None)

if callable(create_profile_if_needed) and user_id:
    try:
        create_profile_if_needed(user_id, user_email, user_name)
    except Exception:
        pass

if is_logged_in and callable(sidebar_user_widget):
    try:
        sidebar_user_widget()
    except Exception:
        pass

st.markdown('<div class="home-wrap">', unsafe_allow_html=True)

if not is_logged_in:
    st.markdown(
        """
        <div class="status-box" style="margin-top:18px; max-width:720px;">
          <div class="status-title">Welcome to QuantDesk Pro</div>
          <div class="status-text">
            Please sign in to access portfolio analytics, macro monitoring,
            derivatives tools, volatility surface analysis, and risk dashboards.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if st.button("Sign in", use_container_width=True):
            try:
                st.login()
            except Exception:
                st.error("Login is not available from this page yet. In that case, send me your auth.py and I’ll wire it correctly.")

    st.markdown("")
    st.caption("Sign in to continue to the protected pages.")
    st.stop()

render_hero(user_name)
st.markdown("")
render_top_stats()
st.markdown("")
render_feature_cards()
st.markdown("")
render_quick_actions()
st.markdown("")
render_user_panel(user_name, user_email, user_id)

st.markdown("")
st.caption("QuantDesk Pro is a project workspace for portfolio analytics, macro monitoring, derivatives, and risk workflows.")
