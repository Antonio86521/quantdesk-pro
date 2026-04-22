"""
11_Market_Overview.py — QuantDesk Pro
Live cross-asset market overview: real-time prices, heatmaps, 
sector performance, breadth indicators, yield curve snapshot.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from utils import (
    apply_theme, apply_responsive_layout, page_header, section_header,
    ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEAL, TEXT2, BG2, BG3, BG4,
    MPL_BORDER, MPL_GRID, PALETTE, app_footer, safe_pct,
)
from data_loader import load_close_series
from auth import sidebar_user_widget

st.set_page_config(page_title="Market Overview — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Market Overview", "Live cross-asset monitor · Prices · Heatmap · Breadth")
sidebar_user_widget()

# ── Universe ──────────────────────────────────────────────────────────────────
UNIVERSE = {
    "Equities": {
        "S&P 500": "SPY", "NASDAQ 100": "QQQ", "Russell 2000": "IWM",
        "Dow Jones": "DIA", "Euro Stoxx": "FEZ", "Nikkei": "EWJ",
    },
    "Rates & Bonds": {
        "US 10Y": "^TNX", "US 2Y": "^IRX", "TLT (20Y)": "TLT",
        "HYG (HY)": "HYG", "LQD (IG)": "LQD", "TIP (TIPS)": "TIP",
    },
    "FX": {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X", "DXY": "DX-Y.NYB",
        "AUD/USD": "AUDUSD=X", "USD/CHF": "CHF=X",
    },
    "Commodities": {
        "Gold": "GC=F", "Silver": "SI=F", "WTI Crude": "CL=F",
        "Brent": "BZ=F", "Copper": "HG=F", "Nat Gas": "NG=F",
    },
    "Crypto": {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD",
    },
    "Volatility": {
        "VIX": "^VIX", "VVIX": "^VVIX", "MOVE": "^MOVE",
    },
}

SECTORS = {
    "Tech (XLK)": "XLK", "Healthcare (XLV)": "XLV", "Financials (XLF)": "XLF",
    "Energy (XLE)": "XLE", "Consumer Disc (XLY)": "XLY", "Industrials (XLI)": "XLI",
    "Utilities (XLU)": "XLU", "Materials (XLB)": "XLB", "Real Estate (XLRE)": "XLRE",
    "Staples (XLP)": "XLP", "Comm Svcs (XLC)": "XLC",
}

st.sidebar.markdown("## Settings")
period = st.sidebar.selectbox("Lookback", ["1mo", "3mo", "6mo", "1y"], index=1)
load_btn = st.sidebar.button("🔄 Refresh Data", use_container_width=True)


@st.cache_data(ttl=300)
def load_universe(period: str):
    rows = []
    for group, assets in UNIVERSE.items():
        for name, ticker in assets.items():
            try:
                s = load_close_series(ticker, period=period, source="auto")
                if s is None or len(s) < 2:
                    continue
                s = s.dropna()
                last = float(s.iloc[-1])
                prev = float(s.iloc[-2])
                chg1d = (last / prev - 1) * 100
                chg1m = (last / float(s.iloc[max(0, len(s)-22)]) - 1) * 100 if len(s) >= 22 else np.nan
                chg3m = (last / float(s.iloc[max(0, len(s)-63)]) - 1) * 100 if len(s) >= 63 else np.nan
                vol20 = float(s.pct_change().dropna().tail(20).std() * np.sqrt(252) * 100) if len(s) >= 22 else np.nan
                rows.append({
                    "Group": group, "Asset": name, "Ticker": ticker,
                    "Last": last, "1D %": chg1d, "1M %": chg1m,
                    "3M %": chg3m, "20D Vol %": vol20,
                })
            except Exception:
                continue
    return pd.DataFrame(rows) if rows else pd.DataFrame()


@st.cache_data(ttl=300)
def load_sectors(period: str):
    rows = []
    for name, ticker in SECTORS.items():
        try:
            s = load_close_series(ticker, period=period, source="auto")
            if s is None or len(s) < 2:
                continue
            s = s.dropna()
            last, prev = float(s.iloc[-1]), float(s.iloc[-2])
            chg1d = (last / prev - 1) * 100
            chg1m = (last / float(s.iloc[max(0, len(s)-22)]) - 1) * 100 if len(s) >= 22 else np.nan
            chg3m = (last / float(s.iloc[max(0, len(s)-63)]) - 1) * 100 if len(s) >= 63 else np.nan
            rows.append({"Sector": name, "1D %": chg1d, "1M %": chg1m, "3M %": chg3m})
        except Exception:
            continue
    return pd.DataFrame(rows) if rows else pd.DataFrame()


with st.spinner("Loading market data…"):
    df = load_universe(period)
    sec_df = load_sectors(period)

if df.empty:
    st.error("Could not load market data. Check your connection.")
    st.stop()

# ── HEADLINE CARDS ─────────────────────────────────────────────────────────────
section_header("Key Market Levels")

key_assets = ["S&P 500", "NASDAQ 100", "US 10Y", "VIX", "Gold", "Bitcoin", "DXY", "EUR/USD"]
key_rows = df[df["Asset"].isin(key_assets)].set_index("Asset")

cols = st.columns(min(8, len(key_rows)))
for i, asset in enumerate(key_assets):
    if asset not in key_rows.index or i >= len(cols):
        continue
    row = key_rows.loc[asset]
    chg = row["1D %"]
    pos = chg >= 0
    clr = GREEN if pos else RED
    sign = "+" if pos else ""

    last_val = row["Last"]
    if last_val >= 10000:
        last_fmt = f"{last_val:,.0f}"
    elif last_val >= 100:
        last_fmt = f"{last_val:,.2f}"
    else:
        last_fmt = f"{last_val:.4f}" if last_val < 10 else f"{last_val:.2f}"

    cols[i].markdown(
        f"""
        <div style="background:{BG3};border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px;padding:14px 16px;">
          <div style="font-size:9.5px;color:#7a8fa8;text-transform:uppercase;
                      letter-spacing:0.5px;margin-bottom:6px;">{asset}</div>
          <div style="font-family:'DM Mono',monospace;font-size:18px;font-weight:500;
                      color:#dde4f0;letter-spacing:-0.5px;">{last_fmt}</div>
          <div style="font-size:11px;color:{clr};margin-top:4px;">{sign}{chg:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

# ── PERFORMANCE HEATMAP ────────────────────────────────────────────────────────
section_header("Cross-Asset Performance Heatmap")

tab1, tab2, tab3 = st.tabs(["1D Return", "1M Return", "3M Return"])

def draw_heatmap(col: str, label: str):
    pivot_data = []
    for group in UNIVERSE.keys():
        group_df = df[df["Group"] == group][["Asset", col]].dropna()
        if not group_df.empty:
            pivot_data.append(group_df.set_index("Asset")[col])
    if not pivot_data:
        st.info("No data available.")
        return

    # Build a flat bar-style heatmap
    all_assets = df[["Group", "Asset", col]].dropna()
    n = len(all_assets)
    if n == 0:
        return

    vals = all_assets[col].values
    vmax = max(np.nanpercentile(np.abs(vals), 90), 0.5)

    cmap = mcolors.LinearSegmentedColormap.from_list("perf", [RED, "#131920", GREEN])

    fig, axes = plt.subplots(1, len(UNIVERSE), figsize=(16, 3.5),
                             gridspec_kw={"wspace": 0.05})
    if len(UNIVERSE) == 1:
        axes = [axes]

    for ax, (group_name, _) in zip(axes, UNIVERSE.items()):
        group_df = df[df["Group"] == group_name][["Asset", col]].dropna()
        if group_df.empty:
            ax.set_visible(False)
            continue

        group_vals = group_df[col].values
        n_g = len(group_vals)
        colors = [cmap((v + vmax) / (2 * vmax)) for v in group_vals]

        ax.barh(range(n_g), group_vals, color=colors, edgecolor="#0d1117", height=0.8)
        ax.set_yticks(range(n_g))
        ax.set_yticklabels(group_df["Asset"].values, fontsize=8)
        ax.set_title(group_name, fontsize=9, pad=6)
        ax.axvline(0, color="#3d5068", lw=0.8, ls="--")
        ax.grid(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        # Annotate bars
        for j, (v, name) in enumerate(zip(group_vals, group_df["Asset"].values)):
            ax.text(v + (0.05 if v >= 0 else -0.05), j,
                    f"{v:+.1f}%", va="center",
                    ha="left" if v >= 0 else "right",
                    fontsize=7, color="#dde4f0")

    fig.patch.set_facecolor("#080b10")
    st.pyplot(fig, use_container_width=True)
    plt.close()

with tab1:
    draw_heatmap("1D %", "1-Day")
with tab2:
    draw_heatmap("1M %", "1-Month")
with tab3:
    draw_heatmap("3M %", "3-Month")

st.divider()

# ── SECTOR ROTATION ───────────────────────────────────────────────────────────
left_col, right_col = st.columns([1.4, 1])

with left_col:
    section_header("Sector Performance (S&P 500)")
    if not sec_df.empty:
        sec_sorted = sec_df.sort_values("1M %", ascending=True)
        fig, ax = plt.subplots(figsize=(8, 5.5))
        colors = [GREEN if v >= 0 else RED for v in sec_sorted["1M %"]]
        bars = ax.barh(sec_sorted["Sector"], sec_sorted["1M %"],
                       color=colors, edgecolor="#0d1117", height=0.7)
        ax.axvline(0, color="#3d5068", lw=0.8, ls="--")
        ax.set_xlabel("1-Month Return (%)")
        ax.set_title("Sector 1M Returns", pad=8)
        for bar, val in zip(bars, sec_sorted["1M %"]):
            ax.text(val + (0.1 if val >= 0 else -0.1), bar.get_y() + bar.get_height() / 2,
                    f"{val:+.1f}%", va="center",
                    ha="left" if val >= 0 else "right",
                    fontsize=8, color="#dde4f0")
        ax.grid(True, alpha=0.2, axis="x")
        st.pyplot(fig, use_container_width=True)
        plt.close()
    else:
        st.info("Sector data unavailable.")

with right_col:
    section_header("Full Asset Table")
    show_group = st.selectbox("Filter group", ["All"] + list(UNIVERSE.keys()))
    disp = df if show_group == "All" else df[df["Group"] == show_group]
    disp = disp[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]].copy()

    def colour_row(row):
        styles = []
        for col in row.index:
            if col in ["1D %", "1M %", "3M %"] and pd.notna(row[col]):
                styles.append(f"color: {'#0ecb81' if row[col] >= 0 else '#f6465d'}")
            else:
                styles.append("")
        return styles

    st.dataframe(
        disp.style
        .format({"Last": "{:,.3f}", "1D %": "{:+.2f}%", "1M %": "{:+.2f}%",
                 "3M %": "{:+.2f}%", "20D Vol %": "{:.1f}%"}, na_rep="—")
        .apply(colour_row, axis=1),
        use_container_width=True, height=500, hide_index=True,
    )

st.divider()

# ── YIELD CURVE SNAPSHOT ──────────────────────────────────────────────────────
section_header("Yield Curve Snapshot")

yield_tickers = {
    "3M": "^IRX", "2Y": "^IRX", "5Y": "^FVX",
    "10Y": "^TNX", "30Y": "^TYX",
}
yield_maturities = {"3M": 0.25, "2Y": 2, "5Y": 5, "10Y": 10, "30Y": 30}

yield_data = {}
for label, ticker in {"3M": "^IRX", "5Y": "^FVX", "10Y": "^TNX", "30Y": "^TYX"}.items():
    try:
        s = load_close_series(ticker, period="5d", source="auto")
        if s is not None and not s.empty:
            yield_data[label] = float(s.iloc[-1])
    except Exception:
        pass

if len(yield_data) >= 2:
    mats = [yield_maturities[k] for k in yield_data]
    ylds = list(yield_data.values())

    yc1, yc2, yc3 = st.columns(3)
    with yc1:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(mats, ylds, color=ACCENT, marker="o", lw=2, markersize=6)
        ax.fill_between(mats, ylds, alpha=0.1, color=ACCENT)
        for m, y in zip(mats, ylds):
            ax.annotate(f"{y:.2f}%", (m, y), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=8, color="#dde4f0")
        ax.set_xlabel("Maturity (Years)")
        ax.set_ylabel("Yield (%)")
        ax.set_title("US Treasury Yield Curve")
        ax.grid(True, alpha=0.2)
        st.pyplot(fig, use_container_width=True)
        plt.close()
    with yc2:
        spread_10_3m = yield_data.get("10Y", 0) - yield_data.get("3M", 0)
        spread_10_2y = yield_data.get("10Y", 0) - yield_data.get("3M", 0)
        pos = spread_10_3m >= 0
        st.metric("10Y − 3M Spread", f"{spread_10_3m:.2f} pts",
                  delta="Normal" if pos else "Inverted ⚠")
        st.metric("10Y Yield", f"{yield_data.get('10Y', 0):.2f}%")
        st.metric("30Y Yield", f"{yield_data.get('30Y', 0):.2f}%")
    with yc3:
        for label, val in yield_data.items():
            st.metric(f"{label} Yield", f"{val:.2f}%")
else:
    st.info("Yield curve data requires market hours data. Try refreshing.")

app_footer()
