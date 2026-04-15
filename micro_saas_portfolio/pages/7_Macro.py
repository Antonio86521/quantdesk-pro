from auth import require_login, sidebar_user_widget
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from utils import apply_theme, page_header, ACCENT, ACCENT2, GREEN, RED, YELLOW, PALETTE
from data_loader import load_macro_dataset, load_macro_snapshot
from analytics import annualized_vol, correlation_matrix


st.set_page_config(page_title="Macro Dashboard", layout="wide", page_icon="🌍")
apply_theme()
page_header("Macro Dashboard", "Rates · FX · Commodities · Indices · Cross-Asset Regimes")

require_login()
sidebar_user_widget()

# ── Universe ────────────────────────────────────────────────────────────────
MACRO_UNIVERSE = {
    "US 2Y Yield": "^IRX",
    "US 10Y Yield": "^TNX",
    "US 30Y Yield": "^TYX",
    "Dollar Index": "DX-Y.NYB",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "USD/CHF": "CHF=X",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "WTI Crude": "CL=F",
    "Brent Crude": "BZ=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F",
    "Corn": "ZC=F",
    "Wheat": "ZW=F",
    "S&P 500": "^GSPC",
    "Nasdaq 100": "^NDX",
    "Russell 2000": "^RUT",
    "Euro Stoxx 50": "^STOXX50E",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "US Aggregate Bonds": "AGG",
    "US High Yield": "HYG",
    "TLT (20Y+)": "TLT",
    "LQD IG Credit": "LQD",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
}

GROUPS = {
    "Rates": ["US 2Y Yield", "US 10Y Yield", "US 30Y Yield"],
    "FX": ["Dollar Index", "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF"],
    "Commodities": ["Gold", "Silver", "WTI Crude", "Brent Crude", "Natural Gas", "Copper", "Corn", "Wheat"],
    "Equities": ["S&P 500", "Nasdaq 100", "Russell 2000", "Euro Stoxx 50", "Nikkei 225", "Hang Seng"],
    "Bonds & Credit": ["US Aggregate Bonds", "US High Yield", "TLT (20Y+)", "LQD IG Credit"],
    "Crypto": ["Bitcoin", "Ethereum"],
}

# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Macro Inputs")
period = st.sidebar.selectbox("Lookback period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
focus_group = st.sidebar.selectbox("Focus group", ["All"] + list(GROUPS.keys()))
run_macro = st.sidebar.button("Load Macro Dashboard", use_container_width=True)

if not run_macro:
    st.info("Choose the lookback period and click **Load Macro Dashboard**.")
    st.stop()

if focus_group == "All":
    active_labels = list(MACRO_UNIVERSE.keys())
else:
    active_labels = GROUPS[focus_group]

active_universe = {label: MACRO_UNIVERSE[label] for label in active_labels}

with st.spinner("Loading macro data…"):
    prices = load_macro_dataset(active_universe, period=period)
    snap = load_macro_snapshot(active_universe, period=period)

if prices.empty or snap.empty:
    st.error("Could not load macro data. Some Yahoo Finance symbols may be temporarily unavailable.")
    st.stop()

snap = snap.copy()
snap["Direction"] = np.where(snap["1D %"] >= 0, "Risk-On", "Risk-Off")

# ── Headline cards ──────────────────────────────────────────────────────────
st.markdown("### Cross-Asset Snapshot")
up_count = int((snap["1D %"] > 0).sum())
down_count = int((snap["1D %"] < 0).sum())
strongest = snap.sort_values("1D %", ascending=False).iloc[0]
weakest = snap.sort_values("1D %", ascending=True).iloc[0]
avg_vol = snap["20D Vol %"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Assets Loaded", f"{len(snap)}")
c2.metric("Up Today", f"{up_count}", delta=f"{up_count - down_count}")
c3.metric("Avg 20D Vol", f"{avg_vol:.1f}%" if pd.notna(avg_vol) else "N/A")
c4.metric("Best 1D Move", f"{strongest['Asset']}", delta=f"{strongest['1D %']:.2f}%")
c5.metric("Worst 1D Move", f"{weakest['Asset']}", delta=f"{weakest['1D %']:.2f}%")

# ── Table ───────────────────────────────────────────────────────────────────
st.markdown("### Macro Monitor")

def highlight_macro(row):
    styles = []
    for col in row.index:
        if col in ["1D %", "5D %", "1M %", "3M %"]:
            val = row[col]
            if pd.isna(val):
                styles.append("")
            else:
                styles.append(f"color: {'#00e676' if val >= 0 else '#ff1744'}")
        else:
            styles.append("")
    return styles

fmt = {
    "Last": "{:.2f}",
    "1D %": "{:.2f}%",
    "5D %": "{:.2f}%",
    "1M %": "{:.2f}%",
    "3M %": "{:.2f}%",
    "20D Vol %": "{:.2f}%",
}

st.dataframe(
    snap.sort_values(["1D %", "3M %"], ascending=[False, False]).style.format(fmt).apply(highlight_macro, axis=1),
    use_container_width=True,
    height=460,
)

# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Relative Performance", "Heatmap", "Correlation", "Rates & FX"])

with tab1:
    st.markdown("#### Growth of 100")
    norm = prices / prices.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, col in enumerate(norm.columns):
        ax.plot(norm.index, norm[col], label=col, lw=1.7, color=PALETTE[i % len(PALETTE)], alpha=0.95)
    ax.set_ylabel("Indexed to 100")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, ncols=2)
    st.pyplot(fig)
    plt.close()

    st.markdown("#### 1M Momentum Ranking")
    rank_df = snap.sort_values("1M %", ascending=False)[["Asset", "1M %", "3M %", "20D Vol %"]].reset_index(drop=True)
    fig_rank, ax_rank = plt.subplots(figsize=(10, max(4, len(rank_df) * 0.35)))
    colors = [GREEN if x >= 0 else RED for x in rank_df["1M %"]]
    ax_rank.barh(rank_df["Asset"], rank_df["1M %"], color=colors, edgecolor="#0a0e1a")
    ax_rank.axvline(0, color="white", lw=0.8, ls="--")
    ax_rank.set_title("1M Cross-Asset Momentum (%)")
    ax_rank.grid(True, alpha=0.25, axis="x")
    ax_rank.invert_yaxis()
    st.pyplot(fig_rank)
    plt.close()

with tab2:
    st.markdown("#### Performance Heatmap")
    heat = snap.set_index("Asset")[["1D %", "5D %", "1M %", "3M %"]]
    fig_h, ax_h = plt.subplots(figsize=(8, max(4, len(heat) * 0.35)))
    cmap = mcolors.LinearSegmentedColormap.from_list("macro_perf", [RED, "#111827", GREEN])
    values = heat.values
    vmax = np.nanmax(np.abs(values)) if np.isfinite(values).any() else 1
    im = ax_h.imshow(values, aspect="auto", cmap=cmap, vmin=-vmax, vmax=vmax)
    ax_h.set_xticks(range(len(heat.columns)))
    ax_h.set_xticklabels(heat.columns)
    ax_h.set_yticks(range(len(heat.index)))
    ax_h.set_yticklabels(heat.index)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            if pd.notna(values[i, j]):
                ax_h.text(j, i, f"{values[i, j]:.1f}", ha="center", va="center", color="white", fontsize=8)
    plt.colorbar(im, ax=ax_h, label="Return (%)")
    st.pyplot(fig_h)
    plt.close()

with tab3:
    st.markdown("#### Correlation of Daily Returns")
    ret = prices.pct_change().dropna(how="all")
    corr = correlation_matrix(ret).fillna(0)
    fig_c, ax_c = plt.subplots(figsize=(10, 8))
    cmap_c = mcolors.LinearSegmentedColormap.from_list("corr", [RED, "#111827", ACCENT])
    im2 = ax_c.imshow(corr.values, cmap=cmap_c, vmin=-1, vmax=1)
    ax_c.set_xticks(range(len(corr.columns)))
    ax_c.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
    ax_c.set_yticks(range(len(corr.index)))
    ax_c.set_yticklabels(corr.index, fontsize=8)
    plt.colorbar(im2, ax=ax_c, label="Correlation")
    st.pyplot(fig_c)
    plt.close()

    st.markdown("#### 20D Annualised Volatility")
    vol_rows = []
    for col in prices.columns:
        ret_col = prices[col].pct_change().dropna()
        if len(ret_col) >= 20:
            vol_rows.append({"Asset": col, "Ann. Vol %": annualized_vol(ret_col.tail(20)) * 100})
    vol_df = pd.DataFrame(vol_rows).sort_values("Ann. Vol %", ascending=False)
    if not vol_df.empty:
        fig_v, ax_v = plt.subplots(figsize=(9, max(4, len(vol_df) * 0.35)))
        ax_v.barh(vol_df["Asset"], vol_df["Ann. Vol %"], color=ACCENT2, edgecolor="#0a0e1a")
        ax_v.set_title("20D Annualised Volatility (%)")
        ax_v.grid(True, alpha=0.25, axis="x")
        ax_v.invert_yaxis()
        st.pyplot(fig_v)
        plt.close()

with tab4:
    rate_labels = [x for x in active_labels if x in GROUPS["Rates"]]
    fx_labels = [x for x in active_labels if x in GROUPS["FX"]]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Rates Curve Proxies")
        if rate_labels:
            rates_df = snap[snap["Asset"].isin(rate_labels)].copy()
            fig_r, ax_r = plt.subplots(figsize=(7, 4))
            ax_r.bar(rates_df["Asset"], rates_df["Last"], color=[YELLOW, ACCENT, ACCENT2][:len(rates_df)], edgecolor="#0a0e1a")
            ax_r.set_ylabel("Yield proxy level")
            ax_r.set_title("US Yield Proxies")
            ax_r.grid(True, alpha=0.25, axis="y")
            st.pyplot(fig_r)
            plt.close()

            if len(rates_df) >= 2:
                try:
                    y2 = float(rates_df.loc[rates_df["Asset"] == "US 2Y Yield", "Last"].iloc[0])
                    y10 = float(rates_df.loc[rates_df["Asset"] == "US 10Y Yield", "Last"].iloc[0])
                    st.metric("10Y - 2Y Spread", f"{(y10 - y2):.2f}")
                except Exception:
                    pass
        else:
            st.info("Select All or the Rates group to view rates charts.")

    with col2:
        st.markdown("#### FX Dashboard")
        if fx_labels:
            fx_df = snap[snap["Asset"].isin(fx_labels)].copy().sort_values("1D %", ascending=False)
            fig_fx, ax_fx = plt.subplots(figsize=(7, 4))
            colors_fx = [GREEN if x >= 0 else RED for x in fx_df["1D %"]]
            ax_fx.bar(fx_df["Asset"], fx_df["1D %"], color=colors_fx, edgecolor="#0a0e1a")
            ax_fx.axhline(0, color="white", lw=0.8, ls="--")
            ax_fx.set_ylabel("1D Change (%)")
            ax_fx.set_title("FX Daily Moves")
            ax_fx.grid(True, alpha=0.25, axis="y")
            plt.xticks(rotation=30, ha="right")
            st.pyplot(fig_fx)
            plt.close()
        else:
            st.info("Select All or the FX group to view FX charts.")

st.markdown("---")
st.caption("Macro data uses Yahoo Finance symbols via yfinance. Some macro tickers can occasionally be delayed or unavailable depending on the instrument.")
