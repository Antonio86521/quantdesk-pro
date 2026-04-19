import datetime
import streamlit as st

from data_loader import load_close_series
from utils import apply_theme, apply_responsive_layout, page_header, app_footer


st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

apply_theme()
apply_responsive_layout()


st.markdown(
    """
    <style>
    .home-shell {
        max-width: 1000px;
        margin: 0 auto;
    }

    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1.2rem !important;
    }

    .topbar-box {
        border: 1px solid #143458;
        background: linear-gradient(90deg, #06111d 0%, #08182b 100%);
        padding: 10px 14px;
        min-height: 46px;
        display: flex;
        align-items: center;
        border-radius: 0;
    }

    .topbar-brand {
        color: #35c2ff;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-right: 12px;
    }

    .topbar-divider {
        width: 1px;
        height: 18px;
        background: #143458;
        margin-right: 12px;
        display: inline-block;
        vertical-align: middle;
    }

    .topbar-page {
        color: #7f8ea3;
        font-size: 12px;
        vertical-align: middle;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: #00d27a;
        display: inline-block;
    }

    .live-label {
        color: #d6deeb;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .top-pill {
        border: 1px solid #143458;
        border-radius: 10px;
        padding: 3px 8px;
        color: #d6deeb;
        font-size: 10px;
        font-weight: 700;
        background: #08182b;
        display: inline-block;
    }

    .hero {
        border: 1px solid #143458;
        border-radius: 18px;
        padding: 16px 20px;
        background:
          radial-gradient(circle at top right, rgba(53,194,255,0.08), transparent 26%),
          linear-gradient(90deg, #07121f 0%, #0b233b 100%);
        margin-bottom: 12px;
    }

    .hero-kicker {
        color: #35c2ff;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        color: #ffffff;
        font-size: 19px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 7px;
    }

    .hero-sub {
        color: #7f8ea3;
        font-size: 12px;
    }

    .market-strip {
        border: 1px solid #143458;
        border-radius: 14px;
        overflow: hidden;
        background: linear-gradient(90deg, #07121f 0%, #091a31 100%);
        margin-bottom: 12px;
    }

    .market-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
    }

    .market-cell {
        padding: 10px 12px;
        border-right: 1px solid #143458;
        min-height: 64px;
    }

    .market-cell:last-child {
        border-right: none;
    }

    .market-label {
        color: #7f8ea3;
        font-size: 8px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .market-value {
        color: #ffffff;
        font-size: 13px;
        font-weight: 900;
        margin-bottom: 6px;
    }

    .market-delta {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
    }

    .kpi-card {
        border: 1px solid #143458;
        border-radius: 14px;
        background: linear-gradient(180deg, #071320 0%, #09192b 100%);
        padding: 13px 14px 11px 14px;
        min-height: 150px;
    }

    .kpi-kicker {
        color: #7fa3d6;
        font-size: 9px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }

    .kpi-value {
        color: #ffffff;
        font-size: 16px;
        font-weight: 900;
        margin-bottom: 6px;
    }

    .kpi-sub {
        color: #7f8ea3;
        font-size: 11px;
        margin-bottom: 14px;
    }

    .kpi-sub.green {
        color: #00d27a;
    }

    .sparkbar-wrap {
        display: flex;
        align-items: flex-end;
        gap: 3px;
        height: 38px;
        margin-top: 6px;
    }

    .sparkbar {
        flex: 1;
        border-radius: 0;
    }

    .table-shell {
        border: 1px solid #143458;
        border-radius: 14px;
        overflow: hidden;
        background: linear-gradient(180deg, #071320 0%, #08182b 100%);
        margin-top: 2px;
    }

    .table-header,
    .table-row {
        display: grid;
        grid-template-columns: 1.6fr 1fr 0.8fr 0.8fr;
        align-items: center;
    }

    .table-header {
        padding: 10px 14px;
        border-bottom: 1px solid #143458;
        color: #7fa3d6;
        font-size: 8px;
        font-weight: 900;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }

    .table-row {
        padding: 13px 14px;
        border-bottom: 1px solid rgba(20,52,88,0.65);
    }

    .table-row:last-child {
        border-bottom: none;
    }

    .ticker-name,
    .price-text {
        color: #ffffff;
        font-weight: 800;
        font-size: 12px;
    }

    .return-pos {
        color: #00ff9a;
        font-weight: 900;
        font-size: 12px;
    }

    .return-neg {
        color: #ff4d6d;
        font-weight: 900;
        font-size: 12px;
    }

    .signal-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        width: fit-content;
    }

    .signal-up {
        color: #00ff9a;
        background: rgba(0,210,122,0.12);
        border: 1px solid rgba(0,210,122,0.18);
    }

    .signal-down {
        color: #ff4d6d;
        background: rgba(255,92,92,0.12);
        border: 1px solid rgba(255,92,92,0.18);
    }

    .signal-neutral {
        color: #7fa3d6;
        background: rgba(127,163,214,0.12);
        border: 1px solid rgba(127,163,214,0.18);
    }

    .footer-row {
        display: flex;
        justify-content: space-between;
        color: #7f8ea3;
        font-size: 10px;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-top: 14px;
    }

    div[data-testid="stPageLink"] {
        margin: 0 !important;
    }

    div[data-testid="stPageLink"] a {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        height: 34px !important;
        border-radius: 999px !important;
        border: 1px solid #1c4b78 !important;
        background: linear-gradient(180deg, #061525 0%, #08192d 100%) !important;
        color: #6ecbff !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        letter-spacing: 0.04em !important;
        text-decoration: none !important;
        padding: 0 14px !important;
        white-space: nowrap !important;
    }

    div[data-testid="stPageLink"] a:hover {
        border-color: #35c2ff !important;
        background: #0b213a !important;
        color: #a8e4ff !important;
    }

    div[data-testid="stPopover"] button {
        min-height: 34px !important;
        border-radius: 10px !important;
        border: 1px solid #143458 !important;
        background: #08182b !important;
        color: #d6deeb !important;
        font-weight: 800 !important;
        padding: 0 10px !important;
    }

    @media (max-width: 900px) {
        .market-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .table-header,
        .table-row {
            grid-template-columns: 1.2fr 1fr 0.8fr 0.9fr;
        }
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

            rows.append({"label": label, "value": value, "chg": chg})
        except Exception:
            continue

    return rows


def market_strip_html():
    data = load_market_bar_data()
    if not data:
        return ""

    cells = []
    for item in data:
        chg = float(item["chg"])
        positive = chg >= 0
        color = "#00d27a" if positive else "#ff5c5c"
        bg = "rgba(0,210,122,0.14)" if positive else "rgba(255,92,92,0.14)"
        sign = "+" if positive else ""

        cells.append(
            f'<div class="market-cell">'
            f'<div class="market-label">{item["label"]}</div>'
            f'<div class="market-value">{item["value"]}</div>'
            f'<div class="market-delta" style="color:{color}; background:{bg};">{sign}{chg:.2f}%</div>'
            f'</div>'
        )

    cells_html = "".join(cells)

    return (
        '<div class="market-strip">'
        '<div class="market-grid">'
        f'{cells_html}'
        '</div>'
        '</div>'
    )


def sparkbars(values, positive=True):
    color = "rgba(39, 150, 155, 0.55)" if positive else "rgba(120, 44, 74, 0.65)"
    out = '<div class="sparkbar-wrap">'
    for v in values:
        out += f'<div class="sparkbar" style="height:{v}px; background:{color};"></div>'
    out += "</div>"
    return out


hour = datetime.datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

st.markdown('<div class="home-shell">', unsafe_allow_html=True)

top_left, top_right = st.columns([10, 3])

with top_left:
    st.markdown(
        """
        <div class="topbar-box">
            <span class="topbar-brand">QuantDesk Pro</span>
            <span class="topbar-divider"></span>
            <span class="topbar-page">Dashboard</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_right:
    right_a, right_b = st.columns([3, 1])
    with right_a:
        st.markdown(
            """
            <div class="topbar-box" style="justify-content:flex-end; gap:10px;">
                <span class="live-dot"></span>
                <span class="live-label">LIVE</span>
                <span class="top-pill">Pro</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right_b:
        with st.popover("⋯"):
            st.page_link("pages/8_portfolio_manager.py", label="Portfolio Manager")
            st.page_link("pages/9_portfolio_analysis.py", label="Saved Analysis")
            st.page_link("pages/6_Screener.py", label="Screener")
            st.page_link("pages/7_Macro.py", label="Macro")

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">Market Intelligence Terminal</div>
        <div class="hero-title">{greeting} — markets are open</div>
        <div class="hero-sub">7 analytical modules · Real-time data · Portfolio sync</div>
    </div>
    """,
    unsafe_allow_html=True,
)

market_html = market_strip_html()
if market_html:
    st.html(market_html)

section_intro("The home page is a quick command center. Use it for a delayed public-market snapshot, navigation, and a high-level view of the platform's most important analytics blocks.", title="Dashboard purpose")
glossary_expander("How to read the dashboard", ["Portfolio Value Card", "Sharpe Card", "VaR Card"])

nav_cols = st.columns(8)
with nav_cols[0]:
    st.page_link("ap.py", label="Home")
with nav_cols[1]:
    st.page_link("pages/1_Portfolio.py", label="Portfolio")
with nav_cols[2]:
    st.page_link("pages/2_Risk_Attribution.py", label="Risk")
with nav_cols[3]:
    st.page_link("pages/3__Derivatives.py", label="Derivatives")
with nav_cols[4]:
    st.page_link("pages/4_Vol_Surface.py", label="Vol Surface")
with nav_cols[5]:
    st.page_link("pages/5_Monte_Carlo__Strategy_Lab.py", label="Monte Carlo")
with nav_cols[6]:
    st.page_link("pages/6_Screener.py", label="Screener")
with nav_cols[7]:
    st.page_link("pages/7_Macro.py", label="Macro")

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-kicker">Portfolio Value</div>
            <div class="kpi-value">$142,840</div>
            <div class="kpi-sub">+$3,241 today · <span style="color:#00ff9a; font-weight:800;">+2.32%</span></div>
            {sparkbars([22, 26, 25, 16, 29, 31, 36], positive=True)}
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-kicker">Sharpe Ratio</div>
            <div class="kpi-value">1.84</div>
            <div class="kpi-sub green">Above benchmark · 0.62 alpha</div>
            {sparkbars([14, 18, 24, 25, 27, 31, 35], positive=True)}
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-kicker">VaR 95%</div>
            <div class="kpi-value">-1.42%</div>
            <div class="kpi-sub">Daily · Historical method</div>
            {sparkbars([24, 18, 28, 20, 31, 21, 26], positive=False)}
        </div>
        """,
        unsafe_allow_html=True,
    )

table_rows = [
    ("AAPL", "$212.49", "+18.4%", "UPTREND", "up"),
    ("MSFT", "$384.21", "+12.1%", "UPTREND", "up"),
    ("NVDA", "$108.77", "-8.3%", "OVERSOLD", "down"),
    ("SPY", "$538.42", "+9.7%", "NEUTRAL", "neutral"),
]

rows_html = ""
for ticker, price, ret, signal, cls in table_rows:
    return_cls = "return-pos" if ret.startswith("+") else "return-neg"
    signal_cls = "signal-up" if cls == "up" else "signal-down" if cls == "down" else "signal-neutral"
    rows_html += f"""
    <div class="table-row">
        <div class="ticker-name">{ticker}</div>
        <div class="price-text">{price}</div>
        <div class="{return_cls}">{ret}</div>
        <div><span class="signal-pill {signal_cls}">{signal}</span></div>
    </div>
    """

section_intro("This watchlist table is a quick-read panel for price, recent return, and a simplified signal label. It is designed for orientation, not execution.", title="Watchlist explanation")

st.markdown(
    f"""
    <div class="table-shell">
        <div class="table-header">
            <div>Ticker</div>
            <div>Price</div>
            <div>Return</div>
            <div>Signal</div>
        </div>
        {rows_html}
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="footer-row">
        <div>QuantDesk Pro · v2.0</div>
        <div>Data: yfinance · Alpha Vantage</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
