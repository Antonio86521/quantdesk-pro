"""
Macro Dashboard Pro
===================
Cross-asset global markets monitor covering rates, FX, commodities,
equities, bonds and crypto.

Features
--------
- Live snapshot table with colour-coded performance columns
- FX heatmap, inflation proxy basket, yield curve
- Rolling volatility, correlation matrix
- Equal-weight basket backtest with drawdown and contribution charts
- Market regime detection (trend + VIX overlay)
- Cross-asset leadership and 10Y-3M spread tracker
- Sharpe ratio, Sortino ratio and Calmar ratio in backtest
- RSI signal column in the overview table
- Custom ticker support

Notes
-----
- Data cached for 10 minutes via @st.cache_data
- Data sourced from Yahoo Finance via yfinance through load_close_series()
- Educational use only
"""

import datetime
from typing import Dict, List, Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from auth import require_login, sidebar_user_widget
from utils import (
    app_footer,
    ACCENT, ACCENT2, AMBER, AMBER as YELLOW, AMBER as ORANGE,
    BORDER, MPL_BORDER, GREEN, MUTED, PALETTE, RED, TEXT, TEXT2, BG3,
    apply_theme, apply_responsive_layout, page_header,
)
from data_loader import load_close_series
from analytics import annualized_return, annualized_vol, correlation_matrix, rolling_vol


# ══════════════════════════════════════════════════════════════════════════════
# PAGE SETUP
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Macro Dashboard Pro",
    layout="wide",
    page_icon="🌍",
)

apply_theme()
apply_responsive_layout()
require_login()
sidebar_user_widget()


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

UNIVERSE: Dict[str, str] = {
    # Rates
    "US 3M": "^IRX",
    "US 5Y": "^FVX",
    "US 10Y": "^TNX",
    "US 30Y": "^TYX",

    # FX
    "DXY": "DX-Y.NYB",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "USD/CHF": "CHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X",

    # Commodities
    "Gold": "GC=F",
    "Silver": "SI=F",
    "WTI": "CL=F",
    "Brent": "BZ=F",
    "Nat Gas": "NG=F",
    "Copper": "HG=F",
    "Corn": "ZC=F",
    "Wheat": "ZW=F",

    # Equities
    "S&P 500": "^GSPC",
    "Nasdaq 100": "^NDX",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "Euro Stoxx 50": "^STOXX50E",
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "VIX": "^VIX",

    # Bond ETFs
    "TLT": "TLT",
    "IEF": "IEF",
    "SHY": "SHY",
    "HYG": "HYG",
    "LQD": "LQD",
    "TIP": "TIP",

    # Crypto
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",
}

GROUPS: Dict[str, List[str]] = {
    "All": list(UNIVERSE.keys()),
    "Rates": ["US 3M", "US 5Y", "US 10Y", "US 30Y"],
    "FX": ["DXY", "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD"],
    "Commodities": ["Gold", "Silver", "WTI", "Brent", "Nat Gas", "Copper", "Corn", "Wheat"],
    "Equities": [
        "S&P 500", "Nasdaq 100", "Dow Jones", "Russell 2000",
        "Euro Stoxx 50", "DAX", "FTSE 100", "Nikkei 225", "Hang Seng", "VIX",
    ],
    "Bonds": ["TLT", "IEF", "SHY", "HYG", "LQD", "TIP"],
    "Crypto": ["Bitcoin", "Ethereum", "Solana"],
}

RATE_ORDER = ["US 3M", "US 5Y", "US 10Y", "US 30Y"]
RATE_MATURITY = {
    "US 3M": 0.25,
    "US 5Y": 5.0,
    "US 10Y": 10.0,
    "US 30Y": 30.0,
}

FX_LABELS = GROUPS["FX"]
COMMODITY_LABELS = GROUPS["Commodities"]
EQUITY_LABELS = GROUPS["Equities"]
BOND_LABELS = GROUPS["Bonds"]
CRYPTO_LABELS = GROUPS["Crypto"]

BACKTEST_EXCLUDE = {"VIX", "US 3M", "US 5Y", "US 10Y", "US 30Y"}

BASE_REQUIRED = [
    "S&P 500",
    "Nasdaq 100",
    "VIX",
    "US 3M",
    "US 5Y",
    "US 10Y",
    "US 30Y",
    "DXY",
    "EUR/USD",
    "Gold",
    "WTI",
    "TLT",
    "HYG",
    "LQD",
    "TIP",
    "Bitcoin",
]


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

if "load_macro_clicked" not in st.session_state:
    st.session_state["load_macro_clicked"] = False


def _set_load_macro_clicked() -> None:
    st.session_state["load_macro_clicked"] = True


# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def render_header() -> None:
    st.markdown(
        """
        <div style="margin-bottom:18px;padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.06);">
          <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;
                      letter-spacing:-0.3px;color:#dde4f0;">Macro Dashboard</div>
          <div style="font-size:12px;color:#7a8fa8;margin-top:3px;">
            Rates · FX · Commodities · Equities · Bonds · Crypto · Regime Detection
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_block(title: str, value: str, delta: str | None = None, delta_color: str | None = None) -> None:
    delta_html = (
        f'<div style="color:{delta_color or MUTED}; font-size:10.5px; margin-top:5px;">{delta}</div>'
        if delta
        else ""
    )
    st.markdown(
        f"""
        <div style="background:#131920; border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px; padding:14px 16px; min-height:88px;">
          <div style="color:#7a8fa8; font-size:10px; letter-spacing:0.4px;
                      text-transform:uppercase; margin-bottom:6px;">{title}</div>
          <div style="font-family:'DM Mono',monospace; font-size:22px; font-weight:500;
                      letter-spacing:-0.5px; color:#dde4f0;">{value}</div>
          {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_box(title: str, subtitle: str = "") -> None:
    sub_html = (
        f'<div style="color:#7a8fa8; font-size:11px; margin-top:4px;">{subtitle}</div>'
        if subtitle
        else ""
    )
    st.markdown(
        f"""
        <div style="font-size:9.5px;color:#3d5068;letter-spacing:1px;
                    text-transform:uppercase;font-weight:600;margin:2px 0 10px;">
          {title}
        </div>
        {sub_html}
        """,
        unsafe_allow_html=True,
    )


def _apply_chart_style(ax, title: str = "") -> None:
    ax.set_facecolor("#0d1117")
    ax.figure.patch.set_facecolor("#080b10")
    ax.tick_params(colors="#8899aa", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(MPL_BORDER)
    ax.grid(True, alpha=0.18, color=MPL_BORDER)
    if title:
        ax.set_title(title, color=TEXT, fontsize=10, fontweight="bold", pad=8)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

render_header()

st.sidebar.markdown("## ⚙️ Macro Controls")
st.sidebar.caption("Configure the lookback period, asset group and analytical parameters below.")

period = st.sidebar.selectbox(
    "Lookback period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3,
    help="Historical window used for all charts and calculations.",
)

focus_group = st.sidebar.selectbox(
    "Focus group",
    list(GROUPS.keys()),
    index=0,
    help="Which asset class to highlight in the overview table.",
)

roll_window = st.sidebar.slider(
    "Rolling vol window (days)",
    min_value=5,
    max_value=60,
    value=20,
    step=5,
    help="Number of trading days used to compute rolling realised volatility.",
)

benchmark_label = st.sidebar.selectbox(
    "Benchmark",
    ["S&P 500", "Gold", "DXY", "Bitcoin", "TLT"],
    index=0,
    help="Reference asset for the backtest comparison.",
)

backtest_assets = st.sidebar.multiselect(
    "Backtest basket",
    [x for x in UNIVERSE if x not in BACKTEST_EXCLUDE],
    default=["S&P 500", "Gold", "TLT"],
    help="Assets included in the equal-weight backtest portfolio.",
)

custom_input = st.sidebar.text_input(
    "Custom Yahoo tickers",
    placeholder="e.g. GLD, USO, XLE",
    help="Comma-separated Yahoo Finance tickers to add to the universe.",
)

st.sidebar.markdown("---")
st.sidebar.button(
    "🚀 Load Macro Dashboard",
    use_container_width=True,
    on_click=_set_load_macro_clicked,
)

if not st.session_state["load_macro_clicked"]:
    st.markdown(
        f"""
        <div style="background:#0d1117;
                    border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:36px;
                    margin-top:16px; text-align:center;">
          <div style="font-size:46px; margin-bottom:10px;">🌍</div>
          <div style="font-size:22px; font-weight:800; color:{TEXT}; margin-bottom:8px;">
            Global Macro Control Center
          </div>
          <div style="color:{MUTED}; font-size:13px; line-height:1.9; max-width:760px; margin:0 auto;">
            Configure your parameters in the sidebar, then press
            <strong style="color:{ACCENT};">Load Macro Dashboard</strong> to pull live data.<br>
            The dashboard covers <strong>rates · FX · commodities · equities · bonds · crypto</strong>
            with snapshot tables, momentum rankings, yield curve, FX heatmap, inflation proxy,
            correlation matrix, equal-weight backtest and market-regime detection.
          </div>
          <div style="margin-top:20px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
            <span style="padding:4px 12px; border-radius:999px; font-size:11px;
                         border:1px solid {BORDER}; color:{ACCENT};">
              {len(UNIVERSE)} assets in universe
            </span>
            <span style="padding:4px 12px; border-radius:999px; font-size:11px;
                         border:1px solid {BORDER}; color:{ACCENT2};">
              Data cached 10 min
            </span>
            <span style="padding:4px 12px; border-radius:999px; font-size:11px;
                         border:1px solid {BORDER}; color:{MUTED};">
              Educational use only
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# DATA HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def parse_custom_tickers(raw: str) -> List[str]:
    if not raw.strip():
        return []
    seen = set()
    out = []
    for item in raw.split(","):
        sym = item.strip().upper()
        if sym and sym not in seen:
            seen.add(sym)
            out.append(sym)
    return out


@st.cache_data(ttl=600)
def load_macro_prices(labels: List[str], period: str = "1y") -> pd.DataFrame:
    data: Dict[str, pd.Series] = {}

    for label in labels:
        ticker = UNIVERSE.get(label, label)
        try:
            s = load_close_series(ticker, period=period, source="auto")
            if s is None:
                continue
            if isinstance(s, pd.DataFrame):
                if s.empty:
                    continue
                s = s.iloc[:, 0]

            s = pd.to_numeric(s, errors="coerce").dropna()
            if s.empty:
                continue

            data[label] = s
        except Exception:
            continue

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data).sort_index().dropna(how="all")


def _safe_pct_change(series: pd.Series) -> pd.Series:
    return series.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan).dropna()


def _rsi(series: pd.Series, window: int = 14) -> float:
    delta = series.diff().dropna()
    if len(delta) < window:
        return float("nan")

    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()

    loss = loss.replace(0, np.nan)
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    if rsi.empty:
        return float("nan")
    return float(rsi.iloc[-1])


def _sharpe(returns: pd.Series, rf: float = 0.0) -> float:
    if returns.empty:
        return float("nan")
    excess = returns - rf / 252
    std = excess.std()
    if std == 0 or pd.isna(std):
        return float("nan")
    return float(excess.mean() / std * np.sqrt(252))


def _sortino(returns: pd.Series, rf: float = 0.0) -> float:
    if returns.empty:
        return float("nan")
    excess = returns - rf / 252
    downside = excess[excess < 0].std()
    if downside == 0 or pd.isna(downside):
        return float("nan")
    return float(excess.mean() / downside * np.sqrt(252))


def _calmar(returns: pd.Series) -> float:
    if returns.empty:
        return float("nan")
    curve = (1 + returns).cumprod()
    max_dd = (curve / curve.cummax() - 1).min()
    if max_dd == 0 or pd.isna(max_dd):
        return float("nan")
    ann_ret = annualized_return(returns)
    return float(ann_ret / abs(max_dd))


def calc_snapshot(prices: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for col in prices.columns:
        s = pd.to_numeric(prices[col], errors="coerce").dropna()
        if len(s) < 3:
            continue

        rets = _safe_pct_change(s)
        last = float(s.iloc[-1])

        def perf(n: int) -> float:
            if len(s) <= n:
                return float("nan")
            return (float(s.iloc[-1] / s.iloc[-1 - n]) - 1.0) * 100

        year_start = s[s.index.year == s.index[-1].year]
        ytd = (
            (float(s.iloc[-1] / year_start.iloc[0]) - 1.0) * 100
            if len(year_start) > 1
            else float("nan")
        )

        rows.append(
            {
                "Asset": col,
                "Last": last,
                "1D %": perf(1),
                "5D %": perf(5),
                "1M %": perf(21),
                "3M %": perf(63),
                "YTD %": ytd,
                "20D Vol %": annualized_vol(rets.tail(20)) * 100 if len(rets) >= 20 else float("nan"),
                "Ann. Ret %": annualized_return(rets) * 100 if len(rets) > 10 else float("nan"),
                "RSI(14)": _rsi(s, 14),
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def compute_regime(prices: pd.DataFrame) -> Tuple[str, str]:
    if "S&P 500" not in prices.columns:
        return "Unavailable", MUTED

    spx = prices["S&P 500"].dropna()
    if len(spx) < 60:
        return "Unavailable", MUTED

    sma20 = spx.rolling(20).mean()
    sma60 = spx.rolling(60).mean()

    latest_spx = float(spx.iloc[-1])
    latest_20 = float(sma20.iloc[-1]) if pd.notna(sma20.iloc[-1]) else np.nan
    latest_60 = float(sma60.iloc[-1]) if pd.notna(sma60.iloc[-1]) else np.nan

    if not (np.isfinite(latest_20) and np.isfinite(latest_60)):
        return "Unavailable", MUTED

    vix_ser = prices["VIX"].dropna() if "VIX" in prices.columns else pd.Series(dtype=float)
    vix = float(vix_ser.iloc[-1]) if not vix_ser.empty else np.nan

    if latest_spx > latest_20 > latest_60:
        if np.isfinite(vix) and vix >= 25:
            return "Bull / High Vol", YELLOW
        return "Bull Market", GREEN

    if latest_spx < latest_20 < latest_60:
        return "Bear Market", RED

    return "Transition / Choppy", ORANGE


def build_spread_stats(snapshot: pd.DataFrame) -> Tuple[float, str, str]:
    if not {"US 10Y", "US 3M"}.issubset(set(snapshot["Asset"].values)):
        return float("nan"), "Unavailable", MUTED

    y10 = float(snapshot.loc[snapshot["Asset"] == "US 10Y", "Last"].iloc[0])
    y3m = float(snapshot.loc[snapshot["Asset"] == "US 3M", "Last"].iloc[0])

    spread_pct_pts = y10 - y3m
    state = "Inverted ⚠" if spread_pct_pts < 0 else "Normal"
    color = RED if spread_pct_pts < 0 else GREEN
    return spread_pct_pts, state, color


# ══════════════════════════════════════════════════════════════════════════════
# TABLE STYLING
# ══════════════════════════════════════════════════════════════════════════════

def style_perf_table(df: pd.DataFrame):
    fmt = {
        "Last": "{:,.2f}",
        "1D %": "{:.2f}%",
        "5D %": "{:.2f}%",
        "1M %": "{:.2f}%",
        "3M %": "{:.2f}%",
        "YTD %": "{:.2f}%",
        "20D Vol %": "{:.2f}%",
        "Ann. Ret %": "{:.2f}%",
        "RSI(14)": "{:.1f}",
    }
    fmt = {k: v for k, v in fmt.items() if k in df.columns}

    perf_cols = {"1D %", "5D %", "1M %", "3M %", "YTD %", "Ann. Ret %"}

    def row_style(row):
        styled = []
        for c in row.index:
            if c in perf_cols and pd.notna(row[c]):
                styled.append(f"color:{GREEN}" if row[c] >= 0 else f"color:{RED}")
            else:
                styled.append("")
        return styled

    def rsi_style(val):
        if pd.isna(val):
            return ""
        if val >= 70:
            return f"color:{RED}"
        if val <= 30:
            return f"color:{GREEN}"
        return ""

    styler = df.style.format(fmt, na_rep="—").apply(row_style, axis=1)

    if "RSI(14)" in df.columns:
        try:
            styler = styler.map(rsi_style, subset=["RSI(14)"])
        except Exception:
            try:
                styler = styler.applymap(rsi_style, subset=["RSI(14)"])
            except Exception:
                pass

    return styler


# ══════════════════════════════════════════════════════════════════════════════
# CHART SECTIONS
# ══════════════════════════════════════════════════════════════════════════════

def create_fx_heatmap(snapshot: pd.DataFrame) -> None:
    fx = snapshot[snapshot["Asset"].isin([x for x in FX_LABELS if x in snapshot["Asset"].values])].copy()
    if fx.empty:
        st.info("No FX data available.")
        return

    heat_cols = ["1D %", "5D %", "1M %", "3M %"]
    heat = fx.set_index("Asset")[heat_cols].dropna(how="all")

    if heat.empty:
        st.info("No FX heatmap data available.")
        return

    vals = heat.values.astype(float)
    finite_vals = vals[np.isfinite(vals)]
    vmax = max(np.nanpercentile(np.abs(finite_vals), 90) if finite_vals.size else 1, 0.20)

    cmap = mcolors.LinearSegmentedColormap.from_list("fx_heat", [RED, "#111827", GREEN])

    fig, ax = plt.subplots(figsize=(8, max(3.5, len(heat) * 0.48)))
    _apply_chart_style(ax, "FX Performance Heatmap")
    im = ax.imshow(vals, cmap=cmap, vmin=-vmax, vmax=vmax, aspect="auto")

    ax.set_xticks(range(len(heat_cols)))
    ax.set_xticklabels(heat_cols, fontsize=9, color="#aabbcc")
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index, fontsize=9, color="#aabbcc")

    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            if np.isfinite(vals[i, j]):
                ax.text(j, i, f"{vals[i, j]:.2f}", ha="center", va="center", fontsize=8, color="white", fontweight="bold")

    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def create_inflation_proxy_chart(prices: pd.DataFrame) -> None:
    req = [x for x in ["Gold", "WTI", "Copper", "Corn", "TIP"] if x in prices.columns]
    if len(req) < 3:
        st.info("Need at least 3 of: Gold, WTI, Copper, Corn, TIP to build the inflation proxy.")
        return

    base = prices[req].dropna(how="all").ffill().dropna()
    if base.empty:
        st.info("Inflation proxy: insufficient data.")
        return

    norm = base / base.iloc[0] * 100
    proxy = norm.mean(axis=1)

    with st.expander("ℹ️ What is the Inflation Proxy Basket?", expanded=False):
        st.markdown(
            "An equal-weight composite of commodity and inflation-linked assets "
            "(Gold, WTI crude, Copper, Corn, TIP ETF). When the basket rises relative "
            "to its base value, broad price pressures may be building. "
            "This is a proxy, not a direct inflation measure."
        )

    fig, ax = plt.subplots(figsize=(10, 4))
    _apply_chart_style(ax, "Inflation Proxy Basket (Indexed to 100)")

    for i, col in enumerate(norm.columns):
        ax.plot(norm.index, norm[col], lw=1.3, alpha=0.65, color=PALETTE[i % len(PALETTE)], label=col)

    ax.plot(proxy.index, proxy.values, lw=2.6, color="white", label="Basket Average", zorder=5)
    ax.axhline(100, color=MUTED, lw=0.8, ls="--")
    ax.legend(fontsize=8, ncols=3, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def create_backtest(prices: pd.DataFrame, basket: List[str], benchmark: str) -> None:
    valid_assets = [x for x in basket if x in prices.columns]
    if not valid_assets:
        st.info("Choose at least one valid asset for the backtest.")
        return

    panel = prices[valid_assets].dropna(how="all").ffill().dropna()
    if panel.empty or len(panel) < 10:
        st.info("Not enough data for the backtest.")
        return

    returns = panel.pct_change(fill_method=None).dropna()
    if returns.empty:
        st.info("Not enough return history.")
        return

    weights = np.repeat(1.0 / len(valid_assets), len(valid_assets))
    port_ret = returns.dot(weights)
    port_curve = (1 + port_ret).cumprod()
    drawdown = port_curve / port_curve.cummax() - 1

    bench_curve = None
    if benchmark in prices.columns:
        bench = prices[benchmark].reindex(panel.index).ffill().dropna()
        if len(bench) > 1:
            bench_curve = bench / bench.iloc[0]

    total_return = (port_curve.iloc[-1] - 1) * 100
    ann_ret = annualized_return(port_ret) * 100
    ann_vol = annualized_vol(port_ret) * 100
    max_dd = drawdown.min() * 100
    sharpe = _sharpe(port_ret)
    sortino = _sortino(port_ret)
    calmar = _calmar(port_ret)

    with st.expander("ℹ️ About this backtest", expanded=False):
        st.markdown(
            f"**Equal-weight portfolio** rebalanced daily across: {', '.join(valid_assets)}.  \n"
            "Returns assume no transaction costs, slippage or taxes.  \n"
            "**Sharpe** = annualised excess return ÷ annualised vol.  \n"
            "**Sortino** = annualised excess return ÷ downside deviation.  \n"
            "**Calmar** = annualised return ÷ |max drawdown|.  \n"
            "*Past performance is not indicative of future results.*"
        )

    cols = st.columns(7)
    metrics = [
        ("Total Return", f"{total_return:.2f}%"),
        ("Ann. Return", f"{ann_ret:.2f}%"),
        ("Ann. Vol", f"{ann_vol:.2f}%"),
        ("Max Drawdown", f"{max_dd:.2f}%"),
        ("Sharpe", f"{sharpe:.2f}" if np.isfinite(sharpe) else "—"),
        ("Sortino", f"{sortino:.2f}" if np.isfinite(sortino) else "—"),
        ("Calmar", f"{calmar:.2f}" if np.isfinite(calmar) else "—"),
    ]

    for col, (label, val) in zip(cols, metrics):
        col.metric(label, val)

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), gridspec_kw={"height_ratios": [3, 1.2]})
    ax_growth, ax_dd = axes

    _apply_chart_style(ax_growth, "Portfolio Growth (Equal-Weight Basket)")
    ax_growth.plot(port_curve.index, port_curve.values, lw=2.2, color=ACCENT, label="Basket")

    if bench_curve is not None and not bench_curve.empty:
        aligned = bench_curve.reindex(port_curve.index).dropna()
        if not aligned.empty:
            ax_growth.plot(aligned.index, aligned.values, lw=1.8, ls="--", color=ACCENT2, label=benchmark)

    ax_growth.axhline(1.0, color=MUTED, lw=0.7, ls=":")
    ax_growth.legend(fontsize=8, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)

    _apply_chart_style(ax_dd, "Drawdown from Peak")
    ax_dd.fill_between(drawdown.index, drawdown.values, 0, color=RED, alpha=0.45)
    ax_dd.plot(drawdown.index, drawdown.values, lw=1.2, color=RED)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    contrib = ((panel.iloc[-1] / panel.iloc[0]) - 1).sort_values()
    fig2, ax2 = plt.subplots(figsize=(8, max(3.5, len(contrib) * 0.44)))
    _apply_chart_style(ax2, "Individual Asset Total Returns in Basket")

    bar_colors = [GREEN if v >= 0 else RED for v in contrib.values]
    ax2.barh(contrib.index, contrib.values * 100, color=bar_colors, edgecolor="#0d1117", height=0.65)
    ax2.axvline(0, color="white", lw=0.8, ls="--")
    ax2.set_xlabel("Return (%)", color="#aabbcc", fontsize=9)
    ax2.tick_params(axis="y", colors="#aabbcc")

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)


# ══════════════════════════════════════════════════════════════════════════════
# DATA PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

custom_tickers = parse_custom_tickers(custom_input)
active_labels = GROUPS[focus_group].copy()

for sym in custom_tickers:
    UNIVERSE.setdefault(sym, sym)
    if sym not in active_labels:
        active_labels.append(sym)

labels_to_load = list(dict.fromkeys(active_labels + BASE_REQUIRED + backtest_assets + [benchmark_label]))

with st.spinner("Loading cross-asset market data…"):
    prices = load_macro_prices(labels_to_load, period=period)

if prices.empty:
    st.error("❌ No market data could be loaded. Check your connection or try a different period.")
    st.stop()

snap = calc_snapshot(prices)
if snap.empty:
    st.error("❌ Snapshot could not be built from the loaded data.")
    st.stop()

up_today = int((snap["1D %"] > 0).sum())
down_today = int((snap["1D %"] < 0).sum())
avg_vol = snap["20D Vol %"].mean()
regime_label, regime_color = compute_regime(prices)
curve_spread, spread_state, spread_color = build_spread_stats(snap)

headline = [
    x for x in ["S&P 500", "Nasdaq 100", "VIX", "US 10Y", "DXY", "Gold", "WTI", "Bitcoin"]
    if x in snap["Asset"].values
]

if headline:
    hl_cols = st.columns(min(8, len(headline)))
    for i, lbl in enumerate(headline[: len(hl_cols)]):
        row = snap.loc[snap["Asset"] == lbl].iloc[0]
        delta = row["1D %"]
        color = GREEN if pd.notna(delta) and delta >= 0 else RED
        last_fmt = f"{row['Last']:,.2f}" if abs(row["Last"]) < 100_000 else f"{row['Last']:,.0f}"

        with hl_cols[i]:
            metric_block(lbl, last_fmt, f"{delta:+.2f}%" if pd.notna(delta) else "—", color)

st.markdown("")

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    metric_block("Assets Loaded", str(len(snap)))
with k2:
    metric_block(
        "Up / Down Today",
        f"{up_today} / {down_today}",
        "Breadth positive" if up_today >= down_today else "Breadth negative",
        GREEN if up_today >= down_today else RED,
    )
with k3:
    metric_block("Avg 20D Vol", f"{avg_vol:.1f}%", "Realised volatility cross-asset")
with k4:
    metric_block(
        "10Y − 3M Spread",
        f"{curve_spread:.2f} pts" if np.isfinite(curve_spread) else "—",
        spread_state,
        spread_color,
    )
with k5:
    metric_block("Market Regime", regime_label)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tabs = st.tabs([
    "📊 Overview",
    "💱 FX & Commodities",
    "📈 Equities & Crypto",
    "📉 Rates & Bonds",
    "🔗 Correlation",
    "🧮 Backtest",
    "🎯 Regime",
])

with tabs[0]:
    left, right = st.columns([1.35, 1], gap="large")

    with left:
        section_box(
            "Cross-Asset Monitor",
            "Sortable snapshot — green/red = return direction; RSI(14) > 70 = overbought, < 30 = oversold",
        )
        sort_by = st.selectbox(
            "Sort by",
            ["1D %", "1M %", "3M %", "YTD %", "20D Vol %", "Ann. Ret %", "RSI(14)", "Asset"],
            key="macro_sort",
        )
        ascending = st.checkbox("Ascending", value=False, key="macro_asc")
        disp = snap.sort_values(sort_by, ascending=ascending).reset_index(drop=True)

        cols = ["Asset", "Last", "1D %", "5D %", "1M %", "3M %", "YTD %", "20D Vol %", "Ann. Ret %", "RSI(14)"]
        st.dataframe(style_perf_table(disp[cols]), use_container_width=True, height=540)

    with right:
        section_box("1M Momentum Ranking", "Relative strength — sorted by 1-month return")
        rank = snap.dropna(subset=["1M %"]).sort_values("1M %")

        fig, ax = plt.subplots(figsize=(8, max(4, len(rank) * 0.28)))
        _apply_chart_style(ax, "1-Month Return (%)")
        bar_cols = [GREEN if v >= 0 else RED for v in rank["1M %"]]
        ax.barh(rank["Asset"], rank["1M %"], color=bar_cols, edgecolor="#0d1117", height=0.7)
        ax.axvline(0, color="white", lw=0.8, ls="--")
        ax.set_xlabel("Return (%)", color="#aabbcc", fontsize=9)
        ax.tick_params(axis="y", colors="#aabbcc", labelsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        section_box("Performance Heatmap", "Colour intensity = magnitude; red = negative, green = positive")
        heat_cols_ov = ["1D %", "5D %", "1M %", "3M %", "YTD %"]
        heat = snap.set_index("Asset")[heat_cols_ov].dropna(how="all")

        vals = heat.values.astype(float)
        finite_vals = vals[np.isfinite(vals)]
        vmax = max(np.nanpercentile(np.abs(finite_vals), 95) if finite_vals.size else 1, 0.25)
        cmap = mcolors.LinearSegmentedColormap.from_list("perf_heat", [RED, "#111827", GREEN])

        fig2, ax2 = plt.subplots(figsize=(8, max(4, len(heat) * 0.28)))
        _apply_chart_style(ax2, "Multi-Horizon Performance Heatmap")
        im = ax2.imshow(vals, aspect="auto", cmap=cmap, vmin=-vmax, vmax=vmax)

        ax2.set_xticks(range(len(heat_cols_ov)))
        ax2.set_xticklabels(heat_cols_ov, fontsize=9, color="#aabbcc")
        ax2.set_yticks(range(len(heat.index)))
        ax2.set_yticklabels(heat.index, fontsize=8, color="#aabbcc")

        for i in range(vals.shape[0]):
            for j in range(vals.shape[1]):
                if np.isfinite(vals[i, j]):
                    ax2.text(j, i, f"{vals[i, j]:.1f}", ha="center", va="center", fontsize=7, color="white")

        plt.colorbar(im, ax=ax2, fraction=0.025, pad=0.02)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

with tabs[1]:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        section_box("FX Dashboard", "Major currency pairs — performance and heatmap")
        fx_snap = snap[snap["Asset"].isin([x for x in FX_LABELS if x in snap["Asset"].values])].copy()

        if not fx_snap.empty:
            st.dataframe(
                style_perf_table(fx_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %", "RSI(14)"]]),
                use_container_width=True,
                height=300,
            )

            with st.expander("ℹ️ Reading the FX table", expanded=False):
                st.markdown(
                    "DXY measures the US dollar against a basket of six major currencies. "
                    "A rising DXY often signals USD strength, which can pressure commodities, "
                    "emerging markets and risk assets."
                )

        create_fx_heatmap(snap)

    with c2:
        section_box("Commodities + Inflation Proxy", "Energy, metals, agriculture and inflation-linked basket")
        comm_snap = snap[snap["Asset"].isin([x for x in COMMODITY_LABELS if x in snap["Asset"].values])].copy()

        if not comm_snap.empty:
            st.dataframe(
                style_perf_table(comm_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %", "RSI(14)"]]),
                use_container_width=True,
                height=300,
            )

        create_inflation_proxy_chart(prices)

with tabs[2]:
    left, right = st.columns(2, gap="large")

    with left:
        section_box("Global Equities", "US and international equity index performance")
        eq_snap = snap[snap["Asset"].isin([x for x in EQUITY_LABELS if x in snap["Asset"].values])].copy()

        if not eq_snap.empty:
            st.dataframe(
                style_perf_table(eq_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %", "RSI(14)"]]),
                use_container_width=True,
                height=320,
            )

        eq_prices = prices[[x for x in EQUITY_LABELS if x in prices.columns]]
        if not eq_prices.empty:
            sel = st.multiselect(
                "Equity indices to chart",
                eq_prices.columns.tolist(),
                default=eq_prices.columns.tolist()[:5],
                key="macro_eq_sel",
            )
            if sel:
                norm = eq_prices[sel] / eq_prices[sel].iloc[0] * 100
                fig, ax = plt.subplots(figsize=(10, 4))
                _apply_chart_style(ax, "Equity Indices — Indexed to 100")
                for i, col in enumerate(norm.columns):
                    ax.plot(norm.index, norm[col], lw=1.8, label=col, color=PALETTE[i % len(PALETTE)])
                ax.axhline(100, color="white", lw=0.8, ls="--")
                ax.legend(fontsize=8, ncols=3, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

    with right:
        section_box("Crypto Monitor", "Crypto prices, rolling volatility and RSI signals")
        crypto_snap = snap[snap["Asset"].isin([x for x in CRYPTO_LABELS if x in snap["Asset"].values])].copy()

        if not crypto_snap.empty:
            st.dataframe(
                style_perf_table(crypto_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %", "RSI(14)"]]),
                use_container_width=True,
                height=200,
            )

        crypto_prices = prices[[x for x in CRYPTO_LABELS if x in prices.columns]]
        if not crypto_prices.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            _apply_chart_style(ax2, f"Rolling {roll_window}D Annualised Volatility (%)")

            for i, col in enumerate(crypto_prices.columns):
                rv = rolling_vol(crypto_prices[col].pct_change(fill_method=None).dropna(), window=roll_window) * 100
                ax2.plot(rv.index, rv.values, lw=1.8, label=col, color=PALETTE[i % len(PALETTE)])

            ax2.legend(fontsize=8, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

with tabs[3]:
    left, right = st.columns(2, gap="large")

    with left:
        section_box("Rates Panel", "US Treasury yield trend and current yield curve shape")
        rate_snap = snap[snap["Asset"].isin([x for x in RATE_ORDER if x in snap["Asset"].values])].copy()

        if not rate_snap.empty:
            st.dataframe(
                style_perf_table(rate_snap[["Asset", "Last", "1D %", "1M %", "3M %"]]),
                use_container_width=True,
                height=220,
            )

        available = [x for x in RATE_ORDER if x in prices.columns]
        if available:
            fig, ax = plt.subplots(figsize=(10, 4))
            _apply_chart_style(ax, "Treasury Yield Trend Panel")

            for i, col in enumerate(available):
                s = prices[col].dropna()
                ax.plot(s.index, s.values, lw=1.7, label=col, color=PALETTE[i % len(PALETTE)])

            ax.set_ylabel("Yield (%)", color="#aabbcc", fontsize=9)
            ax.legend(fontsize=8, ncols=2, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            xs = [RATE_MATURITY[x] for x in available]
            ys = [float(prices[x].dropna().iloc[-1]) for x in available]

            fig2, ax2 = plt.subplots(figsize=(10, 3.5))
            _apply_chart_style(ax2, "Current Yield Curve")
            ax2.plot(xs, ys, marker="o", lw=2.2, color=ACCENT, zorder=5)

            for x_pt, y_pt, lbl in zip(xs, ys, available):
                ax2.annotate(f"{y_pt:.2f}%", (x_pt, y_pt), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8, color=ACCENT)

            ax2.set_xticks(xs)
            ax2.set_xticklabels(available, color="#aabbcc")
            ax2.set_ylabel("Yield (%)", color="#aabbcc", fontsize=9)

            if np.isfinite(curve_spread) and curve_spread < 0:
                ax2.axhspan(min(ys) - 0.1, max(ys) + 0.1, alpha=0.06, color=RED)
                ax2.set_title("Current Yield Curve ⚠ INVERTED", color=RED, fontsize=10, fontweight="bold", pad=8)

            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

    with right:
        section_box("Bonds & Credit", "Duration, credit spreads and inflation-linked proxies")
        bond_snap = snap[snap["Asset"].isin([x for x in BOND_LABELS if x in snap["Asset"].values])].copy()

        if not bond_snap.empty:
            st.dataframe(
                style_perf_table(bond_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]),
                use_container_width=True,
                height=220,
            )

        if {"HYG", "LQD"}.issubset(prices.columns):
            ratio = (prices["HYG"] / prices["LQD"]).dropna()
            fig3, ax3 = plt.subplots(figsize=(10, 3.5))
            _apply_chart_style(ax3, "HYG / LQD Credit Risk Proxy")
            ax3.plot(ratio.index, ratio.values, lw=2.0, color=ACCENT2)
            ax3.axhline(ratio.mean(), color="white", lw=0.8, ls="--", label=f"Mean: {ratio.mean():.3f}")
            ax3.legend(fontsize=8, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

        if {"TLT", "TIP"}.issubset(prices.columns):
            spread = ((prices["TIP"] / prices["TIP"].iloc[0]) - (prices["TLT"] / prices["TLT"].iloc[0])) * 100
            fig4, ax4 = plt.subplots(figsize=(10, 3.5))
            _apply_chart_style(ax4, "TIP vs TLT Relative Performance (Inflation vs Duration)")
            ax4.plot(spread.index, spread.values, lw=2.0, color=YELLOW)
            ax4.axhline(0, color="white", lw=0.8, ls="--")
            ax4.fill_between(spread.index, spread.values, 0, where=(spread.values > 0), alpha=0.18, color=GREEN)
            ax4.fill_between(spread.index, spread.values, 0, where=(spread.values < 0), alpha=0.18, color=RED)
            plt.tight_layout()
            st.pyplot(fig4)
            plt.close(fig4)

with tabs[4]:
    section_box(
        "Correlation Matrix",
        "Daily return correlation — blue = positive, red = negative; values near ±1 = strong co-movement",
    )

    corr_assets = st.multiselect(
        "Assets for correlation",
        prices.columns.tolist(),
        default=prices.columns.tolist()[: min(14, len(prices.columns))],
        key="macro_corr_assets",
    )

    if len(corr_assets) >= 2:
        rets = prices[corr_assets].pct_change(fill_method=None).dropna(how="all")
        corr = correlation_matrix(rets)
        n = len(corr_assets)

        fig, ax = plt.subplots(figsize=(max(7, n * 0.72), max(5, n * 0.58)))
        _apply_chart_style(ax, f"Return Correlation Matrix ({period} lookback)")
        cmap = mcolors.LinearSegmentedColormap.from_list("corr", [RED, "#111827", ACCENT])
        im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)

        ax.set_xticks(range(n))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8, color="#aabbcc")
        ax.set_yticks(range(n))
        ax.set_yticklabels(corr.index, fontsize=8, color="#aabbcc")

        for i in range(n):
            for j in range(n):
                ax.text(
                    j,
                    i,
                    f"{corr.values[i, j]:.2f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white",
                    fontweight="bold" if abs(corr.values[i, j]) > 0.7 else "normal",
                )

        plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Select at least two assets to compute the correlation matrix.")

with tabs[5]:
    section_box(
        "Macro Basket Backtest",
        "Equal-weight portfolio — Sharpe, Sortino, Calmar, drawdown profile and asset contributions",
    )
    create_backtest(prices, backtest_assets, benchmark_label)

with tabs[6]:
    left, right = st.columns(2, gap="large")

    with left:
        section_box("Market Regime Detector", "Trend structure (SMA 20/60) + VIX volatility overlay")

        regime_descriptions = {
            "Bull Market": "S&P 500 is above both its 20-day and 60-day moving averages with VIX below 25.",
            "Bull / High Vol": "S&P 500 is in an uptrend but VIX ≥ 25 signals elevated fear.",
            "Bear Market": "S&P 500 is below both its 20-day and 60-day moving averages.",
            "Transition / Choppy": "Price and moving averages are in a mixed state.",
            "Unavailable": "Insufficient data to determine regime.",
        }

        desc = regime_descriptions.get(regime_label, "")

        st.markdown(
            f"""
            <div style="background:linear-gradient(180deg,#0d1117 0%,#0d1526 100%);
                        border:1px solid {regime_color}; border-radius:12px;
                        padding:18px; margin-bottom:12px;">
              <div style="color:{MUTED}; font-size:10px; font-weight:800;
                          letter-spacing:0.14em; text-transform:uppercase;">Current Regime</div>
              <div style="color:{regime_color}; font-size:28px; font-weight:900; margin-top:8px;">
                {regime_label}
              </div>
              <div style="color:{MUTED}; font-size:11px; margin-top:8px; line-height:1.6;">
                {desc}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if "S&P 500" in prices.columns:
            spx = prices["S&P 500"].dropna()
            sma20 = spx.rolling(20).mean()
            sma60 = spx.rolling(60).mean()

            fig, ax = plt.subplots(figsize=(10, 4))
            _apply_chart_style(ax, "S&P 500 Trend Structure")
            ax.plot(spx.index, spx.values, lw=1.9, color=ACCENT, label="S&P 500")
            ax.plot(sma20.index, sma20.values, lw=1.2, ls="--", color=YELLOW, label="SMA 20")
            ax.plot(sma60.index, sma60.values, lw=1.2, ls="--", color=RED, label="SMA 60")
            ax.fill_between(
                spx.index,
                sma60.reindex(spx.index),
                spx.values,
                where=(spx.values < sma60.reindex(spx.index).values),
                alpha=0.12,
                color=RED,
                interpolate=True,
            )
            ax.legend(fontsize=8, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with right:
        section_box("Cross-Asset Leadership", "Relative 1M and 3M performance of key macro assets")
        leaders = snap[snap["Asset"].isin([x for x in ["S&P 500", "Gold", "TLT", "DXY", "Bitcoin", "WTI"] if x in snap["Asset"].values])]

        if not leaders.empty:
            st.dataframe(
                leaders[["Asset", "1M %", "3M %", "20D Vol %", "RSI(14)"]]
                .set_index("Asset")
                .style.format({
                    "1M %": "{:.2f}%",
                    "3M %": "{:.2f}%",
                    "20D Vol %": "{:.2f}%",
                    "RSI(14)": "{:.1f}",
                }),
                use_container_width=True,
                height=270,
            )

        if {"US 10Y", "US 3M"}.issubset(prices.columns):
            spread_ts = (prices["US 10Y"] - prices["US 3M"]).dropna()

            fig2, ax2 = plt.subplots(figsize=(10, 4))
            _apply_chart_style(ax2, "10Y − 3M Yield Spread Through Time")
            ax2.plot(spread_ts.index, spread_ts.values, color=ACCENT2, lw=2.0)
            ax2.axhline(0, color=RED, lw=1.0, ls="--", label="Inversion threshold")
            ax2.fill_between(spread_ts.index, spread_ts.values, 0, where=(spread_ts.values < 0), alpha=0.18, color=RED, label="Inverted")
            ax2.fill_between(spread_ts.index, spread_ts.values, 0, where=(spread_ts.values >= 0), alpha=0.10, color=GREEN)
            ax2.set_ylabel("Spread (pts)", color="#aabbcc", fontsize=9)
            ax2.legend(fontsize=8, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

        if "VIX" in prices.columns:
            vix = prices["VIX"].dropna()

            fig3, ax3 = plt.subplots(figsize=(10, 3.5))
            _apply_chart_style(ax3, "VIX — Fear Gauge")
            ax3.plot(vix.index, vix.values, lw=1.8, color=ORANGE)
            ax3.axhline(20, color=YELLOW, lw=0.9, ls="--", label="Elevated (20)")
            ax3.axhline(30, color=RED, lw=0.9, ls="--", label="Panic (30)")
            ax3.fill_between(vix.index, vix.values, 20, where=(vix.values > 20), alpha=0.15, color=RED)
            ax3.legend(fontsize=8, facecolor="#0d1117", labelcolor="#aabbcc", framealpha=0.6)
            ax3.set_ylabel("VIX", color="#aabbcc", fontsize=9)
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    f"""
    <div style="color:{MUTED}; font-size:11px; text-align:center;
                letter-spacing:0.10em; text-transform:uppercase;">
      QuantDesk Pro · Macro Dashboard Pro ·
      Data via yfinance ·
      Cached {datetime.datetime.utcnow().strftime('%H:%M UTC')} ·
      Educational use only — not financial advice
    </div>
    """,
    unsafe_allow_html=True,
)
app_footer()
