import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from auth import require_login, sidebar_user_widget
from utils import (
    apply_theme,
    page_header,
    ACCENT,
    ACCENT2,
    GREEN,
    RED,
    YELLOW,
    ORANGE,
    PALETTE,
    MUTED,
    BORDER,
    TEXT,
)
from data_loader import load_close_series
from analytics import annualized_return, annualized_vol, correlation_matrix, rolling_vol

st.set_page_config(page_title="Macro Dashboard", layout="wide", page_icon="🌍")
apply_theme()
st.markdown("""
<div style="padding: 2px 0 14px 0; border-bottom: 1px solid #1b2638; margin-bottom: 16px;">
  <div style="display:flex; align-items:center; gap:10px;">
    <span style="font-size:24px; font-weight:800; color:#d6deeb;">
      Macro Dashboard
    </span>
    <span style="
        padding:2px 7px;
        border-radius:999px;
        font-size:9px;
        font-weight:800;
        border:1px solid #1b2638;
        color:#35c2ff;">
      LIVE
    </span>
  </div>
  <div style="margin-top:6px; font-size:11px; color:#7f8ea3;">
    RATES · FX · COMMODITIES · EQUITIES · CRYPTO · REGIMES
  </div>
</div>
""", unsafe_allow_html=True)

require_login()
sidebar_user_widget()


# ══════════════════════════════════════════════════════════════════════════════
# Universe
# ══════════════════════════════════════════════════════════════════════════════

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
    "Equities": ["S&P 500", "Nasdaq 100", "Dow Jones", "Russell 2000", "Euro Stoxx 50",
                 "DAX", "FTSE 100", "Nikkei 225", "Hang Seng", "VIX"],
    "Bonds": ["TLT", "IEF", "SHY", "HYG", "LQD", "TIP"],
    "Crypto": ["Bitcoin", "Ethereum", "Solana"],
}


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════

st.sidebar.markdown("## Macro Controls")
period = st.sidebar.selectbox("Lookback period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
focus_group = st.sidebar.selectbox("Focus group", list(GROUPS.keys()), index=0)
roll_window = st.sidebar.slider("Rolling vol window", 5, 60, 20, 5)
benchmark_label = st.sidebar.selectbox(
    "Benchmark for correlation",
    ["S&P 500", "Gold", "DXY", "Bitcoin", "TLT"],
    index=0,
)
custom_input = st.sidebar.text_input("Custom Yahoo tickers", placeholder="e.g. GLD, USO, XLE")
run_page = st.sidebar.button("Load Macro Dashboard", use_container_width=True, on_click=_set_load_macro_clicked)

if not st.session_state.get("load_macro_clicked", False):
    st.markdown("""
    <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                border:1px solid #1b2638; border-radius:8px; padding:26px; text-align:center; margin-top:16px;">
      <div style="font-size:34px; margin-bottom:8px;">🌍</div>
      <div style="color:#d6deeb; font-size:17px; font-weight:800; margin-bottom:8px;">
        Global Macro Monitor
      </div>
      <div style="color:#7f8ea3; font-size:13px; line-height:1.8;">
        Cross-asset dashboard for rates, FX, commodities, equities, bonds and crypto.<br>
        Select a universe and click <strong style="color:#35c2ff;">Load Macro Dashboard</strong>.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# Data helpers
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def load_macro_prices(labels, period="1y") -> pd.DataFrame:
    df = pd.DataFrame()
    for label in labels:
        ticker = UNIVERSE.get(label, label)
        s = load_close_series(ticker, period=period)
        if not s.empty:
            df[label] = s
    return df.dropna(how="all")


def calc_snapshot(prices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in prices.columns:
        s = prices[col].dropna()
        if len(s) < 3:
            continue

        ret = s.pct_change().dropna()
        last = float(s.iloc[-1])

        def perf(n):
            if len(s) > n:
                return (float(s.iloc[-1] / s.iloc[-1 - n]) - 1.0) * 100
            return np.nan

        year_start = s[s.index.year == s.index[-1].year]
        ytd = ((float(s.iloc[-1] / year_start.iloc[0]) - 1.0) * 100) if len(year_start) > 1 else np.nan

        rows.append({
            "Asset":      col,
            "Last":       last,
            "1D %":       perf(1),
            "5D %":       perf(5),
            "1M %":       perf(21),
            "3M %":       perf(63),
            "YTD %":      ytd,
            "20D Vol %":  annualized_vol(ret.tail(20)) * 100 if len(ret) >= 20 else np.nan,
            "Ann. Ret %": annualized_return(ret) * 100 if len(ret) > 10 else np.nan,
        })

    return pd.DataFrame(rows)


def style_perf_table(df: pd.DataFrame):
    fmt = {
        "Last":       "{:,.2f}",
        "1D %":       "{:.2f}%",
        "5D %":       "{:.2f}%",
        "1M %":       "{:.2f}%",
        "3M %":       "{:.2f}%",
        "YTD %":      "{:.2f}%",
        "20D Vol %":  "{:.2f}%",
        "Ann. Ret %": "{:.2f}%",
    }

    def row_style(row):
        out = []
        for col in row.index:
            if col in ["1D %", "5D %", "1M %", "3M %", "YTD %", "Ann. Ret %"]:
                v = row[col]
                if pd.isna(v):
                    out.append("")
                else:
                    out.append(f"color: {GREEN if v >= 0 else RED}")
            else:
                out.append("")
        return out

    return df.style.format(fmt, na_rep="—").apply(row_style, axis=1)


def section_box(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                border:1px solid #1b2638; border-radius:8px; padding:12px 14px; margin-bottom:12px;">
      <div style="color:#d6deeb; font-size:12px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase;">
        {title}
      </div>
      {"" if not subtitle else f'<div style="color:#7f8ea3; font-size:11px; margin-top:6px;">{subtitle}</div>'}
    </div>
    """, unsafe_allow_html=True)


def monitor_strip(items):
    blocks = ""
    for label, value, delta in items:
        delta_str = str(delta)
        if delta_str.startswith("+"):
            color = GREEN
        elif delta_str.startswith("-"):
            color = RED
        else:
            color = MUTED

        blocks += f"""
        <div style="padding:7px 12px; border-right:1px solid {BORDER}; min-width:120px; display:flex; align-items:center; gap:6px;">
          <span style="color:{MUTED}; font-size:9px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;">{label}</span>
          <span style="color:{TEXT}; font-size:13px; font-weight:700;">{value}</span>
          <span style="color:{color}; font-size:11px; font-weight:700;">{delta}</span>
        </div>
        """

    st.markdown(f"""
    <div style="display:flex; flex-wrap:wrap; gap:0; background:linear-gradient(180deg,#0b1220 0%, #0e1627 100%);
                border:1px solid {BORDER}; border-radius:7px; overflow:hidden; margin-bottom:12px;">
      {blocks}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Load data
# ══════════════════════════════════════════════════════════════════════════════

active_labels = GROUPS[focus_group].copy()

if custom_input.strip():
    for sym in [x.strip().upper() for x in custom_input.split(",") if x.strip()]:
        if sym not in UNIVERSE:
            UNIVERSE[sym] = sym
        if sym not in active_labels:
            active_labels.append(sym)

with st.spinner("Loading cross-asset market data…"):
    prices = load_macro_prices(active_labels, period=period)

if prices.empty:
    st.error("No macro data could be loaded.")
    st.stop()

snap = calc_snapshot(prices)
if snap.empty:
    st.error("Snapshot could not be built from the loaded data.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# Header monitor
# ══════════════════════════════════════════════════════════════════════════════

headline_labels = [x for x in ["S&P 500", "Nasdaq 100", "VIX", "US 10Y", "DXY", "Gold", "WTI", "Bitcoin", "EUR/USD"]
                   if x in snap["Asset"].values]
monitor_items = []

for lbl in headline_labels:
    row   = snap.loc[snap["Asset"] == lbl].iloc[0]
    value = f"{row['Last']:,.2f}" if abs(row["Last"]) < 1000 else f"{row['Last']:,.0f}"
    delta = f"{row['1D %']:+.2f}%" if pd.notna(row["1D %"]) else "—"
    monitor_items.append((lbl, value, delta))

monitor_strip(monitor_items)


# ══════════════════════════════════════════════════════════════════════════════
# Top summary
# ══════════════════════════════════════════════════════════════════════════════

up_today   = int((snap["1D %"] > 0).sum())
down_today = int((snap["1D %"] < 0).sum())
avg_vol    = snap["20D Vol %"].mean()

best_1d  = snap.loc[snap["1D %"].idxmax()]  if snap["1D %"].notna().any()  else None
worst_1d = snap.loc[snap["1D %"].idxmin()]  if snap["1D %"].notna().any()  else None
best_3m  = snap.loc[snap["3M %"].idxmax()]  if snap["3M %"].notna().any()  else None
worst_3m = snap.loc[snap["3M %"].idxmin()]  if snap["3M %"].notna().any()  else None

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Assets", f"{len(snap)}")
c2.metric("Up Today", f"{up_today}", delta=f"{up_today - down_today:+d}")
c3.metric("Avg 20D Vol", f"{avg_vol:.1f}%")
c4.metric("Best 1D",  best_1d["Asset"]  if best_1d  is not None else "—",
          delta=f"{best_1d['1D %']:.2f}%"  if best_1d  is not None else None)
c5.metric("Worst 1D", worst_1d["Asset"] if worst_1d is not None else "—",
          delta=f"{worst_1d['1D %']:.2f}%" if worst_1d is not None else None)
c6.metric("Best 3M",  best_3m["Asset"]  if best_3m  is not None else "—",
          delta=f"{best_3m['3M %']:.2f}%"  if best_3m  is not None else None)

st.markdown("")


# ══════════════════════════════════════════════════════════════════════════════
# Tabs
# ══════════════════════════════════════════════════════════════════════════════

tabs = st.tabs([
    "Monitor",
    "FX & Commodities",
    "Equities",
    "Rates & Bonds",
    "Crypto",
    "Correlation",
    "Regime / Yield Curve",
])

# ── Tab 1: Monitor ────────────────────────────────────────────────────────────
with tabs[0]:
    left, right = st.columns([1.4, 1], gap="large")

    with left:
        section_box("Cross-Asset Monitor", "Sortable snapshot across the loaded universe")
        sort_by   = st.selectbox("Sort by", ["1D %", "1M %", "3M %", "YTD %", "20D Vol %", "Ann. Ret %", "Asset"], key="macro_sort")
        ascending = st.checkbox("Ascending sort", value=False)
        disp      = snap.sort_values(sort_by, ascending=ascending).reset_index(drop=True)
        cols      = ["Asset", "Last", "1D %", "5D %", "1M %", "3M %", "YTD %", "20D Vol %", "Ann. Ret %"]
        st.dataframe(style_perf_table(disp[cols]), use_container_width=True, height=520)

    with right:
        section_box("1M Momentum Ranking", "Cross-asset relative strength")
        rank = snap.dropna(subset=["1M %"]).sort_values("1M %", ascending=True)
        fig, ax = plt.subplots(figsize=(8, max(4, len(rank) * 0.28)))
        colors = [GREEN if v >= 0 else RED for v in rank["1M %"]]
        ax.barh(rank["Asset"], rank["1M %"], color=colors, edgecolor="#0a0e1a", height=0.7)
        ax.axvline(0, color="white", lw=0.8, ls="--")
        ax.set_title("1-Month Return (%)")
        ax.grid(True, alpha=0.2, axis="x")
        plt.tight_layout()
        st.pyplot(fig); plt.close()

        section_box("Performance Heatmap", "Fast cross-asset view")
        heat_cols = ["1D %", "5D %", "1M %", "3M %", "YTD %"]
        heat = snap.set_index("Asset")[heat_cols].dropna(how="all")
        fig2, ax2 = plt.subplots(figsize=(8, max(4, len(heat) * 0.28)))
        cmap = mcolors.LinearSegmentedColormap.from_list("perf", [RED, "#111827", GREEN])
        vals = heat.values.astype(float)
        vmax = np.nanpercentile(np.abs(vals[np.isfinite(vals)]), 95) if np.isfinite(vals).any() else 1
        vmax = max(vmax, 0.25)
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
        st.pyplot(fig2); plt.close()

# ── Tab 2: FX & Commodities ───────────────────────────────────────────────────
with tabs[1]:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        section_box("FX Dashboard", "Dollar, majors and relative performance")
        fx_labels = [x for x in GROUPS["FX"] if x in snap["Asset"].values]
        fx_snap   = snap[snap["Asset"].isin(fx_labels)].copy()
        st.dataframe(
            style_perf_table(fx_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]),
            use_container_width=True, height=320,
        )

        fx_prices = prices[[x for x in fx_labels if x in prices.columns]]
        if not fx_prices.empty:
            selected_fx = st.multiselect("FX comparison", fx_prices.columns.tolist(),
                                         default=fx_prices.columns.tolist()[:4], key="fx_compare")
            if selected_fx:
                norm = fx_prices[selected_fx] / fx_prices[selected_fx].iloc[0] * 100
                fig, ax = plt.subplots(figsize=(8, 4))
                for i, col in enumerate(norm.columns):
                    ax.plot(norm.index, norm[col], lw=1.8, label=col, color=PALETTE[i % len(PALETTE)])
                ax.axhline(100, color="white", lw=0.7, ls="--")
                ax.set_title("FX Indexed to 100"); ax.legend(fontsize=8, ncols=2); ax.grid(True, alpha=0.2)
                plt.tight_layout(); st.pyplot(fig); plt.close()

    with col2:
        section_box("Commodity Dashboard", "Precious metals, energy, industrials and grains")
        comm_labels = [x for x in GROUPS["Commodities"] if x in snap["Asset"].values]
        comm_snap   = snap[snap["Asset"].isin(comm_labels)].copy()
        st.dataframe(
            style_perf_table(comm_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]),
            use_container_width=True, height=320,
        )

        comm_prices = prices[[x for x in comm_labels if x in prices.columns]]
        if not comm_prices.empty:
            selected_comm = st.multiselect("Commodity comparison", comm_prices.columns.tolist(),
                                           default=comm_prices.columns.tolist()[:4], key="comm_compare")
            if selected_comm:
                norm = comm_prices[selected_comm] / comm_prices[selected_comm].iloc[0] * 100
                fig2, ax2 = plt.subplots(figsize=(8, 4))
                for i, col in enumerate(norm.columns):
                    ax2.plot(norm.index, norm[col], lw=1.8, label=col, color=PALETTE[i % len(PALETTE)])
                ax2.axhline(100, color="white", lw=0.7, ls="--")
                ax2.set_title("Commodities Indexed to 100"); ax2.legend(fontsize=8, ncols=2); ax2.grid(True, alpha=0.2)
                plt.tight_layout(); st.pyplot(fig2); plt.close()

# ── Tab 3: Equities ───────────────────────────────────────────────────────────
with tabs[2]:
    section_box("Global Equities", "US and international index performance")
    eq_labels = [x for x in GROUPS["Equities"] if x in snap["Asset"].values]
    eq_snap   = snap[snap["Asset"].isin(eq_labels)].copy()
    eq_prices = prices[[x for x in eq_labels if x in prices.columns]]

    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig, ax = plt.subplots(figsize=(8, max(4, len(eq_snap) * 0.28)))
        eq_sorted = eq_snap.dropna(subset=["1D %"]).sort_values("1D %")
        colors = [GREEN if v >= 0 else RED for v in eq_sorted["1D %"]]
        ax.barh(eq_sorted["Asset"], eq_sorted["1D %"], color=colors, edgecolor="#0a0e1a")
        ax.axvline(0, color="white", lw=0.8, ls="--")
        ax.set_title("Equity 1D Move (%)"); ax.grid(True, alpha=0.2, axis="x")
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with c2:
        fig2, ax2 = plt.subplots(figsize=(8, max(4, len(eq_snap) * 0.28)))
        eq_sorted_3m = eq_snap.dropna(subset=["3M %"]).sort_values("3M %")
        colors2 = [GREEN if v >= 0 else RED for v in eq_sorted_3m["3M %"]]
        ax2.barh(eq_sorted_3m["Asset"], eq_sorted_3m["3M %"], color=colors2, edgecolor="#0a0e1a")
        ax2.axvline(0, color="white", lw=0.8, ls="--")
        ax2.set_title("Equity 3M Move (%)"); ax2.grid(True, alpha=0.2, axis="x")
        plt.tight_layout(); st.pyplot(fig2); plt.close()

    if not eq_prices.empty:
        selected_eq = st.multiselect("Indices to chart", eq_prices.columns.tolist(),
                                     default=eq_prices.columns.tolist()[:5], key="eq_compare")
        if selected_eq:
            norm = eq_prices[selected_eq] / eq_prices[selected_eq].iloc[0] * 100
            fig3, ax3 = plt.subplots(figsize=(11, 4))
            for i, col in enumerate(norm.columns):
                ax3.plot(norm.index, norm[col], lw=1.8, label=col, color=PALETTE[i % len(PALETTE)])
            ax3.axhline(100, color="white", lw=0.7, ls="--")
            ax3.set_title("Equity Indices Indexed to 100"); ax3.legend(fontsize=8, ncols=3); ax3.grid(True, alpha=0.2)
            plt.tight_layout(); st.pyplot(fig3); plt.close()

# ── Tab 4: Rates & Bonds ──────────────────────────────────────────────────────
with tabs[3]:
    left, right = st.columns(2, gap="large")

    with left:
        section_box("Rates", "Treasury yield proxies and curve signals")
        rate_labels = [x for x in GROUPS["Rates"] if x in snap["Asset"].values]
        rate_snap   = snap[snap["Asset"].isin(rate_labels)].copy()
        st.dataframe(
            style_perf_table(rate_snap[["Asset", "Last", "1D %", "1M %", "3M %"]]),
            use_container_width=True, height=240,
        )

        if {"US 5Y", "US 10Y"}.issubset(rate_snap["Asset"].values):
            y5  = float(rate_snap.loc[rate_snap["Asset"] == "US 5Y",  "Last"].iloc[0])
            y10 = float(rate_snap.loc[rate_snap["Asset"] == "US 10Y", "Last"].iloc[0])
            s1, s2 = st.columns(2)
            s1.metric("10Y - 5Y Spread", f"{y10 - y5:.2f}")
            if {"US 3M", "US 10Y"}.issubset(rate_snap["Asset"].values):
                y3m = float(rate_snap.loc[rate_snap["Asset"] == "US 3M", "Last"].iloc[0])
                s2.metric("10Y - 3M Spread", f"{y10 - y3m:.2f}")

        yc_labels = [x for x in ["US 3M", "US 5Y", "US 10Y", "US 30Y"] if x in prices.columns]
        if len(yc_labels) >= 2:
            maturity_map = {"US 3M": 0.25, "US 5Y": 5, "US 10Y": 10, "US 30Y": 30}
            x_yc = [maturity_map[k] for k in yc_labels]
            y_yc = [float(prices[k].dropna().iloc[-1]) for k in yc_labels]
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(x_yc, y_yc, marker="o", lw=2, color=ACCENT)
            ax.set_xticks(x_yc); ax.set_xticklabels(yc_labels)
            ax.set_title("Yield Curve"); ax.set_ylabel("Yield"); ax.grid(True, alpha=0.2)
            plt.tight_layout(); st.pyplot(fig); plt.close()

    with right:
        section_box("Bonds & Credit", "Treasury duration, IG, HY and inflation links")
        bond_labels = [x for x in GROUPS["Bonds"] if x in snap["Asset"].values]
        bond_snap   = snap[snap["Asset"].isin(bond_labels)].copy()
        st.dataframe(
            style_perf_table(bond_snap[["Asset", "Last", "1D %", "1M %", "3M %", "20D Vol %"]]),
            use_container_width=True, height=240,
        )

        bond_prices = prices[[x for x in bond_labels if x in prices.columns]]
        if {"HYG", "LQD"}.issubset(bond_prices.columns):
            ratio = (bond_prices["HYG"] / bond_prices["LQD"]).dropna()
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.plot(ratio.index, ratio.values, color=ACCENT2, lw=1.8)
            ax2.axhline(ratio.mean(), color="white", lw=0.8, ls="--")
            ax2.set_title("HYG / LQD Credit Risk Proxy"); ax2.grid(True, alpha=0.2)
            plt.tight_layout(); st.pyplot(fig2); plt.close()

# ── Tab 5: Crypto ─────────────────────────────────────────────────────────────
with tabs[4]:
    section_box("Crypto Monitor", "Major crypto assets and volatility")
    crypto_labels = [x for x in GROUPS["Crypto"] if x in snap["Asset"].values]
    crypto_snap   = snap[snap["Asset"].isin(crypto_labels)].copy()
    crypto_prices = prices[[x for x in crypto_labels if x in prices.columns]]

    if crypto_snap.empty:
        st.warning("No crypto data available.")
    else:
        n_crypto_cols = max(1, min(len(crypto_snap), 3))
        top_cols = st.columns(n_crypto_cols)
        for i, (_, row) in enumerate(crypto_snap.iterrows()):
            top_cols[i].metric(
                row["Asset"],
                f"${row['Last']:,.2f}",
                delta=f"{row['1D %']:.2f}%" if pd.notna(row["1D %"]) else None,
            )

    if not crypto_prices.empty:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            fig, ax = plt.subplots(figsize=(8, 4))
            for i, col in enumerate(crypto_prices.columns):
                ax.plot(crypto_prices.index, crypto_prices[col], lw=1.8, label=col,
                        color=PALETTE[i % len(PALETTE)])
            ax.set_yscale("log"); ax.set_title("Crypto Prices (log scale)")
            ax.legend(fontsize=8); ax.grid(True, alpha=0.2)
            plt.tight_layout(); st.pyplot(fig); plt.close()

        with c2:
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            for i, col in enumerate(crypto_prices.columns):
                rv = rolling_vol(crypto_prices[col].pct_change().dropna(), window=roll_window) * 100
                ax2.plot(rv.index, rv.values, lw=1.8, label=col, color=PALETTE[i % len(PALETTE)])
            ax2.set_title(f"Rolling {roll_window}D Annualised Vol (%)")
            ax2.legend(fontsize=8); ax2.grid(True, alpha=0.2)
            plt.tight_layout(); st.pyplot(fig2); plt.close()

# ── Tab 6: Correlation ────────────────────────────────────────────────────────
with tabs[5]:
    section_box("Correlation Matrix", "Daily return correlation across selected assets")
    corr_assets = st.multiselect(
        "Assets for correlation",
        prices.columns.tolist(),
        default=prices.columns.tolist()[:min(14, len(prices.columns))],
    )

    if len(corr_assets) >= 2:
        rets = prices[corr_assets].pct_change().dropna(how="all")
        corr = correlation_matrix(rets)

        fig, ax = plt.subplots(figsize=(max(7, len(corr_assets) * 0.7), max(5, len(corr_assets) * 0.55)))
        cmap_corr = mcolors.LinearSegmentedColormap.from_list("corr", [RED, "#111827", ACCENT])
        im = ax.imshow(corr.values, cmap=cmap_corr, vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr.columns))); ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(len(corr.index)));   ax.set_yticklabels(corr.index, fontsize=8)
        for i in range(len(corr.index)):
            for j in range(len(corr.columns)):
                ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=7, color="white")
        plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
        plt.tight_layout(); st.pyplot(fig); plt.close()

        if benchmark_label in prices.columns:
            section_box("Correlation vs Benchmark", benchmark_label)
            bench_ret = prices[benchmark_label].pct_change().dropna()
            vals = []
            for col in corr_assets:
                if col == benchmark_label:
                    continue
                aligned = pd.concat([prices[col].pct_change(), bench_ret], axis=1).dropna()
                if len(aligned) > 10:
                    vals.append((col, aligned.iloc[:, 0].corr(aligned.iloc[:, 1])))

            if vals:
                df_corr = pd.DataFrame(vals, columns=["Asset", "Correlation"]).sort_values("Correlation")
                fig2, ax2 = plt.subplots(figsize=(9, max(4, len(df_corr) * 0.3)))
                colors_corr = [GREEN if v >= 0 else RED for v in df_corr["Correlation"]]
                ax2.barh(df_corr["Asset"], df_corr["Correlation"], color=colors_corr, edgecolor="#0a0e1a")
                ax2.axvline(0, color="white", lw=0.8, ls="--"); ax2.set_xlim(-1.05, 1.05)
                ax2.grid(True, alpha=0.2, axis="x")
                plt.tight_layout(); st.pyplot(fig2); plt.close()
    else:
        st.info("Select at least two assets.")

# ── Tab 7: Regime / Yield Curve ───────────────────────────────────────────────
with tabs[6]:
    left, right = st.columns(2, gap="large")

    with left:
        section_box("Market Regime", "Simple trend + vol overlay using S&P 500 and VIX")
        if "S&P 500" in prices.columns:
            spx   = prices["S&P 500"].dropna()
            sma20 = spx.rolling(20).mean()
            sma60 = spx.rolling(60).mean()
            vix   = prices["VIX"].dropna() if "VIX" in prices.columns else pd.Series(dtype=float)

            latest_spx = float(spx.iloc[-1])
            latest_20  = float(sma20.iloc[-1]) if pd.notna(sma20.iloc[-1]) else np.nan
            latest_60  = float(sma60.iloc[-1]) if pd.notna(sma60.iloc[-1]) else np.nan
            latest_vix = float(vix.iloc[-1]) if len(vix) else np.nan

            if pd.notna(latest_20) and pd.notna(latest_60):
                if latest_spx > latest_20 > latest_60:
                    regime = "Bull Market" if (pd.isna(latest_vix) or latest_vix < 25) else "Bull / High Vol"
                    clr    = GREEN if "Bull Market" in regime else YELLOW
                elif latest_spx < latest_20 < latest_60:
                    regime, clr = "Bear Market", RED
                else:
                    regime, clr = "Choppy / Transition", ACCENT
            else:
                regime, clr = "Unknown", MUTED

            st.markdown(f"""
            <div style="background:linear-gradient(180deg,#0b1220 0%, #0d1526 100%);
                        border:1px solid {clr}; border-radius:10px; padding:18px; margin-bottom:12px;">
              <div style="color:#7f8ea3; font-size:10px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;">
                Current Regime
              </div>
              <div style="color:{clr}; font-size:28px; font-weight:800; margin-top:6px;">
                {regime}
              </div>
            </div>
            """, unsafe_allow_html=True)

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(spx.index, spx.values, color=ACCENT, lw=1.8, label="S&P 500")
            ax.plot(sma20.index, sma20.values, color=YELLOW, lw=1.1, ls="--", label="SMA 20")
            ax.plot(sma60.index, sma60.values, color=RED,    lw=1.1, ls="--", label="SMA 60")
            ax.legend(fontsize=8); ax.grid(True, alpha=0.2); ax.set_title("S&P 500 Trend Structure")
            plt.tight_layout(); st.pyplot(fig); plt.close()
        else:
            st.info("Load the 'All' or 'Equities' group to see the regime panel.")

    with right:
        section_box("Yield Curve Monitor", "Current curve shape and inversion risk")
        yc_labels = [x for x in ["US 3M", "US 5Y", "US 10Y", "US 30Y"] if x in prices.columns]
        if len(yc_labels) >= 2:
            maturity_map = {"US 3M": 0.25, "US 5Y": 5, "US 10Y": 10, "US 30Y": 30}
            hist    = prices[yc_labels].dropna(how="all")
            current = hist.dropna().iloc[-1] if not hist.dropna().empty else None

            if current is not None:
                xs = [maturity_map[k] for k in yc_labels]
                ys = [float(current[k]) for k in yc_labels]

                fig2, ax2 = plt.subplots(figsize=(8, 4))
                ax2.plot(xs, ys, marker="o", lw=2, color=ACCENT)
                ax2.set_xticks(xs); ax2.set_xticklabels(yc_labels)
                ax2.set_title("Current Yield Curve"); ax2.grid(True, alpha=0.2)
                plt.tight_layout(); st.pyplot(fig2); plt.close()

                if "US 10Y" in current.index and "US 3M" in current.index:
                    spread = float(current["US 10Y"] - current["US 3M"])
                    st.metric("10Y - 3M Spread", f"{spread:.2f}",
                              delta="Inverted" if spread < 0 else "Normal")
        else:
            st.info("Load the 'All' or 'Rates' group to see the yield curve.")

st.markdown("---")
st.markdown(
    """
    <div style="color:#7f8ea3; font-size:11px; text-align:center; letter-spacing:0.10em; text-transform:uppercase;">
      QuantDesk Pro | Macro Dashboard | Data via yfinance | For educational and research purposes only
    </div>
    """,
    unsafe_allow_html=True,
)

