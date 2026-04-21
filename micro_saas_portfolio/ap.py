"""
ap.py — QuantDesk Pro dashboard.
Apex Capital design: dark navy palette, Syne + DM Mono, glass cards,
live ticker tape, real market data, polished layout.
"""

import datetime
import streamlit as st

from data_loader import load_close_series, load_macro_snapshot
from utils import apply_theme, apply_responsive_layout, app_footer, ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEXT, TEXT2, BG2, BG3, BG4, BORDER

st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

apply_theme()
apply_responsive_layout()

# ── Extra homepage-specific styles ───────────────────────────────────────────
st.markdown(
    f"""
    <style>
    /* Remove default Streamlit top padding on home */
    .block-container {{ padding-top: 0 !important; }}

    /* ── Topbar ── */
    .apex-topbar {{
      height: 54px;
      background: {BG2};
      border-bottom: 1px solid rgba(255,255,255,0.06);
      display: flex; align-items: center;
      padding: 0 22px; gap: 16px;
      position: sticky; top: 0; z-index: 50;
    }}
    .apex-logo-mark {{
      width: 34px; height: 34px; border-radius: 9px; flex-shrink: 0;
      background: linear-gradient(135deg, #2f80ed 0%, #7c5cfc 100%);
      display: flex; align-items: center; justify-content: center;
      font-family: 'Syne', sans-serif; font-weight: 800; font-size: 14px; color: #fff;
      box-shadow: 0 0 22px rgba(47,128,237,0.4);
    }}
    .apex-brand {{
      font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700;
      letter-spacing: -0.3px; color: {TEXT};
    }}
    .apex-brand-sub {{
      font-size: 10px; color: {TEXT2}; letter-spacing: 0.8px;
      text-transform: uppercase; margin-top: 1px;
    }}

    /* ── Ticker tape ── */
    .ticker-wrap {{
      flex: 1; overflow: hidden; display: flex; padding: 0 16px;
      border-left: 1px solid rgba(255,255,255,0.06);
      border-right: 1px solid rgba(255,255,255,0.06);
    }}
    .ticker-inner {{
      display: flex; gap: 28px;
      animation: tickerscroll 30s linear infinite;
      white-space: nowrap; font-family: 'DM Mono', monospace; font-size: 11px;
    }}
    .ticker-inner:hover {{ animation-play-state: paused; }}
    @keyframes tickerscroll {{
      0%   {{ transform: translateX(0); }}
      100% {{ transform: translateX(-50%); }}
    }}
    .t-sym {{ color: {TEXT2}; }}
    .t-val {{ color: {TEXT}; font-weight: 500; margin: 0 2px 0 5px; }}
    .t-up  {{ color: {GREEN}; }}
    .t-dn  {{ color: {RED}; }}

    /* ── Topbar right ── */
    .apex-topbar-right {{
      display: flex; gap: 8px; align-items: center; flex-shrink: 0;
    }}
    .apex-clock {{
      font-family: 'DM Mono', monospace; font-size: 11px; color: {TEXT2};
      border-right: 1px solid rgba(255,255,255,0.08); padding-right: 12px;
    }}
    .apex-btn {{
      padding: 5px 13px; border-radius: 7px;
      font-size: 11.5px; font-weight: 500; cursor: pointer;
      border: 1px solid rgba(255,255,255,0.11);
      background: {BG3}; color: {TEXT};
      font-family: 'Inter', sans-serif;
    }}
    .apex-btn-p {{
      background: #2f80ed; border-color: #2f80ed; color: #fff;
    }}

    /* ── Hero ── */
    .apex-hero {{
      background: {BG2};
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 14px;
      padding: 22px 24px;
      margin: 16px 0 14px;
      display: flex; align-items: center; justify-content: space-between; gap: 20px;
    }}
    .apex-hero-kicker {{
      font-size: 9.5px; color: {ACCENT2};
      letter-spacing: 1.4px; text-transform: uppercase;
      font-weight: 600; margin-bottom: 8px;
    }}
    .apex-hero-title {{
      font-family: 'Syne', sans-serif;
      font-size: 22px; font-weight: 700;
      letter-spacing: -0.4px; color: {TEXT};
      line-height: 1.2; margin-bottom: 6px;
    }}
    .apex-hero-sub {{ font-size: 12px; color: {TEXT2}; }}
    .apex-hero-stats {{
      display: flex; gap: 24px; flex-shrink: 0;
    }}
    .apex-hs {{
      text-align: center;
    }}
    .apex-hs-val {{
      font-family: 'DM Mono', monospace; font-size: 20px;
      font-weight: 500; letter-spacing: -0.5px;
    }}
    .apex-hs-lbl {{
      font-size: 9.5px; color: {TEXT2};
      text-transform: uppercase; letter-spacing: 0.8px;
      margin-top: 3px;
    }}

    /* ── Market strip ── */
    .apex-strip {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      background: {BG2};
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 14px; overflow: hidden;
      margin-bottom: 14px;
    }}
    .apex-strip-cell {{
      padding: 14px 16px;
      border-right: 1px solid rgba(255,255,255,0.04);
    }}
    .apex-strip-cell:last-child {{ border-right: none; }}
    .apex-sc-lbl {{
      font-size: 9px; color: {TEXT2};
      letter-spacing: 0.8px; text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .apex-sc-val {{
      font-family: 'DM Mono', monospace; font-size: 16px;
      font-weight: 500; letter-spacing: -0.5px;
      margin-bottom: 5px; color: {TEXT};
    }}
    .apex-sc-chg {{
      font-size: 10.5px; padding: 2px 7px;
      border-radius: 4px; display: inline-block;
    }}

    /* ── Module grid ── */
    .apex-module {{
      background: {BG2};
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 14px; padding: 16px 18px;
      cursor: pointer; transition: border-color 0.14s;
      height: 100%;
    }}
    .apex-module:hover {{ border-color: rgba(255,255,255,0.14); }}
    .apex-mod-icon {{
      font-size: 22px; margin-bottom: 10px;
    }}
    .apex-mod-title {{
      font-family: 'Syne', sans-serif;
      font-size: 13px; font-weight: 600; color: {TEXT};
      margin-bottom: 4px;
    }}
    .apex-mod-sub {{ font-size: 11px; color: {TEXT2}; line-height: 1.5; }}
    .apex-mod-tag {{
      display: inline-block; margin-top: 10px;
      padding: 2px 7px; border-radius: 4px;
      font-size: 10px; font-weight: 500;
      background: rgba(47,128,237,0.12); color: {ACCENT2};
    }}

    /* ── Section heading ── */
    .apex-section {{
      font-family: 'Syne', sans-serif;
      font-size: 11px; font-weight: 600;
      color: {TEXT2}; letter-spacing: 1px;
      text-transform: uppercase; margin-bottom: 12px;
    }}

    /* ── Watchlist ── */
    .wl-row {{
      display: flex; align-items: center; justify-content: space-between;
      padding: 10px 14px; background: {BG3};
      border-radius: 8px; margin-bottom: 5px;
      border: 1px solid transparent; transition: border-color 0.13s;
    }}
    .wl-row:hover {{ border-color: rgba(255,255,255,0.08); }}
    .wl-sym {{ font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 500; }}
    .wl-name {{ font-size: 10px; color: {TEXT2}; margin-top: 1px; }}
    .wl-price {{ font-family: 'DM Mono', monospace; font-size: 14px; text-align: right; }}
    .wl-chg {{ font-size: 10.5px; text-align: right; margin-top: 1px; }}

    @media (max-width: 900px) {{
      .apex-strip {{ grid-template-columns: repeat(3, 1fr); }}
      .apex-hero-stats {{ display: none; }}
    }}
    @media (max-width: 600px) {{
      .apex-strip {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Data loaders ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _market_data():
    specs = {
        "S&P 500": "SPY",
        "NASDAQ": "QQQ",
        "VIX": "^VIX",
        "BTC": "BTC-USD",
        "DXY": "DX-Y.NYB",
        "10Y Yield": "^TNX",
    }
    rows = []
    for label, ticker in specs.items():
        try:
            s = load_close_series(ticker, period="5d", source="auto")
            if s is None or s.empty or len(s) < 2:
                continue
            last = float(s.iloc[-1])
            prev = float(s.iloc[-2])
            chg = (last / prev - 1) * 100
            if label == "10Y Yield":
                val = f"{last:.2f}%"
            elif last >= 10_000:
                val = f"{last:,.0f}"
            elif last >= 100:
                val = f"{last:,.2f}"
            else:
                val = f"{last:.2f}"
            rows.append({"label": label, "value": val, "chg": chg})
        except Exception:
            continue
    return rows


@st.cache_data(ttl=300)
def _watchlist_data():
    tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "SPY"]
    names   = ["Apple", "Microsoft", "NVIDIA", "Alphabet", "Amazon", "Meta", "Tesla", "S&P 500 ETF"]
    rows = []
    for t, n in zip(tickers, names):
        try:
            s = load_close_series(t, period="5d", source="auto")
            if s is None or s.empty or len(s) < 2:
                continue
            last = float(s.iloc[-1])
            prev = float(s.iloc[-2])
            chg = (last / prev - 1) * 100
            rows.append({"sym": t, "name": n, "price": last, "chg": chg})
        except Exception:
            continue
    return rows


# ── Build ticker tape HTML ─────────────────────────────────────────────────────

def _ticker_tape_html(market_rows: list) -> str:
    items = []
    for r in market_rows:
        cls = "t-up" if r["chg"] >= 0 else "t-dn"
        sign = "+" if r["chg"] >= 0 else ""
        items.append(
            f'<span class="t-sym">{r["label"]}</span>'
            f'<span class="t-val">{r["value"]}</span>'
            f'<span class="{cls}">{sign}{r["chg"]:.2f}%</span>'
        )
    inner = "  ·  ".join(items)
    # duplicate for seamless loop
    return f'<div class="ticker-inner">{inner}&nbsp;&nbsp;&nbsp;&nbsp;{inner}</div>'


# ── Hour-based greeting ────────────────────────────────────────────────────────
hour = datetime.datetime.now().hour
if hour < 12:
    greeting = "Good morning"
elif hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"


# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner(""):
    market_rows  = _market_data()
    watchlist    = _watchlist_data()

ticker_tape = _ticker_tape_html(market_rows)


# ── TOPBAR ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="apex-topbar">
      <div style="display:flex;align-items:center;gap:10px;flex-shrink:0;">
        <div class="apex-logo-mark">QD</div>
        <div>
          <div class="apex-brand">QuantDesk Pro</div>
          <div class="apex-brand-sub">Portfolio Intelligence</div>
        </div>
      </div>
      <div class="ticker-wrap">
        {ticker_tape}
      </div>
      <div class="apex-topbar-right">
        <div class="apex-clock" id="apex-clock">—</div>
        <button class="apex-btn">Export</button>
        <button class="apex-btn apex-btn-p">+ New Trade</button>
      </div>
    </div>
    <script>
      function _updateClock() {{
        const d = new Date();
        const hh = String(d.getHours()).padStart(2,'0');
        const mm = String(d.getMinutes()).padStart(2,'0');
        const ss = String(d.getSeconds()).padStart(2,'0');
        const el = document.getElementById('apex-clock');
        if(el) el.textContent = hh+':'+mm+':'+ss+' EST';
      }}
      setInterval(_updateClock, 1000); _updateClock();
    </script>
    """,
    unsafe_allow_html=True,
)


# ── HERO ──────────────────────────────────────────────────────────────────────
n_up   = sum(1 for r in watchlist if r["chg"] >= 0)
n_down = len(watchlist) - n_up

st.markdown(
    f"""
    <div class="apex-hero">
      <div>
        <div class="apex-hero-kicker">Market Intelligence Terminal</div>
        <div class="apex-hero-title">{greeting} — welcome back</div>
        <div class="apex-hero-sub">
          10 analytical modules · Real-time market data · Cloud portfolio sync
        </div>
      </div>
      <div class="apex-hero-stats">
        <div class="apex-hs">
          <div class="apex-hs-val" style="color:{GREEN};">{n_up}</div>
          <div class="apex-hs-lbl">Advancing</div>
        </div>
        <div style="width:1px;background:rgba(255,255,255,0.06);"></div>
        <div class="apex-hs">
          <div class="apex-hs-val" style="color:{RED};">{n_down}</div>
          <div class="apex-hs-lbl">Declining</div>
        </div>
        <div style="width:1px;background:rgba(255,255,255,0.06);"></div>
        <div class="apex-hs">
          <div class="apex-hs-val" style="color:{ACCENT2};">10</div>
          <div class="apex-hs-lbl">Modules</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── MARKET STRIP ──────────────────────────────────────────────────────────────
if market_rows:
    cells = []
    for r in market_rows:
        pos = r["chg"] >= 0
        clr = GREEN if pos else RED
        bg  = "rgba(14,203,129,0.1)" if pos else "rgba(246,70,93,0.1)"
        sign = "+" if pos else ""
        cells.append(
            f'<div class="apex-strip-cell">'
            f'  <div class="apex-sc-lbl">{r["label"]}</div>'
            f'  <div class="apex-sc-val">{r["value"]}</div>'
            f'  <div class="apex-sc-chg" style="color:{clr};background:{bg};">'
            f'    {sign}{r["chg"]:.2f}%'
            f'  </div>'
            f'</div>'
        )
    st.markdown(
        f'<div class="apex-strip">{"".join(cells)}</div>',
        unsafe_allow_html=True,
    )


# ── NAV LINKS ─────────────────────────────────────────────────────────────────
st.markdown('<div class="apex-section">Navigation</div>', unsafe_allow_html=True)
nav_cols = st.columns(9)
pages = [
    ("ap.py",                                 "🏠 Home"),
    ("pages/1_Portfolio.py",                  "📈 Portfolio"),
    ("pages/2_Risk_Attribution.py",           "⚡ Risk"),
    ("pages/3__Derivatives.py",               "⚙ Derivatives"),
    ("pages/4_Vol_Surface.py",                "🌊 Vol Surface"),
    ("pages/5_Monte_Carlo__Strategy_Lab.py",  "🎲 Monte Carlo"),
    ("pages/6_Screener.py",                   "🔍 Screener"),
    ("pages/7_Macro.py",                      "🌍 Macro"),
    ("pages/8_portfolio_manager.py",          "💼 Portfolios"),
]
for col, (path, label) in zip(nav_cols, pages):
    with col:
        st.page_link(path, label=label)


# ── MODULE CARDS + WATCHLIST ──────────────────────────────────────────────────
st.markdown('<div class="apex-section" style="margin-top:18px;">Modules</div>', unsafe_allow_html=True)

modules = [
    ("pages/1_Portfolio.py",                 "📈", "Portfolio Analytics",     "Performance · Attribution · Technicals",       "Core"),
    ("pages/2_Risk_Attribution.py",          "⚡", "Risk & Attribution",      "VaR · Stress Test · Factor Beta",              "Risk"),
    ("pages/3__Derivatives.py",              "⚙", "Derivatives Pricer",      "Black-Scholes · Binomial · Monte Carlo",       "Options"),
    ("pages/4_Vol_Surface.py",               "🌊", "Vol Surface",             "IV Smile · Term Structure · 3D Surface",       "Options"),
    ("pages/5_Monte_Carlo__Strategy_Lab.py", "🎲", "Monte Carlo Lab",         "Strategy payoffs · Path simulation",           "Analytics"),
    ("pages/6_Screener.py",                  "🔍", "Stock Screener",          "Multi-ticker signals · Momentum · RSI",        "Tools"),
    ("pages/7_Macro.py",                     "🌍", "Macro Dashboard",         "Rates · FX · Commodities · Economic data",     "Macro"),
    ("pages/8_portfolio_manager.py",         "💼", "Portfolio Manager",       "Create, edit and save portfolios",             "Pro"),
    ("pages/9_portfolio_analysis.py",        "📊", "Saved Portfolio Analysis","Benchmark diagnostics · Export packs",         "Pro"),
    ("pages/10_Factor_Exposure.py",          "🧪", "Factor Exposure",         "Fama-French regression · Style map",           "Pro"),
]

tag_colors = {
    "Core":      (ACCENT2,  "rgba(47,128,237,0.12)"),
    "Risk":      (RED,      "rgba(246,70,93,0.12)"),
    "Options":   ("#00c9a7","rgba(0,201,167,0.12)"),
    "Analytics": (AMBER,    "rgba(240,165,0,0.12)"),
    "Tools":     (ACCENT2,  "rgba(47,128,237,0.12)"),
    "Macro":     (PURPLE,   "rgba(124,92,252,0.12)"),
    "Pro":       ("#d4a853","rgba(212,168,83,0.12)"),
}

main_col, watch_col = st.columns([2.2, 1])

with main_col:
    # 5 + 5 layout
    row1 = st.columns(5)
    row2 = st.columns(5)
    for i, (path, icon, title, sub, tag) in enumerate(modules):
        col = row1[i] if i < 5 else row2[i - 5]
        tc, tbg = tag_colors.get(tag, (ACCENT2, "rgba(47,128,237,0.12)"))
        with col:
            st.markdown(
                f"""
                <div class="apex-module">
                  <div class="apex-mod-icon">{icon}</div>
                  <div class="apex-mod-title">{title}</div>
                  <div class="apex-mod-sub">{sub}</div>
                  <div class="apex-mod-tag" style="color:{tc};background:{tbg};">{tag}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(path, label=f"Open {title}")

with watch_col:
    st.markdown('<div class="apex-section">Watchlist</div>', unsafe_allow_html=True)

    if watchlist:
        rows_html = ""
        for r in watchlist:
            pos = r["chg"] >= 0
            clr = GREEN if pos else RED
            sign = "+" if pos else ""
            rows_html += (
                f'<div class="wl-row">'
                f'  <div>'
                f'    <div class="wl-sym">{r["sym"]}</div>'
                f'    <div class="wl-name">{r["name"]}</div>'
                f'  </div>'
                f'  <div>'
                f'    <div class="wl-price">${r["price"]:,.2f}</div>'
                f'    <div class="wl-chg" style="color:{clr};">{sign}{r["chg"]:.2f}%</div>'
                f'  </div>'
                f'</div>'
            )
        st.markdown(rows_html, unsafe_allow_html=True)
    else:
        st.info("No watchlist data available right now.")

    st.markdown('<div class="apex-section" style="margin-top:18px;">Quick Access</div>', unsafe_allow_html=True)
    st.page_link("pages/8_portfolio_manager.py",  label="💼 Portfolio Manager")
    st.page_link("pages/9_portfolio_analysis.py", label="📊 Saved Analysis")
    st.page_link("pages/6_Screener.py",           label="🔍 Run Screener")
    st.page_link("pages/7_Macro.py",              label="🌍 Macro Dashboard")


app_footer()
