"""
ap.py — public QuantDesk Pro home page.

No login required.
Designed as a clean landing page for the full multi-page app.
"""

import streamlit as st
import pandas as pd
from data_loader import load_close_series

from utils import apply_theme

# Optional helper from your project
try:
    from utils import terminal_ribbon
except Exception:
    terminal_ribbon = None


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


# ──────────────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────────────
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

        .stButton > button {
            border-radius: 12px !important;
            font-weight: 800 !important;
            border: 1px solid var(--border) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                Quant<span class="brand-accent">Desk</span> <span class="brand-accent2">Pro</span>
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


def render_future_upgrades():
    st.markdown('<div class="section-title">Future Upgrades</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="status-box">
          <div class="status-title">Roadmap</div>
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

@st.cache_data(ttl=600)
def load_market_bar_data():
    tickers = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^NDX",
        "Gold": "GC=F",
        "WTI": "CL=F",
        "EUR/USD": "EURUSD=X",
        "BTC": "BTC-USD",
        "US 10Y": "^TNX",
    }

    rows = []
    for label, ticker in tickers.items():
        try:
            s = load_close_series(ticker, period="1mo", source="auto")
            if s is None or s.empty or len(s) < 2:
                continue

            last = float(s.iloc[-1])
            prev = float(s.iloc[-2])
            chg = ((last / prev) - 1) * 100

            if abs(last) >= 1000:
                value = f"{last:,.0f}"
            else:
                value = f"{last:,.2f}"

            rows.append({
                "label": label,
                "value": value,
                "chg": chg,
            })
        except Exception:
            continue

    return rows


def render_market_bar():
    data = load_market_bar_data()
    if not data:
        return

    blocks = ""
    for item in data:
        chg = item["chg"]
        color = "#00e676" if chg >= 0 else "#ff4d6d"
        sign = "+" if chg >= 0 else ""

        blocks += f"""
        <div style="
            padding:10px 16px;
            border-right:1px solid #1f2d45;
            min-width:135px;
            display:flex;
            flex-direction:column;
            gap:2px;
        ">
            <div style="
                color:#7f8ea3;
                font-size:10px;
                font-weight:800;
                letter-spacing:0.12em;
                text-transform:uppercase;
            ">
                {item["label"]}
            </div>
            <div style="
                color:#e5eefb;
                font-size:15px;
                font-weight:800;
            ">
                {item["value"]}
            </div>
            <div style="
                color:{color};
                font-size:11px;
                font-weight:800;
            ">
                {sign}{chg:.2f}%
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div style="
            display:flex;
            flex-wrap:wrap;
            overflow:hidden;
            border:1px solid #1f2d45;
            border-radius:16px;
            background:linear-gradient(180deg, #0b1220 0%, #0e1627 100%);
            margin-top:6px;
            margin-bottom:8px;
        ">
            {blocks}
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

st.markdown('<div class="home-wrap">', unsafe_allow_html=True)

render_hero()
st.markdown("")
render_top_stats()
st.markdown("")
render_feature_cards()
st.markdown("")
render_quick_actions()
st.markdown("")

st.markdown("")
st.caption("QuantDesk Pro is a project workspace for portfolio analytics, macro monitoring, derivatives, and risk workflows.")
