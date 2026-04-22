"""ap.py — QuantDesk Pro · Dashboard"""

import datetime
import streamlit as st

from data_loader import load_close_series
from utils import (
    apply_theme, apply_responsive_layout, app_footer,
    ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEAL,
    TEXT, TEXT2, TEXT3, BG, BG2, BG3, BG4, BG5,
    GREEN2, RED2,
)

st.set_page_config(
    page_title="QuantDesk Pro — Dashboard",
    layout="wide", page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()
apply_responsive_layout()

# ── Page CSS ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

.block-container {{
  padding-top: 0 !important;
  max-width: 1340px !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
}}

/* ── Topbar ─────────────────────────────────────────────── */
.qd-topbar {{
  position: sticky; top: 0; z-index: 99;
  height: 56px;
  background: rgba(8,11,16,0.96);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex; align-items: center;
  padding: 0 28px; gap: 20px;
}}
/* Never let topbar cover Streamlit sidebar controls */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[kind="header"] {{
  z-index: 100 !important;
  position: relative !important;
}}
.qd-logo {{
  display: flex; align-items: center; gap: 11px; flex-shrink: 0;
  text-decoration: none;
}}
.qd-logo-mark {{
  width: 34px; height: 34px; border-radius: 9px;
  background: linear-gradient(135deg, #2d7ff9 0%, #7c5cfc 100%);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif; font-weight: 800; font-size: 14px; color: #fff;
  box-shadow: 0 0 24px rgba(45,127,249,0.5), 0 0 0 1px rgba(45,127,249,0.2);
  flex-shrink: 0;
}}
.qd-logo-text {{ line-height: 1; }}
.qd-logo-name {{
  font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700;
  color: #e2eaf6; letter-spacing: -0.3px;
}}
.qd-logo-sub {{
  font-size: 9px; color: #4a6280; letter-spacing: 1px;
  text-transform: uppercase; margin-top: 2px;
}}
.qd-ticker-belt {{
  flex: 1; overflow: hidden; min-width: 0;
  border-left: 1px solid rgba(255,255,255,0.06);
  border-right: 1px solid rgba(255,255,255,0.06);
  padding: 0 18px; height: 100%; display: flex; align-items: center;
}}
.qd-ticker-track {{
  display: flex; gap: 32px; white-space: nowrap;
  font-family: 'DM Mono', monospace; font-size: 11.5px;
  animation: belt 36s linear infinite;
}}
.qd-ticker-track:hover {{ animation-play-state: paused; cursor: default; }}
@keyframes belt {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}
.tk-s {{ color: #4a6280; }}
.tk-v {{ color: #c8d8ea; font-weight: 500; margin: 0 3px 0 5px; }}
.tk-u {{ color: #0ec97d; }}
.tk-d {{ color: #f5415a; }}
.qd-tb-right {{
  display: flex; align-items: center; gap: 10px; flex-shrink: 0;
}}
.qd-clock {{
  font-family: 'DM Mono', monospace; font-size: 11px; color: #4a6280;
  padding-right: 14px; border-right: 1px solid rgba(255,255,255,0.07);
  white-space: nowrap; letter-spacing: 0.5px;
}}
.qd-btn {{
  padding: 6px 16px; border-radius: 7px; cursor: pointer;
  font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 500;
  border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05);
  color: #c8d8ea; transition: all 0.15s; white-space: nowrap;
}}
.qd-btn:hover {{
  background: rgba(255,255,255,0.09); border-color: rgba(255,255,255,0.18);
}}
.qd-btn-accent {{
  background: #2d7ff9; border-color: #2d7ff9; color: #fff;
  box-shadow: 0 0 20px rgba(45,127,249,0.3);
}}
.qd-btn-accent:hover {{ background: #1a6de0; box-shadow: 0 0 28px rgba(45,127,249,0.4); }}

/* ── Page wrapper ─────────────────────────────────────── */
.qd-page {{ padding: 0 0 40px; }}

/* ── Hero ─────────────────────────────────────────────── */
.qd-hero {{
  position: relative; overflow: hidden;
  background: linear-gradient(135deg,
    rgba(45,127,249,0.08) 0%,
    rgba(124,92,252,0.05) 40%,
    rgba(8,11,16,0) 70%
  ), #0d1117;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 18px;
  padding: 32px 36px;
  margin: 22px 0 18px;
  display: flex; align-items: center;
  justify-content: space-between; gap: 32px;
}}
.qd-hero-glow {{
  position: absolute; top: -80px; right: -80px;
  width: 320px; height: 320px; border-radius: 50%;
  background: radial-gradient(circle, rgba(45,127,249,0.1) 0%, transparent 65%);
  pointer-events: none;
}}
.qd-hero-glow2 {{
  position: absolute; bottom: -60px; left: 200px;
  width: 200px; height: 200px; border-radius: 50%;
  background: radial-gradient(circle, rgba(124,92,252,0.07) 0%, transparent 65%);
  pointer-events: none;
}}
.qd-hero-left {{ position: relative; z-index: 1; }}
.qd-hero-eyebrow {{
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 10px; color: {ACCENT2}; letter-spacing: 1.8px;
  text-transform: uppercase; font-weight: 700; margin-bottom: 12px;
  background: rgba(45,127,249,0.1); border: 1px solid rgba(45,127,249,0.2);
  padding: 3px 10px; border-radius: 20px;
}}
.qd-hero-eyebrow::before {{
  content: ''; width: 6px; height: 6px; border-radius: 50%;
  background: {ACCENT2}; animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{
  0%, 100% {{ opacity: 1; transform: scale(1); }}
  50% {{ opacity: 0.5; transform: scale(0.8); }}
}}
.qd-hero-h1 {{
  font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 700;
  letter-spacing: -0.8px; color: #e2eaf6; line-height: 1.15; margin-bottom: 10px;
}}
.qd-hero-sub {{
  font-size: 13.5px; color: #5a7a9a; line-height: 1.7;
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
}}
.qd-hero-sub-dot {{
  width: 3px; height: 3px; border-radius: 50%;
  background: #2a3d55; display: inline-block;
}}
.qd-hero-stats {{
  display: flex; flex-shrink: 0; position: relative; z-index: 1;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px; overflow: hidden;
}}
.qd-hs {{
  padding: 20px 28px; text-align: center;
  border-right: 1px solid rgba(255,255,255,0.06);
}}
.qd-hs:last-child {{ border-right: none; }}
.qd-hs-val {{
  font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 300;
  letter-spacing: -1px; line-height: 1;
}}
.qd-hs-lbl {{
  font-size: 9.5px; color: #4a6280; text-transform: uppercase;
  letter-spacing: 1px; margin-top: 7px; font-weight: 600;
}}

/* ── Market strip ──────────────────────────────────────── */
.qd-strip {{
  display: grid; grid-template-columns: repeat(6, 1fr);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px; overflow: hidden;
  margin-bottom: 26px;
}}
.qd-sc {{
  padding: 16px 20px;
  border-right: 1px solid rgba(255,255,255,0.05);
  transition: background 0.15s;
  background: #0d1117;
}}
.qd-sc:last-child {{ border-right: none; }}
.qd-sc:hover {{ background: #111820; }}
.qd-sc-asset {{
  font-size: 9px; color: #4a6280; letter-spacing: 1px;
  text-transform: uppercase; font-weight: 700; margin-bottom: 9px;
}}
.qd-sc-price {{
  font-family: 'DM Mono', monospace; font-size: 20px;
  font-weight: 300; letter-spacing: -0.8px; color: #e2eaf6;
  margin-bottom: 8px; line-height: 1;
}}
.qd-sc-change {{
  display: inline-flex; align-items: center; gap: 3px;
  padding: 3px 8px; border-radius: 5px;
  font-size: 11px; font-weight: 600; font-family: 'DM Mono', monospace;
}}

/* ── Section label ─────────────────────────────────────── */
.qd-section {{
  display: flex; align-items: center; gap: 14px;
  font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
  text-transform: uppercase; color: #2a3d55;
  margin: 28px 0 16px;
}}
.qd-section::after {{
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(90deg, rgba(255,255,255,0.06), transparent);
}}

/* ── Module card ───────────────────────────────────────── */
.qd-card {{
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px; padding: 20px 20px 18px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer; height: 100%;
  display: flex; flex-direction: column;
}}
.qd-card:hover {{
  border-color: rgba(45,127,249,0.35);
  background: rgba(45,127,249,0.04);
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(45,127,249,0.1);
}}
.qd-card-icon {{
  font-size: 22px; margin-bottom: 14px;
  width: 42px; height: 42px; border-radius: 10px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  display: flex; align-items: center; justify-content: center;
}}
.qd-card-name {{
  font-family: 'Syne', sans-serif; font-size: 13.5px; font-weight: 700;
  color: #e2eaf6; margin-bottom: 7px; letter-spacing: -0.2px;
}}
.qd-card-desc {{
  font-size: 11.5px; color: #4a6280; line-height: 1.6;
  flex: 1;
}}
.qd-card-footer {{
  margin-top: 14px; display: flex; align-items: center;
  justify-content: space-between;
}}
.qd-tag {{
  display: inline-block; padding: 3px 9px; border-radius: 5px;
  font-size: 10px; font-weight: 700; letter-spacing: 0.3px;
}}
.qd-card-arrow {{
  font-size: 14px; color: #2a3d55;
  transition: all 0.15s; font-family: 'DM Mono', monospace;
}}
.qd-card:hover .qd-card-arrow {{
  color: {ACCENT2}; transform: translateX(3px);
}}

/* ── Watchlist panel ───────────────────────────────────── */
.qd-panel {{
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px; padding: 20px;
  height: 100%;
}}
.qd-panel-hd {{
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 18px;
}}
.qd-panel-title {{
  font-family: 'Syne', sans-serif; font-size: 14px;
  font-weight: 700; color: #e2eaf6;
}}
.qd-live-badge {{
  display: flex; align-items: center; gap: 5px;
  font-size: 9.5px; font-weight: 700; letter-spacing: 0.8px;
  text-transform: uppercase; color: {GREEN};
  background: rgba(14,201,125,0.1);
  border: 1px solid rgba(14,201,125,0.2);
  padding: 3px 8px; border-radius: 20px;
}}
.qd-live-dot {{
  width: 5px; height: 5px; border-radius: 50%;
  background: {GREEN}; animation: pulse 2s ease-in-out infinite;
}}
.qd-wl-row {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 11px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}}
.qd-wl-row:last-child {{ border-bottom: none; }}
.qd-wl-sym {{
  font-family: 'DM Mono', monospace; font-size: 13px;
  font-weight: 500; color: #c8d8ea;
}}
.qd-wl-co {{
  font-size: 10.5px; color: #3a5570; margin-top: 2px;
}}
.qd-wl-r {{ text-align: right; }}
.qd-wl-px {{
  font-family: 'DM Mono', monospace; font-size: 13.5px;
  font-weight: 400; color: #e2eaf6;
}}
.qd-wl-chg {{ font-size: 11px; margin-top: 2px; font-family: 'DM Mono', monospace; }}

/* ── Quick links ───────────────────────────────────────── */
.qd-quick {{
  display: flex; flex-direction: column; gap: 6px; margin-top: 4px;
}}
.qd-ql {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-radius: 9px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  transition: all 0.15s; text-decoration: none;
}}
.qd-ql:hover {{
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,255,255,0.1);
}}
.qd-ql-label {{ font-size: 12.5px; color: #8ba3bd; font-weight: 500; }}
.qd-ql-arrow {{ font-size: 12px; color: #2a3d55; }}

/* page link styles handled globally in utils.py */

/* ── Tablet ── */
@media (max-width: 1100px) {{
  .qd-strip {{ grid-template-columns: repeat(3, 1fr); }}
  .qd-hero-stats {{ display: none; }}
  .qd-page {{ padding: 0 16px 32px; }}
  .qd-hero {{ padding: 24px 22px; margin: 16px 0 14px; }}
  .qd-hero-h1 {{ font-size: 26px; }}
}}

/* ── Mobile ── */
@media (max-width: 768px) {{
  .qd-topbar {{ padding: 0 14px; gap: 10px; height: 50px; }}
  .qd-ticker-belt {{ display: none; }}
  .qd-logo-sub {{ display: none; }}
  .qd-logo-name {{ font-size: 14px; }}
  .qd-btn:not(.qd-btn-accent) {{ display: none; }}
  .qd-clock {{ display: none; }}
  .qd-page {{ padding: 0 12px 24px; }}
  .qd-hero {{ flex-direction: column; padding: 20px 18px; gap: 16px; }}
  .qd-hero-h1 {{ font-size: 22px; }}
  .qd-hero-sub {{ font-size: 12px; gap: 8px; }}
  .qd-hero-stats {{ width: 100%; justify-content: space-around; }}
  .qd-hs {{ padding: 12px 16px; }}
  .qd-hs-val {{ font-size: 22px; }}
  .qd-strip {{ grid-template-columns: repeat(2, 1fr); border-radius: 10px; }}
  .qd-sc {{ padding: 12px 14px; }}
  .qd-sc-price {{ font-size: 16px; }}
}}

@media (max-width: 480px) {{
  .qd-strip {{ grid-template-columns: repeat(2, 1fr); }}
  .qd-hero-h1 {{ font-size: 19px; }}
}}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _market():
    specs = {
        "S&P 500": "SPY", "NASDAQ 100": "QQQ", "VIX": "^VIX",
        "Bitcoin": "BTC-USD", "DXY": "DX-Y.NYB", "10Y Yield": "^TNX",
    }
    rows = []
    for label, ticker in specs.items():
        try:
            s = load_close_series(ticker, period="5d", source="auto")
            if s is None or len(s) < 2: continue
            last, prev = float(s.iloc[-1]), float(s.iloc[-2])
            chg = (last / prev - 1) * 100
            if label == "10Y Yield":
                val = f"{last:.2f}%"
            elif last >= 10_000:
                val = f"{last:,.0f}"
            elif last >= 1_000:
                val = f"{last:,.2f}"
            else:
                val = f"{last:.2f}"
            rows.append({"label": label, "value": val, "chg": chg})
        except Exception:
            continue
    return rows


@st.cache_data(ttl=300)
def _watchlist():
    specs = [
        ("AAPL", "Apple Inc."), ("MSFT", "Microsoft Corp."),
        ("NVDA", "NVIDIA Corp."), ("GOOGL", "Alphabet Inc."),
        ("AMZN", "Amazon.com"), ("META", "Meta Platforms"),
        ("TSLA", "Tesla Inc."), ("SPY", "S&P 500 ETF"),
    ]
    rows = []
    for ticker, name in specs:
        try:
            s = load_close_series(ticker, period="5d", source="auto")
            if s is None or len(s) < 2: continue
            last, prev = float(s.iloc[-1]), float(s.iloc[-2])
            chg = (last / prev - 1) * 100
            rows.append({"sym": ticker, "name": name, "price": last, "chg": chg})
        except Exception:
            continue
    return rows


# ── Load data ──────────────────────────────────────────────────────────────────
hour     = datetime.datetime.now().hour
greeting = ("Good morning" if hour < 12
            else "Good afternoon" if hour < 18
            else "Good evening")

with st.spinner(""):
    mrows = _market()
    wlist = _watchlist()

n_up   = sum(1 for r in wlist if r["chg"] >= 0)
n_down = len(wlist) - n_up

# ── Ticker tape ────────────────────────────────────────────────────────────────
tape_items = []
for r in mrows:
    cls  = "tk-u" if r["chg"] >= 0 else "tk-d"
    sign = "+" if r["chg"] >= 0 else ""
    tape_items.append(
        f'<span class="tk-s">{r["label"]}</span>'
        f'<span class="tk-v">{r["value"]}</span>'
        f'<span class="{cls}">{sign}{r["chg"]:.2f}%</span>'
    )
tape_inner = "  &nbsp;·&nbsp;  ".join(tape_items)

# ── TOPBAR ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qd-topbar">
  <div class="qd-logo">
    <div class="qd-logo-mark">QD</div>
    <div class="qd-logo-text">
      <div class="qd-logo-name">QuantDesk Pro</div>
      <div class="qd-logo-sub">Portfolio Intelligence</div>
    </div>
  </div>

  <div class="qd-ticker-belt">
    <div class="qd-ticker-track">
      {tape_inner}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{tape_inner}
    </div>
  </div>

  <div class="qd-tb-right">
    <div class="qd-clock" id="qd-clock">--:--:-- EST</div>
    <button class="qd-btn">↓ Export</button>
    <button class="qd-btn qd-btn-accent">＋ New Trade</button>
  </div>

<script>
(function() {{
  function tick() {{
    var d = new Date();
    var el = document.getElementById('qd-clock');
    if (!el) return;
    var h = String(d.getHours()).padStart(2,'0');
    var m = String(d.getMinutes()).padStart(2,'0');
    var s = String(d.getSeconds()).padStart(2,'0');
    el.textContent = h + ':' + m + ':' + s + ' EST';
  }}
  setInterval(tick, 1000);
  tick();
}})();
</script>
""", unsafe_allow_html=True)

# ── PAGE WRAPPER START ─────────────────────────────────────────────────────────
st.markdown('<div class="qd-page">', unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qd-hero">
  <div class="qd-hero-glow"></div>
  <div class="qd-hero-glow2"></div>

  <div class="qd-hero-left">
    <div class="qd-hero-eyebrow">Market Intelligence Terminal</div>
    <div class="qd-hero-h1">{greeting} — welcome back</div>
    <div class="qd-hero-sub">
      <span>14 analytical modules</span>
      <span class="qd-hero-sub-dot"></span>
      <span>Real-time market data</span>
      <span class="qd-hero-sub-dot"></span>
      <span>Cloud portfolio sync</span>
    </div>
  </div>

  <div class="qd-hero-stats">
    <div class="qd-hs">
      <div class="qd-hs-val" style="color:{GREEN};">{n_up}</div>
      <div class="qd-hs-lbl">Advancing</div>
    </div>
    <div class="qd-hs">
      <div class="qd-hs-val" style="color:{RED};">{n_down}</div>
      <div class="qd-hs-lbl">Declining</div>
    </div>
    <div class="qd-hs">
      <div class="qd-hs-val" style="color:{ACCENT2};">14</div>
      <div class="qd-hs-lbl">Modules</div>
    </div>
    <div class="qd-hs">
      <div class="qd-hs-val" style="color:#e2eaf6;">Live</div>
      <div class="qd-hs-lbl">Data Feed</div>
    </div>
  </div>
""", unsafe_allow_html=True)

# ── MARKET STRIP ──────────────────────────────────────────────────────────────
if mrows:
    cells_html = ""
    for r in mrows:
        pos  = r["chg"] >= 0
        clr  = GREEN if pos else RED
        bg   = "rgba(14,201,125,0.12)" if pos else "rgba(245,65,90,0.12)"
        sign = "+" if pos else ""
        arrow = "▲" if pos else "▼"
        cells_html += f"""
<div class="qd-sc">
  <div class="qd-sc-asset">{r["label"]}</div>
  <div class="qd-sc-price">{r["value"]}</div>
  <div class="qd-sc-change" style="color:{clr}; background:{bg};">
    {arrow} {sign}{r["chg"]:.2f}%
  </div>
</div>"""
    st.markdown(f'<div class="qd-strip">{cells_html}</div>', unsafe_allow_html=True)

# ── NAV ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="qd-section">Navigation</div>', unsafe_allow_html=True)

NAV_PAGES = [
    ("ap.py",                                    "🏠", "Home"),
    ("pages/1_Portfolio.py",                     "📈", "Portfolio"),
    ("pages/2_Risk_Attribution.py",              "⚡", "Risk"),
    ("pages/3__Derivatives.py",                  "⚙", "Derivatives"),
    ("pages/4_Vol_Surface.py",                   "🌊", "Vol Surface"),
    ("pages/5_Monte_Carlo__Strategy_Lab.py",     "🎲", "Monte Carlo"),
    ("pages/6_Screener.py",                      "🔍", "Screener"),
    ("pages/7_Macro.py",                         "🌍", "Macro"),
    ("pages/15_Market_Overview.py",              "📡", "Markets"),
    ("pages/16_Alerts.py",                       "🔔", "Alerts"),
]
nav_cols = st.columns(len(NAV_PAGES))
for col, (path, icon, label) in zip(nav_cols, NAV_PAGES):
    with col:
        try:
            st.page_link(path, label=f"{icon} {label}")
        except Exception:
            st.markdown(
                f'<div style="font-size:11px;color:#2a3d55;text-align:center;padding:7px 0;">{icon} {label}</div>',
                unsafe_allow_html=True,
            )

# ── MODULES + WATCHLIST ────────────────────────────────────────────────────────
st.markdown('<div class="qd-section">Modules</div>', unsafe_allow_html=True)

# Updated paths with correct numbering
MODULES = [
    # path, icon, name, desc, tag, tag_color, tag_bg
    ("pages/1_Portfolio.py",                 "📈", "Portfolio Analytics",
     "Performance · Attribution · Technicals · Rolling metrics",
     "Core", ACCENT2, "rgba(45,127,249,0.13)"),

    ("pages/2_Risk_Attribution.py",          "⚡", "Risk & Attribution",
     "VaR · CVaR · Stress Test · Factor Beta · Drawdown",
     "Risk", RED, "rgba(245,65,90,0.13)"),

    ("pages/3__Derivatives.py",              "⚙", "Derivatives Pricer",
     "Black-Scholes · Binomial · Monte Carlo · IV solver",
     "Options", TEAL, "rgba(0,201,167,0.13)"),

    ("pages/4_Vol_Surface.py",               "🌊", "Vol Surface",
     "IV Smile · Term structure · 3D surface · Put/Call skew",
     "Options", TEAL, "rgba(0,201,167,0.13)"),

    ("pages/5_Monte_Carlo__Strategy_Lab.py", "🎲", "Monte Carlo Lab",
     "GBM simulation · Payoff diagrams · Strategy builder",
     "Quant", PURPLE, "rgba(124,92,252,0.13)"),

    ("pages/6_Screener.py",                  "🔍", "Stock Screener",
     "Multi-ticker signals · RSI · Momentum · Volume ratio",
     "Tools", ACCENT2, "rgba(45,127,249,0.13)"),

    ("pages/7_Macro.py",                     "🌍", "Macro Dashboard",
     "Rates · FX · Commodities · Regime detection · Backtest",
     "Macro", PURPLE, "rgba(124,92,252,0.13)"),

    ("pages/8_portfolio_manager.py",         "💼", "Portfolio Manager",
     "Create · Edit · Save portfolios · Fund mode · NAV",
     "Pro", AMBER, "rgba(240,165,0,0.13)"),

    ("pages/9_portfolio_analysis.py",        "📊", "Saved Analysis",
     "Benchmark diagnostics · Export packs · Commentary",
     "Pro", AMBER, "rgba(240,165,0,0.13)"),

    ("pages/10_Factor_Exposure.py",          "🧪", "Factor Exposure",
     "Fama-French regression · Style map · R² decomposition",
     "Quant", PURPLE, "rgba(124,92,252,0.13)"),

    ("pages/15_Market_Overview.py",          "📡", "Market Overview",
     "Live cross-asset heatmap · Sectors · Yield curve",
     "Live", GREEN, "rgba(14,201,125,0.13)"),

    ("pages/16_Alerts.py",                   "🔔", "Price Alerts",
     "Threshold monitoring · Triggered log · Live status",
     "Tools", ACCENT2, "rgba(45,127,249,0.13)"),

    ("pages/17_Trade_Journal.py",            "📓", "Trade Journal",
     "Log trades · P&L curve · Win rate · Setup analytics",
     "Tools", GREEN, "rgba(14,201,125,0.13)"),

    ("pages/18_Reports.py",                  "📄", "Report Generator",
     "Portfolio · Risk digest · Macro snapshot · PDF export",
     "Pro", AMBER, "rgba(240,165,0,0.13)"),
]

main_col, side_col = st.columns([2.6, 1], gap="large")

with main_col:
    # 2 rows of 7 — but use 4 columns for better card sizing
    ROW_SIZE = 4
    rows = [MODULES[i:i+ROW_SIZE] for i in range(0, len(MODULES), ROW_SIZE)]

    for row_mods in rows:
        cols = st.columns(ROW_SIZE, gap="small")
        for col, (path, icon, name, desc, tag, tc, tbg) in zip(cols, row_mods):
            with col:
                st.markdown(f"""
<div class="qd-card">
    <div class="qd-card-icon">{icon}</div>
    <div class="qd-card-name">{name}</div>
    <div class="qd-card-desc">{desc}</div>
    <div class="qd-card-footer">
      <span class="qd-tag" style="color:{tc};background:{tbg};">{tag}</span>
      <span class="qd-card-arrow">→</span>
    </div>
  </div>""", unsafe_allow_html=True)
                try:
                    st.page_link(path, label="Open")
                except Exception:
                    pass
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

with side_col:
    # ── Watchlist ──────────────────────────────────────────
    wl_html = ""
    for r in wlist:
        pos  = r["chg"] >= 0
        clr  = GREEN if pos else RED
        sign = "+" if pos else ""
        arrow = "▲" if pos else "▼"
        wl_html += f"""
<div class="qd-wl-row">
  <div>
    <div class="qd-wl-sym">{r["sym"]}</div>
    <div class="qd-wl-co">{r["name"]}</div>
  </div>
  <div class="qd-wl-r">
    <div class="qd-wl-px">${r["price"]:,.2f}</div>
    <div class="qd-wl-chg" style="color:{clr};">{arrow} {sign}{r["chg"]:.2f}%</div>
  </div>
</div>"""

    st.markdown(f"""
<div class="qd-panel">
  <div class="qd-panel-hd">
    <div class="qd-panel-title">Watchlist</div>
    <div class="qd-live-badge">
      <div class="qd-live-dot"></div>Live
    </div>
  </div>
  {wl_html if wl_html else '<div style="color:#2a3d55;font-size:12px;padding:8px 0;">No data available.</div>'}
</div>
""", unsafe_allow_html=True)

    # ── Quick Access ───────────────────────────────────────
    st.markdown('<div class="qd-section" style="margin-top:20px;">Quick Access</div>', unsafe_allow_html=True)

    QUICK = [
        ("pages/8_portfolio_manager.py",  "💼", "Portfolio Manager"),
        ("pages/9_portfolio_analysis.py", "📊", "Saved Analysis"),
        ("pages/15_Market_Overview.py",   "📡", "Market Overview"),
        ("pages/17_Trade_Journal.py",     "📓", "Trade Journal"),
        ("pages/18_Reports.py",           "📄", "Reports"),
        ("pages/16_Alerts.py",            "🔔", "Price Alerts"),
    ]
    for path, icon, label in QUICK:
        try:
            st.page_link(path, label=f"{icon}  {label}")
        except Exception:
            pass

st.markdown("</div>", unsafe_allow_html=True)  # close qd-page
app_footer()
