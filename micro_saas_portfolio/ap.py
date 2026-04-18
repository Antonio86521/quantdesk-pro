import datetime
import streamlit as st

from data_loader import load_close_series
from utils import apply_theme, apply_responsive_layout


st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

apply_theme()
apply_responsive_layout()


# ─────────────────────────────────────────────
# PAGE CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    .home-shell {
        max-width: 1080px;
        margin: 0 auto;
    }

    .topbar-box {
        border: 1px solid #143458;
        background: linear-gradient(90deg, #071320 0%, #08182b 100%);
        padding: 12px 16px;
        min-height: 52px;
        display: flex;
        align-items: center;
        border-radius: 0;
    }

    .topbar-brand {
        color: #35c2ff;
        font-size: 13px;
        font-weight: 900;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-right: 14px;
    }

    .topbar-divider {
        width: 1px;
        height: 18px;
        background: #143458;
        margin-right: 14px;
        display: inline-block;
        vertical-align: middle;
    }

    .topbar-page {
        color: #7f8ea3;
        font-size: 13px;
        vertical-align: middle;
    }

    .live-wrap {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 10px;
        height: 52px;
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
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .top-pill {
        border: 1px solid #143458;
        border-radius: 10px;
        padding: 4px 9px;
        color: #d6deeb;
        font-size: 11px;
        font-weight: 700;
        background: #08182b;
        display: inline-block;
    }

    .hero {
        border: 1px solid #143458;
        border-radius: 18px;
        padding: 18px 22px;
        background:
          radial-gradient(circle at top right, rgba(53,194,255,0.10), transparent 28%),
          linear-gradient(90deg, #08121f 0%, #0b2036 100%);
        margin-bottom: 14px;
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
        font-size: 20px;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 8px;
    }

    .hero-sub {
        color: #7f8ea3;
        font-size: 13px;
    }

    .market-strip {
        border: 1px solid #143458;
        border-radius: 14px;
        overflow: hidden;
        background: linear-gradient(90deg, #08121f 0%, #0a1830 100%);
        margin-bottom: 14px;
    }

    .market-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
    }

    .market-cell {
        padding: 12px 16px;
        border-right: 1px solid #143458;
        min-height: 74px;
    }

    .market-cell:last-child {
        border-right: none;
    }

    .market-label {
        color: #7f8ea3;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .market-value {
        color: #ffffff;
        font-size: 15px;
        font-weight: 900;
        margin-bottom: 8px;
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
        border-radius: 16px;
        background: linear-gradient(180deg, #071320 0%, #09192b 100%);
        padding: 16px 16px 14px 16px;
        min-height: 170px;
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
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .kpi-sub {
        color: #7f8ea3;
        font-size: 12px;
        margin-bottom: 16px;
    }

    .kpi-sub.green {
        color: #00d27a;
    }

    .sparkbar-wrap {
        display: flex;
        align-items: flex-end;
        gap: 4px;
        height: 54px;
        margin-top: 10px;
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
        margin-top: 4px;
    }

    .table-header,
    .table-row {
        display: grid;
        grid-template-columns: 1.6fr 1fr 0.8fr 0.8fr;
        align-items: center;
    }

    .table-header {
        padding: 12px 16px;
        border-bottom: 1px solid #143458;
        color: #7fa3d6;
        font-size: 9px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }

    .table-row {
        padding: 16px;
        border-bottom: 1px solid rgba(20,52,88,0.85);
    }

    .table-row:last-child {
        border-bottom: none;
    }

    .ticker-name,
    .price-text {
        color: #ffffff;
        font-weight: 800;
        font-size: 13px;
    }

    .return-pos {
        color: #00ff9a;
        font-weight: 900;
        font-size: 13px;
    }

    .return-neg {
        color: #ff4d6d;
        font-weight: 900;
        font-size: 13px;
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
        min-height: 38px !important;
        border-radius: 999px !important;
        border: 1px solid #143458 !important;
        background: linear-gradient(180deg, #071320 0%, #09182a 100%) !important;
        color: #35c2ff !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        text-decoration: none !important;
        padding: 0 14px !important;
        white-space: nowrap !important;
    }

    div[data-testid="stPageLink"] a:hover {
        border-color: #35c2ff !important;
        background: #0b1d33 !important;
    }

    div[data-testid="stPopover"] button {
        min-height: 38px !important;
        border-radius: 10px !important;
        border: 1px solid #143458 !important;
        background: #08182b !important;
        color: #d6deeb !important;
        font-weight: 800 !important;
        padding: 0 12px !important;
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


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
hour = datetime.datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

st.markdown('<div class="home-shell">', unsafe_allow_html=True)

# top row
top_left, top_live, top_pro, top_menu = st.columns([10, 1, 1, 1])

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

with top_live:
    st.markdown(
        """
        <div class="live-wrap">
            <span class="live-dot"></span>
            <span class="live-label">Live</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_pro:
    st.markdown(
        """
        <div class="live-wrap">
            <span class="top-pill">Pro</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_menu:
    with st.popover("⋯"):
        st.page_link("pages/8_portfolio_manager.py", label="Portfolio Manager")
        st.page_link("pages/9_portfolio_analysis.py", label="Saved Portfolio Analysis")
        st.page_link("pages/6_Screener.py", label="Screener")
        st.page_link("pages/7_Macro.py", label="Macro")

# hero
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

# market strip
market_html = market_strip_html()
if market_html:
    st.html(market_html)

# nav pills
nav_cols = st.columns(8)
with nav_cols[0]:
    st.page_link("ap.py", label="Overview")
with nav_cols[1]:
    st.page_link("pages/1_Portfolio.py", label="Portfolio Analytics")
with nav_cols[2]:
    st.page_link("pages/2_Risk_Attribution.py", label="Risk & Attribution")
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

# kpi cards
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

# table
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
