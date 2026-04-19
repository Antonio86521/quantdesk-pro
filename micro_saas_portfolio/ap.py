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

# ── Page-level styles ──────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .qd-topbar-left {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 18px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 28px;
    }
    .qd-logo-mark {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        background: #2563eb;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 800;
        color: #fff;
        letter-spacing: 0.04em;
        flex-shrink: 0;
    }
    .qd-app-name {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.01em;
    }
    .qd-sep { color: #cbd5e1; font-size: 13px; }
    .qd-page-crumb { font-size: 13px; color: #94a3b8; }
    .qd-live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10b981;
        display: inline-block;
        animation: qdpulse 2s ease-in-out infinite;
    }
    @keyframes qdpulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.35; }
    }
    .qd-status-text {
        font-size: 12px;
        font-weight: 600;
        color: #10b981;
        letter-spacing: 0.04em;
    }
    .qd-plan-pill {
        background: #eff6ff;
        color: #2563eb;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 999px;
        border: 1px solid #bfdbfe;
    }
    .qd-market-strip {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        background: #fff;
        margin-bottom: 28px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .qd-market-cell {
        padding: 14px 16px;
        border-right: 1px solid #e2e8f0;
    }
    .qd-market-cell:last-child { border-right: none; }
    .qd-market-ticker {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        color: #94a3b8;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .qd-market-price {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
        font-family: 'DM Mono', monospace;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .qd-market-chg {
        font-size: 12px;
        font-weight: 600;
        font-family: 'DM Mono', monospace;
    }
    .qd-section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
    }
    .qd-section-title {
        font-size: 14px;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.01em;
    }
    .qd-section-meta { font-size: 12px; color: #94a3b8; }
    .qd-table {
        width: 100%;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        background: #fff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .qd-table-head {
        display: grid;
        grid-template-columns: 1.8fr 1fr 0.9fr 0.8fr;
        padding: 10px 18px;
        border-bottom: 1px solid #e2e8f0;
        background: #f8fafc;
    }
    .qd-th {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #94a3b8;
    }
    .qd-table-row {
        display: grid;
        grid-template-columns: 1.8fr 1fr 0.9fr 0.8fr;
        padding: 13px 18px;
        border-bottom: 1px solid #f1f5f9;
        align-items: center;
    }
    .qd-table-row:last-child { border-bottom: none; }
    .qd-ticker { font-size: 14px; font-weight: 700; color: #0f172a; }
    .qd-exchange { font-size: 11px; color: #94a3b8; margin-top: 1px; }
    .qd-price {
        font-size: 14px;
        font-weight: 600;
        font-family: 'DM Mono', monospace;
        color: #0f172a;
        letter-spacing: -0.01em;
    }
    .qd-chg-pos { font-size: 13px; font-weight: 600; color: #10b981; font-family: 'DM Mono', monospace; }
    .qd-chg-neg { font-size: 13px; font-weight: 600; color: #ef4444; font-family: 'DM Mono', monospace; }
    .qd-signal {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .qd-signal-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .qd-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
        margin-top: 36px;
    }
    .qd-footer-left  { font-size: 12px; color: #94a3b8; font-weight: 500; }
    .qd-footer-right { font-size: 12px; color: #cbd5e1; }
    div[data-testid="stPageLink"] { margin: 0 !important; }
    div[data-testid="stPageLink"] a {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 32px !important;
        border-radius: 8px !important;
        border: 1px solid transparent !important;
        color: #64748b !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        padding: 0 10px !important;
        white-space: nowrap !important;
        transition: all 0.12s ease !important;
    }
    div[data-testid="stPageLink"] a:hover {
        background: #f1f5f9 !important;
        color: #0f172a !important;
        border-color: #e2e8f0 !important;
    }
    div[data-testid="stPopover"] button {
        min-height: 32px !important;
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        background: #fff !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 0 12px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stPopover"] button:hover {
        border-color: #2563eb !important;
        color: #2563eb !important;
    }
    @media (max-width: 900px) {
        .qd-market-strip { grid-template-columns: repeat(3, 1fr); }
        .qd-table-head,
        .qd-table-row   { grid-template-columns: 1.4fr 1fr 0.9fr 0.9fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Data ───────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_market_data() -> list:
    tickers = {
        "SPY":  "SPY",
        "QQQ":  "QQQ",
        "VIX":  "^VIX",
        "BTC":  "BTC-USD",
        "DXY":  "DX-Y.NYB",
        "10Y":  "^TNX",
    }
    rows = []
    for label, ticker in tickers.items():
        try:
            s = load_close_series(ticker, period="5d", source="auto")
            if s is None or s.empty or len(s) < 2:
                continue
            last = float(s.iloc[-1])
            prev = float(s.iloc[-2])
            chg  = ((last / prev) - 1) * 100
            if label == "10Y":
                display = f"{last / 10:.2f}%"
            elif label in ("BTC",) or abs(last) >= 1000:
                display = f"{last:,.0f}"
            else:
                display = f"{last:,.2f}"
            rows.append({"label": label, "display": display, "chg": chg})
        except Exception:
            continue
    return rows


@st.cache_data(ttl=300)
def load_watchlist_data() -> list:
    entries = [
        ("AAPL", "NASDAQ"),
        ("MSFT", "NASDAQ"),
        ("NVDA", "NASDAQ"),
        ("SPY",  "NYSE"),
    ]
    rows = []
    for ticker, exchange in entries:
        try:
            s = load_close_series(ticker, period="5d", source="auto")
            if s is None or s.empty or len(s) < 2:
                continue
            last = float(s.iloc[-1])
            prev = float(s.iloc[-2])
            chg  = ((last / prev) - 1) * 100
            rows.append({
                "ticker":   ticker,
                "exchange": exchange,
                "price":    f"${last:,.2f}",
                "chg":      chg,
            })
        except Exception:
            continue
    return rows


# ── HTML helpers ───────────────────────────────────────────────────────────────

def _market_strip_html(data: list) -> str:
    cells = []
    for item in data:
        chg   = float(item["chg"])
        color = "#10b981" if chg >= 0 else "#ef4444"
        sign  = "+" if chg >= 0 else ""
        cells.append(
            f'<div class="qd-market-cell">'
            f'<div class="qd-market-ticker">{item["label"]}</div>'
            f'<div class="qd-market-price">{item["display"]}</div>'
            f'<div class="qd-market-chg" style="color:{color};">{sign}{chg:.2f}%</div>'
            f'</div>'
        )
    return '<div class="qd-market-strip">' + "".join(cells) + '</div>'


def _signal(chg: float) -> tuple:
    if chg > 1.5:
        return "Strong Buy", "#10b981", "#065f46"
    if chg > 0:
        return "Buy",        "#10b981", "#065f46"
    if chg > -1.5:
        return "Neutral",    "#f59e0b", "#92400e"
    return "Caution",        "#ef4444", "#991b1b"


def _watchlist_html(rows: list) -> str:
    if not rows:
        return (
            '<div style="padding:24px 18px;color:#94a3b8;font-size:13px;'
            'border:1px solid #e2e8f0;border-radius:10px;background:#fff;">'
            'No watchlist data available.</div>'
        )
    head = (
        '<div class="qd-table-head">'
        '<div class="qd-th">Asset</div>'
        '<div class="qd-th">Price</div>'
        '<div class="qd-th">1D Change</div>'
        '<div class="qd-th">Signal</div>'
        '</div>'
    )
    body = ""
    for r in rows:
        chg     = float(r["chg"])
        chg_cls = "qd-chg-pos" if chg >= 0 else "qd-chg-neg"
        sign    = "+" if chg >= 0 else ""
        sig_lbl, dot_color, sig_color = _signal(chg)
        body += (
            f'<div class="qd-table-row">'
            f'<div><div class="qd-ticker">{r["ticker"]}</div>'
            f'<div class="qd-exchange">{r["exchange"]}</div></div>'
            f'<div class="qd-price">{r["price"]}</div>'
            f'<div class="{chg_cls}">{sign}{chg:.2f}%</div>'
            f'<div class="qd-signal" style="color:{sig_color};">'
            f'<span class="qd-signal-dot" style="background:{dot_color};"></span>'
            f'{sig_lbl}</div>'
            f'</div>'
        )
    return '<div class="qd-table">' + head + body + '</div>'


# ── Page ───────────────────────────────────────────────────────────────────────

now      = datetime.datetime.now()
hour     = now.hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
date_str = now.strftime("%A, %B %-d")

# ── Top bar ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([9, 3])

with col_left:
    st.markdown(
        '<div class="qd-topbar-left">'
        '<div class="qd-logo-mark">QD</div>'
        '<span class="qd-app-name">QuantDesk</span>'
        '<span class="qd-sep">·</span>'
        '<span class="qd-page-crumb">Dashboard</span>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_right:
    status_col, menu_col = st.columns([5, 2])
    with status_col:
        st.markdown(
            '<div style="padding-bottom:18px;border-bottom:1px solid #e2e8f0;margin-bottom:28px;'
            'display:flex;align-items:center;justify-content:flex-end;gap:8px;">'
            '<span class="qd-live-dot"></span>'
            '<span class="qd-status-text">Live</span>'
            '<span class="qd-plan-pill">Pro</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    with menu_col:
        st.markdown(
            '<div style="padding-bottom:18px;border-bottom:1px solid #e2e8f0;margin-bottom:28px;">',
            unsafe_allow_html=True,
        )
        with st.popover("···"):
            st.page_link("pages/8_portfolio_manager.py", label="Portfolio Manager")
            st.page_link("pages/9_portfolio_analysis.py", label="Saved Analysis")
            st.page_link("pages/6_Screener.py",           label="Screener")
            st.page_link("pages/7_Macro.py",              label="Macro")
        st.markdown('</div>', unsafe_allow_html=True)

# ── Greeting ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="margin-bottom:24px;">'
    f'<div style="font-size:22px;font-weight:700;color:#0f172a;'
    f'letter-spacing:-0.02em;margin-bottom:3px;">{greeting}</div>'
    f'<div style="font-size:13px;color:#94a3b8;">{date_str} · Market overview</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Market strip ───────────────────────────────────────────────────────────────
with st.spinner("Loading market data…"):
    market_data = load_market_data()

if market_data:
    st.markdown(_market_strip_html(market_data), unsafe_allow_html=True)
else:
    st.warning("Market data unavailable — check your data source connection.")

# ── Navigation ─────────────────────────────────────────────────────────────────
nav_cols = st.columns(8)
_nav = [
    ("ap.py",                                "Home"),
    ("pages/1_Portfolio.py",                 "Portfolio"),
    ("pages/2_Risk_Attribution.py",          "Risk"),
    ("pages/3__Derivatives.py",              "Derivatives"),
    ("pages/4_Vol_Surface.py",               "Vol Surface"),
    ("pages/5_Monte_Carlo__Strategy_Lab.py", "Monte Carlo"),
    ("pages/6_Screener.py",                  "Screener"),
    ("pages/7_Macro.py",                     "Macro"),
]
for col, (path, label) in zip(nav_cols, _nav):
    with col:
        st.page_link(path, label=label)

st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)

# ── Live market metrics ────────────────────────────────────────────────────────
if market_data:
    st.markdown(
        '<div style="font-size:11px;font-weight:700;letter-spacing:0.08em;'
        'text-transform:uppercase;color:#94a3b8;margin-bottom:12px;">Snapshot</div>',
        unsafe_allow_html=True,
    )
    metric_cols = st.columns(len(market_data))
    for col, item in zip(metric_cols, market_data):
        chg  = float(item["chg"])
        sign = "+" if chg >= 0 else ""
        col.metric(
            label=item["label"],
            value=item["display"],
            delta=f"{sign}{chg:.2f}%",
        )
    st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)

# ── Watchlist ──────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="qd-section-header">'
    '<div class="qd-section-title">Watchlist</div>'
    '<div class="qd-section-meta">1-day performance · Live</div>'
    '</div>',
    unsafe_allow_html=True,
)

with st.spinner("Loading watchlist…"):
    watchlist = load_watchlist_data()

st.markdown(_watchlist_html(watchlist), unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="qd-footer">'
    '<div class="qd-footer-left">QuantDesk Pro · v2.0</div>'
    '<div class="qd-footer-right">Data: yfinance · Alpha Vantage</div>'
    '</div>',
    unsafe_allow_html=True,
)
