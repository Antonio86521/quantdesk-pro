"""
ap.py — QuantDesk Pro home page.
Place this file at the ROOT of your project (same level as the pages/ folder).
No login required.
"""

import streamlit as st
from data_loader import load_close_series
from utils import apply_theme, apply_responsive_layout

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuantDesk Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
apply_theme()
apply_responsive_layout()


# ── Extra home-page CSS ───────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .hero-wrap {
        position: relative;
        overflow: hidden;
        border: 1px solid #1a2840;
        border-radius: 14px;
        padding: 32px 36px 28px 36px;
        background:
            radial-gradient(circle at top right,  rgba(0,212,255,0.07) 0%, transparent 40%),
            radial-gradient(circle at bottom left, rgba(124,92,252,0.07) 0%, transparent 40%),
            linear-gradient(180deg, #0a1120 0%, #0d1628 100%);
        margin-bottom: 20px;
    }

    .hero-eyebrow {
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        color: #00d4ff;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 38px;
        font-weight: 600;
        line-height: 1.1;
        letter-spacing: -0.02em;
        color: #e2eaf5;
        margin-bottom: 10px;
    }

    .hero-title span.c1 { color: #00d4ff; }
    .hero-title span.c2 { color: #7c5cfc; }

    .hero-sub {
        font-family: 'DM Sans', sans-serif;
        color: #5a7a9a;
        font-size: 14px;
        line-height: 1.7;
        max-width: 700px;
        margin-bottom: 20px;
        font-weight: 300;
    }

    .pill-row { display: flex; gap: 8px; flex-wrap: wrap; }

    .pill {
        border: 1px solid #1a2840;
        border-radius: 999px;
        padding: 5px 12px;
        font-family: 'DM Sans', sans-serif;
        font-size: 11px;
        font-weight: 500;
        color: #5a7a9a;
        background: rgba(255,255,255,0.02);
    }

    /* Market bar */
    .mbar-wrap {
        border: 1px solid #1a2840;
        border-radius: 10px;
        overflow: hidden;
        background: linear-gradient(180deg, #0a1120 0%, #0d1628 100%);
        margin-bottom: 20px;
    }

    .mbar-header {
        padding: 8px 16px;
        border-bottom: 1px solid #1a2840;
        font-family: 'Space Mono', monospace;
        font-size: 9px;
        color: #5a7a9a;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .mbar-body { display: flex; flex-wrap: wrap; }

    .mbar-item {
        padding: 10px 16px;
        border-right: 1px solid #1a2840;
        min-width: 120px;
        display: flex;
        flex-direction: column;
        gap: 3px;
    }

    .mbar-label {
        font-family: 'Space Mono', monospace;
        font-size: 9px;
        color: #5a7a9a;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .mbar-value {
        font-family: 'Space Mono', monospace;
        font-size: 15px;
        font-weight: 700;
        color: #e2eaf5;
    }

    .mbar-chg {
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 999px;
        width: fit-content;
    }

    .mbar-up   { color: #00e5a0; background: rgba(0,229,160,0.10); border: 1px solid rgba(0,229,160,0.2); }
    .mbar-down { color: #ff4560; background: rgba(255,69,96,0.10);  border: 1px solid rgba(255,69,96,0.2); }

    /* Module cards */
    .module-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 20px;
    }

    .module-card {
        border: 1px solid #1a2840;
        border-radius: 10px;
        padding: 18px 18px 14px 18px;
        background: linear-gradient(180deg, #0a1120 0%, #0d1628 100%);
        transition: border-color 0.18s, background 0.18s;
        cursor: default;
    }

    .module-card:hover {
        border-color: rgba(0,212,255,0.35);
        background: linear-gradient(180deg, #0c1628 0%, #0f1a34 100%);
    }

    .module-icon {
        font-size: 20px;
        margin-bottom: 10px;
        display: block;
    }

    .module-name {
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        font-weight: 600;
        color: #e2eaf5;
        margin-bottom: 5px;
    }

    .module-desc {
        font-family: 'DM Sans', sans-serif;
        font-size: 12px;
        color: #5a7a9a;
        line-height: 1.6;
        font-weight: 300;
    }

    .module-tag {
        display: inline-block;
        margin-top: 10px;
        font-family: 'Space Mono', monospace;
        font-size: 9px;
        color: #5a7a9a;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        border: 1px solid #1a2840;
        padding: 2px 8px;
        border-radius: 4px;
    }

    .module-tag-pro {
        color: #7c5cfc;
        border-color: rgba(124,92,252,0.3);
        background: rgba(124,92,252,0.06);
    }

    /* Section divider */
    .section-label {
        font-family: 'Space Mono', monospace;
        font-size: 9px;
        color: #5a7a9a;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin: 20px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #1a2840;
    }

    /* Footer */
    .home-footer {
        font-family: 'Space Mono', monospace;
        font-size: 9px;
        color: #5a7a9a;
        letter-spacing: 0.12em;
        padding-top: 14px;
        border-top: 1px solid #1a2840;
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }

    @media (max-width: 768px) {
        .module-grid { grid-template-columns: 1fr 1fr !important; }
        .hero-title  { font-size: 28px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Market bar data ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_market_bar():
    universe = {
        "S&P 500":  "^GSPC",
        "Nasdaq":   "^NDX",
        "VIX":      "^VIX",
        "Gold":     "GC=F",
        "WTI":      "CL=F",
        "EUR/USD":  "EURUSD=X",
        "BTC":      "BTC-USD",
        "US 10Y":   "^TNX",
        "DXY":      "DX-Y.NYB",
    }
    rows = []
    for label, sym in universe.items():
        try:
            s = load_close_series(sym, period="5d", source="auto")
            if s is None or len(s) < 2:
                continue
            last = float(s.iloc[-1])
            prev = float(s.iloc[-2])
            chg  = (last / prev - 1) * 100
            if label == "US 10Y":
                display = f"{last/10:.2f}%"
            elif abs(last) >= 1000:
                display = f"{last:,.0f}"
            else:
                display = f"{last:,.2f}"
            rows.append({"label": label, "value": display, "chg": chg})
        except Exception:
            continue
    return rows


def render_market_bar(data: list):
    if not data:
        st.caption("Market data unavailable — check your API keys.")
        return

    items_html = ""
    for d in data:
        chg   = d["chg"]
        cls   = "mbar-up" if chg >= 0 else "mbar-down"
        sign  = "+" if chg >= 0 else ""
        items_html += f"""
        <div class="mbar-item">
          <span class="mbar-label">{d['label']}</span>
          <span class="mbar-value">{d['value']}</span>
          <span class="mbar-chg {cls}">{sign}{chg:.2f}%</span>
        </div>
        """

    st.markdown(
        f"""
        <div class="mbar-wrap">
          <div class="mbar-header">
            <span class="qdp-live-dot"></span>
            LIVE MARKET SNAPSHOT
          </div>
          <div class="mbar-body">{items_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Module definitions ────────────────────────────────────────────────────────
MODULES = [
    {
        "icon": "📈",
        "name": "Portfolio Analytics",
        "desc": "Track performance, P&L, risk-adjusted returns, technicals, and benchmark attribution.",
        "tag":  "FREE",
        "pro":  False,
    },
    {
        "icon": "📊",
        "name": "Risk & Attribution",
        "desc": "Rolling VaR, CVaR, beta, stress tests, per-asset vol contribution.",
        "tag":  "FREE",
        "pro":  False,
    },
    {
        "icon": "⚙️",
        "name": "Derivatives Lab",
        "desc": "Black-Scholes, binomial trees, Monte Carlo pricing, Greeks and payoff diagrams.",
        "tag":  "FREE",
        "pro":  False,
    },
    {
        "icon": "🌊",
        "name": "Vol Surface",
        "desc": "Live implied vol smile, ATM term structure, 3D surface and put/call skew.",
        "tag":  "FREE",
        "pro":  False,
    },
    {
        "icon": "🎲",
        "name": "Monte Carlo Lab",
        "desc": "GBM path simulation, strategy back-testing, scenario distribution analysis.",
        "tag":  "FREE",
        "pro":  False,
    },
    {
        "icon": "🔍",
        "name": "Screener",
        "desc": "Multi-ticker snapshot with RSI signals, momentum, Sharpe, volume ratios.",
        "tag":  "FREE",
        "pro":  False,
    },
    {
        "icon": "🌐",
        "name": "Macro Monitor",
        "desc": "Rates, FX heatmaps, commodities, cross-asset correlation and regime tracking.",
        "tag":  "FREE",
        "pro":  False,
    },
    {
        "icon": "💼",
        "name": "Portfolio Manager",
        "desc": "Save portfolios to your account, add positions, edit holdings and sync across sessions.",
        "tag":  "PRO",
        "pro":  True,
    },
    {
        "icon": "🔬",
        "name": "Saved Analysis",
        "desc": "Load any saved portfolio and run full analytics instantly — no re-entry needed.",
        "tag":  "PRO",
        "pro":  True,
    },
]


def render_modules():
    cards_html = ""
    for m in MODULES:
        tag_cls  = "module-tag-pro" if m["pro"] else ""
        cards_html += f"""
        <div class="module-card">
          <span class="module-icon">{m['icon']}</span>
          <div class="module-name">{m['name']}</div>
          <div class="module-desc">{m['desc']}</div>
          <span class="module-tag {tag_cls}">{m['tag']}</span>
        </div>
        """

    st.markdown(
        f'<div class="module-grid">{cards_html}</div>',
        unsafe_allow_html=True,
    )


# ── Page render ───────────────────────────────────────────────────────────────

# Hero
st.markdown(
    """
    <div class="hero-wrap">
      <div class="hero-eyebrow">Market Intelligence Terminal</div>
      <div class="hero-title">
        Quant<span class="c1">Desk</span> <span class="c2">Pro</span>
      </div>
      <div class="hero-sub">
        Professional-grade analytics for portfolio monitoring, macro research,
        derivatives pricing, volatility analysis, and risk attribution —
        all in one terminal-style workspace.
      </div>
      <div class="pill-row">
        <div class="pill">9 modules</div>
        <div class="pill">Real-time data</div>
        <div class="pill">yFinance + Alpha Vantage</div>
        <div class="pill">Supabase persistence</div>
        <div class="pill">No code required</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Live market bar
with st.spinner("Loading market data…"):
    market_data = load_market_bar()
render_market_bar(market_data)

# Module grid
st.markdown(
    '<div class="section-label">Modules</div>',
    unsafe_allow_html=True,
)
render_modules()

# Footer
st.markdown(
    """
    <div class="home-footer">
      <span>QUANTDESK PRO · v2.0</span>
      <span>Data: yFinance · Alpha Vantage &nbsp;|&nbsp; Storage: Supabase</span>
    </div>
    """,
    unsafe_allow_html=True,
)
