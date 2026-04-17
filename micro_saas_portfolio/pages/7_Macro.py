import datetime

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from auth import require_login, sidebar_user_widget
from utils import (
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
)
from data_loader import load_close_series
from analytics import annualized_return, annualized_vol, correlation_matrix, rolling_vol


st.set_page_config(page_title="Macro Dashboard Pro", layout="wide", page_icon="🌍")
apply_theme()
require_login()
sidebar_user_widget()

st.markdown(
    f"""
    <div style="padding: 4px 0 16px 0; border-bottom: 1px solid {BORDER}; margin-bottom: 18px;">
      <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
        <span style="font-size:28px; font-weight:900; color:{TEXT}; letter-spacing:-0.02em;">
          Macro Dashboard Pro
        </span>
        <span style="padding:3px 8px; border-radius:999px; font-size:10px; font-weight:800;
                     border:1px solid {BORDER}; color:{ACCENT};">
          MULTI-ASSET
        </span>
        <span style="padding:3px 8px; border-radius:999px; font-size:10px; font-weight:800;
                     border:1px solid {BORDER}; color:{ACCENT2};">
          CROSS-ASSET
        </span>
      </div>
      <div style="margin-top:7px; font-size:12px; color:{MUTED};">
        Global markets monitor for rates, FX, commodities, equities, bonds and crypto with relative performance,
        regime tracking and simple backtesting.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


UNIVERSE = {
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
    # Bonds / ETFs
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

GROUPS = {
    "All": list(UNIVERSE.keys()),
    "Rates": ["US 3M", "US 5Y", "US 10Y", "US 30Y"],
    "FX": ["DXY", "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD"],
    "Commodities": ["Gold", "Silver", "WTI", "Brent", "Nat Gas", "Copper", "Corn", "Wheat"],
    "Equities": [
        "S&P 500", "Nasdaq 100", "Dow Jones", "Russell 2000", "Euro Stoxx 50",
        "DAX", "FTSE 100", "Nikkei 225", "Hang Seng", "VIX",
    ],
    "Bonds": ["TLT", "IEF", "SHY", "HYG", "LQD", "TIP"],
    "Crypto": ["Bitcoin", "Ethereum", "Solana"],
}

RATE_ORDER = ["US 3M", "US 5Y", "US 10Y", "US 30Y"]
RATE_MATURITY = {"US 3M": 0.25, "US 5Y": 5, "US 10Y": 10, "US 30Y": 30}
FX_LABELS = GROUPS["FX"]
COMMODITY_LABELS = GROUPS["Commodities"]
EQUITY_LABELS = GROUPS["Equities"]
BOND_LABELS = GROUPS["Bonds"]
CRYPTO_LABELS = GROUPS["Crypto"]

if "load_macro_clicked" not in st.session_state:
    st.session_state["load_macro_clicked"] = False


def _set_load_macro_clicked():
    st.session_state["load_macro_clicked"] = True


st.sidebar.markdown("## Macro Controls")
period = st.sidebar.selectbox("Lookback period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
focus_group = st.sidebar.selectbox("Focus group", list(GROUPS.keys()), index=0)
roll_window = st.sidebar.slider("Rolling vol window", 5, 60, 20, 5)
benchmark_label = st.sidebar.selectbox(
    "Benchmark for correlation / backtest",
    ["S&P 500", "Gold", "DXY", "Bitcoin", "TLT"],
    index=0,
)
backtest_assets = st.sidebar.multiselect(
    "Backtest basket",
    [x for x in UNIVERSE.keys() if x not in {"VIX", "US 3M", "US 5Y", "US 10Y", "US 30Y"}],
    default=["S&P 500", "Gold", "TLT"],
)
custom_input = st.sidebar.text_input("Custom Yahoo tickers", placeholder="e.g. GLD, USO, XLE")
run_page = st.sidebar.button("Load Macro Dashboard", use_container_width=True, on_click=_set_load_macro_clicked)

if not st.session_state["load_macro_clicked"]:
    st.markdown(
        f"""
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                    border:1px solid {BORDER}; border-radius:12px; padding:28px; margin-top:16px; text-align:center;">
          <div style="font-size:38px; margin-bottom:8px;">🌍</div>
          <div style="font-size:20px; font-weight:800; color:{TEXT}; margin-bottom:6px;">Global Macro Control Center</div>
          <div style="color:{MUTED}; font-size:13px; line-height:1.8; max-width:760px; margin:0 auto;">
            Load a cross-asset dashboard with monitor tables, FX heatmap, rates panel, inflation proxy,
            macro backtesting, yield curve and regime tracking.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


@st.cache_data(ttl=600)
def load_macro_prices(labels, period="1y") -> pd.DataFrame:
    data = {}
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


@st.cache_data(ttl=600)
def load_single_series(label: str, period: str = "1y") -> pd.Series:
    ticker = UNIVERSE.get(label, label)
    s = load_close_series(ticker, period=period, source="auto")
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    return pd.to_numeric(s, errors="coerce").dropna()


def metric_block(title: str, value: str, delta: str | None = None, delta_color: str | None = None):
    delta_html = ""
    if delta:
        color = delta_color or MUTED
        delta_html = f'<div style="color:{color}; font-size:12px; font-weight:700; margin-top:4px;">{delta}</div>'
    st.markdown(
        f"""
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0e1627 100%); border:1px solid {BORDER};
                    border-radius:12px; padding:14px 16px; min-height:92px;">
          <div style="color:{MUTED}; font-size:10px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">{title}</div>
          <div style="color:{TEXT}; font-size:24px; font-weight:900; margin-top:8px;">{value}</div>
          {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_box(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                    border:1px solid {BORDER}; border-radius:10px; padding:12px 14px; margin-bottom:12px;">
          <div style="color:{TEXT}; font-size:12px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">{title}</div>
          {'' if not subtitle else f'<div style="color:{MUTED}; font-size:11px; margin-top:6px;">{subtitle}</div>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    }

    def row_style(row):
        out = []
        perf_cols = ["1D %", "5D %", "1M %", "3M %", "YTD %", "Ann. Ret %"]
        for col in row.index:
            if col in perf_cols:
                v = row[col]
                if pd.isna(v):
                    out.append("")
                else:
                    out.append(f"color: {GREEN if v >= 0 else RED}")
            else:
                out.append("")
        return out

    return df.style.format(fmt, na_rep="—").apply(row_style, axis=1)


def calc_snapshot(prices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in prices.columns:
        s = prices[col].dropna()
        if len(s) < 3:
            continue
        rets = s.pct_change().dropna()
        last = float(s.iloc[-1])

        def perf(n: int):
            if len(s) > n:
                return (float(s.iloc[-1] / s.iloc[-1 - n]) - 1.0) * 100
            return np.nan

        year_start = s[s.index.year == s.index[-1].year]
        ytd = ((float(s.iloc[-1] / year_start.iloc[0]) - 1.0) * 100) if len(year_start) > 1 else np.nan

        rows.append(
            {
                "Asset": col,
                "Last": last,
                "1D %": perf(1),
                "5D %": perf(5),
                "1M %": perf(21),
                "3M %": perf(63),
                "YTD %": ytd,
                "20D Vol %": annualized_vol(rets.tail(20)) * 100 if len(rets) >= 20 else np.nan,
                "Ann. Ret %": annualized_return(rets) * 100 if len(rets) > 10 else np.nan,
            }
        )
    return pd.DataFrame(rows)


def compute_regime(prices: pd.DataFrame) -> tuple[str, str]:
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
    vix = float(prices["VIX"].dropna().iloc[-1]) if "VIX" in prices.columns and not prices["VIX"].dropna().empty else np.nan

    if not np.isfinite(latest_20) or not np.isfinite(latest_60):
        return "Unavailable", MUTED
    if latest_spx > latest_20 > latest_60:
        if np.isfinite(vix) and vix >= 25:
            return "Bull / High Vol", YELLOW
        return "Bull Market", GREEN
    if latest_spx < latest_20 < latest_60:
        return "Bear Market", RED
    return "Transition / Choppy", ORANGE


def create_fx_heatmap(snapshot: pd.DataFrame):
    fx = snapshot[snapshot["Asset"].isin([x for x in FX_LABELS if x in snapshot["Asset"].values])].copy()
    if fx.empty:
        st.info("No FX data available.")
        return
    heat_cols = ["1D %", "5D %", "1M %", "3M %"]
    heat = fx.set_index("Asset")[heat_cols].dropna(how="all")
    vals = heat.values.astype(float)
    vmax = np.nanpercentile(np.abs(vals[np.isfinite(vals)]), 90) if np.isfinite(vals).any() else 1
    vmax = max(vmax, 0.20)
    cmap = mcolors.LinearSegmentedColormap.from_list("fx_heat", [RED, "#111827", GREEN])

    fig, ax = plt.subplots(figsize=(8, max(3.5, len(heat) * 0.45)))
    im = ax.imshow(vals, cmap=cmap, vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(heat_cols)))
    ax.set_xticklabels(heat_cols, fontsize=9)
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index, fontsize=9)
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            if np.isfinite(vals[i, j]):
                ax.text(j, i, f"{vals[i, j]:.2f}", ha="center", va="center", fontsize=8, color="white")
    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def create_inflation_proxy_chart(prices: pd.DataFrame):
    req = [x for x in ["Gold", "WTI", "Copper", "Corn", "TIP"] if x in prices.columns]
    if len(req) < 3:
        st.info("Need Gold, WTI, Copper/Corn and TIP to build the inflation proxy.")
        return

    base = pd.DataFrame(index=prices.index)
    for col in req:
        base[col] = prices[col]
    base = base.dropna(how="all").ffill().dropna()
    if base.empty:
        st.info("Inflation proxy data unavailable.")
        return

    norm = base / base.iloc[0] * 100
    proxy = norm.mean(axis=1)

    fig, ax = plt.subplots(figsize=(10, 4))
    for i, col in enumerate(norm.columns):
        ax.plot(norm.index, norm[col], lw=1.3, alpha=0.65, color=PALETTE[i % len(PALETTE)], label=col)
    ax.plot(proxy.index, proxy.values, lw=2.6, color="white", label="Inflation Proxy Basket")
    ax.axhline(100, color=MUTED, lw=0.8, ls="--")
    ax.set_title("Inflation Proxy Basket (Indexed to 100)")
    ax.grid(True, alpha=0.22)
    ax.legend(fontsize=8, ncols=3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def create_backtest(prices: pd.DataFrame, basket: list[str], benchmark: str):
    valid_assets = [x for x in basket if x in prices.columns]
    if len(valid_assets) < 1:
        st.info("Choose at least one valid asset for the backtest.")
        return

    panel = prices[valid_assets].dropna(how="all").ffill().dropna()
    if panel.empty or len(panel) < 10:
        st.info("Not enough data for the backtest.")
        return

    returns = panel.pct_change().dropna()
    if returns.empty:
        st.info("Not enough return history for the backtest.")
        return

    weights = np.repeat(1 / len(valid_assets), len(valid_assets))
    port_ret = returns.dot(weights)
    port_curve = (1 + port_ret).cumprod()

    bench_curve = None
    if benchmark in prices.columns:
        bench = prices[benchmark].reindex(panel.index).ffill().dropna()
        if len(bench) > 1:
            bench_curve = bench / bench.iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    total_return = (port_curve.iloc[-1] - 1) * 100
    ann_ret = annualized_return(port_ret) * 100
    ann_vol = annualized_vol(port_ret) * 100
    drawdown = port_curve / port_curve.cummax() - 1
    max_dd = drawdown.min() * 100
    c1.metric("Backtest Return", f"{total_return:.2f}%")
    c2.metric("Backtest Ann. Return", f"{ann_ret:.2f}%")
    c3.metric("Backtest Ann. Vol", f"{ann_vol:.2f}%")
    c4.metric("Backtest Max DD", f"{max_dd:.2f}%")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(port_curve.index, port_curve.values, lw=2.2, color=ACCENT, label="Equal-Weight Basket")
    if bench_curve is not None and not bench_curve.empty:
        aligned_bench = bench_curve.reindex(port_curve.index).dropna()
        if not aligned_bench.empty:
            ax.plot(aligned_bench.index, aligned_bench.values, lw=1.8, ls="--", color=ACCENT2, label=benchmark)
    ax.set_title("Macro Basket Backtest")
    ax.grid(True, alpha=0.22)
    ax.legend(fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    contrib = ((panel.iloc[-1] / panel.iloc[0]) - 1).sort_values()
    fig2, ax2 = plt.subplots(figsize=(8, max(3.5, len(contrib) * 0.42)))
    colors = [GREEN if v >= 0 else RED for v in contrib.values]
    ax2.barh(contrib.index, contrib.values * 100, color=colors, edgecolor="#0a0e1a")
    ax2.axvline(0, color="white", lw=0.8, ls="--")
    ax2.set_title("Asset Total Returns in Basket")
    ax2.grid(True, alpha=0.22, axis="x")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)


active_labels = GROUPS[focus_group].copy()
if custom_input.strip():
    for sym in [x.strip().upper() for x in custom_input.split(",") if x.strip()]:
        if sym not in UNIVERSE:
            UNIVERSE[sym] = sym
        if sym not in active_labels:
            active_labels.append(sym)

base_required = [
    "S&P 500", "Nasdaq 100", "VIX", "US 3M", "US 5Y", "US 10Y", "US 30Y",
    "DXY", "EUR/USD", "Gold", "WTI", "TLT", "HYG", "LQD", "TIP", "Bitcoin"
]
labels_to_load = list(dict.fromkeys(active_labels + base_required + backtest_assets + [benchmark_label]))

with st.spinner("Loading cross-asset market data…"):
    prices = load_macro_prices(labels_to_load, period=period)

if prices.empty:
    st.error("No macro data could be loaded.")
    st.stop()

snap = calc_snapshot(prices)
if snap.empty:
    st.error("Snapshot could not be built from the loaded data.")
    st.stop()

up_today = int((snap["1D %"] > 0).sum())
down_today = int((snap["1D %"] < 0).sum())
avg_vol = snap["20D Vol %"].mean()
regime_label, regime_color = compute_regime(prices)

curve_spread = np.nan
if {"US 10Y", "US 3M"}.issubset(snap["Asset"].values):
    y10 = float(snap.loc[snap["Asset"] == "US 10Y", "Last"].iloc[0])
    y3m = float(snap.loc[snap["Asset"] == "US 3M", "Last"].iloc[0])
    curve_spread = y10 - y3m

headline = [x for x in ["S&P 500", "Nasdaq 100", "VIX", "US 10Y", "DXY", "Gold", "WTI", "Bitcoin"] if x in snap["Asset"].values]
blocks = st.columns(min(5, len(headline))) if headline else []
for i, lbl in enumerate(headline[:5]):
    row = snap.loc[snap["Asset"] == lbl].iloc[0]
    delta = row["1D %"]
    color = GREEN if pd.notna(delta) and delta >= 0 else RED
    metric_block(lbl, f"{row['Last']:,.2f}" if abs(row["Last"]) < 1000 else f"{row['Last']:,.0f}", f"{delta:+.2f}%" if pd.notna(delta) else "—", color)

st.markdown("")
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    metric_block("Assets Loaded", f"{len(snap)}")
with k2:
    metric_block("Up Today", f"{up_today}", f"Down: {down_today}", GREEN if up_today >= down_today else RED)
with k3:
    metric_block("Avg 20D Vol", f"{avg_vol:.1f}%")
with k4:
    spread_delta = "Inverted" if np.isfinite(curve_spread) and curve_spread < 0 else "Normal"
    metric_block("10Y - 3M", f"{curve_spread:.2f}" if np.isfinite(curve_spread) else "—", spread_delta, RED if spread_delta == "Inverted" else GREEN)
with k5:
    metric_block("Market Regime", regime_label, None, regime_color)


tabs = st.tabs([
    "Overview",
    "FX & Commodities",
    "Equities & Crypto",
    "Rates & Bonds",
    "Correlation",
    "Backtest",
    "Regime",
])

with tabs[0]:
    left, right = st.columns([1.35, 1], gap="large")
    with left:
        section_box("Cross-Asset Monitor", "Sortable snapshot across the loaded macro universe")
        sort_by = st.selectbox("Sort by", ["1D %", "1M %", "3M %", "YTD %", "20D Vol %", "Ann. Ret %", "Asset"], key="macro_sort")
        ascending = st.checkbox("Ascending sort", value=False, key="macro_asc")
        disp = snap.sort_values(sort_by, ascending=ascending).reset_index(drop=True)
        cols = ["Asset", "Last", "1D %", "5D %", "1M %", "3M %", "YTD %", "20D Vol %", "Ann. Ret %"]
        st.dataframe(style_perf_table(disp[cols]), use_container_width=True, height=520)

    with right:
        section_box("1M Momentum Ranking", "Relative strength across loaded assets")
        rank = snap.dropna(subset=["1M %"]).sort_values("1M %")
        fig, ax = plt.subplots(figsize=(8, max(4, len(rank) * 0.28)))
        colors = [GREEN if v >= 0 else RED for v in rank["1M %"]]
        ax.barh(rank["Asset"], rank["1M %"], color=colors, edgecolor="#0a0e1a", height=0.7)
        ax.axvline(0, color="white", lw=0.8, ls="--")
        ax.set_title("1-Month Return (%)")
        ax.grid(True, alpha=0.2, axis="x")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        section_box("Performance Heatmap", "Quick heatmap across core horizons")
        heat_cols = ["1D %", "5D %", "1M %", "3M %", "YTD %"]
        heat = snap.set_index("Asset")[heat_cols].dropna(how="all")
        vals = heat.values.astype(float)
        vmax = np.nanpercentile(np.abs(vals[np.isfinite(vals)]), 95) if np.isfinite(vals).any() else 1
        vmax = max(vmax, 0.25)
        cmap = mcolors.LinearSegmentedColormap.from_list("perf_heat", [RED, "#111827", GREEN])
        fig2, ax2 = plt.subplots(figsize=(8, max(4, len(heat) * 0.28)))
        im = ax2.imshow(vals, aspect="auto", cmap=cmap, vmin=-vmax, vmax=vmax)
        ax2.set_xticks(range(len(heat_cols)))
        ax2.set_xticklabels(heat_cols, fontsize=9)
        ax2.set_yticks(range(len(heat.index)))
        ax2.set_yticklabels(heat.index, fontsize=8)
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
        section_box("FX Dashboard", "Majors performance and relative FX heatmap")
        fx_snap = snap[snap["Asset"].isin([x for x in FX_LABELS if x in snap["Asset"].values])].copy()
        st.dataframe(style_perf_table(fx_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]), use_container_width=True, height=280)
        create_fx_heatmap(snap)

    with c2:
        section_box("Commodities + Inflation Proxy", "Energy, metals and inflation-sensitive basket")
        comm_snap = snap[snap["Asset"].isin([x for x in COMMODITY_LABELS if x in snap["Asset"].values])].copy()
        st.dataframe(style_perf_table(comm_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]), use_container_width=True, height=280)
        create_inflation_proxy_chart(prices)

with tabs[2]:
    left, right = st.columns(2, gap="large")
    with left:
        section_box("Global Equities", "US and international equity index performance")
        eq_snap = snap[snap["Asset"].isin([x for x in EQUITY_LABELS if x in snap["Asset"].values])].copy()
        st.dataframe(style_perf_table(eq_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]), use_container_width=True, height=300)
        eq_prices = prices[[x for x in EQUITY_LABELS if x in prices.columns]]
        if not eq_prices.empty:
            sel = st.multiselect("Equity indices to chart", eq_prices.columns.tolist(), default=eq_prices.columns.tolist()[:5], key="macro_eq_sel")
            if sel:
                norm = eq_prices[sel] / eq_prices[sel].iloc[0] * 100
                fig, ax = plt.subplots(figsize=(10, 4))
                for i, col in enumerate(norm.columns):
                    ax.plot(norm.index, norm[col], lw=1.8, label=col, color=PALETTE[i % len(PALETTE)])
                ax.axhline(100, color="white", lw=0.8, ls="--")
                ax.set_title("Equity Indices Indexed to 100")
                ax.grid(True, alpha=0.22)
                ax.legend(fontsize=8, ncols=3)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

    with right:
        section_box("Crypto Monitor", "Crypto prices and rolling volatility")
        crypto_snap = snap[snap["Asset"].isin([x for x in CRYPTO_LABELS if x in snap["Asset"].values])].copy()
        st.dataframe(style_perf_table(crypto_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]), use_container_width=True, height=300)
        crypto_prices = prices[[x for x in CRYPTO_LABELS if x in prices.columns]]
        if not crypto_prices.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            for i, col in enumerate(crypto_prices.columns):
                rv = rolling_vol(crypto_prices[col].pct_change().dropna(), window=roll_window) * 100
                ax2.plot(rv.index, rv.values, lw=1.8, label=col, color=PALETTE[i % len(PALETTE)])
            ax2.set_title(f"Rolling {roll_window}D Annualised Volatility (%)")
            ax2.grid(True, alpha=0.22)
            ax2.legend(fontsize=8)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

with tabs[3]:
    left, right = st.columns(2, gap="large")
    with left:
        section_box("Rates Panel", "Treasury trend panel and current yield curve")
        rate_snap = snap[snap["Asset"].isin([x for x in RATE_ORDER if x in snap["Asset"].values])].copy()
        st.dataframe(style_perf_table(rate_snap[["Asset", "Last", "1D %", "1M %", "3M %"]]), use_container_width=True, height=210)
        available = [x for x in RATE_ORDER if x in prices.columns]
        if available:
            fig, ax = plt.subplots(figsize=(10, 4))
            for i, col in enumerate(available):
                ax.plot(prices[col].dropna().index, prices[col].dropna().values, lw=1.7, label=col, color=PALETTE[i % len(PALETTE)])
            ax.set_title("Rates Trend Panel")
            ax.grid(True, alpha=0.22)
            ax.legend(fontsize=8, ncols=2)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            xs = [RATE_MATURITY[x] for x in available]
            ys = [float(prices[x].dropna().iloc[-1]) for x in available]
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(xs, ys, marker="o", lw=2.2, color=ACCENT)
            ax2.set_xticks(xs)
            ax2.set_xticklabels(available)
            ax2.set_title("Current Yield Curve")
            ax2.grid(True, alpha=0.22)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

    with right:
        section_box("Bonds & Credit", "Duration, credit and inflation-linked proxies")
        bond_snap = snap[snap["Asset"].isin([x for x in BOND_LABELS if x in snap["Asset"].values])].copy()
        st.dataframe(style_perf_table(bond_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]), use_container_width=True, height=210)
        if {"HYG", "LQD"}.issubset(prices.columns):
            ratio = (prices["HYG"] / prices["LQD"]).dropna()
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            ax3.plot(ratio.index, ratio.values, lw=2.0, color=ACCENT2)
            ax3.axhline(ratio.mean(), color="white", lw=0.8, ls="--")
            ax3.set_title("HYG / LQD Credit Risk Proxy")
            ax3.grid(True, alpha=0.22)
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

        if {"TLT", "TIP"}.issubset(prices.columns):
            spread = ((prices["TIP"] / prices["TIP"].iloc[0]) - (prices["TLT"] / prices["TLT"].iloc[0])) * 100
            fig4, ax4 = plt.subplots(figsize=(10, 4))
            ax4.plot(spread.index, spread.values, lw=2.0, color=YELLOW)
            ax4.axhline(0, color="white", lw=0.8, ls="--")
            ax4.set_title("TIP Relative Performance vs TLT (Inflation vs Duration)")
            ax4.grid(True, alpha=0.22)
            plt.tight_layout()
            st.pyplot(fig4)
            plt.close(fig4)

with tabs[4]:
    section_box("Correlation Matrix", "Daily return correlation across selected assets")
    corr_assets = st.multiselect(
        "Assets for correlation",
        prices.columns.tolist(),
        default=prices.columns.tolist()[: min(14, len(prices.columns))],
        key="macro_corr_assets",
    )
    if len(corr_assets) >= 2:
        rets = prices[corr_assets].pct_change().dropna(how="all")
        corr = correlation_matrix(rets)
        fig, ax = plt.subplots(figsize=(max(7, len(corr_assets) * 0.7), max(5, len(corr_assets) * 0.55)))
        cmap = mcolors.LinearSegmentedColormap.from_list("corr", [RED, "#111827", ACCENT])
        im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(len(corr.index)))
        ax.set_yticklabels(corr.index, fontsize=8)
        for i in range(len(corr.index)):
            for j in range(len(corr.columns)):
                ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=7, color="white")
        plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Select at least two assets.")

with tabs[5]:
    section_box("Macro Basket Backtest", "Simple equal-weight backtest across selected assets")
    create_backtest(prices, backtest_assets, benchmark_label)

with tabs[6]:
    left, right = st.columns(2, gap="large")
    with left:
        section_box("Market Regime", "Trend + volatility overlay using S&P 500 and VIX")
        st.markdown(
            f"""
            <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%); border:1px solid {regime_color};
                        border-radius:12px; padding:18px; margin-bottom:12px;">
              <div style="color:{MUTED}; font-size:10px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">Current Regime</div>
              <div style="color:{regime_color}; font-size:28px; font-weight:900; margin-top:8px;">{regime_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if "S&P 500" in prices.columns:
            spx = prices["S&P 500"].dropna()
            sma20 = spx.rolling(20).mean()
            sma60 = spx.rolling(60).mean()
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(spx.index, spx.values, lw=1.9, color=ACCENT, label="S&P 500")
            ax.plot(sma20.index, sma20.values, lw=1.2, ls="--", color=YELLOW, label="SMA 20")
            ax.plot(sma60.index, sma60.values, lw=1.2, ls="--", color=RED, label="SMA 60")
            ax.set_title("S&P 500 Trend Structure")
            ax.grid(True, alpha=0.22)
            ax.legend(fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with right:
        section_box("Cross-Asset Leadership", "Relative leadership among key macro assets")
        leaders = snap[snap["Asset"].isin([x for x in ["S&P 500", "Gold", "TLT", "DXY", "Bitcoin", "WTI"] if x in snap["Asset"].values])]
        if not leaders.empty:
            leaders = leaders[["Asset", "1M %", "3M %", "20D Vol %"]].set_index("Asset")
            st.dataframe(leaders.style.format({"1M %": "{:.2f}%", "3M %": "{:.2f}%", "20D Vol %": "{:.2f}%"}), use_container_width=True, height=250)
        if {"US 10Y", "US 3M"}.issubset(prices.columns):
            spread = (prices["US 10Y"] - prices["US 3M"]).dropna()
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(spread.index, spread.values, color=ACCENT2, lw=2.0)
            ax2.axhline(0, color="white", lw=0.8, ls="--")
            ax2.set_title("10Y - 3M Curve Spread Through Time")
            ax2.grid(True, alpha=0.22)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

st.markdown("---")
st.markdown(
    f"""
    <div style="color:{MUTED}; font-size:11px; text-align:center; letter-spacing:0.10em; text-transform:uppercase;">
      QuantDesk Pro | Macro Dashboard Pro | Data via yfinance + Alpha Vantage fallback | Educational use only
    </div>
    """,
    unsafe_allow_html=True,
)


