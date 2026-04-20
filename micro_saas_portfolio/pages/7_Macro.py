"""
Macro Dashboard Pro
===================
Cross-asset global markets monitor: rates · FX · commodities · equities · bonds · crypto.

Key fixes vs previous version
------------------------------
- Correlation matrix: rate tickers (yield levels) use daily *differences*, not pct_change,
  so the matrix never shows all-NaN values
- Full universe always loaded regardless of focus-group selection — every tab has data
- Chart styling unified: dark axes, matching tick colours, consistent padding
- RSI(14) column with overbought/oversold colouring in every table
- Backtest adds Sharpe, Sortino, Calmar; drawdown panel below growth curve
- Yield curve highlights inversion with red shading + banner
- VIX chart with panic-zone fill
- 40D rolling S&P 500 / Gold correlation in Regime tab
- All section headers have educational expanders
"""

import datetime

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import streamlit as st

from auth import require_login, sidebar_user_widget
from utils import (
    app_footer,
    ACCENT,
    ACCENT2,
    BORDER,
    GREEN,
    MUTED,
    ORANGE,
    PALETTE,
    RED,
    TEXT,
    YELLOW,
    apply_theme,
    apply_responsive_layout,
)
from data_loader import load_close_series
from analytics import annualized_return, annualized_vol, correlation_matrix, rolling_vol

# ── Page setup ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Macro Dashboard Pro", layout="wide", page_icon="🌍")
apply_theme()
apply_responsive_layout()

# Local design tokens
BG_CARD  = "#080d18"
BG_CARD2 = "#0c1220"

# ══════════════════════════════════════════════════════════════════════════════
# UNIVERSE
# ══════════════════════════════════════════════════════════════════════════════

UNIVERSE: dict[str, str] = {
    "US 3M":  "^IRX",  "US 5Y":  "^FVX",
    "US 10Y": "^TNX",  "US 30Y": "^TYX",
    "DXY":     "DX-Y.NYB", "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "USD/CHF": "CHF=X",    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X",
    "Gold":    "GC=F",  "Silver":  "SI=F",
    "WTI":     "CL=F",  "Brent":   "BZ=F",
    "Nat Gas": "NG=F",  "Copper":  "HG=F",
    "Corn":    "ZC=F",  "Wheat":   "ZW=F",
    "S&P 500":       "^GSPC",   "Nasdaq 100":    "^NDX",
    "Dow Jones":     "^DJI",    "Russell 2000":  "^RUT",
    "Euro Stoxx 50": "^STOXX50E","DAX":           "^GDAXI",
    "FTSE 100":      "^FTSE",   "Nikkei 225":    "^N225",
    "Hang Seng":     "^HSI",    "VIX":           "^VIX",
    "TLT": "TLT", "IEF": "IEF", "SHY": "SHY",
    "HYG": "HYG", "LQD": "LQD", "TIP": "TIP",
    "Bitcoin":  "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD",
}

# Rate instruments are yield *levels* — handled with diff() not pct_change()
RATE_TICKERS = {"US 3M", "US 5Y", "US 10Y", "US 30Y"}

GROUPS: dict[str, list[str]] = {
    "All":         list(UNIVERSE.keys()),
    "Rates":       ["US 3M", "US 5Y", "US 10Y", "US 30Y"],
    "FX":          ["DXY", "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD"],
    "Commodities": ["Gold", "Silver", "WTI", "Brent", "Nat Gas", "Copper", "Corn", "Wheat"],
    "Equities":    ["S&P 500", "Nasdaq 100", "Dow Jones", "Russell 2000",
                    "Euro Stoxx 50", "DAX", "FTSE 100", "Nikkei 225", "Hang Seng", "VIX"],
    "Bonds":       ["TLT", "IEF", "SHY", "HYG", "LQD", "TIP"],
    "Crypto":      ["Bitcoin", "Ethereum", "Solana"],
}

RATE_ORDER    = ["US 3M", "US 5Y", "US 10Y", "US 30Y"]
RATE_MATURITY = {"US 3M": 0.25, "US 5Y": 5.0, "US 10Y": 10.0, "US 30Y": 30.0}
FX_LABELS        = GROUPS["FX"]
COMMODITY_LABELS = GROUPS["Commodities"]
EQUITY_LABELS    = GROUPS["Equities"]
BOND_LABELS      = GROUPS["Bonds"]
CRYPTO_LABELS    = GROUPS["Crypto"]
_BACKTEST_EXCL   = RATE_TICKERS | {"VIX"}

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

if "macro_loaded" not in st.session_state:
    st.session_state["macro_loaded"] = False


def _trigger_load():
    st.session_state["macro_loaded"] = True


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Macro Controls")
    st.caption("Set parameters then press **Load** to pull live data.")

    period = st.selectbox(
        "Lookback period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3,
        help="Historical window for all charts and calculations.",
    )
    focus_group = st.selectbox(
        "Highlight group", list(GROUPS.keys()), index=0,
        help="Asset class pinned to top of the overview sort.",
    )
    roll_window = st.slider(
        "Rolling vol window (days)", 5, 60, 20, 5,
        help="Trading days used for rolling realised vol.",
    )
    benchmark_label = st.selectbox(
        "Benchmark", ["S&P 500", "Gold", "DXY", "Bitcoin", "TLT"], index=0,
        help="Reference asset for the backtest comparison line.",
    )
    backtest_assets = st.multiselect(
        "Backtest basket",
        [x for x in UNIVERSE if x not in _BACKTEST_EXCL],
        default=["S&P 500", "Gold", "TLT"],
        help="Assets included in the equal-weight backtest.",
    )
    custom_input = st.text_input(
        "Custom Yahoo tickers", placeholder="e.g. GLD, USO, XLE",
        help="Comma-separated Yahoo Finance tickers to add.",
    )
    st.markdown("---")
    st.button("🚀  Load Macro Dashboard", use_container_width=True, on_click=_trigger_load)
    sidebar_user_widget()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    f"""
    <div style="padding:6px 0 18px 0; border-bottom:1px solid {BORDER}; margin-bottom:20px;">
      <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
        <span style="font-size:26px; font-weight:900; color:{TEXT}; letter-spacing:-0.02em;">
          🌍 Macro Dashboard Pro
        </span>
        <span style="padding:3px 10px; border-radius:999px; font-size:10px; font-weight:800;
                     border:1px solid {BORDER}; color:{ACCENT}; letter-spacing:0.08em;">MULTI-ASSET</span>
        <span style="padding:3px 10px; border-radius:999px; font-size:10px; font-weight:800;
                     border:1px solid {BORDER}; color:{ACCENT2}; letter-spacing:0.08em;">CROSS-ASSET</span>
      </div>
      <div style="margin-top:6px; font-size:12px; color:{MUTED}; line-height:1.6;">
        Global markets monitor — rates · FX · commodities · equities · bonds · crypto ·
        regime tracking · backtest · correlation
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# LANDING SCREEN
# ══════════════════════════════════════════════════════════════════════════════

if not st.session_state["macro_loaded"]:
    st.markdown(
        f"""
        <div style="background:{BG_CARD2}; border:1px solid {BORDER}; border-radius:14px;
                    padding:44px 32px; margin-top:20px; text-align:center;">
          <div style="font-size:52px; margin-bottom:12px;">🌍</div>
          <div style="font-size:22px; font-weight:900; color:{TEXT}; margin-bottom:10px;">
            Global Macro Control Center
          </div>
          <div style="color:{MUTED}; font-size:13px; line-height:2.0; max-width:680px; margin:0 auto;">
            Configure parameters in the sidebar, then press
            <strong style="color:{ACCENT};">Load Macro Dashboard</strong>.<br>
            Covers <strong>rates · FX · commodities · equities · bonds · crypto</strong>
            with snapshot tables, momentum rankings, yield curve, FX heatmap,
            inflation proxy, correlation matrix, equal-weight backtest and regime detection.
          </div>
          <div style="margin-top:24px; display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
            <span style="padding:4px 14px; border-radius:999px; font-size:11px;
                         border:1px solid {BORDER}; color:{ACCENT};">{len(UNIVERSE)} assets in universe</span>
            <span style="padding:4px 14px; border-radius:999px; font-size:11px;
                         border:1px solid {BORDER}; color:{ACCENT2};">Cached 10 min · yfinance</span>
            <span style="padding:4px 14px; border-radius:999px; font-size:11px;
                         border:1px solid {BORDER}; color:{MUTED};">Educational use only</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def load_macro_prices(labels: list[str], period: str = "1y") -> pd.DataFrame:
    """
    Fetch close-price series for every label.
    Failed / empty tickers are silently skipped so a partial result is always returned.
    """
    data: dict[str, pd.Series] = {}
    for label in labels:
        ticker = UNIVERSE.get(label, label)
        try:
            s = load_close_series(ticker, period=period, source="auto")
            if s is None:
                continue
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0] if not s.empty else None
            if s is None:
                continue
            s = pd.to_numeric(s, errors="coerce").dropna()
            if not s.empty:
                data[label] = s
        except Exception:
            continue
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data).sort_index().dropna(how="all")


# Add any custom tickers to the universe
if custom_input.strip():
    for sym in [x.strip().upper() for x in custom_input.split(",") if x.strip()]:
        UNIVERSE.setdefault(sym, sym)

# Always load the entire universe so every tab has data, regardless of focus group
labels_to_load = list(dict.fromkeys(list(UNIVERSE.keys()) + backtest_assets + [benchmark_label]))

with st.spinner("⏳ Fetching cross-asset market data…"):
    prices = load_macro_prices(labels_to_load, period=period)

if prices.empty:
    st.error("❌ No market data loaded. Check your connection or try a different lookback period.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _perf(s: pd.Series, n: int) -> float:
    s = s.dropna()
    return (float(s.iloc[-1] / s.iloc[-1 - n]) - 1.0) * 100 if len(s) > n else float("nan")


def _rsi(s: pd.Series, w: int = 14) -> float:
    s = s.dropna()
    d = s.diff().dropna()
    if len(d) < w:
        return float("nan")
    gain = d.clip(lower=0).rolling(w).mean()
    loss = (-d.clip(upper=0)).rolling(w).mean()
    rs   = gain / loss.replace(0, np.nan)
    rsi  = (100 - 100 / (1 + rs)).dropna()
    return float(rsi.iloc[-1]) if not rsi.empty else float("nan")


def _sharpe(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else float("nan")


def _sortino(r: pd.Series) -> float:
    r  = r.dropna()
    dd = r[r < 0].std()
    return float(r.mean() / dd * np.sqrt(252)) if dd > 0 else float("nan")


def _calmar(r: pd.Series) -> float:
    curve  = (1 + r.dropna()).cumprod()
    max_dd = (curve / curve.cummax() - 1).min()
    return float(annualized_return(r) / abs(max_dd)) if max_dd != 0 else float("nan")


def calc_snapshot(prices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in prices.columns:
        s    = prices[col].dropna()
        rets = s.pct_change().dropna()
        if len(s) < 3:
            continue
        ys = s[s.index.year == s.index[-1].year]
        ytd = (float(s.iloc[-1] / ys.iloc[0]) - 1.0) * 100 if len(ys) > 1 else float("nan")
        rows.append({
            "Asset":      col,
            "Last":       float(s.iloc[-1]),
            "1D %":       _perf(s, 1),
            "5D %":       _perf(s, 5),
            "1M %":       _perf(s, 21),
            "3M %":       _perf(s, 63),
            "YTD %":      ytd,
            "20D Vol %":  annualized_vol(rets.tail(20)) * 100 if len(rets) >= 20 else float("nan"),
            "Ann. Ret %": annualized_return(rets) * 100      if len(rets) > 10 else float("nan"),
            "RSI(14)":    _rsi(s),
        })
    return pd.DataFrame(rows)


def compute_regime(prices: pd.DataFrame) -> tuple[str, str, str]:
    """Returns (label, hex_colour, plain-English description)."""
    if "S&P 500" not in prices.columns:
        return "Unavailable", MUTED, "Insufficient data."
    spx = prices["S&P 500"].dropna()
    if len(spx) < 60:
        return "Unavailable", MUTED, "Need ≥60 days of S&P 500 data."
    sma20 = spx.rolling(20).mean()
    sma60 = spx.rolling(60).mean()
    px, m20, m60 = float(spx.iloc[-1]), float(sma20.iloc[-1]), float(sma60.iloc[-1])
    if not (np.isfinite(m20) and np.isfinite(m60)):
        return "Unavailable", MUTED, "Moving average could not be computed."
    vix_s = prices["VIX"].dropna() if "VIX" in prices.columns else pd.Series(dtype=float)
    vix   = float(vix_s.iloc[-1]) if not vix_s.empty else float("nan")
    if px > m20 > m60:
        if np.isfinite(vix) and vix >= 25:
            return ("Bull / High Vol", YELLOW,
                    "Uptrend intact but VIX ≥ 25 signals elevated fear. "
                    "May represent a mid-cycle correction or early regime shift — "
                    "risk assets can still advance but drawdown risk is higher.")
        return ("Bull Market", GREEN,
                "S&P 500 above its 20-day and 60-day SMAs with VIX below 25. "
                "Trend is positive and volatility is contained. "
                "Risk assets typically perform well in this environment.")
    if px < m20 < m60:
        return ("Bear Market", RED,
                "S&P 500 below both moving averages — downtrend confirmed. "
                "Capital preservation and defensive assets are typically favoured. "
                "Watch credit spreads and VIX for regime-change signals.")
    return ("Transition / Choppy", ORANGE,
            "Price and moving averages are in a mixed state with no clear trend. "
            "Conviction is low in both directions — position sizing should reflect uncertainty.")


# ══════════════════════════════════════════════════════════════════════════════
# SNAPSHOT + TOP-LEVEL KPIs
# ══════════════════════════════════════════════════════════════════════════════

snap = calc_snapshot(prices)
if snap.empty:
    st.error("❌ Snapshot could not be built. Try a longer lookback period.")
    st.stop()

regime_label, regime_color, regime_desc = compute_regime(prices)
up_today   = int((snap["1D %"] > 0).sum())
down_today = int((snap["1D %"] < 0).sum())
avg_vol    = snap["20D Vol %"].mean()

_r10 = snap.loc[snap["Asset"] == "US 10Y", "Last"]
_r3m = snap.loc[snap["Asset"] == "US 3M",  "Last"]
curve_spread = float(_r10.iloc[0]) - float(_r3m.iloc[0]) if (not _r10.empty and not _r3m.empty) else float("nan")
_inverted    = np.isfinite(curve_spread) and curve_spread < 0


# ── UI helpers ─────────────────────────────────────────────────────────────────

def metric_card(col, title: str, value: str, delta: str = "", dcol: str = ""):
    with col:
        dh = (f'<div style="color:{dcol or MUTED}; font-size:11px; font-weight:700; '
              f'margin-top:3px;">{delta}</div>') if delta else ""
        st.markdown(
            f"""
            <div style="background:{BG_CARD2}; border:1px solid {BORDER};
                        border-radius:10px; padding:14px 16px; min-height:86px;">
              <div style="color:{MUTED}; font-size:9px; font-weight:800;
                          letter-spacing:0.16em; text-transform:uppercase;">{title}</div>
              <div style="color:{TEXT}; font-size:22px; font-weight:900;
                          margin-top:7px; line-height:1.15;">{value}</div>
              {dh}
            </div>
            """, unsafe_allow_html=True,
        )


def section_hdr(title: str, sub: str = ""):
    sh = (f'<div style="color:{MUTED}; font-size:11px; margin-top:5px; line-height:1.5;">'
          f'{sub}</div>') if sub else ""
    st.markdown(
        f"""
        <div style="background:{BG_CARD2}; border:1px solid {BORDER};
                    border-radius:8px; padding:11px 14px; margin-bottom:10px;">
          <div style="color:{TEXT}; font-size:11px; font-weight:800;
                      letter-spacing:0.15em; text-transform:uppercase;">{title}</div>
          {sh}
        </div>
        """, unsafe_allow_html=True,
    )


def style_table(df: pd.DataFrame):
    fmt = {c: "{:.2f}%" for c in ["1D %","5D %","1M %","3M %","YTD %","20D Vol %","Ann. Ret %"]}
    fmt.update({"Last": "{:,.2f}", "RSI(14)": "{:.1f}"})
    fmt = {k: v for k, v in fmt.items() if k in df.columns}
    perf = {"1D %","5D %","1M %","3M %","YTD %","Ann. Ret %"}

    def row_style(row):
        return [(f"color:{GREEN}" if row[c] >= 0 else f"color:{RED}")
                if c in perf and pd.notna(row[c]) else "" for c in row.index]

    def rsi_map(v):
        if pd.isna(v): return ""
        return f"color:{RED}" if v >= 70 else (f"color:{GREEN}" if v <= 30 else "")

    styler = df.style.format(fmt, na_rep="—").apply(row_style, axis=1)
    if "RSI(14)" in df.columns:
        styler = styler.applymap(rsi_map, subset=["RSI(14)"])
    return styler


def _fig(h: float = 4.2, w: float = 10.0):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG_CARD)
    ax.set_facecolor(BG_CARD)
    ax.tick_params(colors="#7a8fa6", labelsize=8)
    for sp in ax.spines.values():
        sp.set_edgecolor("#1c2a3a")
    ax.grid(True, alpha=0.14, color="#1c2a3a", linewidth=0.7)
    return fig, ax


def _fig2(h_ratios: list, total_h: float = 7.0, w: float = 10.0):
    fig, axes = plt.subplots(len(h_ratios), 1, figsize=(w, total_h),
                             gridspec_kw={"height_ratios": h_ratios, "hspace": 0.06})
    fig.patch.set_facecolor(BG_CARD)
    for ax in axes:
        ax.set_facecolor(BG_CARD)
        ax.tick_params(colors="#7a8fa6", labelsize=8)
        for sp in ax.spines.values():
            sp.set_edgecolor("#1c2a3a")
        ax.grid(True, alpha=0.14, color="#1c2a3a", linewidth=0.7)
    return fig, axes


def _t(ax, title: str):
    ax.set_title(title, color="#c8d8e8", fontsize=9, fontweight="bold", pad=8, loc="left")


def _leg(ax, **kw):
    ax.legend(fontsize=7.5, facecolor=BG_CARD2, edgecolor="#1c2a3a",
              labelcolor="#8fa8c0", framealpha=0.85, **kw)


def _show(fig):
    plt.tight_layout(pad=0.6)
    st.pyplot(fig)
    plt.close(fig)


# ── Headline ticker cards ──────────────────────────────────────────────────────
_HL = ["S&P 500", "Nasdaq 100", "VIX", "US 10Y", "DXY", "Gold", "WTI", "Bitcoin"]
headline = [x for x in _HL if x in snap["Asset"].values]
if headline:
    hc = st.columns(len(headline))
    for i, lbl in enumerate(headline):
        row  = snap.loc[snap["Asset"] == lbl].iloc[0]
        d    = row["1D %"]
        dc   = (GREEN if d >= 0 else RED) if pd.notna(d) else MUTED
        last = row["Last"]
        metric_card(hc[i], lbl,
                    f"{last:,.2f}" if last < 10_000 else f"{last:,.0f}",
                    f"{d:+.2f}%" if pd.notna(d) else "—", dc)

st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

# ── KPI row ────────────────────────────────────────────────────────────────────
kc = st.columns(5)
metric_card(kc[0], "Assets Loaded",   str(len(snap)))
metric_card(kc[1], "Up / Down Today", f"{up_today} / {down_today}",
            "Breadth positive" if up_today >= down_today else "Breadth negative",
            GREEN if up_today >= down_today else RED)
metric_card(kc[2], "Avg 20D Vol",     f"{avg_vol:.1f}%", "Realised — cross-asset")
metric_card(kc[3], "10Y − 3M Spread",
            f"{curve_spread:.2f}bps" if np.isfinite(curve_spread) else "—",
            "⚠ Inverted" if _inverted else "Normal",
            RED if _inverted else GREEN)
metric_card(kc[4], "Market Regime",   regime_label, delta_col=regime_color)

st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tabs = st.tabs([
    "📊  Overview",
    "💱  FX & Commodities",
    "📈  Equities & Crypto",
    "📉  Rates & Bonds",
    "🔗  Correlation",
    "🧮  Backtest",
    "🎯  Regime",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 0 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    L, R = st.columns([1.4, 1], gap="large")

    with L:
        section_hdr(
            "Cross-Asset Monitor",
            "Green/red = return direction · RSI > 70 = overbought (red) · RSI < 30 = oversold (green)",
        )
        sc  = st.selectbox("Sort by",
                           ["1D %","1M %","3M %","YTD %","20D Vol %","Ann. Ret %","RSI(14)","Asset"],
                           key="ov_sort")
        asc = st.checkbox("Ascending", False, key="ov_asc")
        DISP_COLS = ["Asset","Last","1D %","5D %","1M %","3M %","YTD %","20D Vol %","Ann. Ret %","RSI(14)"]
        disp = snap.sort_values(sc, ascending=asc).reset_index(drop=True)
        st.dataframe(style_table(disp[DISP_COLS]), use_container_width=True, height=520)

    with R:
        section_hdr("1M Momentum Ranking", "Sorted by 1-month return")
        rank = snap.dropna(subset=["1M %"]).sort_values("1M %")
        fig, ax = _fig(max(4, len(rank) * 0.30), 8)
        _t(ax, "1-Month Return (%)")
        bc = [GREEN if v >= 0 else RED for v in rank["1M %"]]
        ax.barh(rank["Asset"], rank["1M %"], color=bc, edgecolor=BG_CARD, height=0.68)
        ax.axvline(0, color="#ffffff25", lw=0.8, ls="--")
        ax.set_xlabel("Return (%)", color="#7a8fa6", fontsize=8)
        ax.tick_params(axis="y", labelsize=7.5, colors="#8fa8c0")
        _show(fig)

        section_hdr("Performance Heatmap",
                    "Colour intensity = magnitude · red = negative · green = positive")
        HC = ["1D %","5D %","1M %","3M %","YTD %"]
        hd = snap.set_index("Asset")[HC].dropna(how="all")
        vv = hd.values.astype(float)
        fv = vv[np.isfinite(vv)]
        vm = max(np.nanpercentile(np.abs(fv), 95) if fv.size else 1, 0.25)
        cmap = mcolors.LinearSegmentedColormap.from_list("ph", [RED, "#0d1526", GREEN])
        fig2, ax2 = _fig(max(4, len(hd) * 0.30), 8)
        _t(ax2, "Multi-Horizon Performance Heatmap")
        im = ax2.imshow(vv, aspect="auto", cmap=cmap, vmin=-vm, vmax=vm)
        ax2.set_xticks(range(len(HC)));   ax2.set_xticklabels(HC, fontsize=8, color="#8fa8c0")
        ax2.set_yticks(range(len(hd)));   ax2.set_yticklabels(hd.index, fontsize=7, color="#8fa8c0")
        for i in range(vv.shape[0]):
            for j in range(vv.shape[1]):
                if np.isfinite(vv[i, j]):
                    ax2.text(j, i, f"{vv[i,j]:.1f}", ha="center", va="center",
                             fontsize=6.5, color="white")
        plt.colorbar(im, ax=ax2, fraction=0.025, pad=0.02)
        _show(fig2)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — FX & COMMODITIES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    C1, C2 = st.columns(2, gap="large")

    with C1:
        section_hdr("FX Dashboard", "Major currency pairs — performance and RSI signals")
        fx_s = snap[snap["Asset"].isin([x for x in FX_LABELS if x in snap["Asset"].values])]
        if not fx_s.empty:
            st.dataframe(style_table(fx_s[["Asset","Last","1D %","1M %","3M %","20D Vol %","RSI(14)"]]),
                         use_container_width=True, height=270)
        with st.expander("ℹ️ Reading the FX table"):
            st.markdown(
                "**DXY** measures USD vs a basket of six major currencies. "
                "Rising DXY = USD strength → typically pressures commodities, EM assets and risk. "
                "**EUR/USD** is the world's most liquid pair and often leads macro FX trends.  \n"
                "**RSI > 70** = potentially overbought; **RSI < 30** = potentially oversold."
            )
        # FX heatmap
        hc = ["1D %","5D %","1M %","3M %"]
        hd = fx_s.set_index("Asset")[hc].dropna(how="all") if not fx_s.empty else pd.DataFrame()
        if not hd.empty:
            vv = hd.values.astype(float)
            fv = vv[np.isfinite(vv)]
            vm = max(np.nanpercentile(np.abs(fv), 90) if fv.size else 1, 0.2)
            cmap = mcolors.LinearSegmentedColormap.from_list("fx", [RED, "#0d1526", GREEN])
            fig, ax = _fig(max(3.5, len(hd) * 0.54), 8)
            _t(ax, "FX Performance Heatmap")
            im = ax.imshow(vv, cmap=cmap, vmin=-vm, vmax=vm, aspect="auto")
            ax.set_xticks(range(len(hc)));  ax.set_xticklabels(hc, fontsize=9, color="#8fa8c0")
            ax.set_yticks(range(len(hd)));  ax.set_yticklabels(hd.index, fontsize=8.5, color="#8fa8c0")
            for i in range(vv.shape[0]):
                for j in range(vv.shape[1]):
                    if np.isfinite(vv[i, j]):
                        ax.text(j, i, f"{vv[i,j]:.2f}", ha="center", va="center",
                                fontsize=8, color="white", fontweight="bold")
            plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
            _show(fig)

    with C2:
        section_hdr("Commodities + Inflation Proxy",
                    "Energy, metals, agricultural and inflation-linked basket")
        cm_s = snap[snap["Asset"].isin([x for x in COMMODITY_LABELS if x in snap["Asset"].values])]
        if not cm_s.empty:
            st.dataframe(style_table(cm_s[["Asset","Last","1D %","1M %","3M %","20D Vol %","RSI(14)"]]),
                         use_container_width=True, height=310)
        with st.expander("ℹ️ What is the Inflation Proxy Basket?"):
            st.markdown(
                "An equal-weight composite of Gold, WTI crude, Copper, Corn and TIP ETF. "
                "When the basket rises, broad price pressures may be building. "
                "This is a *directional proxy* only — not a direct inflation measure."
            )
        req = [x for x in ["Gold","WTI","Copper","Corn","TIP"] if x in prices.columns]
        if len(req) >= 3:
            base = prices[req].dropna(how="all").ffill().dropna()
            if not base.empty:
                norm  = base / base.iloc[0] * 100
                proxy = norm.mean(axis=1)
                fig, ax = _fig(4.2, 8)
                _t(ax, "Inflation Proxy Basket (Indexed to 100)")
                for i, col in enumerate(norm.columns):
                    ax.plot(norm.index, norm[col], lw=1.2, alpha=0.6,
                            color=PALETTE[i % len(PALETTE)], label=col)
                ax.plot(proxy.index, proxy.values, lw=2.5, color="white",
                        label="Basket Avg", zorder=5)
                ax.axhline(100, color=MUTED, lw=0.7, ls="--")
                _leg(ax, ncols=3)
                ax.set_ylabel("Index (base=100)", color="#7a8fa6", fontsize=8)
                _show(fig)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — EQUITIES & CRYPTO
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    L, R = st.columns(2, gap="large")

    with L:
        section_hdr("Global Equities", "US and international equity index performance")
        eq_s = snap[snap["Asset"].isin([x for x in EQUITY_LABELS if x in snap["Asset"].values])]
        if not eq_s.empty:
            st.dataframe(style_table(eq_s[["Asset","Last","1D %","1M %","3M %","20D Vol %","RSI(14)"]]),
                         use_container_width=True, height=340)
        eq_p = prices[[x for x in EQUITY_LABELS if x in prices.columns]]
        if not eq_p.empty:
            sel = st.multiselect("Indices to chart", eq_p.columns.tolist(),
                                 default=eq_p.columns.tolist()[:5], key="eq_sel")
            if sel:
                norm = eq_p[sel] / eq_p[sel].iloc[0] * 100
                fig, ax = _fig(4.2, 10)
                _t(ax, "Equity Indices — Indexed to 100")
                for i, col in enumerate(norm.columns):
                    ax.plot(norm.index, norm[col], lw=1.7, label=col,
                            color=PALETTE[i % len(PALETTE)])
                ax.axhline(100, color="#ffffff18", lw=0.7, ls="--")
                ax.set_ylabel("Index (base=100)", color="#7a8fa6", fontsize=8)
                _leg(ax, ncols=3)
                _show(fig)

    with R:
        section_hdr("Crypto Monitor", "Prices, rolling volatility and RSI signals")
        cr_s = snap[snap["Asset"].isin([x for x in CRYPTO_LABELS if x in snap["Asset"].values])]
        if not cr_s.empty:
            st.dataframe(style_table(cr_s[["Asset","Last","1D %","1M %","3M %","20D Vol %","RSI(14)"]]),
                         use_container_width=True, height=200)
        cr_p = prices[[x for x in CRYPTO_LABELS if x in prices.columns]]
        if not cr_p.empty:
            fig, ax = _fig(4.2, 10)
            _t(ax, f"Rolling {roll_window}D Annualised Volatility (%)")
            for i, col in enumerate(cr_p.columns):
                rv = rolling_vol(cr_p[col].pct_change().dropna(), window=roll_window) * 100
                ax.plot(rv.index, rv.values, lw=1.8, label=col,
                        color=PALETTE[i % len(PALETTE)])
            ax.set_ylabel("Ann. Vol (%)", color="#7a8fa6", fontsize=8)
            _leg(ax)
            _show(fig)
        with st.expander("ℹ️ Crypto volatility context"):
            st.markdown(
                "Crypto typically exhibits **annualised realised vol of 60–120%**, "
                "far above equities (≈15–25%) or bonds (≈5–10%). "
                "Spikes in rolling vol coincide with liquidation cascades, "
                "exchange failures or macro shocks."
            )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — RATES & BONDS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    L, R = st.columns(2, gap="large")

    with L:
        section_hdr("Rates Panel", "US Treasury yield levels and yield curve shape")
        rt_s = snap[snap["Asset"].isin([x for x in RATE_ORDER if x in snap["Asset"].values])]
        if not rt_s.empty:
            st.dataframe(style_table(rt_s[["Asset","Last","1D %","1M %","3M %"]]),
                         use_container_width=True, height=215)
        avail = [x for x in RATE_ORDER if x in prices.columns]
        if avail:
            fig, ax = _fig(4.0, 10)
            _t(ax, "Treasury Yield Trend")
            for i, col in enumerate(avail):
                s = prices[col].dropna()
                ax.plot(s.index, s.values, lw=1.6, label=col, color=PALETTE[i % len(PALETTE)])
            ax.set_ylabel("Yield (%)", color="#7a8fa6", fontsize=8)
            _leg(ax, ncols=2)
            _show(fig)

            xs = [RATE_MATURITY[x] for x in avail]
            ys = [float(prices[x].dropna().iloc[-1]) for x in avail]
            fig2, ax2 = _fig(3.2, 10)
            if _inverted:
                ax2.set_facecolor("#1a0808")
                _t(ax2, "Current Yield Curve  ⚠  INVERTED")
                ax2.title.set_color(RED)
            else:
                _t(ax2, "Current Yield Curve")
            ax2.plot(xs, ys, marker="o", lw=2.2, color=ACCENT, zorder=5, markersize=6)
            for xp, yp, lb in zip(xs, ys, avail):
                ax2.annotate(f"{yp:.2f}%", (xp, yp), textcoords="offset points",
                             xytext=(0, 10), ha="center", fontsize=8, color=ACCENT)
            ax2.set_xticks(xs); ax2.set_xticklabels(avail, color="#8fa8c0", fontsize=8)
            ax2.set_ylabel("Yield (%)", color="#7a8fa6", fontsize=8)
            _show(fig2)

        with st.expander("ℹ️ Yield curve interpretation"):
            spread_txt = f"{curve_spread:.2f} bps" if np.isfinite(curve_spread) else "N/A"
            st.markdown(
                "A **normal** yield curve slopes upward (longer maturities yield more). "
                "An **inverted** curve has historically preceded US recessions by 6–18 months. "
                f"Current 10Y − 3M spread: **{spread_txt}** — "
                f"{'⚠ **Inverted**' if _inverted else '✓ Normal'}."
            )

    with R:
        section_hdr("Bonds & Credit", "Duration, credit spreads and inflation-linked proxies")
        bd_s = snap[snap["Asset"].isin([x for x in BOND_LABELS if x in snap["Asset"].values])]
        if not bd_s.empty:
            st.dataframe(style_table(bd_s[["Asset","Last","1D %","1M %","3M %","20D Vol %"]]),
                         use_container_width=True, height=215)

        if {"HYG","LQD"}.issubset(prices.columns):
            ratio = (prices["HYG"] / prices["LQD"]).dropna()
            fig3, ax3 = _fig(3.5, 10)
            _t(ax3, "HYG / LQD — Credit Risk Proxy")
            ax3.plot(ratio.index, ratio.values, lw=1.9, color=ACCENT2)
            ax3.axhline(ratio.mean(), color="#ffffff25", lw=0.8, ls="--",
                        label=f"Mean {ratio.mean():.3f}")
            _leg(ax3)
            _show(fig3)
            with st.expander("ℹ️ HYG / LQD ratio"):
                st.markdown(
                    "**Rising** → risk-on, credit appetite improving (HY outperforming IG).  \n"
                    "**Falling** → risk-off / credit stress — watch for equity follow-through."
                )

        if {"TLT","TIP"}.issubset(prices.columns):
            spd = ((prices["TIP"] / prices["TIP"].iloc[0]) -
                   (prices["TLT"] / prices["TLT"].iloc[0])) * 100
            fig4, ax4 = _fig(3.5, 10)
            _t(ax4, "TIP vs TLT — Inflation vs Duration")
            ax4.plot(spd.index, spd.values, lw=1.9, color=YELLOW)
            ax4.axhline(0, color="#ffffff18", lw=0.7, ls="--")
            ax4.fill_between(spd.index, spd.values, 0, where=(spd.values > 0),
                             alpha=0.15, color=GREEN)
            ax4.fill_between(spd.index, spd.values, 0, where=(spd.values < 0),
                             alpha=0.15, color=RED)
            ax4.set_ylabel("Rel. Perf (%)", color="#7a8fa6", fontsize=8)
            _show(fig4)
            with st.expander("ℹ️ TIP vs TLT"):
                st.markdown(
                    "**TIP outperforming** → inflation expectations rising.  \n"
                    "**TLT outperforming** → deflation / recession fears, flight to nominal duration."
                )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — CORRELATION
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    section_hdr(
        "Correlation Matrix",
        "Daily return correlation · blue = positive · red = negative · bold text = |corr| > 0.7",
    )
    with st.expander("ℹ️ How to read this matrix"):
        st.markdown(
            "**+1** → assets move perfectly together (no diversification benefit).  \n"
            "**−1** → assets move perfectly opposite (natural hedge).  \n"
            "**0** → no linear relationship.  \n\n"
            "**Note on rate tickers** (US 3M, 5Y, 10Y, 30Y): these are yield *levels*, "
            "not prices. The matrix uses daily *differences* for rate series "
            "(e.g. +2bps) and daily *% returns* for all other assets, "
            "ensuring meaningful correlation values instead of all-NaN."
        )

    corr_assets = st.multiselect(
        "Assets for correlation",
        prices.columns.tolist(),
        default=prices.columns.tolist()[: min(16, len(prices.columns))],
        key="corr_sel",
    )

    if len(corr_assets) >= 2:
        # Build a mixed returns frame: diff() for rates, pct_change() for everything else
        parts = []
        for col in corr_assets:
            s = prices[col].dropna()
            r = s.diff().dropna() if col in RATE_TICKERS else s.pct_change().dropna()
            r.name = col
            parts.append(r)
        rets_df = pd.concat(parts, axis=1).dropna(how="all")
        valid   = rets_df.dropna(axis=1, how="all").columns.tolist()

        if len(valid) < 2:
            st.warning("Not enough overlapping data. Try a different combination or longer period.")
        else:
            corr = rets_df[valid].corr()
            n    = len(valid)
            fig, ax = plt.subplots(figsize=(max(7, n * 0.76), max(5, n * 0.62)))
            fig.patch.set_facecolor(BG_CARD)
            ax.set_facecolor(BG_CARD)
            for sp in ax.spines.values():
                sp.set_edgecolor("#1c2a3a")
            cmap = mcolors.LinearSegmentedColormap.from_list("corr", [RED, "#0d1526", ACCENT])
            im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
            ax.set_xticks(range(n))
            ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8, color="#8fa8c0")
            ax.set_yticks(range(n))
            ax.set_yticklabels(corr.index, fontsize=8, color="#8fa8c0")
            ax.set_title(f"Return Correlation Matrix ({period} lookback)",
                         color="#c8d8e8", fontsize=10, fontweight="bold", pad=10)
            for i in range(n):
                for j in range(n):
                    v = corr.values[i, j]
                    if np.isfinite(v):
                        ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                                fontsize=6.5, color="white",
                                fontweight="bold" if abs(v) > 0.7 else "normal")
            cb = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
            cb.ax.tick_params(colors="#7a8fa6", labelsize=7)
            plt.tight_layout(pad=0.8)
            st.pyplot(fig)
            plt.close(fig)
    else:
        st.info("Select at least two assets.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — BACKTEST
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    section_hdr(
        "Macro Basket Backtest",
        "Equal-weight portfolio · daily rebalance · no transaction costs · educational only",
    )
    with st.expander("ℹ️ About this backtest"):
        bnames = ", ".join(backtest_assets) if backtest_assets else "no assets selected"
        st.markdown(
            f"**Portfolio**: equal-weight — {bnames}.  \n"
            "Rebalanced daily (academic assumption).  No costs, slippage or taxes.  \n"
            "**Sharpe** = ann. excess return ÷ ann. std dev.  \n"
            "**Sortino** = ann. excess return ÷ downside deviation.  \n"
            "**Calmar** = ann. return ÷ |max drawdown|.  \n"
            "*Past performance is not indicative of future results.*"
        )

    valid_bt = [x for x in backtest_assets if x in prices.columns]
    if not valid_bt:
        st.info("Choose at least one valid investable asset in the sidebar Backtest basket.")
    else:
        panel = prices[valid_bt].dropna(how="all").ffill().dropna()
        if len(panel) < 10:
            st.info("Not enough data — try a longer lookback period.")
        else:
            rets       = panel.pct_change().dropna()
            w          = np.repeat(1.0 / len(valid_bt), len(valid_bt))
            port_ret   = rets.dot(w)
            port_curve = (1 + port_ret).cumprod()
            dd         = port_curve / port_curve.cummax() - 1

            bench_curve: pd.Series | None = None
            if benchmark_label in prices.columns:
                b = prices[benchmark_label].reindex(panel.index).ffill().dropna()
                if len(b) > 1:
                    bench_curve = b / b.iloc[0]

            tr = (port_curve.iloc[-1] - 1) * 100
            ar = annualized_return(port_ret) * 100
            av = annualized_vol(port_ret) * 100
            md = dd.min() * 100
            sh = _sharpe(port_ret)
            so = _sortino(port_ret)
            ca = _calmar(port_ret)

            mc = st.columns(7)
            for col, (lbl, val) in zip(mc, [
                ("Total Return",  f"{tr:.2f}%"),
                ("Ann. Return",   f"{ar:.2f}%"),
                ("Ann. Vol",      f"{av:.2f}%"),
                ("Max Drawdown",  f"{md:.2f}%"),
                ("Sharpe",        f"{sh:.2f}" if np.isfinite(sh) else "—"),
                ("Sortino",       f"{so:.2f}" if np.isfinite(so) else "—"),
                ("Calmar",        f"{ca:.2f}" if np.isfinite(ca) else "—"),
            ]):
                col.metric(lbl, val)

            st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

            # Growth + drawdown dual panel
            fig, (ax1, ax2) = _fig2([3, 1.2], 7.0, 11)
            _t(ax1, "Portfolio Growth vs Benchmark")
            ax1.plot(port_curve.index, port_curve.values, lw=2.2, color=ACCENT, label="Basket")
            if bench_curve is not None and not bench_curve.empty:
                al = bench_curve.reindex(port_curve.index).dropna()
                ax1.plot(al.index, al.values, lw=1.6, ls="--", color=ACCENT2,
                         label=benchmark_label)
            ax1.axhline(1.0, color="#ffffff12", lw=0.6, ls=":")
            ax1.set_ylabel("Growth of $1", color="#7a8fa6", fontsize=8)
            _leg(ax1)
            ax1.tick_params(labelbottom=False)

            _t(ax2, "Drawdown from Peak")
            ax2.fill_between(dd.index, dd.values, 0, color=RED, alpha=0.38)
            ax2.plot(dd.index, dd.values, lw=1.0, color=RED)
            ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
            ax2.set_ylabel("Drawdown", color="#7a8fa6", fontsize=8)
            plt.tight_layout(pad=0.6)
            st.pyplot(fig); plt.close(fig)

            # Per-asset contribution bar
            contrib = ((panel.iloc[-1] / panel.iloc[0]) - 1).sort_values()
            fig2, ax2b = _fig(max(3.2, len(contrib) * 0.48), 11)
            _t(ax2b, "Individual Asset Total Returns in Basket")
            bc = [GREEN if v >= 0 else RED for v in contrib.values]
            ax2b.barh(contrib.index, contrib.values * 100, color=bc,
                      edgecolor=BG_CARD, height=0.65)
            ax2b.axvline(0, color="#ffffff20", lw=0.7, ls="--")
            ax2b.set_xlabel("Return (%)", color="#7a8fa6", fontsize=8)
            ax2b.tick_params(axis="y", labelsize=8, colors="#8fa8c0")
            _show(fig2)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — REGIME
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    L, R = st.columns(2, gap="large")

    with L:
        section_hdr("Market Regime Detector",
                    "S&P 500 trend (SMA 20 / SMA 60) + VIX volatility overlay")
        st.markdown(
            f"""
            <div style="background:{BG_CARD2}; border:1.5px solid {regime_color};
                        border-radius:12px; padding:18px 20px; margin-bottom:12px;">
              <div style="color:{MUTED}; font-size:9px; font-weight:800;
                          letter-spacing:0.18em; text-transform:uppercase;">Current Regime</div>
              <div style="color:{regime_color}; font-size:26px; font-weight:900;
                          margin-top:8px; letter-spacing:-0.01em;">{regime_label}</div>
              <div style="color:{MUTED}; font-size:11px; margin-top:10px;
                          line-height:1.7; max-width:480px;">{regime_desc}</div>
            </div>
            """, unsafe_allow_html=True,
        )
        if "S&P 500" in prices.columns:
            spx   = prices["S&P 500"].dropna()
            sma20 = spx.rolling(20).mean()
            sma60 = spx.rolling(60).mean()
            fig, ax = _fig(4.2, 10)
            _t(ax, "S&P 500 — Trend Structure (SMA 20 / 60)")
            ax.plot(spx.index, spx.values, lw=1.9, color=ACCENT, label="S&P 500")
            ax.plot(sma20.index, sma20.values, lw=1.1, ls="--", color=YELLOW, label="SMA 20")
            ax.plot(sma60.index, sma60.values, lw=1.1, ls="--", color=RED,    label="SMA 60")
            ax.fill_between(spx.index,
                            sma60.reindex(spx.index).values, spx.values,
                            where=(spx.values < sma60.reindex(spx.index).values),
                            alpha=0.12, color=RED, interpolate=True)
            ax.set_ylabel("Index Level", color="#7a8fa6", fontsize=8)
            _leg(ax)
            _show(fig)

        if "VIX" in prices.columns:
            vix = prices["VIX"].dropna()
            fig2, ax2 = _fig(3.2, 10)
            _t(ax2, "VIX — Fear Gauge")
            ax2.plot(vix.index, vix.values, lw=1.8, color=ORANGE)
            ax2.axhline(20, color=YELLOW, lw=0.8, ls="--", label="Elevated (20)")
            ax2.axhline(30, color=RED,    lw=0.8, ls="--", label="Panic (30)")
            ax2.fill_between(vix.index, vix.values, 20,
                             where=(vix.values > 20), alpha=0.14, color=RED)
            ax2.set_ylabel("VIX", color="#7a8fa6", fontsize=8)
            _leg(ax2)
            _show(fig2)

    with R:
        section_hdr("Cross-Asset Leadership",
                    "Relative 1M and 3M performance of key macro assets")
        _lead = ["S&P 500","Gold","TLT","DXY","Bitcoin","WTI","VIX"]
        leaders = snap[snap["Asset"].isin([x for x in _lead if x in snap["Asset"].values])]
        if not leaders.empty:
            st.dataframe(
                leaders[["Asset","1M %","3M %","20D Vol %","RSI(14)"]].set_index("Asset")
                .style.format({"1M %":"{:.2f}%","3M %":"{:.2f}%",
                               "20D Vol %":"{:.2f}%","RSI(14)":"{:.1f}"}),
                use_container_width=True, height=280,
            )

        if {"US 10Y","US 3M"}.issubset(prices.columns):
            spd_ts = (prices["US 10Y"] - prices["US 3M"]).dropna()
            fig3, ax3 = _fig(3.8, 10)
            _t(ax3, "10Y − 3M Yield Spread")
            ax3.plot(spd_ts.index, spd_ts.values, color=ACCENT2, lw=1.9)
            ax3.axhline(0, color=RED, lw=0.9, ls="--", label="Inversion (0)")
            ax3.fill_between(spd_ts.index, spd_ts.values, 0,
                             where=(spd_ts.values < 0),  alpha=0.18, color=RED,   label="Inverted")
            ax3.fill_between(spd_ts.index, spd_ts.values, 0,
                             where=(spd_ts.values >= 0), alpha=0.10, color=GREEN)
            ax3.set_ylabel("Spread (bps)", color="#7a8fa6", fontsize=8)
            _leg(ax3)
            _show(fig3)

        # S&P 500 / Gold rolling correlation — hedge effectiveness check
        if {"S&P 500","Gold"}.issubset(prices.columns):
            rc = (prices["S&P 500"].pct_change()
                  .rolling(40)
                  .corr(prices["Gold"].pct_change())
                  .dropna())
            if not rc.empty:
                fig4, ax4 = _fig(3.2, 10)
                _t(ax4, "40D Rolling Correlation: S&P 500 vs Gold")
                ax4.plot(rc.index, rc.values, lw=1.8, color=YELLOW)
                ax4.axhline(0,    color="#ffffff20", lw=0.7, ls="--")
                ax4.axhline(-0.3, color=GREEN,       lw=0.7, ls=":", label="Hedge threshold (−0.3)")
                ax4.fill_between(rc.index, rc.values, 0,
                                 where=(rc.values < 0), alpha=0.13, color=GREEN)
                ax4.set_ylim(-1, 1)
                ax4.set_ylabel("Correlation", color="#7a8fa6", fontsize=8)
                _leg(ax4)
                _show(fig4)
                with st.expander("ℹ️ S&P 500 / Gold rolling correlation"):
                    st.markdown(
                        "When correlation is **negative**, gold is acting as an equity hedge "
                        "(classic risk-off behaviour). When it turns **positive**, both assets "
                        "move together — common during liquidity crises or broad USD selling."
                    )


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"""
    <div style="color:{MUTED}; font-size:10px; text-align:center;
                letter-spacing:0.10em; text-transform:uppercase; padding:4px 0 8px 0;">
      QuantDesk Pro · Macro Dashboard Pro ·
      Data via yfinance · Cached {datetime.datetime.utcnow().strftime("%H:%M UTC")} ·
      Educational use only — not financial advice
    </div>
    """,
    unsafe_allow_html=True,
)
app_footer()

