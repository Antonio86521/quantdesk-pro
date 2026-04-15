"""
ap.py — QuantDesk Pro home page.

Entry point for the Streamlit multi-page app.
Run with:  streamlit run ap.py
"""

import streamlit as st
import pandas as pd

from utils import apply_theme, terminal_ribbon
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_ribbon_item(label: str, ticker: str):
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

    delta = f"{chg:+.2f}%"
    return (label, value, delta)


def module_card(icon: str, title: str, page_path: str, features: list[str], status: str = "LIVE"):
    st.markdown(
        f"""
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                    border:1px solid #1b2638; border-radius:8px; padding:14px 14px 10px 14px;
                    min-height:210px; margin-bottom:12px;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
            <div>
              <div style="font-size:20px; line-height:1;">{icon}</div>
              <div style="color:#d6deeb; font-size:14px; font-weight:800; letter-spacing:0.04em; margin-top:8px;">
                {title}
              </div>
            </div>
            <div style="display:inline-block; padding:2px 8px; border-radius:999px;
                        border:1px solid #1b2638; color:#35c2ff; font-size:9px; font-weight:800;
                        letter-spacing:0.12em; text-transform:uppercase;">
              {status}
            </div>
          </div>
          <ul style="margin:8px 0 12px 0; padding-left:18px;">
            {"".join(f'<li style="color:#7f8ea3; font-size:12px; margin:4px 0;">{f}</li>' for f in features)}
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(f"Open {title}", key=f"open_{page_path}", use_container_width=True):
        st.switch_page(page_path)


# ── Login gate ────────────────────────────────────────────────────────────────

if _auth_configured():
    if not st.user.get("is_logged_in", False):
        st.markdown(
            """
            <div style="padding: 42px 0 10px 0; text-align:center;">
              <span style="font-size:44px; font-weight:900; letter-spacing:-1px; color:#d6deeb;">
                Quant<span style="color:#35c2ff;">Desk</span> <span style="color:#4f8cff;">Pro</span>
              </span>
            </div>
            <div style="text-align:center; font-size:12px; color:#7f8ea3; letter-spacing:0.16em;
                        text-transform:uppercase; margin-bottom:28px;">
              Multi-Asset Analytics Workstation
            </div>
            """,
            unsafe_allow_html=True,
        )

        col = st.columns([1, 1.6, 1])[1]
        with col:
            st.markdown(
                """
                <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                            border:1px solid #1b2638; border-radius:10px;
                            padding:30px 34px; text-align:center;">
                  <div style="font-size:28px; margin-bottom:10px;">🔐</div>
                  <div style="color:#d6deeb; font-size:18px; font-weight:800; margin-bottom:10px;">
                    Secure Access
                  </div>
                  <p style="color:#7f8ea3; font-size:14px; line-height:1.8; margin:0 0 20px 0;">
                    Sign in to access portfolio analytics, derivatives tools, macro dashboards,
                    volatility surfaces, and saved workspace data.
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                "Sign in with Google",
                on_click=st.login,
                kwargs={"provider": "google"},
                use_container_width=True,
                key="login_btn",
            )
        st.stop()

    user_id = get_user_id()
    user_email = get_user_email()
    user_name = get_user_name()
    if user_id:
        create_profile_if_needed(user_id, user_email, user_name)

sidebar_user_widget()


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="
    padding: 6px 0 14px 0;
    border-bottom:1px solid #1b2638;
    margin-bottom:16px;
">
  <div style="
      font-size:30px;
      font-weight:900;
      letter-spacing:-0.5px;
      color:#ffffff;
  ">
    Quant<span style="color:#35c2ff;">Desk</span>
    <span style="color:#4f8cff;">Pro</span>
  </div>

  <div style="
      margin-top:6px;
      color:#7f8ea3;
      font-size:11px;
      letter-spacing:0.14em;
      text-transform:uppercase;
  ">
    Multi-Asset Analytics Workstation
  </div>
</div>
""", unsafe_allow_html=True)


if _auth_configured():
    name = get_user_name()
    st.markdown(
        f"""
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                    border:1px solid #1b2638; border-radius:8px;
                    padding:10px 14px; margin-bottom:12px;">
          <span style="color:#d6deeb; font-size:13px; font-weight:700;">
            USER SESSION:
          </span>
          <span style="color:#7f8ea3; font-size:13px; margin-left:8px;">
            {name}
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Top ribbon ────────────────────────────────────────────────────────────────

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


# ── Main layout ───────────────────────────────────────────────────────────────

left, right = st.columns([2.15, 1], gap="large")

with left:
    st.markdown(
        """
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                    border:1px solid #1b2638; border-radius:8px; padding:12px 14px; margin-bottom:14px;">
          <div style="color:#d6deeb; font-size:12px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">
            Workspace Launcher
          </div>
          <div style="color:#7f8ea3; font-size:11px; margin-top:6px;">
            Launch analytics modules, risk tools, derivatives screens, and macro monitors.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    modules = [
        (
            "📊",
            "Portfolio Analytics",
            "pages/1_Portfolio.py",
            [
                "P&L, Sharpe, Sortino, Calmar",
                "Benchmark comparison & alpha/beta",
                "Technical indicators and holdings view",
                "Save & load portfolios",
            ],
        ),
        (
            "⚠️",
            "Risk & Attribution",
            "pages/2_Risk_Attribution.py",
            [
                "Rolling vol, beta, correlation",
                "VaR / CVaR and stress testing",
                "Return distribution and heatmaps",
                "Volatility contribution analysis",
            ],
        ),
        (
            "📐",
            "Derivatives",
            "pages/3__Derivatives.py",
            [
                "Black-Scholes, Binomial, Monte Carlo",
                "Greeks and ITM probability",
                "Live option chain",
                "P&L heatmaps and parity checks",
            ],
        ),
        (
            "🌊",
            "Volatility Surface",
            "pages/4_Vol_Surface.py",
            [
                "Smile by expiry",
                "ATM term structure",
                "2D IV heatmaps",
                "3D implied vol surface",
            ],
        ),
        (
            "🎲",
            "Monte Carlo & Strategy Lab",
            "pages/5_Monte_Carlo__Strategy_Lab.py",
            [
                "GBM path simulation",
                "MC vs BS convergence",
                "Strategy payoff diagrams",
                "Breakeven and risk summary",
            ],
        ),
        (
            "🔬",
            "Screener & Watchlist",
            "pages/6_Screener.py",
            [
                "Multi-ticker snapshot",
                "RSI and momentum signals",
                "52-week proximity view",
                "Volume and volatility filters",
            ],
        ),
        (
            "🌍",
            "Macro Dashboard",
            "pages/7_Macro.py",
            [
                "FX, commodities, rates and bonds",
                "Cross-asset correlation",
                "Regime analysis",
                "Yield curve and macro monitor",
            ],
        ),
    ]

    grid_cols = st.columns(3)
    for i, (icon, title, page_path, features) in enumerate(modules):
        with grid_cols[i % 3]:
            module_card(icon, title, page_path, features)

with right:
    st.markdown(
        """
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                    border:1px solid #1b2638; border-radius:8px; padding:12px 14px; margin-bottom:12px;">
          <div style="color:#d6deeb; font-size:12px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">
            System Status
          </div>
          <div style="color:#7f8ea3; font-size:11px; margin-top:6px;">
            Workspace, routing, and market data health.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status_df = pd.DataFrame(
        {
            "Module": [
                "Portfolio",
                "Risk",
                "Derivatives",
                "Vol Surface",
                "Strategy Lab",
                "Screener",
                "Macro",
            ],
            "Status": ["READY", "READY", "READY", "READY", "READY", "READY", "READY"],
        }
    )
    st.dataframe(status_df, use_container_width=True, height=282)

    st.markdown(
        """
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                    border:1px solid #1b2638; border-radius:8px; padding:12px 14px; margin:12px 0;">
          <div style="color:#d6deeb; font-size:12px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">
            Quick Access
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    st.markdown(
        """
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                    border:1px solid #1b2638; border-radius:8px; padding:12px 14px; margin:12px 0;">
          <div style="color:#d6deeb; font-size:12px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">
            Desk Notes
          </div>
          <div style="color:#7f8ea3; font-size:12px; line-height:1.8; margin-top:8px;">
            • Use the Macro Dashboard as the flagship terminal page.<br>
            • Then tighten Portfolio and Risk layouts for a denser desk-style experience.<br>
            • Later add watchlists, movers, news, and alert panels.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
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

