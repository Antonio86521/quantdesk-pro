"""ap.py — QuantDesk Pro · Dashboard"""

import datetime
import streamlit as st

from data_loader import load_close_series
from utils import (
    apply_theme, apply_responsive_layout, app_footer,
    ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEAL,
    TEXT, TEXT2, TEXT3, BG2, BG3,
    GREEN2, RED2,
)

st.set_page_config(
    page_title="QuantDesk Pro — Dashboard",
    layout="wide", page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()
apply_responsive_layout()

st.markdown(f"""
<style>
.block-container {{ padding-top: 0 !important; }}
.qd-topbar {{
  position: sticky; top: 0; z-index: 100;
  height: 52px;
  background: rgba(13,17,23,0.94);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255,255,255,0.055);
  display: flex; align-items: center; padding: 0 20px; gap: 14px;
}}
.qd-logo-mark {{
  width: 32px; height: 32px; border-radius: 8px; flex-shrink: 0;
  background: linear-gradient(135deg, #2d7ff9, #7c5cfc);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne',sans-serif; font-weight: 800; font-size: 13px; color: #fff;
  box-shadow: 0 0 18px rgba(45,127,249,0.45);
}}
.qd-brand {{ font-family:'Syne',sans-serif; font-size:14.5px; font-weight:700; color:{TEXT}; letter-spacing:-0.2px; }}
.qd-brand-sub {{ font-size:9.5px; color:{TEXT2}; letter-spacing:0.8px; text-transform:uppercase; margin-top:1px; }}
.qd-ticker-wrap {{
  flex:1; overflow:hidden; height:100%;
  border-left:1px solid rgba(255,255,255,0.055);
  border-right:1px solid rgba(255,255,255,0.055);
  padding:0 14px; display:flex; align-items:center;
}}
.qd-ticker-inner {{
  display:flex; gap:26px; white-space:nowrap;
  font-family:'DM Mono',monospace; font-size:11px;
  animation: qticker 32s linear infinite;
}}
.qd-ticker-inner:hover {{ animation-play-state:paused; }}
@keyframes qticker {{ 0% {{ transform:translateX(0); }} 100% {{ transform:translateX(-50%); }} }}
.tk-sym {{ color:{TEXT2}; margin-right:4px; }}
.tk-val {{ color:{TEXT}; font-weight:500; }}
.tk-up {{ color:{GREEN}; margin-left:3px; }}
.tk-dn {{ color:{RED}; margin-left:3px; }}
.qd-topbar-right {{ display:flex; gap:8px; align-items:center; flex-shrink:0; }}
.qd-clock {{ font-family:'DM Mono',monospace; font-size:10.5px; color:{TEXT2}; white-space:nowrap; padding-right:12px; border-right:1px solid rgba(255,255,255,0.08); }}
.qd-tbtn {{ padding:5px 13px; border-radius:7px; cursor:pointer; font-family:'Inter',sans-serif; font-size:11.5px; font-weight:500; border:1px solid rgba(255,255,255,0.10); background:{BG3}; color:{TEXT}; transition:all 0.14s; }}
.qd-tbtn:hover {{ background:#161e2a; border-color:rgba(255,255,255,0.16); }}
.qd-tbtn-p {{ background:#2d7ff9; border-color:#2d7ff9; color:#fff; }}
.qd-hero {{
  background: linear-gradient(120deg, rgba(45,127,249,0.07) 0%, rgba(124,92,252,0.04) 60%, transparent 100%), {BG2};
  border:1px solid rgba(255,255,255,0.055); border-radius:16px;
  padding:26px 30px; margin:16px 0 16px;
  display:flex; align-items:center; justify-content:space-between; gap:24px;
  position:relative; overflow:hidden;
}}
.qd-hero::before {{
  content:''; position:absolute; top:-60px; right:-60px;
  width:220px; height:220px; border-radius:50%;
  background:radial-gradient(circle, rgba(45,127,249,0.07) 0%, transparent 70%);
  pointer-events:none;
}}
.qd-hero-kicker {{ font-size:9.5px; color:{ACCENT2}; letter-spacing:1.6px; text-transform:uppercase; font-weight:700; margin-bottom:9px; }}
.qd-hero-title {{ font-family:'Syne',sans-serif; font-size:27px; font-weight:700; letter-spacing:-0.6px; color:{TEXT}; line-height:1.15; margin-bottom:7px; }}
.qd-hero-sub {{ font-size:12.5px; color:{TEXT2}; line-height:1.6; }}
.qd-hero-stats {{ display:flex; flex-shrink:0; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.055); border-radius:12px; overflow:hidden; }}
.qd-hs {{ padding:16px 24px; text-align:center; border-right:1px solid rgba(255,255,255,0.055); }}
.qd-hs:last-child {{ border-right:none; }}
.qd-hs-val {{ font-family:'DM Mono',monospace; font-size:24px; font-weight:400; letter-spacing:-0.8px; line-height:1; }}
.qd-hs-lbl {{ font-size:9.5px; color:{TEXT2}; text-transform:uppercase; letter-spacing:0.8px; margin-top:5px; }}
.qd-strip {{ display:grid; grid-template-columns:repeat(6,1fr); background:{BG2}; border:1px solid rgba(255,255,255,0.055); border-radius:14px; overflow:hidden; margin-bottom:20px; }}
.qd-sc {{ padding:15px 17px; border-right:1px solid rgba(255,255,255,0.04); transition:background 0.14s; }}
.qd-sc:last-child {{ border-right:none; }}
.qd-sc:hover {{ background:rgba(255,255,255,0.025); }}
.qd-sc-lbl {{ font-size:9px; color:{TEXT2}; letter-spacing:0.9px; text-transform:uppercase; margin-bottom:7px; }}
.qd-sc-val {{ font-family:'DM Mono',monospace; font-size:18px; font-weight:400; letter-spacing:-0.5px; color:{TEXT}; margin-bottom:6px; }}
.qd-sc-chg {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:10.5px; font-weight:600; font-family:'DM Mono',monospace; }}
.qd-sdash {{ font-size:9.5px; color:#344d68; letter-spacing:1.4px; text-transform:uppercase; font-weight:700; margin:20px 0 10px; display:flex; align-items:center; gap:10px; }}
.qd-sdash::after {{ content:''; flex:1; height:1px; background:rgba(255,255,255,0.055); }}
.qd-mod {{ background:{BG2}; border:1px solid rgba(255,255,255,0.055); border-radius:14px; padding:18px 18px 15px; transition:all 0.18s ease; cursor:pointer; height:100%; }}
.qd-mod:hover {{ border-color:rgba(45,127,249,0.3); background:rgba(45,127,249,0.04); transform:translateY(-2px); box-shadow:0 10px 36px rgba(0,0,0,0.35); }}
.qd-mod-icon {{ font-size:20px; margin-bottom:11px; }}
.qd-mod-title {{ font-family:'Syne',sans-serif; font-size:13px; font-weight:600; color:{TEXT}; margin-bottom:5px; }}
.qd-mod-sub {{ font-size:11px; color:{TEXT2}; line-height:1.55; }}
.qd-mod-tag {{ display:inline-block; margin-top:11px; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:600; }}
.qd-wl {{ display:flex; align-items:center; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.04); }}
.qd-wl:last-child {{ border-bottom:none; }}
.qd-wl-sym {{ font-family:'DM Mono',monospace; font-size:13px; font-weight:500; color:{TEXT}; }}
.qd-wl-name {{ font-size:10.5px; color:{TEXT2}; margin-top:1px; }}
.qd-wl-price {{ font-family:'DM Mono',monospace; font-size:14px; color:{TEXT}; text-align:right; }}
.qd-wl-chg {{ font-size:11px; text-align:right; margin-top:2px; }}
@media(max-width:900px) {{ .qd-strip {{ grid-template-columns:repeat(3,1fr); }} .qd-hero-stats {{ display:none; }} }}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _market():
    specs = {"S&P 500":"SPY","NASDAQ":"QQQ","VIX":"^VIX","BTC":"BTC-USD","DXY":"DX-Y.NYB","10Y Yield":"^TNX"}
    rows = []
    for label, ticker in specs.items():
        try:
            s = load_close_series(ticker, period="5d", source="auto")
            if s is None or len(s) < 2: continue
            last, prev = float(s.iloc[-1]), float(s.iloc[-2])
            chg = (last / prev - 1) * 100
            val = (f"{last:.2f}%" if label=="10Y Yield" else f"{last:,.0f}" if last>=10000 else f"{last:,.2f}")
            rows.append({"label":label,"value":val,"chg":chg})
        except Exception: continue
    return rows


@st.cache_data(ttl=300)
def _watch():
    specs = [("AAPL","Apple"),("MSFT","Microsoft"),("NVDA","NVIDIA"),("GOOGL","Alphabet"),("AMZN","Amazon"),("META","Meta"),("TSLA","Tesla"),("SPY","S&P 500 ETF")]
    rows = []
    for ticker, name in specs:
        try:
            s = load_close_series(ticker, period="5d", source="auto")
            if s is None or len(s) < 2: continue
            last, prev = float(s.iloc[-1]), float(s.iloc[-2])
            chg = (last / prev - 1) * 100
            rows.append({"sym":ticker,"name":name,"price":last,"chg":chg})
        except Exception: continue
    return rows


hour     = datetime.datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
mrows    = _market()
wlist    = _watch()
n_up     = sum(1 for r in wlist if r["chg"] >= 0)
n_down   = len(wlist) - n_up

# ── TOPBAR ────────────────────────────────────────────────────────────────────
items = []
for r in mrows:
    cls = "tk-up" if r["chg"] >= 0 else "tk-dn"
    s   = "+" if r["chg"] >= 0 else ""
    items.append(f'<span class="tk-sym">{r["label"]}</span><span class="tk-val">{r["value"]}</span><span class="{cls}">{s}{r["chg"]:.2f}%</span>')
tape = "  ·  ".join(items)

st.markdown(f"""
<div class="qd-topbar">
  <div style="display:flex;align-items:center;gap:10px;flex-shrink:0;">
    <div class="qd-logo-mark">QD</div>
    <div><div class="qd-brand">QuantDesk Pro</div><div class="qd-brand-sub">Portfolio Intelligence</div></div>
  </div>
  <div class="qd-ticker-wrap">
    <div class="qd-ticker-inner">{tape}&nbsp;&nbsp;&nbsp;&nbsp;{tape}</div>
  </div>
  <div class="qd-topbar-right">
    <div class="qd-clock" id="qd-clock">--:--:--</div>
    <button class="qd-tbtn">↓ Export</button>
    <button class="qd-tbtn qd-tbtn-p">＋ New Trade</button>
  </div>
</div>
<script>
(function(){{function tick(){{var d=new Date(),el=document.getElementById('qd-clock');
if(el)el.textContent=String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0')+':'+String(d.getSeconds()).padStart(2,'0')+' EST';}}
setInterval(tick,1000);tick();}})();
</script>""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qd-hero">
  <div>
    <div class="qd-hero-kicker">Market Intelligence Terminal</div>
    <div class="qd-hero-title">{greeting} — welcome back</div>
    <div class="qd-hero-sub">14 analytical modules &nbsp;·&nbsp; Real-time market data &nbsp;·&nbsp; Cloud portfolio sync</div>
  </div>
  <div class="qd-hero-stats">
    <div class="qd-hs"><div class="qd-hs-val" style="color:{GREEN};">{n_up}</div><div class="qd-hs-lbl">Advancing</div></div>
    <div class="qd-hs"><div class="qd-hs-val" style="color:{RED};">{n_down}</div><div class="qd-hs-lbl">Declining</div></div>
    <div class="qd-hs"><div class="qd-hs-val" style="color:{ACCENT2};">14</div><div class="qd-hs-lbl">Modules</div></div>
  </div>
</div>""", unsafe_allow_html=True)

# ── STRIP ──────────────────────────────────────────────────────────────────────
if mrows:
    cells = []
    for r in mrows:
        pos  = r["chg"] >= 0
        clr  = GREEN if pos else RED
        bg   = GREEN2 if pos else RED2
        s    = "+" if pos else ""
        cells.append(f'<div class="qd-sc"><div class="qd-sc-lbl">{r["label"]}</div><div class="qd-sc-val">{r["value"]}</div><div class="qd-sc-chg" style="color:{clr};background:{bg};">{s}{r["chg"]:.2f}%</div></div>')
    st.markdown(f'<div class="qd-strip">{"".join(cells)}</div>', unsafe_allow_html=True)

# ── NAV ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="qd-sdash">Navigation</div>', unsafe_allow_html=True)
nav_cols = st.columns(10)
nav_pages = [
    ("ap.py","🏠 Home"),("pages/1_Portfolio.py","📈 Portfolio"),
    ("pages/2_Risk_Attribution.py","⚡ Risk"),("pages/3__Derivatives.py","⚙ Derivatives"),
    ("pages/4_Vol_Surface.py","🌊 Vol Surface"),("pages/5_Monte_Carlo__Strategy_Lab.py","🎲 Monte Carlo"),
    ("pages/6_Screener.py","🔍 Screener"),("pages/7_Macro.py","🌍 Macro"),
    ("pages/15_Market_Overview.py","📡 Markets"),("pages/16_Alerts.py","🔔 Alerts"),
]
for col, (path, label) in zip(nav_cols, nav_pages):
    with col: st.page_link(path, label=label)

# ── MODULES + WATCHLIST ────────────────────────────────────────────────────────
st.markdown('<div class="qd-sdash" style="margin-top:22px;">Modules</div>', unsafe_allow_html=True)

MODS = [
    ("pages/1_Portfolio.py","📈","Portfolio Analytics","Performance · Attribution · Technicals","Core",ACCENT2,"rgba(45,127,249,0.13)"),
    ("pages/2_Risk_Attribution.py","⚡","Risk & Attribution","VaR · Stress Test · Factor Beta","Risk",RED,"rgba(245,65,90,0.13)"),
    ("pages/3__Derivatives.py","⚙","Derivatives Pricer","Black-Scholes · Binomial · Monte Carlo","Options",TEAL,"rgba(0,201,167,0.13)"),
    ("pages/4_Vol_Surface.py","🌊","Vol Surface","IV Smile · Term Structure · 3D","Options",TEAL,"rgba(0,201,167,0.13)"),
    ("pages/5_Monte_Carlo__Strategy_Lab.py","🎲","Monte Carlo Lab","GBM simulation · Payoff diagrams","Quant",PURPLE,"rgba(124,92,252,0.13)"),
    ("pages/6_Screener.py","🔍","Stock Screener","Multi-ticker · RSI · Momentum","Tools",ACCENT2,"rgba(45,127,249,0.13)"),
    ("pages/7_Macro.py","🌍","Macro Dashboard","Rates · FX · Commodities · Regime","Macro",PURPLE,"rgba(124,92,252,0.13)"),
    ("pages/8_portfolio_manager.py","💼","Portfolio Manager","Create · Edit · Save portfolios","Pro",AMBER,"rgba(240,165,0,0.13)"),
    ("pages/9_portfolio_analysis.py","📊","Saved Analysis","Benchmark · Diagnostics · Export","Pro",AMBER,"rgba(240,165,0,0.13)"),
    ("pages/10_Factor_Exposure.py","🧪","Factor Exposure","Fama-French · Style map · R²","Quant",PURPLE,"rgba(124,92,252,0.13)"),
    ("pages/15_Market_Overview.py","📡","Market Overview","Live heatmap · Sectors · Yield curve","Live",GREEN,"rgba(14,201,125,0.13)"),
    ("pages/16_Alerts.py","🔔","Price Alerts","Threshold monitoring · Live status","Tools",ACCENT2,"rgba(45,127,249,0.13)"),
    ("pages/17_Trade_Journal.py","📓","Trade Journal","Log · P&L · Win rate · Equity curve","Tools",GREEN,"rgba(14,201,125,0.13)"),
    ("pages/18_Reports.py","📄","Report Generator","Portfolio · Risk · Macro · Export","Pro",AMBER,"rgba(240,165,0,0.13)"),
]

main_col, watch_col = st.columns([2.5, 1])

with main_col:
    row1 = st.columns(7)
    row2 = st.columns(7)
    for i, (path, icon, title, sub, tag, tc, tbg) in enumerate(MODS):
        col = row1[i] if i < 7 else row2[i-7]
        with col:
            st.markdown(f"""
<div class="qd-mod">
  <div class="qd-mod-icon">{icon}</div>
  <div class="qd-mod-title">{title}</div>
  <div class="qd-mod-sub">{sub}</div>
  <div class="qd-mod-tag" style="color:{tc};background:{tbg};">{tag}</div>
</div>""", unsafe_allow_html=True)
            st.page_link(path, label=f"Open →")

with watch_col:
    wl_rows = "".join([
        f'''<div class="qd-wl">
  <div><div class="qd-wl-sym">{r["sym"]}</div><div class="qd-wl-name">{r["name"]}</div></div>
  <div>
    <div class="qd-wl-price">${r["price"]:,.2f}</div>
    <div class="qd-wl-chg" style="color:{GREEN if r['chg']>=0 else RED};">{'+' if r['chg']>=0 else ''}{r['chg']:.2f}%</div>
  </div>
</div>'''
        for r in wlist
    ]) if wlist else f'<div style="color:{TEXT2};font-size:12px;padding:10px 0;">No data.</div>'

    st.markdown(f"""
<div style="background:{BG2};border:1px solid rgba(255,255,255,0.055);border-radius:14px;padding:18px;">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
    <div style="font-family:'Syne',sans-serif;font-size:13.5px;font-weight:600;color:{TEXT};">Watchlist</div>
    <div style="font-size:10px;color:{GREEN};letter-spacing:0.8px;text-transform:uppercase;
                background:rgba(14,201,125,0.1);padding:2px 7px;border-radius:4px;">● Live</div>
  </div>
  {wl_rows}
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="qd-sdash" style="margin-top:16px;">Quick Access</div>', unsafe_allow_html=True)
    for path, label in [
        ("pages/8_portfolio_manager.py","💼 Portfolio Manager"),
        ("pages/9_portfolio_analysis.py","📊 Saved Analysis"),
        ("pages/15_Market_Overview.py","📡 Market Overview"),
        ("pages/17_Trade_Journal.py","📓 Trade Journal"),
        ("pages/18_Reports.py","📄 Reports"),
    ]:
        st.page_link(path, label=label)

app_footer()
