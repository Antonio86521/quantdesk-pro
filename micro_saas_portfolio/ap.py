"""ap.py — QuantDesk Pro dashboard shell."""

import datetime as dt
import streamlit as st
from data_loader import load_close_series
from utils import apply_theme, apply_responsive_layout, terminal_ribbon

st.set_page_config(page_title="QuantDesk Pro", layout="wide", page_icon="📊", initial_sidebar_state="expanded")
apply_theme()
apply_responsive_layout()

st.markdown("""
<style>
.home-shell {padding-top: 0.05rem;}
.topbar {display:flex; align-items:center; justify-content:space-between; gap:12px; border:1px solid #17304d; background:linear-gradient(180deg,#06101c 0%, #07111f 100%); padding:10px 14px; margin-bottom:14px;}
.topbar-left {display:flex; align-items:center; gap:14px; flex-wrap:wrap;}
.brand {color:#35c2ff; font-weight:900; font-size:12px; letter-spacing:0.16em; text-transform:uppercase;}
.crumb {color:#7f8ea3; font-size:12px; border-left:1px solid #17304d; padding-left:14px;}
.topbar-right {display:flex; align-items:center; gap:10px;}
.status-dot {width:7px; height:7px; border-radius:50%; background:#00d27a; display:inline-block; box-shadow:0 0 12px rgba(0,210,122,.4);}
.status-text {color:#7f8ea3; font-size:10px; letter-spacing:.16em; text-transform:uppercase;}
.pill-mini {border:1px solid #17304d; color:#d6deeb; border-radius:8px; padding:4px 7px; font-size:10px; font-weight:800;}
.hero-shell {border:1px solid #17304d; border-radius:16px; padding:18px 22px; margin-bottom:14px; background: radial-gradient(circle at top right, rgba(53,194,255,.09), transparent 24%), linear-gradient(180deg,#07111f 0%, #081527 100%);} 
.eyebrow {color:#35c2ff; font-size:10px; font-weight:800; letter-spacing:0.24em; text-transform:uppercase; margin-bottom:10px;}
.hero-title {color:#f6fbff; font-size:20px; font-weight:900; line-height:1.1; margin-bottom:8px;}
.hero-sub {color:#7f8ea3; font-size:13px;}
.pill-chip {border:1px solid #17304d; color:#7f8ea3; border-radius:999px; padding:7px 12px; font-size:11px; background:#07111f; display:block; text-align:center; text-decoration:none;}
.pill-chip.active {color:#35c2ff; border-color:#35c2ff;}
.home-card {border:1px solid #17304d; border-radius:14px; background:linear-gradient(180deg,#07111f 0%, #081426 100%); padding:14px 16px; height:100%; min-height:174px;}
.kpi-label {color:#7f8ea3; font-size:10px; font-weight:800; letter-spacing:0.18em; text-transform:uppercase; margin-bottom:10px;}
.kpi-value {color:#f6fbff; font-size:18px; font-weight:900; margin-bottom:6px; font-family:'Space Mono', monospace;}
.kpi-note-good {color:#00d27a; font-size:12px; font-weight:700;}
.kpi-note {color:#7f8ea3; font-size:12px;}
.sparkbar {display:flex; align-items:flex-end; gap:3px; height:38px; margin-top:14px;}
.sparkbar span {display:block; flex:1; border-radius:2px 2px 0 0; background:#124d55;}
.sparkbar.red span {background:#4a2235;}
.table-shell {border:1px solid #17304d; border-radius:12px; overflow:hidden; background:linear-gradient(180deg,#07111f 0%, #081426 100%);} 
.table-head, .table-row {display:grid; grid-template-columns: 1.4fr 0.8fr 0.7fr 0.6fr; align-items:center;}
.table-head {padding:10px 16px; border-bottom:1px solid #17304d; color:#7f8ea3; font-size:10px; font-weight:800; letter-spacing:0.18em; text-transform:uppercase;}
.table-row {padding:14px 16px; border-bottom:1px solid rgba(23,48,77,.8); color:#f6fbff; font-size:13px; font-weight:700;}
.table-row:last-child {border-bottom:none;}
.t-positive {color:#00f08b;}
.t-negative {color:#ff4d6d;}
.signal {display:inline-block; padding:3px 8px; border-radius:999px; font-size:9px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; border:1px solid #17304d;}
.signal.good {color:#00f08b; background:rgba(0,210,122,.12);}
.signal.bad {color:#ff4d6d; background:rgba(255,92,92,.12);}
.signal.neutral {color:#7f8ea3; background:rgba(127,142,163,.12);}
.footerbar {display:flex; justify-content:space-between; gap:10px; color:#5f7593; font-size:10px; letter-spacing:0.12em; text-transform:uppercase; padding:14px 4px 0 4px;}
.link-reset a {text-decoration:none !important;}
@media (max-width: 768px) {.topbar {padding:9px 10px;} .hero-title {font-size:18px;} .table-head, .table-row {grid-template-columns: 1.2fr 0.8fr 0.7fr 0.8fr; font-size:11px;} .footerbar {flex-direction:column;}}
</style>
""", unsafe_allow_html=True)

def nav_html(path: str, label: str, active: bool = False):
    cls = "pill-chip active" if active else "pill-chip"
    st.markdown(f'<div class="link-reset"><a href="{path}" target="_self" class="{cls}">{label}</a></div>', unsafe_allow_html=True)

hour = dt.datetime.now().hour
if hour < 12:
    greet = "Good morning — markets are open"
elif hour < 18:
    greet = "Good afternoon — markets are open"
else:
    greet = "Good evening — after-hours dashboard"

st.markdown('<div class="home-shell">', unsafe_allow_html=True)
st.markdown("""<div class="topbar"><div class="topbar-left"><div class="brand">QuantDesk Pro</div><div class="crumb">Dashboard</div></div><div class="topbar-right"><span class="status-dot"></span><span class="status-text">Live</span><span class="pill-mini">Pro</span><span class="pill-mini">...</span></div></div>""", unsafe_allow_html=True)
st.markdown(f"""<div class="hero-shell"><div class="eyebrow">Market Intelligence Terminal</div><div class="hero-title">{greet}</div><div class="hero-sub">7 analytical modules · Real-time data · Portfolio sync</div></div>""", unsafe_allow_html=True)

symbols = [("SPY","SPY"),("QQQ","QQQ"),("VIX","^VIX"),("BTC","BTC-USD"),("DXY","DX-Y.NYB")]
items=[]
for label, ticker in symbols:
    try:
        s = load_close_series(ticker, period="5d", source="auto")
        if s is None or len(s) < 2:
            continue
        price = float(s.iloc[-1]); prev = float(s.iloc[-2]); change = (price-prev)/prev
        price_txt = f"{price:,.0f}" if label == "BTC" else f"{price:,.2f}"
        items.append((label, price_txt, f"{change:+.2%}"))
    except Exception:
        pass
if items:
    terminal_ribbon(items)

nav_cols = st.columns([0.9, 1.15, 1.15, 0.95, 0.9, 0.95, 0.8, 0.7])
navs = [
    ("/", "Overview", True),
    ("pages/1_Portfolio.py", "Portfolio Analytics", False),
    ("pages/2_Risk_Attribution.py", "Risk & Attribution", False),
    ("pages/3__Derivatives.py", "Derivatives", False),
    ("pages/4_Vol_Surface.py", "Vol Surface", False),
    ("pages/5_Monte_Carlo__Strategy_Lab.py", "Monte Carlo", False),
    ("pages/6_Screener.py", "Screener", False),
    ("pages/7_Macro.py", "Macro", False),
]
for col, (path, label, active) in zip(nav_cols, navs):
    with col:
        nav_html(path, label, active)

k1,k2,k3 = st.columns(3)
with k1:
    st.markdown("""<div class="home-card"><div class="kpi-label">Portfolio Value</div><div class="kpi-value">$142,840</div><div class="kpi-note">+$3,241 today · <span class="kpi-note-good">+2.32%</span></div><div class="sparkbar"><span style="height:22px"></span><span style="height:25px"></span><span style="height:24px"></span><span style="height:16px;background:#55243a"></span><span style="height:28px"></span><span style="height:31px"></span><span style="height:36px"></span></div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown("""<div class="home-card"><div class="kpi-label">Sharpe Ratio</div><div class="kpi-value">1.84</div><div class="kpi-note-good">Above benchmark · 0.62 alpha</div><div class="sparkbar"><span style="height:14px"></span><span style="height:17px"></span><span style="height:23px"></span><span style="height:24px"></span><span style="height:26px"></span><span style="height:30px"></span><span style="height:34px"></span></div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown("""<div class="home-card"><div class="kpi-label">VaR 95%</div><div class="kpi-value">-1.42%</div><div class="kpi-note">Daily · Historical method</div><div class="sparkbar red"><span style="height:24px"></span><span style="height:17px"></span><span style="height:27px"></span><span style="height:18px"></span><span style="height:31px"></span><span style="height:19px"></span><span style="height:26px"></span></div></div>""", unsafe_allow_html=True)

st.markdown("""<div class="table-shell"><div class="table-head"><div>Ticker</div><div>Price</div><div>Return</div><div>Signal</div></div><div class="table-row"><div>AAPL</div><div>$212.49</div><div class="t-positive">+18.4%</div><div><span class="signal good">Uptrend</span></div></div><div class="table-row"><div>MSFT</div><div>$384.21</div><div class="t-positive">+12.1%</div><div><span class="signal good">Uptrend</span></div></div><div class="table-row"><div>NVDA</div><div>$108.77</div><div class="t-negative">-8.3%</div><div><span class="signal bad">Oversold</span></div></div><div class="table-row"><div>SPY</div><div>$538.42</div><div class="t-positive">+9.7%</div><div><span class="signal neutral">Neutral</span></div></div></div>""", unsafe_allow_html=True)

st.markdown('<div class="footerbar"><div>QuantDesk Pro · v2.0</div><div>Data: yfinance · Alpha Vantage</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


