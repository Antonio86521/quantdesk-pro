"""
ap.py — QuantDesk Pro home page.

Entry point for the Streamlit multi-page app.
Run with:  streamlit run ap.py
"""

import streamlit as st
from utils import apply_theme
from auth import _auth_configured, get_user_name, get_user_email, get_user_id, sidebar_user_widget
from database import create_profile_if_needed

st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()

# ── Login gate ────────────────────────────────────────────────────────────────
if _auth_configured():
    # Auth is set up — enforce login
    if not st.user.get("is_logged_in", False):
        # ── Login screen
        st.markdown("""
        <div style="padding: 40px 0 16px 0; text-align:center;">
          <span style="font-size:44px; font-weight:900; letter-spacing:-1px; color:#e2e8f0;">
            Quant<span style="color:#00d4ff;">Desk</span> <span style="color:#7c3aed;">Pro</span>
          </span>
        </div>
        <div style="text-align:center; font-size:13px; color:#64748b; letter-spacing:0.15em;
                    text-transform:uppercase; margin-bottom:36px;">
          Professional Quantitative Finance Dashboard
        </div>
        """, unsafe_allow_html=True)

        col = st.columns([1, 2, 1])[1]
        with col:
            st.markdown("""
            <div style="background:#111827; border:1px solid #1e2d45; border-radius:12px;
                        padding:32px 36px; text-align:center;">
              <div style="font-size:28px; margin-bottom:12px;">🔐</div>
              <p style="color:#94a3b8; font-size:15px; line-height:1.8; margin:0 0 24px 0;">
                Sign in with your Google account to access your personal
                portfolio, saved strategies, and all analytics tools.
              </p>
            </div>
            """, unsafe_allow_html=True)
            st.button(
                "🔑  Sign in with Google",
                on_click=st.login,
                kwargs={"provider": "google"},
                use_container_width=True,
                key="login_btn",
            )
        st.stop()

    # ── Logged in — sync profile to Supabase
    user_id    = get_user_id()
    user_email = get_user_email()
    user_name  = get_user_name()
    if user_id:
        create_profile_if_needed(user_id, user_email, user_name)

# ── Sidebar user widget ───────────────────────────────────────────────────────
sidebar_user_widget()

# ── Homepage ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 24px 0 8px 0;">
  <span style="font-size:40px; font-weight:900; letter-spacing:-1px; color:#e2e8f0;">
    Quant<span style="color:#00d4ff;">Desk</span> <span style="color:#7c3aed;">Pro</span>
  </span>
</div>
<div style="font-size:13px; color:#64748b; letter-spacing:0.15em;
            text-transform:uppercase; margin-bottom:28px;">
  Professional Quantitative Finance Dashboard
</div>
""", unsafe_allow_html=True)

# Welcome banner
if _auth_configured():
    name = get_user_name()
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#00d4ff12,#7c3aed12);
                    border:1px solid #1e2d45; border-radius:10px;
                    padding:14px 20px; margin-bottom:20px;">
          <span style="color:#e2e8f0; font-size:15px;">
            Welcome back, <strong>{name}</strong> 👋
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("""
<div style="background:#111827; border:1px solid #1e2d45; border-radius:12px;
            padding:20px 28px; margin-bottom:24px;">
  <p style="color:#94a3b8; margin:0; line-height:1.8; font-size:15px;">
    A full-stack quantitative finance workstation built in Python.
    Analyse your portfolio, price options across three models, study the volatility surface,
    run Monte Carlo simulations, and backtest option strategies — all in one place.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Module cards ──────────────────────────────────────────────────────────────
modules = [
    ("📊", "Portfolio Analytics", "1_Portfolio", [
        "P&L, Sharpe, Sortino, Calmar",
        "Benchmark comparison & alpha/beta",
        "Technical indicators (RSI, MACD, BBands)",
        "Save & load portfolios from database",
    ]),
    ("⚠️", "Risk & Attribution", "2_Risk_Attribution", [
        "Rolling vol, Sharpe, beta, correlation",
        "VaR / CVaR (historical & parametric)",
        "Correlation heatmap",
        "Stress test & custom scenario analysis",
    ]),
    ("📐", "Derivatives", "3_Derivatives", [
        "Black-Scholes, Binomial, Monte Carlo pricing",
        "Full Greeks + ITM probability",
        "Put-call parity checker",
        "Greeks curves & P&L heatmap",
    ]),
    ("🌊", "Volatility Surface", "4_Vol_Surface", [
        "Live options chain from market data",
        "Volatility smile per expiry",
        "ATM IV term structure",
        "2D heatmap & 3D IV surface",
    ]),
    ("🎲", "Monte Carlo & Strategy Lab", "5_Monte_Carlo_Strategy_Lab", [
        "GBM paths with antithetic variates",
        "MC vs BS convergence",
        "14 option strategy payoff diagrams",
        "Breakeven & risk summary",
    ]),
    ("🔬", "Screener & Watchlist", "6_Screener", [
        "Multi-ticker snapshot",
        "RSI & momentum signals",
        "52-week high/low proximity",
        "Volume & volatility filters",
    ]),
]

cols_layout = st.columns(3)
for i, (icon, title, page, features) in enumerate(modules):
    with cols_layout[i % 3]:
        features_html = "".join(
            f'<li style="color:#94a3b8; font-size:13px; margin:3px 0;">{f}</li>'
            for f in features
        )
        st.markdown(f"""
        <div style="background:#111827; border:1px solid #1e2d45; border-radius:10px;
                    padding:18px 20px; margin-bottom:16px; min-height:160px;">
          <div style="font-size:20px; margin-bottom:6px;">{icon}
            <span style="font-size:15px; font-weight:700; color:#e2e8f0;
                         margin-left:6px;">{title}</span>
          </div>
          <ul style="margin:8px 0 0 0; padding-left:18px;">
            {features_html}
          </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="color:#475569; font-size:12px; text-align:center; letter-spacing:0.08em;">
  QuantDesk Pro &nbsp;·&nbsp; Data via yfinance &nbsp;·&nbsp;
  For educational and research purposes only. Not financial advice.
</div>
""", unsafe_allow_html=True)
