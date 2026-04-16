"""
ap.py — QuantDesk Pro home page.
Entry point for the Streamlit multi-page app.
Run with: streamlit run ap.py
"""

import streamlit as st
import pandas as pd

from utils import apply_theme, page_header, section_header, info_card, terminal_ribbon
from auth import (
    _auth_configured,
    get_user_name,
    get_user_email,
    get_user_id,
    sidebar_user_widget,
)
from database import create_profile_if_needed
from data_loader import load_close_series

st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()


def build_ribbon_item(label, ticker):
    s = load_close_series(ticker, period="5d")
    if s.empty or len(s) < 2:
        return (label, "N/A", "—")

    last = float(s.iloc[-1])
    prev = float(s.iloc[-2])
    chg = ((last / prev) - 1) * 100 if prev != 0 else 0.0

    if abs(last) >= 1000:
        value = f"{last:,.0f}"
    elif abs(last) >= 100:
        value = f"{last:,.2f}"
    else:
        value = f"{last:.2f}"

    return (label, value, f"{chg:+.2f}%")


def module_card(icon, title, page_path, features, button_key):
    features_html = "".join(
        f'<li style="color:#7f8ea3; font-size:12px; margin:4px 0;">{item}</li>'
        for item in features
    )

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
            border:1px solid #1b2638;
            border-radius:8px;
            padding:14px;
            min-height:210px;
            margin-bottom:10px;
        ">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:10px;">
            <div>
              <div style="font-size:18px; line-height:1;">{icon}</div>
              <div style="color:#d6deeb; font-size:15px; font-weight:800; margin-top:8px;">
                {title}
              </div>
            </div>
            <div style="
                display:inline-block;
                padding:2px 8px;
                border-radius:999px;
                border:1px solid #1b2638;
                color:#35c2ff;
                font-size:9px;
                font-weight:800;
                letter-spacing:0.12em;
                text-transform:uppercase;
            ">
              Live
            </div>
          </div>

          <ul style="margin:6px 0 12px 0; padding-left:18px;">
            {features_html}
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(f"Open {title}", key=button_key, use_container_width=True):
        st.switch_page(page_path)


if _auth_configured():
    user = getattr(st, "user", {}) or {}
    if not user.get("is_logged_in", False):
        page_header("QuantDesk Pro", "Multi-Asset Analytics Workstation")

        col = st.columns([1, 1.45, 1])[1]
        with col:
            info_card(
                "Secure Access",
                "Sign in to access portfolio analytics, derivatives tools, volatility surfaces, macro dashboards, and saved workspaces."
            )
            if callable(getattr(st, "login", None)):
                st.button(
                    "Sign in with Google",
                    on_click=st.login,
                    kwargs={"provider": "google"},
                    use_container_width=True,
                    key="login_btn",
                )
            else:
                st.error("This Streamlit version does not support built-in authentication.")
        st.stop()

    user_id = get_user_id()
    user_email = get_user_email()
    user_name = get_user_name()
    if user_id:
        create_profile_if_needed(user_id, user_email, user_name)

sidebar_user_widget()

page_header("QuantDesk Pro", "Multi-Asset Analytics Workstation")

if _auth_configured():
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
            border:1px solid #1b2638;
            border-radius:8px;
            padding:10px 14px;
            margin-bottom:12px;
        ">
          <span style="color:#d6deeb; font-size:12px; font-weight:800; letter-spacing:0.12em; text-transform:uppercase;">
            User Session
          </span>
          <span style="color:#7f8ea3; font-size:13px; margin-left:10px;">
            {get_user_name()}
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.spinner("Loading market ribbon…"):
    ribbon_items = [
        build_ribbon_item("SPX", "^GSPC"),
        build_ribbon_item("NDX", "^NDX"),
        build_ribbon_item("VIX", "^VIX"),
        build_ribbon_item("US10Y", "^TNX"),
        build_ribbon_item("DXY", "DX-Y.NYB"),
        build_ribbon_item("GOLD", "GC=F"),
        build_ribbon_item("WTI", "CL=F"),
        build_ribbon_item("BTC", "BTC-USD"),
        build_ribbon_item("EURUSD", "EURUSD=X"),
    ]
terminal_ribbon(ribbon_items)

left, right = st.columns([2.1, 1], gap="large")

with left:
    section_header("Workspace Launcher", "Launch portfolio, risk, derivatives, volatility, screening, and macro tools")

    modules = [
        ("📊", "Portfolio Analytics", "pages/1_Portfolio.py", [
            "P&L and performance metrics",
            "Benchmark comparison",
            "Technicals and holdings view",
            "Portfolio save/load workflow",
        ]),
        ("⚠️", "Risk & Attribution", "pages/2_Risk_Attribution.py", [
            "Rolling risk metrics",
            "VaR / CVaR and stress tests",
            "Correlation and covariance analysis",
            "Volatility contribution view",
        ]),
        ("📐", "Derivatives", "pages/3__Derivatives.py", [
            "Black-Scholes and binomial pricing",
            "Greeks and implied volatility",
            "Live options chain",
            "P&L heatmaps",
        ]),
        ("🌊", "Volatility Surface", "pages/4_Vol_Surface.py", [
            "Smile by expiry",
            "Term structure",
            "2D heatmap",
            "3D vol surface",
        ]),
        ("🎲", "Monte Carlo & Strategy Lab", "pages/5_Monte_Carlo__Strategy_Lab.py", [
            "GBM path simulation",
            "MC vs BS pricing",
            "Payoff diagrams",
            "Breakeven summaries",
        ]),
        ("🔬", "Screener & Watchlist", "pages/6_Screener.py", [
            "Multi-ticker snapshot",
            "Momentum and RSI signals",
            "52-week proximity view",
            "Volume and volatility filters",
        ]),
        ("🌍", "Macro Dashboard", "pages/7_Macro.py", [
            "FX, commodities, rates and bonds",
            "Cross-asset monitoring",
            "Correlation analysis",
            "Regime and yield-curve view",
        ]),
    ]

    grid_cols = st.columns(3)
    for i, (icon, title, page_path, features) in enumerate(modules):
        with grid_cols[i % 3]:
            module_card(icon, title, page_path, features, button_key="open_" + str(i))

with right:
    section_header("System Status", "Workspace and module availability")
    status_df = pd.DataFrame(
        {
            "Module": ["Portfolio", "Risk", "Derivatives", "Vol Surface", "Strategy Lab", "Screener", "Macro"],
            "Status": ["READY", "READY", "READY", "READY", "READY", "READY", "READY"],
        }
    )
    st.dataframe(status_df, use_container_width=True, height=282)

    section_header("Quick Access", "Jump directly into key modules")
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("Open Macro", use_container_width=True, key="qa_macro"):
            st.switch_page("pages/7_Macro.py")
    with qa2:
        if st.button("Open Portfolio", use_container_width=True, key="qa_port"):
            st.switch_page("pages/1_Portfolio.py")

    qb1, qb2 = st.columns(2)
    with qb1:
        if st.button("Open Risk", use_container_width=True, key="qa_risk"):
            st.switch_page("pages/2_Risk_Attribution.py")
    with qb2:
        if st.button("Open Vol Surface", use_container_width=True, key="qa_vol"):
            st.switch_page("pages/4_Vol_Surface.py")

    info_card(
        "Desk Notes",
        "Use Macro as the flagship terminal page. Then tighten Portfolio and Risk for a denser desk-style flow. After that, add watchlists, movers, news, and alert panels."
    )

st.markdown("---")
st.markdown(
    """
    <div style="color:#7f8ea3; font-size:11px; text-align:center; letter-spacing:0.10em; text-transform:uppercase;">
      QuantDesk Pro | Multi-Asset Analytics Workstation | Data via yfinance | For educational and research purposes only
    </div>
    """,
    unsafe_allow_html=True,
)
