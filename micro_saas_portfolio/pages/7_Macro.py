"""
7_Macro.py — QuantDesk Pro | Professional Macro Dashboard
Tabs: Snapshot · FX · Commodities · Rates & Bonds · Equities · Crypto ·
      Correlation · Regime · Yield Curve
"""

from auth import require_login, sidebar_user_widget
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import datetime

from utils import apply_theme, page_header, ACCENT, ACCENT2, GREEN, RED, YELLOW, PALETTE, MUTED, SURFACE, BORDER
from data_loader import load_macro_dataset, load_macro_snapshot, load_price_history, load_close_series
from analytics import annualized_vol, annualized_return, correlation_matrix, rolling_vol

st.set_page_config(page_title="Macro Dashboard", layout="wide", page_icon="🌍")
apply_theme()
page_header("Macro Dashboard", "Rates · FX · Commodities · Equities · Crypto · Regimes")

require_login()
sidebar_user_widget()

# ══════════════════════════════════════════════════════════════════════════════
# Universe Definition
# ══════════════════════════════════════════════════════════════════════════════

UNIVERSE = {
    # Rates
    "US 2Y Yield":    "^IRX",
    "US 10Y Yield":   "^TNX",
    "US 30Y Yield":   "^TYX",
    # FX
    "DXY (Dollar)":   "DX-Y.NYB",
    "EUR/USD":        "EURUSD=X",
    "GBP/USD":        "GBPUSD=X",
    "USD/JPY":        "JPY=X",
    "USD/CHF":        "CHF=X",
    "AUD/USD":        "AUDUSD=X",
    "USD/CAD":        "CADUSD=X",
    "USD/MXN":        "MXN=X",
    "USD/CNY":        "CNY=X",
    # Precious Metals
    "Gold":           "GC=F",
    "Silver":         "SI=F",
    "Platinum":       "PL=F",
    "Palladium":      "PA=F",
    # Energy
    "WTI Crude":      "CL=F",
    "Brent Crude":    "BZ=F",
    "Natural Gas":    "NG=F",
    "Gasoline":       "RB=F",
    "Heating Oil":    "HO=F",
    # Industrial Metals
    "Copper":         "HG=F",
    "Aluminium":      "ALI=F",
    # Agriculture
    "Corn":           "ZC=F",
    "Wheat":          "ZW=F",
    "Soybeans":       "ZS=F",
    "Sugar":          "SB=F",
    "Coffee":         "KC=F",
    "Cotton":         "CT=F",
    # US Equities
    "S&P 500":        "^GSPC",
    "Nasdaq 100":     "^NDX",
    "Russell 2000":   "^RUT",
    "Dow Jones":      "^DJI",
    "VIX":            "^VIX",
    # Global Equities
    "Euro Stoxx 50":  "^STOXX50E",
    "DAX":            "^GDAXI",
    "FTSE 100":       "^FTSE",
    "Nikkei 225":     "^N225",
    "Hang Seng":      "^HSI",
    "Shanghai Comp":  "000001.SS",
    "ASX 200":        "^AXJO",
    "BSE Sensex":     "^BSESN",
    # Bonds & Credit
    "TLT (20Y+)":     "TLT",
    "IEF (7-10Y)":    "IEF",
    "SHY (1-3Y)":     "SHY",
    "AGG (Agg Bond)": "AGG",
    "HYG (High Yield)":"HYG",
    "LQD (IG Credit)":"LQD",
    "EMB (EM Bonds)": "EMB",
    "TIPS":           "TIP",
    # Crypto
    "Bitcoin":        "BTC-USD",
    "Ethereum":       "ETH-USD",
    "Solana":         "SOL-USD",
    "BNB":            "BNB-USD",
}

GROUPS = {
    "Rates":          ["US 2Y Yield", "US 10Y Yield", "US 30Y Yield"],
    "FX":             ["DXY (Dollar)", "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
                       "AUD/USD", "USD/CAD", "USD/MXN", "USD/CNY"],
    "Precious Metals":["Gold", "Silver", "Platinum", "Palladium"],
    "Energy":         ["WTI Crude", "Brent Crude", "Natural Gas", "Gasoline", "Heating Oil"],
    "Industrial":     ["Copper", "Aluminium"],
    "Agriculture":    ["Corn", "Wheat", "Soybeans", "Sugar", "Coffee", "Cotton"],
    "US Equities":    ["S&P 500", "Nasdaq 100", "Russell 2000", "Dow Jones", "VIX"],
    "Global Equities":["Euro Stoxx 50", "DAX", "FTSE 100", "Nikkei 225", "Hang Seng",
                       "Shanghai Comp", "ASX 200", "BSE Sensex"],
    "Bonds & Credit": ["TLT (20Y+)", "IEF (7-10Y)", "SHY (1-3Y)", "AGG (Agg Bond)",
                       "HYG (High Yield)", "LQD (IG Credit)", "EMB (EM Bonds)", "TIPS"],
    "Crypto":         ["Bitcoin", "Ethereum", "Solana", "BNB"],
}

COMMODITIES_ALL = (
    GROUPS["Precious Metals"] + GROUPS["Energy"] +
    GROUPS["Industrial"] + GROUPS["Agriculture"]
)

# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════

st.sidebar.markdown("## ⚙️ Macro Settings")
period = st.sidebar.selectbox("Lookback period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
focus_group = st.sidebar.selectbox("Asset group", ["All"] + list(GROUPS.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("**Custom tickers** *(comma-separated)*")
custom_input = st.sidebar.text_input("Add custom YF tickers", placeholder="e.g. GLD,USO,TAN")

st.sidebar.markdown("---")
benchmark_label = st.sidebar.selectbox(
    "Correlation benchmark",
    ["S&P 500", "Gold", "DXY (Dollar)", "Bitcoin", "TLT (20Y+)"]
)
roll_window = st.sidebar.slider("Rolling vol window (days)", 5, 60, 20, 5)
run_macro = st.sidebar.button("🚀  Load Dashboard", use_container_width=True)

if not run_macro:
    st.markdown("""
    <div style="background:#111827; border:1px solid #1e2d45; border-radius:12px;
                padding:28px 32px; margin-top:16px; text-align:center;">
      <div style="font-size:32px; margin-bottom:10px;">🌍</div>
      <div style="color:#e2e8f0; font-size:16px; font-weight:700; margin-bottom:8px;">
        Professional Macro Dashboard
      </div>
      <div style="color:#64748b; font-size:13px; line-height:1.8;">
        Covers <strong style="color:#94a3b8;">40+ assets</strong> across FX, Commodities,
        Rates, Bonds, Global Equities and Crypto.<br>
        Select your period, asset group, and click <strong style="color:#00d4ff;">Load Dashboard</strong>.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# Build universe
# ══════════════════════════════════════════════════════════════════════════════

if focus_group == "All":
    active_labels = list(UNIVERSE.keys())
else:
    active_labels = GROUPS[focus_group]

active_universe = {lbl: UNIVERSE[lbl] for lbl in active_labels}

# Inject custom tickers
if custom_input.strip():
    for sym in [s.strip().upper() for s in custom_input.split(",") if s.strip()]:
        if sym not in active_universe.values():
            active_universe[sym] = sym

with st.spinner("Fetching macro data — this may take a moment for large universes…"):
    prices = load_macro_dataset(active_universe, period=period)
    snap   = load_macro_snapshot(active_universe, period=period)

if prices.empty or snap.empty:
    st.error("No macro data loaded. Yahoo Finance may be temporarily unavailable for some symbols.")
    st.stop()

snap = snap.copy()

# ══════════════════════════════════════════════════════════════════════════════
# Helper colours / formatting
# ══════════════════════════════════════════════════════════════════════════════

def _clr(v):
    if pd.isna(v):
        return MUTED
    return GREEN if v >= 0 else RED

def _arrow(v):
    if pd.isna(v):
        return "—"
    return f"{'▲' if v >= 0 else '▼'} {abs(v):.2f}%"

FMT = {
    "Last":      "{:.2f}",
    "1D %":      "{:.2f}%",
    "5D %":      "{:.2f}%",
    "1M %":      "{:.2f}%",
    "3M %":      "{:.2f}%",
    "YTD %":     "{:.2f}%",
    "20D Vol %": "{:.2f}%",
}

def _style_df(df):
    def hl(row):
        out = []
        for col in row.index:
            if col in ["1D %","5D %","1M %","3M %","YTD %"]:
                v = row[col]
                out.append(f"color: {'#00e676' if (not pd.isna(v) and v >= 0) else '#ff1744'}")
            else:
                out.append("")
        return out
    return df.style.format(FMT, na_rep="—").apply(hl, axis=1)

# ══════════════════════════════════════════════════════════════════════════════
# HEADLINE METRICS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("### 📡 Cross-Asset Snapshot")

up_c     = int((snap["1D %"] > 0).sum())
dn_c     = int((snap["1D %"] < 0).sum())
avg_vol  = snap["20D Vol %"].mean()
best     = snap.loc[snap["1D %"].idxmax()]   if not snap["1D %"].isna().all() else None
worst    = snap.loc[snap["1D %"].idxmin()]   if not snap["1D %"].isna().all() else None
best_3m  = snap.loc[snap["3M %"].idxmax()]  if not snap["3M %"].isna().all() else None
worst_3m = snap.loc[snap["3M %"].idxmin()]  if not snap["3M %"].isna().all() else None

cols = st.columns(7)
cols[0].metric("Assets",       f"{len(snap)}")
cols[1].metric("Up Today",     f"{up_c}", delta=f"{up_c - dn_c:+d}")
cols[2].metric("Avg 20D Vol",  f"{avg_vol:.1f}%" if pd.notna(avg_vol) else "—")
if best is not None:
    cols[3].metric("Best 1D",  best["Asset"], delta=f"{best['1D %']:.2f}%")
if worst is not None:
    cols[4].metric("Worst 1D", worst["Asset"], delta=f"{worst['1D %']:.2f}%")
if best_3m is not None:
    cols[5].metric("Best 3M",  best_3m["Asset"], delta=f"{best_3m['3M %']:.2f}%")
if worst_3m is not None:
    cols[6].metric("Worst 3M", worst_3m["Asset"], delta=f"{worst_3m['3M %']:.2f}%")

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tabs = st.tabs([
    "📋 Monitor",
    "💱 FX",
    "🛢️ Commodities",
    "📈 Equities",
    "🏦 Rates & Bonds",
    "₿ Crypto",
    "🔗 Correlation",
    "🧭 Regime",
    "📉 Yield Curve",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — MONITOR
# ──────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("#### Full Asset Monitor")

    # Sort control
    sort_by  = st.selectbox("Sort by", ["1D %","3M %","YTD %","20D Vol %","Asset"], key="mon_sort")
    asc_sort = st.checkbox("Ascending", value=False, key="mon_asc")
    disp = snap.sort_values(sort_by, ascending=asc_sort).reset_index(drop=True)

    st.dataframe(
        _style_df(disp[["Asset","Ticker","Last","1D %","5D %","1M %","3M %","YTD %","20D Vol %"]]),
        use_container_width=True,
        height=520,
    )

    # Performance heatmap
    st.markdown("#### Performance Heatmap")
    heat_cols = ["1D %","5D %","1M %","3M %","YTD %"]
    heat = snap.set_index("Asset")[heat_cols].dropna(how="all")
    if not heat.empty:
        fig_h, ax_h = plt.subplots(figsize=(9, max(4, len(heat) * 0.32)))
        cmap = mcolors.LinearSegmentedColormap.from_list("perf", [RED, "#111827", GREEN])
        vals = heat.values.astype(float)
        vmax = np.nanpercentile(np.abs(vals[np.isfinite(vals)]), 95) if np.isfinite(vals).any() else 1
        vmax = max(vmax, 0.1)
        im = ax_h.imshow(vals, aspect="auto", cmap=cmap, vmin=-vmax, vmax=vmax)
        ax_h.set_xticks(range(len(heat_cols))); ax_h.set_xticklabels(heat_cols, fontsize=9)
        ax_h.set_yticks(range(len(heat.index))); ax_h.set_yticklabels(heat.index, fontsize=8)
        for i in range(vals.shape[0]):
            for j in range(vals.shape[1]):
                if np.isfinite(vals[i,j]):
                    ax_h.text(j, i, f"{vals[i,j]:.1f}", ha="center", va="center",
                              color="white", fontsize=7, fontweight="bold")
        plt.colorbar(im, ax=ax_h, label="Return %", fraction=0.02, pad=0.02)
        plt.tight_layout(); st.pyplot(fig_h); plt.close()

    # Momentum bar — 1M
    st.markdown("#### 1M Momentum Ranking")
    rank = snap.dropna(subset=["1M %"]).sort_values("1M %", ascending=True)
    fig_r, ax_r = plt.subplots(figsize=(10, max(4, len(rank) * 0.28)))
    colors_r = [GREEN if v >= 0 else RED for v in rank["1M %"]]
    ax_r.barh(rank["Asset"], rank["1M %"], color=colors_r, edgecolor="#0a0e1a", height=0.7)
    ax_r.axvline(0, color="white", lw=0.8, ls="--")
    ax_r.set_title("1-Month Momentum (%)", fontsize=11)
    ax_r.grid(True, alpha=0.2, axis="x")
    plt.tight_layout(); st.pyplot(fig_r); plt.close()

    # CSV export
    csv = snap.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Export CSV", csv, "macro_snapshot.csv", "text/csv")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — FX
# ──────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("#### 💱 Foreign Exchange")
    fx_labels   = [l for l in GROUPS["FX"] if l in snap["Asset"].values]
    fx_snap     = snap[snap["Asset"].isin(fx_labels)].reset_index(drop=True)
    fx_prices   = prices[[c for c in fx_labels if c in prices.columns]]

    if fx_snap.empty:
        st.warning("No FX data available.")
    else:
        # Cards
        n_fx = len(fx_snap)
        cols = st.columns(min(n_fx, 5))
        for i, row in fx_snap.iterrows():
            c = cols[i % 5]
            clr = GREEN if row["1D %"] >= 0 else RED
            c.markdown(f"""
            <div style="background:#111827; border:1px solid #1e2d45; border-radius:8px;
                        padding:12px; text-align:center; margin-bottom:8px;">
              <div style="color:#94a3b8; font-size:10px; letter-spacing:0.1em; text-transform:uppercase;">
                {row['Asset']}
              </div>
              <div style="color:#e2e8f0; font-size:20px; font-weight:700; margin:4px 0;">
                {row['Last']:.4f}
              </div>
              <div style="color:{clr}; font-size:13px; font-weight:600;">
                {'▲' if row['1D %'] >= 0 else '▼'} {abs(row['1D %']):.2f}%
              </div>
              <div style="color:#475569; font-size:10px;">20D Vol: {row['20D Vol %']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("##### Daily Change (%)")
            fx_sorted = fx_snap.sort_values("1D %")
            clrs = [GREEN if v >= 0 else RED for v in fx_sorted["1D %"]]
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.barh(fx_sorted["Asset"], fx_sorted["1D %"], color=clrs, edgecolor="#0a0e1a", height=0.65)
            ax.axvline(0, color="white", lw=0.8, ls="--")
            ax.set_title("FX 1D Move (%)"); ax.grid(True, alpha=0.2, axis="x")
            plt.tight_layout(); st.pyplot(fig); plt.close()

        with col_b:
            st.markdown("##### Multi-Period Performance")
            periods_show = ["1D %","5D %","1M %","3M %"]
            fx_multi = fx_snap.set_index("Asset")[periods_show].dropna(how="all")
            cmap_fx = mcolors.LinearSegmentedColormap.from_list("fx", [RED,"#111827",GREEN])
            vals_fx = fx_multi.values.astype(float)
            vmax_fx = max(np.nanpercentile(np.abs(vals_fx[np.isfinite(vals_fx)]), 95), 0.5) if np.isfinite(vals_fx).any() else 1
            fig2, ax2 = plt.subplots(figsize=(7, max(3, len(fx_multi) * 0.45)))
            im2 = ax2.imshow(vals_fx, aspect="auto", cmap=cmap_fx, vmin=-vmax_fx, vmax=vmax_fx)
            ax2.set_xticks(range(len(periods_show))); ax2.set_xticklabels(periods_show, fontsize=9)
            ax2.set_yticks(range(len(fx_multi.index))); ax2.set_yticklabels(fx_multi.index, fontsize=9)
            for i in range(vals_fx.shape[0]):
                for j in range(vals_fx.shape[1]):
                    if np.isfinite(vals_fx[i,j]):
                        ax2.text(j, i, f"{vals_fx[i,j]:.2f}", ha="center", va="center",
                                 color="white", fontsize=8, fontweight="bold")
            plt.colorbar(im2, ax=ax2, fraction=0.03)
            plt.tight_layout(); st.pyplot(fig2); plt.close()

        # Normalised price chart
        st.markdown("##### Normalised FX Performance")
        if not fx_prices.empty:
            selected_fx = st.multiselect(
                "Select pairs to compare", fx_prices.columns.tolist(),
                default=fx_prices.columns.tolist()[:5], key="fx_sel"
            )
            if selected_fx:
                norm = fx_prices[selected_fx] / fx_prices[selected_fx].iloc[0] * 100
                fig3, ax3 = plt.subplots(figsize=(11, 4))
                for i, col in enumerate(norm.columns):
                    ax3.plot(norm.index, norm[col], label=col, lw=1.8,
                             color=PALETTE[i % len(PALETTE)])
                ax3.axhline(100, color="white", lw=0.6, ls="--")
                ax3.set_ylabel("Indexed to 100"); ax3.legend(fontsize=8, ncols=3)
                ax3.grid(True, alpha=0.2); ax3.set_title("Normalised FX — Indexed to 100")
                plt.tight_layout(); st.pyplot(fig3); plt.close()

        # Rolling vol
        st.markdown("##### Rolling FX Volatility")
        if not fx_prices.empty:
            sel_vol = st.selectbox("Select pair for vol chart",
                                   [c for c in fx_labels if c in fx_prices.columns], key="fx_vol_sel")
            if sel_vol:
                ret_fx = fx_prices[sel_vol].pct_change().dropna()
                rvol   = rolling_vol(ret_fx, window=roll_window)
                fig4, ax4 = plt.subplots(figsize=(11, 3))
                ax4.plot(rvol.index, rvol * 100, color=ACCENT, lw=1.8)
                ax4.fill_between(rvol.index, rvol * 100, alpha=0.15, color=ACCENT)
                ax4.set_title(f"{sel_vol} — {roll_window}D Rolling Annualised Vol (%)")
                ax4.grid(True, alpha=0.2); ax4.set_ylabel("Vol %")
                plt.tight_layout(); st.pyplot(fig4); plt.close()

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — COMMODITIES
# ──────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("#### 🛢️ Commodities")
    comm_labels = [l for l in COMMODITIES_ALL if l in snap["Asset"].values]
    comm_snap   = snap[snap["Asset"].isin(comm_labels)].reset_index(drop=True)
    comm_prices = prices[[c for c in comm_labels if c in prices.columns]]

    if comm_snap.empty:
        st.warning("No commodity data available.")
    else:
        sub_groups = {
            "Precious Metals": GROUPS["Precious Metals"],
            "Energy":          GROUPS["Energy"],
            "Industrial":      GROUPS["Industrial"],
            "Agriculture":     GROUPS["Agriculture"],
        }
        for grp_name, grp_lbls in sub_groups.items():
            sub = comm_snap[comm_snap["Asset"].isin(grp_lbls)]
            if sub.empty:
                continue
            st.markdown(f"##### {grp_name}")
            ncols_g = min(len(sub), 5)
            gcols = st.columns(ncols_g)
            for idx, (_, row) in enumerate(sub.iterrows()):
                clr = GREEN if row["1D %"] >= 0 else RED
                gcols[idx % ncols_g].markdown(f"""
                <div style="background:#111827; border:1px solid #1e2d45; border-radius:8px;
                            padding:10px; text-align:center; margin-bottom:6px;">
                  <div style="color:#94a3b8; font-size:9px; letter-spacing:0.1em;
                              text-transform:uppercase;">{row['Asset']}</div>
                  <div style="color:#e2e8f0; font-size:18px; font-weight:700; margin:2px 0;">
                    {row['Last']:.2f}
                  </div>
                  <div style="color:{clr}; font-size:12px; font-weight:600;">
                    {'▲' if row['1D %'] >= 0 else '▼'} {abs(row['1D %']):.2f}%
                  </div>
                  <div style="color:#475569; font-size:9px;">Vol: {row['20D Vol %']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        # Commodity sector comparison
        st.markdown("##### Sector 1M Performance")
        sector_1m = {}
        for grp_name, grp_lbls in sub_groups.items():
            sub = comm_snap[comm_snap["Asset"].isin(grp_lbls)]["1M %"].dropna()
            if not sub.empty:
                sector_1m[grp_name] = sub.mean()
        if sector_1m:
            fig_sec, ax_sec = plt.subplots(figsize=(8, 3))
            clrs_sec = [GREEN if v >= 0 else RED for v in sector_1m.values()]
            ax_sec.bar(list(sector_1m.keys()), list(sector_1m.values()),
                       color=clrs_sec, edgecolor="#0a0e1a", width=0.5)
            ax_sec.axhline(0, color="white", lw=0.8, ls="--")
            ax_sec.set_title("Average 1M Return by Commodity Sector (%)")
            ax_sec.grid(True, alpha=0.2, axis="y")
            plt.tight_layout(); st.pyplot(fig_sec); plt.close()

        # Normalised price history
        st.markdown("##### Price History (Indexed)")
        if not comm_prices.empty:
            selected_comm = st.multiselect(
                "Select commodities to chart",
                comm_prices.columns.tolist(),
                default=comm_prices.columns.tolist()[:6], key="comm_sel"
            )
            if selected_comm:
                norm_c = comm_prices[selected_comm] / comm_prices[selected_comm].iloc[0] * 100
                fig_c, ax_c = plt.subplots(figsize=(11, 4))
                for i, col in enumerate(norm_c.columns):
                    ax_c.plot(norm_c.index, norm_c[col], label=col, lw=1.8,
                              color=PALETTE[i % len(PALETTE)])
                ax_c.axhline(100, color="white", lw=0.6, ls="--")
                ax_c.set_ylabel("Indexed to 100"); ax_c.legend(fontsize=8, ncols=3)
                ax_c.grid(True, alpha=0.2); ax_c.set_title("Commodity Price — Indexed to 100")
                plt.tight_layout(); st.pyplot(fig_c); plt.close()

        # Rolling vol for selected commodity
        st.markdown("##### Rolling Volatility")
        if not comm_prices.empty:
            sel_c_vol = st.selectbox("Select commodity", comm_prices.columns.tolist(), key="cv_sel")
            ret_c = comm_prices[sel_c_vol].pct_change().dropna()
            rv_c  = rolling_vol(ret_c, window=roll_window)
            fig_cv, ax_cv = plt.subplots(figsize=(11, 3))
            ax_cv.plot(rv_c.index, rv_c * 100, color=YELLOW, lw=1.8)
            ax_cv.fill_between(rv_c.index, rv_c * 100, alpha=0.15, color=YELLOW)
            ax_cv.set_title(f"{sel_c_vol} — {roll_window}D Rolling Annualised Vol (%)")
            ax_cv.grid(True, alpha=0.2); ax_cv.set_ylabel("Vol %")
            plt.tight_layout(); st.pyplot(fig_cv); plt.close()

        # Full table
        with st.expander("Full Commodity Table"):
            st.dataframe(_style_df(
                comm_snap[["Asset","Last","1D %","5D %","1M %","3M %","YTD %","20D Vol %"]]
            ), use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — EQUITIES
# ──────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("#### 📈 Global Equities")
    eq_labels  = GROUPS["US Equities"] + GROUPS["Global Equities"]
    eq_snap    = snap[snap["Asset"].isin(eq_labels)].reset_index(drop=True)
    eq_prices  = prices[[c for c in eq_labels if c in prices.columns]]

    if eq_snap.empty:
        st.warning("No equity data available.")
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("##### 1D Change (%)")
            eq_s = eq_snap.sort_values("1D %", ascending=True)
            clrs_eq = [GREEN if v >= 0 else RED for v in eq_s["1D %"]]
            fig, ax = plt.subplots(figsize=(7, max(4, len(eq_s) * 0.35)))
            ax.barh(eq_s["Asset"], eq_s["1D %"], color=clrs_eq, edgecolor="#0a0e1a", height=0.7)
            ax.axvline(0, color="white", lw=0.8, ls="--")
            ax.set_title("Equity 1D Move (%)"); ax.grid(True, alpha=0.2, axis="x")
            ax.invert_yaxis(); plt.tight_layout(); st.pyplot(fig); plt.close()

        with col_b:
            st.markdown("##### 3M Performance (%)")
            eq_3m = eq_snap.sort_values("3M %", ascending=True).dropna(subset=["3M %"])
            clrs_3m = [GREEN if v >= 0 else RED for v in eq_3m["3M %"]]
            fig2, ax2 = plt.subplots(figsize=(7, max(4, len(eq_3m) * 0.35)))
            ax2.barh(eq_3m["Asset"], eq_3m["3M %"], color=clrs_3m, edgecolor="#0a0e1a", height=0.7)
            ax2.axvline(0, color="white", lw=0.8, ls="--")
            ax2.set_title("Equity 3M Performance (%)"); ax2.grid(True, alpha=0.2, axis="x")
            ax2.invert_yaxis(); plt.tight_layout(); st.pyplot(fig2); plt.close()

        # VIX chart
        vix_label = "VIX"
        if vix_label in prices.columns:
            st.markdown("##### VIX — Fear Index")
            vix_s = prices[vix_label].dropna()
            fig_v, ax_v = plt.subplots(figsize=(11, 3))
            ax_v.plot(vix_s.index, vix_s.values, color=RED, lw=1.8)
            ax_v.fill_between(vix_s.index, vix_s.values, alpha=0.15, color=RED)
            ax_v.axhline(20, color=YELLOW, lw=1, ls="--", label="VIX=20 (elevated)")
            ax_v.axhline(30, color=RED,    lw=1, ls=":",  label="VIX=30 (fear)")
            current_vix = float(vix_s.iloc[-1])
            regime_str = "🔴 High Fear" if current_vix > 30 else ("🟡 Elevated" if current_vix > 20 else "🟢 Calm")
            ax_v.set_title(f"VIX — {current_vix:.1f} ({regime_str})")
            ax_v.legend(fontsize=8); ax_v.grid(True, alpha=0.2)
            plt.tight_layout(); st.pyplot(fig_v); plt.close()

        # Normalised equity performance
        st.markdown("##### Normalised Equity Performance")
        if not eq_prices.empty:
            selected_eq = st.multiselect(
                "Select indices", eq_prices.columns.tolist(),
                default=eq_prices.columns.tolist()[:6], key="eq_sel"
            )
            if selected_eq:
                norm_eq = eq_prices[selected_eq] / eq_prices[selected_eq].iloc[0] * 100
                fig3, ax3 = plt.subplots(figsize=(11, 4))
                for i, col in enumerate(norm_eq.columns):
                    ax3.plot(norm_eq.index, norm_eq[col], label=col, lw=1.8,
                             color=PALETTE[i % len(PALETTE)])
                ax3.axhline(100, color="white", lw=0.6, ls="--")
                ax3.set_ylabel("Indexed to 100"); ax3.legend(fontsize=8, ncols=3)
                ax3.grid(True, alpha=0.2); ax3.set_title("Global Equity Indices — Indexed to 100")
                plt.tight_layout(); st.pyplot(fig3); plt.close()

        # Full table
        with st.expander("Full Equity Table"):
            st.dataframe(_style_df(
                eq_snap[["Asset","Last","1D %","5D %","1M %","3M %","YTD %","20D Vol %"]]
            ), use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 — RATES & BONDS
# ──────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown("#### 🏦 Rates & Fixed Income")
    bond_labels = GROUPS["Rates"] + GROUPS["Bonds & Credit"]
    bond_snap   = snap[snap["Asset"].isin(bond_labels)].reset_index(drop=True)
    bond_prices = prices[[c for c in bond_labels if c in prices.columns]]

    if bond_snap.empty:
        st.warning("No rates/bonds data available.")
    else:
        # Rate cards
        rate_snap = bond_snap[bond_snap["Asset"].isin(GROUPS["Rates"])]
        if not rate_snap.empty:
            st.markdown("##### US Treasury Yields (Yahoo Proxy)")
            rcols = st.columns(len(rate_snap))
            for i, (_, row) in enumerate(rate_snap.iterrows()):
                clr = GREEN if row["1D %"] <= 0 else RED  # yields up = bonds down
                rcols[i].markdown(f"""
                <div style="background:#111827; border:1px solid #1e2d45; border-radius:10px;
                            padding:18px; text-align:center;">
                  <div style="color:#94a3b8; font-size:11px; letter-spacing:0.1em;
                              text-transform:uppercase; margin-bottom:4px;">{row['Asset']}</div>
                  <div style="color:#e2e8f0; font-size:28px; font-weight:800;">{row['Last']:.2f}</div>
                  <div style="color:{clr}; font-size:13px; font-weight:600; margin-top:4px;">
                    {'▲' if row['1D %'] >= 0 else '▼'} {abs(row['1D %']):.2f}%
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Yield spread
            y2_row  = rate_snap[rate_snap["Asset"] == "US 2Y Yield"]
            y10_row = rate_snap[rate_snap["Asset"] == "US 10Y Yield"]
            y30_row = rate_snap[rate_snap["Asset"] == "US 30Y Yield"]
            if not y2_row.empty and not y10_row.empty:
                y2  = float(y2_row["Last"].iloc[0])
                y10 = float(y10_row["Last"].iloc[0])
                spread = y10 - y2
                inv    = spread < 0
                col1, col2 = st.columns(2)
                col1.metric(
                    "10Y–2Y Spread",
                    f"{spread:.2f}",
                    delta="⚠️ INVERTED — Recession signal" if inv else "Normal slope"
                )
                if not y30_row.empty:
                    y30 = float(y30_row["Last"].iloc[0])
                    col2.metric("30Y–10Y Spread", f"{y30 - y10:.2f}")

        st.markdown("---")

        # Bond ETF performance
        etf_snap = bond_snap[bond_snap["Asset"].isin(GROUPS["Bonds & Credit"])]
        if not etf_snap.empty:
            st.markdown("##### Bond ETF Monitor")
            st.dataframe(_style_df(
                etf_snap[["Asset","Last","1D %","5D %","1M %","3M %","YTD %","20D Vol %"]]
            ), use_container_width=True)

            # Risk-off vs Risk-on bond flows proxy
            st.markdown("##### Bond ETF Performance Comparison")
            bond_etf_cols = [c for c in GROUPS["Bonds & Credit"] if c in bond_prices.columns]
            if bond_etf_cols:
                selected_bonds = st.multiselect(
                    "Select bond ETFs",
                    bond_etf_cols,
                    default=bond_etf_cols[:5], key="bond_sel"
                )
                if selected_bonds:
                    norm_b = bond_prices[selected_bonds] / bond_prices[selected_bonds].iloc[0] * 100
                    fig_b, ax_b = plt.subplots(figsize=(11, 4))
                    for i, col in enumerate(norm_b.columns):
                        ax_b.plot(norm_b.index, norm_b[col], label=col, lw=1.8,
                                  color=PALETTE[i % len(PALETTE)])
                    ax_b.axhline(100, color="white", lw=0.6, ls="--")
                    ax_b.set_ylabel("Indexed to 100"); ax_b.legend(fontsize=8, ncols=3)
                    ax_b.grid(True, alpha=0.2); ax_b.set_title("Bond ETF — Indexed to 100")
                    plt.tight_layout(); st.pyplot(fig_b); plt.close()

            # Credit spread proxy: HYG vs LQD
            hyg_col = "HYG (High Yield)"
            lqd_col = "LQD (IG Credit)"
            if hyg_col in bond_prices.columns and lqd_col in bond_prices.columns:
                st.markdown("##### Credit Spread Proxy (HYG/LQD Ratio)")
                ratio = bond_prices[hyg_col] / bond_prices[lqd_col]
                ratio_ret = ratio.pct_change().dropna()
                fig_cs, ax_cs = plt.subplots(figsize=(11, 3))
                ax_cs.plot(ratio.index, ratio.values, color=ACCENT2, lw=1.8)
                ax_cs.fill_between(ratio.index, ratio.values, ratio.mean(), alpha=0.12, color=ACCENT2)
                ax_cs.axhline(ratio.mean(), color="white", lw=0.8, ls="--", label="Mean")
                ax_cs.set_title("HYG / LQD Ratio — Credit Risk Appetite (higher = risk-on)")
                ax_cs.legend(fontsize=8); ax_cs.grid(True, alpha=0.2)
                plt.tight_layout(); st.pyplot(fig_cs); plt.close()

# ──────────────────────────────────────────────────────────────────────────────
# TAB 6 — CRYPTO
# ──────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown("#### ₿ Crypto Markets")
    crypto_labels = [l for l in GROUPS["Crypto"] if l in snap["Asset"].values]
    crypto_snap   = snap[snap["Asset"].isin(crypto_labels)].reset_index(drop=True)
    crypto_prices = prices[[c for c in crypto_labels if c in prices.columns]]

    if crypto_snap.empty:
        st.warning("No crypto data available.")
    else:
        ccols = st.columns(min(len(crypto_snap), 4))
        for i, (_, row) in enumerate(crypto_snap.iterrows()):
            clr = GREEN if row["1D %"] >= 0 else RED
            ccols[i % 4].markdown(f"""
            <div style="background:#111827; border:1px solid #1e2d45; border-radius:10px;
                        padding:16px; text-align:center; margin-bottom:8px;">
              <div style="color:#94a3b8; font-size:11px; letter-spacing:0.1em;
                          text-transform:uppercase; margin-bottom:6px;">{row['Asset']}</div>
              <div style="color:#e2e8f0; font-size:22px; font-weight:800;">
                ${row['Last']:,.2f}
              </div>
              <div style="color:{clr}; font-size:14px; font-weight:600; margin-top:4px;">
                {'▲' if row['1D %'] >= 0 else '▼'} {abs(row['1D %']):.2f}%
              </div>
              <div style="color:#475569; font-size:10px; margin-top:4px;">
                1M: {row['1M %']:.1f}%  |  Vol: {row['20D Vol %']:.1f}%
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        if not crypto_prices.empty:
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("##### Price History (Log Scale)")
                fig, ax = plt.subplots(figsize=(7, 4))
                for i, col in enumerate(crypto_prices.columns):
                    ax.plot(crypto_prices.index, crypto_prices[col],
                            label=col, lw=1.8, color=PALETTE[i % len(PALETTE)])
                ax.set_yscale("log"); ax.legend(fontsize=9)
                ax.set_title("Crypto Price (log)"); ax.grid(True, alpha=0.2)
                plt.tight_layout(); st.pyplot(fig); plt.close()

            with col_b:
                st.markdown("##### Normalised Performance")
                norm_cr = crypto_prices / crypto_prices.iloc[0] * 100
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                for i, col in enumerate(norm_cr.columns):
                    ax2.plot(norm_cr.index, norm_cr[col],
                             label=col, lw=1.8, color=PALETTE[i % len(PALETTE)])
                ax2.axhline(100, color="white", lw=0.6, ls="--")
                ax2.set_ylabel("Indexed to 100"); ax2.legend(fontsize=9)
                ax2.set_title("Crypto — Indexed to 100"); ax2.grid(True, alpha=0.2)
                plt.tight_layout(); st.pyplot(fig2); plt.close()

            # Rolling vol
            st.markdown("##### Rolling Volatility (Annualised)")
            fig3, ax3 = plt.subplots(figsize=(11, 3))
            for i, col in enumerate(crypto_prices.columns):
                ret_cr = crypto_prices[col].pct_change().dropna()
                rv_cr  = rolling_vol(ret_cr, window=roll_window)
                ax3.plot(rv_cr.index, rv_cr * 100, label=col, lw=1.8,
                         color=PALETTE[i % len(PALETTE)])
            ax3.set_title(f"Crypto {roll_window}D Rolling Vol (%)")
            ax3.legend(fontsize=9); ax3.grid(True, alpha=0.2); ax3.set_ylabel("Vol %")
            plt.tight_layout(); st.pyplot(fig3); plt.close()

            # BTC vs Gold
            btc_col  = "Bitcoin"
            gold_col = "Gold"
            if btc_col in prices.columns and gold_col in prices.columns:
                st.markdown("##### Bitcoin vs Gold (Hedging Asset Comparison)")
                merged = pd.DataFrame({
                    "Bitcoin": prices[btc_col],
                    "Gold":    prices[gold_col],
                }).dropna()
                norm_bg = merged / merged.iloc[0] * 100
                fig4, ax4 = plt.subplots(figsize=(11, 4))
                ax4.plot(norm_bg.index, norm_bg["Bitcoin"], label="Bitcoin",
                         color=YELLOW, lw=2)
                ax4.plot(norm_bg.index, norm_bg["Gold"], label="Gold",
                         color=ACCENT, lw=2)
                ax4.axhline(100, color="white", lw=0.6, ls="--")
                ax4.set_title("Bitcoin vs Gold — Indexed to 100")
                ax4.legend(); ax4.grid(True, alpha=0.2)
                plt.tight_layout(); st.pyplot(fig4); plt.close()

# ──────────────────────────────────────────────────────────────────────────────
# TAB 7 — CORRELATION
# ──────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown("#### 🔗 Cross-Asset Correlation Analysis")

    corr_assets = st.multiselect(
        "Select assets for correlation matrix",
        prices.columns.tolist(),
        default=prices.columns.tolist()[:min(18, len(prices.columns))],
        key="corr_sel"
    )

    if len(corr_assets) < 2:
        st.info("Select at least 2 assets.")
    else:
        ret_c = prices[corr_assets].pct_change().dropna(how="all")
        corr  = correlation_matrix(ret_c)

        fig_c, ax_c = plt.subplots(figsize=(max(7, len(corr_assets) * 0.7),
                                            max(5, len(corr_assets) * 0.6)))
        cmap_c = mcolors.LinearSegmentedColormap.from_list("corr", [RED, "#111827", ACCENT])
        im = ax_c.imshow(corr.values, cmap=cmap_c, vmin=-1, vmax=1)
        ax_c.set_xticks(range(len(corr.columns)))
        ax_c.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
        ax_c.set_yticks(range(len(corr.index)))
        ax_c.set_yticklabels(corr.index, fontsize=8)
        for i in range(len(corr.columns)):
            for j in range(len(corr.index)):
                ax_c.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center",
                          color="white", fontsize=7, fontweight="bold")
        plt.colorbar(im, ax=ax_c, fraction=0.02, pad=0.02)
        ax_c.set_title("Cross-Asset Daily Return Correlation")
        plt.tight_layout(); st.pyplot(fig_c); plt.close()

        # Correlation with benchmark
        st.markdown(f"##### Correlation vs Benchmark: {benchmark_label}")
        if benchmark_label in prices.columns:
            bench_ret = prices[benchmark_label].pct_change().dropna()
            corr_vs = {}
            for col in corr_assets:
                if col == benchmark_label:
                    continue
                asset_ret = prices[col].pct_change().dropna()
                aligned   = pd.concat([asset_ret, bench_ret], axis=1).dropna()
                if len(aligned) > 10:
                    corr_vs[col] = aligned.iloc[:,0].corr(aligned.iloc[:,1])
            if corr_vs:
                cv_df = pd.DataFrame({"Asset": list(corr_vs.keys()),
                                      "Correlation": list(corr_vs.values())})
                cv_df = cv_df.sort_values("Correlation")
                fig_cv, ax_cv = plt.subplots(figsize=(10, max(3, len(cv_df) * 0.3)))
                clrs_cv = [GREEN if v >= 0 else RED for v in cv_df["Correlation"]]
                ax_cv.barh(cv_df["Asset"], cv_df["Correlation"],
                           color=clrs_cv, edgecolor="#0a0e1a", height=0.7)
                ax_cv.axvline(0, color="white", lw=0.8, ls="--")
                ax_cv.set_xlim(-1.1, 1.1)
                ax_cv.set_title(f"Correlation vs {benchmark_label}")
                ax_cv.grid(True, alpha=0.2, axis="x")
                ax_cv.invert_yaxis(); plt.tight_layout(); st.pyplot(fig_cv); plt.close()

        # Rolling correlation pair
        st.markdown("##### Rolling Correlation — Custom Pair")
        col1, col2 = st.columns(2)
        avail = prices.columns.tolist()
        a1 = col1.selectbox("Asset A", avail, index=0, key="rc_a1")
        a2 = col2.selectbox("Asset B", avail, index=min(1, len(avail)-1), key="rc_a2")
        if a1 != a2:
            r1 = prices[a1].pct_change().dropna()
            r2 = prices[a2].pct_change().dropna()
            aligned_rc = pd.concat([r1, r2], axis=1).dropna()
            aligned_rc.columns = [a1, a2]
            roll_c = aligned_rc[a1].rolling(roll_window).corr(aligned_rc[a2])
            fig_rc, ax_rc = plt.subplots(figsize=(11, 3))
            ax_rc.plot(roll_c.index, roll_c.values, color=ACCENT2, lw=1.8)
            ax_rc.axhline(0, color="white", lw=0.8, ls="--")
            ax_rc.fill_between(roll_c.index, roll_c.values, 0,
                               where=roll_c.values >= 0, alpha=0.12, color=GREEN)
            ax_rc.fill_between(roll_c.index, roll_c.values, 0,
                               where=roll_c.values < 0, alpha=0.12, color=RED)
            ax_rc.set_ylim(-1.1, 1.1)
            ax_rc.set_title(f"Rolling {roll_window}D Correlation: {a1} vs {a2}")
            ax_rc.grid(True, alpha=0.2)
            plt.tight_layout(); st.pyplot(fig_rc); plt.close()

# ──────────────────────────────────────────────────────────────────────────────
# TAB 8 — REGIME
# ──────────────────────────────────────────────────────────────────────────────
with tabs[7]:
    st.markdown("#### 🧭 Market Regime Analysis")
    st.caption(
        "Regime classification uses the S&P 500's rolling trend and VIX level to "
        "identify market environments, then shows which asset classes perform best in each regime."
    )

    sp_col  = "S&P 500"
    vix_col = "VIX"

    if sp_col not in prices.columns:
        st.warning("S&P 500 data not loaded. Select 'All' group to enable regime analysis.")
    else:
        sp_ret   = prices[sp_col].pct_change().dropna()
        sp_sma20 = prices[sp_col].rolling(20).mean()
        sp_sma60 = prices[sp_col].rolling(60).mean()

        def classify_regime(sp, sma20, sma60, vix_series=None):
            regimes = []
            for date in sp.index:
                try:
                    s  = float(sp.loc[date])
                    m20 = float(sma20.loc[date]) if date in sma20.index else np.nan
                    m60 = float(sma60.loc[date]) if date in sma60.index else np.nan
                    vix_val = float(vix_series.loc[date]) if (vix_series is not None and date in vix_series.index) else np.nan
                    if np.isnan(m20) or np.isnan(m60):
                        regimes.append("Unknown")
                    elif s > m20 > m60:
                        regimes.append("Bull Market" if (np.isnan(vix_val) or vix_val < 25) else "Bull/Vol")
                    elif s < m20 < m60:
                        regimes.append("Bear Market" if (np.isnan(vix_val) or vix_val > 20) else "Correction")
                    else:
                        regimes.append("Choppy")
                except Exception:
                    regimes.append("Unknown")
            return pd.Series(regimes, index=sp.index)

        vix_series = prices[vix_col].dropna() if vix_col in prices.columns else None
        regimes    = classify_regime(prices[sp_col].dropna(), sp_sma20, sp_sma60, vix_series)
        current_regime = regimes.iloc[-1] if len(regimes) else "Unknown"

        REGIME_COLORS = {
            "Bull Market": GREEN,
            "Bull/Vol":    YELLOW,
            "Choppy":      ACCENT,
            "Correction":  ORANGE if "ORANGE" in dir() else "#ff6e40",
            "Bear Market": RED,
            "Unknown":     MUTED,
        }
        rclr = REGIME_COLORS.get(current_regime, MUTED)

        st.markdown(f"""
        <div style="background:#111827; border:1px solid {rclr}; border-radius:12px;
                    padding:20px 28px; margin-bottom:20px; display:flex; align-items:center; gap:20px;">
          <div style="font-size:40px;">🧭</div>
          <div>
            <div style="color:#94a3b8; font-size:11px; letter-spacing:0.1em; text-transform:uppercase;">
              Current Market Regime
            </div>
            <div style="color:{rclr}; font-size:28px; font-weight:800; margin-top:4px;">
              {current_regime}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Regime timeline
        st.markdown("##### Regime History")
        regime_num = regimes.map({
            "Bull Market": 4, "Bull/Vol": 3, "Choppy": 2,
            "Correction": 1, "Bear Market": 0, "Unknown": 2
        }).fillna(2)
        fig_reg, ax_reg = plt.subplots(figsize=(11, 2.5))
        ax_reg.fill_between(regime_num.index, regime_num.values,
                            cmap=None, alpha=0.8, color=ACCENT2, step="post")
        ax_reg.plot(regime_num.index, regime_num.values, color="white", lw=0.5)
        ax_reg.set_yticks([0,1,2,3,4])
        ax_reg.set_yticklabels(["Bear","Correction","Choppy","Bull/Vol","Bull"], fontsize=8)
        ax_reg.set_title("Market Regime Timeline")
        ax_reg.grid(True, alpha=0.15)
        plt.tight_layout(); st.pyplot(fig_reg); plt.close()

        # SP500 vs SMA overlaid
        st.markdown("##### S&P 500 vs Moving Averages")
        sp_plot = prices[sp_col].dropna()
        fig_sp, ax_sp = plt.subplots(figsize=(11, 4))
        ax_sp.plot(sp_plot.index, sp_plot.values, color=ACCENT, lw=1.8, label="S&P 500")
        ax_sp.plot(sp_sma20.index, sp_sma20.values, color=YELLOW, lw=1.2, ls="--", label="SMA 20")
        ax_sp.plot(sp_sma60.index, sp_sma60.values, color=RED,    lw=1.2, ls="--", label="SMA 60")
        ax_sp.legend(fontsize=9); ax_sp.grid(True, alpha=0.2)
        ax_sp.set_title("S&P 500 with Trend Signals")
        plt.tight_layout(); st.pyplot(fig_sp); plt.close()

        # Regime stats per asset
        st.markdown("##### Asset Performance by Regime")
        regime_stats = []
        for reg in ["Bull Market", "Choppy", "Bear Market"]:
            dates_in_reg = regimes[regimes == reg].index
            for col in prices.columns[:12]:
                ret_r = prices[col].pct_change().dropna()
                in_reg = ret_r[ret_r.index.isin(dates_in_reg)]
                if len(in_reg) > 5:
                    regime_stats.append({
                        "Asset":  col,
                        "Regime": reg,
                        "Ann. Ret %": annualized_return(in_reg) * 100,
                    })
        if regime_stats:
            rs_df  = pd.DataFrame(regime_stats)
            pivot_r = rs_df.pivot(index="Asset", columns="Regime", values="Ann. Ret %")
            avail_cols = [c for c in ["Bull Market","Choppy","Bear Market"] if c in pivot_r.columns]
            if avail_cols:
                st.dataframe(
                    pivot_r[avail_cols].style.format("{:.1f}%").background_gradient(
                        cmap="RdYlGn", axis=None),
                    use_container_width=True
                )

# ──────────────────────────────────────────────────────────────────────────────
# TAB 9 — YIELD CURVE
# ──────────────────────────────────────────────────────────────────────────────
with tabs[8]:
    st.markdown("#### 📉 US Yield Curve")
    st.caption(
        "Yahoo Finance provides yield proxies via index tickers. "
        "^IRX ≈ 3M/13-week bill, ^FVX ≈ 5Y, ^TNX ≈ 10Y, ^TYX ≈ 30Y."
    )

    YIELD_TICKERS = {
        "3M (^IRX)":  "^IRX",
        "5Y (^FVX)":  "^FVX",
        "10Y (^TNX)": "^TNX",
        "30Y (^TYX)": "^TYX",
    }
    MATURITY_YEARS = [0.25, 5, 10, 30]

    with st.spinner("Loading yield curve data…"):
        yield_snaps = {}
        yield_hist  = {}
        for label, sym in YIELD_TICKERS.items():
            s = load_close_series(sym, period=period)
            if not s.empty:
                yield_snaps[label] = float(s.iloc[-1])
                yield_hist[label]  = s

    if len(yield_snaps) < 2:
        st.warning("Insufficient yield data. Some Yahoo Finance yield tickers may be unavailable.")
    else:
        # Current curve
        maturities = []
        yields_now = []
        for i, (label, mat) in enumerate(zip(YIELD_TICKERS.keys(), MATURITY_YEARS)):
            if label in yield_snaps:
                maturities.append(mat)
                yields_now.append(yield_snaps[label])

        # Historical curves
        hist_df = pd.DataFrame(yield_hist).dropna(how="all")
        hist_df.columns = [c for c in YIELD_TICKERS.keys() if c in yield_hist]

        col_a, col_b = st.columns([1.5, 1])

        with col_a:
            st.markdown("##### Current Yield Curve vs 1M / 3M Ago")
            fig_yc, ax_yc = plt.subplots(figsize=(8, 4))

            # Current
            ax_yc.plot(maturities, yields_now, color=ACCENT, lw=2.5, marker="o",
                       markersize=7, label="Current", zorder=4)

            # 1M ago
            try:
                ago_1m = hist_df.iloc[-22] if len(hist_df) >= 22 else None
                if ago_1m is not None:
                    y_1m = [float(ago_1m[c]) if c in ago_1m.index else np.nan
                            for c in YIELD_TICKERS.keys() if c in yield_hist]
                    mat_1m = [m for c, m in zip(YIELD_TICKERS.keys(), MATURITY_YEARS)
                              if c in yield_hist]
                    ax_yc.plot(mat_1m, y_1m, color=YELLOW, lw=1.5, marker="s",
                               markersize=5, ls="--", label="1M ago", alpha=0.7)
            except Exception:
                pass

            # 3M ago
            try:
                ago_3m = hist_df.iloc[-63] if len(hist_df) >= 63 else None
                if ago_3m is not None:
                    y_3m = [float(ago_3m[c]) if c in ago_3m.index else np.nan
                            for c in YIELD_TICKERS.keys() if c in yield_hist]
                    ax_yc.plot(mat_1m, y_3m, color=RED, lw=1.5, marker="^",
                               markersize=5, ls=":", label="3M ago", alpha=0.6)
            except Exception:
                pass

            ax_yc.set_xlabel("Maturity (years)"); ax_yc.set_ylabel("Yield (%)")
            ax_yc.set_title("US Treasury Yield Curve")
            ax_yc.legend(fontsize=9); ax_yc.grid(True, alpha=0.2)
            ax_yc.set_xticks(maturities)
            ax_yc.set_xticklabels(["3M","5Y","10Y","30Y"])
            plt.tight_layout(); st.pyplot(fig_yc); plt.close()

        with col_b:
            st.markdown("##### Yield Snapshot")
            for label in YIELD_TICKERS.keys():
                if label in yield_snaps:
                    st.metric(label, f"{yield_snaps[label]:.2f}%")

            # Spread
            if "3M (^IRX)" in yield_snaps and "10Y (^TNX)" in yield_snaps:
                spread_10_3 = yield_snaps["10Y (^TNX)"] - yield_snaps["3M (^IRX)"]
                inv = spread_10_3 < 0
                st.metric(
                    "10Y–3M Spread",
                    f"{spread_10_3:.2f}%",
                    delta="⚠️ Inverted" if inv else "Normal"
                )

        # Yield time-series
        st.markdown("##### Yield History")
        if not hist_df.empty:
            sel_yields = st.multiselect(
                "Select maturities", hist_df.columns.tolist(),
                default=hist_df.columns.tolist(), key="yc_sel"
            )
            if sel_yields:
                fig_yh, ax_yh = plt.subplots(figsize=(11, 4))
                for i, col in enumerate(sel_yields):
                    ax_yh.plot(hist_df.index, hist_df[col], label=col, lw=1.8,
                               color=PALETTE[i % len(PALETTE)])
                ax_yh.set_ylabel("Yield (%)")
                ax_yh.set_title("US Treasury Yields — Historical")
                ax_yh.legend(fontsize=9); ax_yh.grid(True, alpha=0.2)
                plt.tight_layout(); st.pyplot(fig_yh); plt.close()

        # 10Y–2Y spread over time
        if "5Y (^FVX)" in hist_df.columns and "10Y (^TNX)" in hist_df.columns:
            st.markdown("##### 10Y – 5Y Spread Over Time")
            spread_ts = hist_df["10Y (^TNX)"] - hist_df["5Y (^FVX)"]
            fig_sp, ax_sp = plt.subplots(figsize=(11, 3))
            ax_sp.plot(spread_ts.index, spread_ts.values, color=ACCENT2, lw=1.8)
            ax_sp.fill_between(spread_ts.index, spread_ts.values, 0,
                               where=spread_ts.values >= 0, alpha=0.12, color=GREEN)
            ax_sp.fill_between(spread_ts.index, spread_ts.values, 0,
                               where=spread_ts.values < 0, alpha=0.15, color=RED)
            ax_sp.axhline(0, color="white", lw=0.8, ls="--")
            ax_sp.set_title("10Y – 5Y Spread (negative = curve inversion)")
            ax_sp.grid(True, alpha=0.2)
            plt.tight_layout(); st.pyplot(fig_sp); plt.close()

st.markdown("---")
st.caption(
    "QuantDesk Pro · Macro Dashboard · Data via yfinance · "
    "For educational & research purposes only — not financial advice."
)