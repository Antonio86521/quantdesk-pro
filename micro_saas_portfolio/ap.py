"""
ap.py — refreshed QuantDesk Pro home page.

No login required.
Designed as a dashboard-style landing page for the full multi-page app.
"""

import datetime as dt
import streamlit as st

from data_loader import load_close_series
from utils import apply_theme, apply_responsive_layout

try:
    from auth import _auth_configured, get_user_name
except Exception:
    def _auth_configured():
        return False
    def get_user_name():
        return "User"


st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()
apply_responsive_layout()


def inject_home_css():
    st.markdown(
        """
        <style>
        .home-shell {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            border: 1px solid #1f2d45;
            border-radius: 22px;
            padding: 26px 28px;
            background:
                radial-gradient(circle at top right, rgba(53,194,255,0.12), transparent 26%),
                radial-gradient(circle at bottom left, rgba(124,58,237,0.12), transparent 22%),
                linear-gradient(180deg, #0b1220 0%, #0d1526 100%);
            box-shadow: 0 10px 35px rgba(0,0,0,0.28);
        }

        .hero-kicker {
            color: #35c2ff;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .hero-title {
            font-size: 42px;
            font-weight: 900;
            line-height: 1.0;
            letter-spacing: -0.03em;
            color: #e5eefb;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            color: #7f8ea3;
            font-size: 15px;
            line-height: 1.7;
            max-width: 820px;
            margin-bottom: 0;
        }

        .market-bar {
            border: 1px solid #1f2d45;
            border-radius: 18px;
            overflow: hidden;
            background:
                radial-gradient(circle at top right, rgba(53,194,255,0.06), transparent 30%),
                linear-gradient(180deg, #0b1220 0%, #0e1627 100%);
            box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        }

        .market-bar-head {
            padding: 9px 14px;
            border-bottom: 1px solid #1f2d45;
            color: #7f8ea3;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        .module-card {
            border: 1px solid #1f2d45;
            border-radius: 18px;
            padding: 16px;
            background: linear-gradient(180deg, #0c1322 0%, #0f172a 100%);
            height: 100%;
        }

        .module-kicker {
            color: #7f8ea3;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .module-title {
            color: #e5eefb;
            font-size: 17px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .module-desc {
            color: #7f8ea3;
            font-size: 12px;
            line-height: 1.65;
            margin-bottom: 12px;
        }

        .module-tag {
            display: inline-block;
            margin: 0 6px 6px 0;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 700;
            color: #d6deeb;
            background: rgba(255,255,255,0.03);
            border: 1px solid #1b2638;
        }

        .link-stack {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .status-card {
            border: 1px solid #1f2d45;
            border-radius: 18px;
            padding: 16px;
            background: linear-gradient(180deg, #0c1322 0%, #0f172a 100%);
            min-height: 130px;
        }

        .status-title {
            color: #e5eefb;
            font-size: 14px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .status-text {
            color: #7f8ea3;
            font-size: 12px;
            line-height: 1.7;
        }

        @media (max-width: 768px) {
            .hero-shell { padding: 20px 18px; }
            .hero-title { font-size: 30px; }
            .module-card, .status-card { min-height: unset; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=600)
def load_market_bar_data():
    tickers = {
        "SPY": "SPY",
        "QQQ": "QQQ",
        "VIX": "^VIX",
        "BTC": "BTC-USD",
        "DXY": "DX-Y.NYB",
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
            if label == "US 10Y":
                value = f"{last/10:.2f}%"
            elif abs(last) >= 1000:
                value = f"{last:,.0f}"
            else:
                value = f"{last:,.2f}"
            rows.append((label, value, f"{chg:+.2f}%"))
        except Exception:
            continue
    return rows


def render_hero():
    hour = dt.datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    user_name = get_user_name() if _auth_configured() else "Guest"
    subtitle = (
        "Track portfolios, scan macro conditions, inspect derivatives, and run simulation workflows "
        "from a single dashboard-style workspace."
    )
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-kicker">Market Intelligence Terminal</div>
            <div class="hero-title">{greeting} — welcome to QuantDesk Pro</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if _auth_configured() and user_name:
        st.caption(f"Signed in as {user_name}.")


def render_market_bar():
    rows = load_market_bar_data()
    if not rows:
        return
    blocks = ""
    for label, value, delta in rows:
        up = str(delta).startswith("+")
        color = "#00e676" if up else "#ff4d6d"
        glow = "rgba(0,230,118,0.16)" if up else "rgba(255,77,109,0.16)"
        blocks += f"""
        <div style="padding:12px 16px; min-width:132px; border-right:1px solid #1f2d45; display:flex; flex-direction:column; gap:3px;">
            <div style="color:#7f8ea3; font-size:10px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">{label}</div>
            <div style="color:#e5eefb; font-size:15px; font-weight:900; line-height:1.1;">{value}</div>
            <div style="display:inline-flex; align-items:center; width:fit-content; padding:3px 8px; border-radius:999px; font-size:11px; font-weight:800; color:{color}; background:{glow}; border:1px solid {color}22;">{delta}</div>
        </div>
        """
    st.markdown(
        f"""
        <div class="market-bar">
            <div class="market-bar-head">Live Market Snapshot</div>
            <div style="display:flex; flex-wrap:wrap; align-items:stretch;">{blocks}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def module_link(label: str, path: str, description: str):
    try:
        st.page_link(path, label=label, icon="→")
    except Exception:
        st.markdown(f"**{label}** — {description}")


def render_modules():
    st.markdown('<div class="section-kicker">Core Modules</div>', unsafe_allow_html=True)
    modules = [
        {
            "title": "Portfolio Analytics",
            "desc": "Performance, drawdown, benchmark analysis, and technical overlays for custom baskets.",
            "tags": ["Returns", "Risk", "Technicals"],
            "links": [
                ("Open Portfolio", "pages/1_Portfolio.py", "Portfolio analytics workspace"),
                ("Open Saved Analysis", "pages/9_portfolio_analysis.py", "Saved portfolio analytics"),
            ],
        },
        {
            "title": "Risk & Macro",
            "desc": "Cross-asset monitoring, rolling risk views, rate regime checks, and macro dashboarding.",
            "tags": ["Rolling Risk", "Cross-Asset", "Macro"],
            "links": [
                ("Open Risk & Attribution", "pages/2_Risk_Attribution.py", "Risk analytics page"),
                ("Open Macro Dashboard", "pages/7_Macro.py", "Macro dashboard page"),
                ("Open Screener", "pages/6_Screener.py", "Screener and watchlist"),
            ],
        },
        {
            "title": "Derivatives Lab",
            "desc": "Option pricing, vol surfaces, Monte Carlo simulation, and payoff strategy testing.",
            "tags": ["Options", "Vol Surface", "Monte Carlo"],
            "links": [
                ("Open Derivatives", "pages/3__Derivatives.py", "Derivatives page"),
                ("Open Vol Surface", "pages/4_Vol_Surface.py", "Vol surface page"),
                ("Open Strategy Lab", "pages/5_Monte_Carlo__Strategy_Lab.py", "Monte Carlo and strategy lab"),
            ],
        },
    ]
    cols = st.columns(3)
    for col, module in zip(cols, modules):
        with col:
            st.markdown(
                f"""
                <div class="module-card">
                    <div class="module-kicker">Workspace</div>
                    <div class="module-title">{module['title']}</div>
                    <div class="module-desc">{module['desc']}</div>
                    <div>{''.join(f'<span class="module-tag">{tag}</span>' for tag in module['tags'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="link-stack">', unsafe_allow_html=True)
            for label, path, desc in module["links"]:
                module_link(label, path, desc)
            st.markdown('</div>', unsafe_allow_html=True)


def render_status_cards():
    st.markdown('<div class="section-kicker">Quick Start</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    cards = [
        ("Build a portfolio", "Input a few tickers, shares, and buy prices to generate a clean analytics view."),
        ("Manage saved holdings", "Create persistent portfolios and jump directly into saved portfolio analysis."),
        ("Scan macro conditions", "Use the macro and screener pages to check context before running a trade view."),
    ]
    for col, (title, text) in zip((c1, c2, c3), cards):
        with col:
            st.markdown(
                f"""
                <div class="status-card">
                    <div class="status-title">{title}</div>
                    <div class="status-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


inject_home_css()
st.markdown('<div class="home-shell">', unsafe_allow_html=True)
render_hero()
render_market_bar()
render_modules()
render_status_cards()
st.markdown('</div>', unsafe_allow_html=True)
st.caption("Data sources depend on available provider coverage on each page. Live values use the current data loader configuration.")

