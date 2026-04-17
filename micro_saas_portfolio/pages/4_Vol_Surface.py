import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

from auth import require_login, sidebar_user_widget
from utils import apply_theme, page_header, ACCENT, ACCENT2, GREEN, RED, YELLOW
from data_loader import load_option_expiries, load_option_chain, load_price_history, load_spot_price

st.set_page_config(page_title="Vol Surface", layout="wide", page_icon="📊")
apply_theme()
page_header("Volatility Surface", "Smile · Term Structure · Heatmap · 3D Surface")

def _set_load_vol_clicked():
    st.session_state["load_vol_clicked"] = True

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Inputs")
smile_ticker    = st.sidebar.text_input("Ticker", "AAPL")
min_oi          = st.sidebar.number_input("Min open interest", 0, 10000, 10, 5)
min_vol         = st.sidebar.number_input("Min volume",        0, 10000, 1,  1)
moneyness_band  = st.sidebar.slider("Moneyness band (±%)", 5, 60, 25, 5)
max_expiries    = st.sidebar.slider("Max expiries to load", 2, 8, 4, 1)
option_side     = st.sidebar.selectbox("Option side", ["calls", "puts"])
load_btn        = st.sidebar.button("Load Vol Data", use_container_width=True, on_click=_set_load_vol_clicked)

if not st.session_state.get("load_vol_clicked", False):
    st.info("Enter a ticker in the sidebar and click **Load Vol Data**.")
    st.stop()

# ── Load spot & expiries ──────────────────────────────────────────────────────
ticker = smile_ticker.upper()

with st.spinner(f"Loading data for {ticker}…"):
    spot_df  = load_price_history(ticker, period="5d", source="auto")
    expiries = load_option_expiries(ticker)

if spot_df.empty:
    st.error(f"No price data for **{ticker}**.")
    st.stop()
if not expiries:
    st.warning(f"No options data available for **{ticker}**.")
    st.stop()

spot = float(spot_df["Close"].iloc[-1])
band_lo = spot * (1 - moneyness_band / 100)
band_hi = spot * (1 + moneyness_band / 100)
exps    = expiries[:max_expiries]

st.markdown(f"### {ticker} &nbsp; — &nbsp; Spot: **${spot:.2f}** &nbsp; | &nbsp; {len(expiries)} expiries available")

# ── Helper to clean chain ─────────────────────────────────────────────────────
def clean_chain(chain_dict: dict, side: str, spot: float,
                min_vol: int, min_oi: int, band_lo: float, band_hi: float):
    df = chain_dict[side].copy()
    required = {"strike", "impliedVolatility", "volume", "openInterest"}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    df = df.dropna(subset=list(required))
    df = df[
        (df["impliedVolatility"] > 0) &
        (df["volume"]           >= min_vol) &
        (df["openInterest"]     >= min_oi) &
        (df["strike"].between(band_lo, band_hi))
    ].copy()
    df["moneyness"] = df["strike"] / spot
    df["iv_pct"]    = df["impliedVolatility"] * 100
    return df


# ── Volatility Smile ──────────────────────────────────────────────────────────
st.markdown("### Volatility Smile by Expiry")

n_cols = min(len(exps), 4)
fig, axes = plt.subplots(1, n_cols, figsize=(4 * n_cols, 4), sharey=True)
if n_cols == 1:
    axes = [axes]

smile_data = {}
for idx, exp in enumerate(exps[:4]):
    chain = load_option_chain(ticker, exp)
    df    = clean_chain(chain, option_side, spot, min_vol, min_oi, band_lo, band_hi)
    smile_data[exp] = df
    ax = axes[idx]

    if df.empty:
        ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center",
                transform=ax.transAxes, color="white", fontsize=9)
        ax.set_title(exp, fontsize=9)
        continue

    ax.scatter(df["moneyness"], df["iv_pct"], color=ACCENT, s=22, alpha=0.75, zorder=3)
    if len(df) > 3:
        z  = np.polyfit(df["moneyness"], df["iv_pct"], 2)
        p  = np.poly1d(z)
        xs = np.linspace(df["moneyness"].min(), df["moneyness"].max(), 120)
        ax.plot(xs, p(xs), color=ACCENT2, lw=1.8)

    ax.axvline(1.0, color=YELLOW, ls="--", lw=1, label="ATM")
    ax.set_title(exp, fontsize=9)
    ax.set_xlabel("K / S", fontsize=8)
    if idx == 0:
        ax.set_ylabel("IV (%)")
    ax.grid(True, alpha=0.3)

plt.suptitle(f"{ticker} — Volatility Smile ({option_side.capitalize()})", y=1.01, fontsize=12)
plt.tight_layout()
st.pyplot(fig); plt.close()

# ── ATM IV Term Structure ─────────────────────────────────────────────────────
st.markdown("### ATM IV Term Structure")
atm_ivs = []
for exp in expiries[:8]:
    chain = load_option_chain(ticker, exp)
    df    = clean_chain(chain, option_side, spot, min_vol, min_oi,
                        spot * 0.7, spot * 1.3)  # wider band for ATM search
    if df.empty:
        continue
    atm_row = df.iloc[(df["strike"] - spot).abs().argsort()[:1]]
    atm_ivs.append({
        "expiry":    exp,
        "iv":        float(atm_row["iv_pct"].values[0]),
        "atm_strike": float(atm_row["strike"].values[0]),
    })

if atm_ivs:
    df_ts = pd.DataFrame(atm_ivs)
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    x = range(len(df_ts))
    ax2.plot(x, df_ts["iv"], color=ACCENT, marker="o", lw=2, markersize=7, zorder=3)
    ax2.fill_between(x, df_ts["iv"], alpha=0.12, color=ACCENT)
    for i, row in df_ts.iterrows():
        ax2.annotate(f"{row['iv']:.1f}%", (i, row["iv"]),
                     textcoords="offset points", xytext=(0, 8),
                     ha="center", fontsize=8, color="white")
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_ts["expiry"], rotation=30, ha="right", fontsize=8)
    ax2.set_ylabel("ATM IV (%)")
    ax2.set_title(f"{ticker} ATM Implied Volatility Term Structure")
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2); plt.close()

    # Term structure table
    with st.expander("Term Structure Data"):
        st.dataframe(
            df_ts.style.format({"iv": "{:.2f}%", "atm_strike": "${:.2f}"}),
            use_container_width=True,
        )
else:
    st.warning("Not enough data to build the term structure.")

# ── IV Heatmap ────────────────────────────────────────────────────────────────
st.markdown("### IV Heatmap (Strike × Expiry)")

surface_data = []
for exp in exps:
    chain = load_option_chain(ticker, exp)
    df    = clean_chain(chain, option_side, spot, min_vol, min_oi, band_lo, band_hi)
    if df.empty:
        continue
    for _, row in df.iterrows():
        surface_data.append({
            "expiry": exp,
            "strike": row["strike"],
            "iv":     row["iv_pct"],
        })

if surface_data:
    sdf   = pd.DataFrame(surface_data)
    pivot = sdf.pivot_table(index="expiry", columns="strike", values="iv", aggfunc="mean")
    pivot = pivot.sort_index(axis=0).sort_index(axis=1)
    pivot = pivot.dropna(axis=1, thresh=max(1, int(len(pivot) * 0.4)))

    if not pivot.empty:
        fig3, ax3 = plt.subplots(figsize=(12, max(3, len(pivot) * 0.8)))
        im = ax3.imshow(pivot.values, aspect="auto", cmap="plasma", interpolation="nearest")
        ax3.set_xticks(range(len(pivot.columns)))
        ax3.set_xticklabels(
            [f"${x:.0f}" for x in pivot.columns], rotation=45, ha="right", fontsize=7
        )
        ax3.set_yticks(range(len(pivot.index)))
        ax3.set_yticklabels(pivot.index, fontsize=8)

        # Annotate cells
        for i in range(pivot.values.shape[0]):
            for j in range(pivot.values.shape[1]):
                val = pivot.values[i, j]
                if not np.isnan(val):
                    ax3.text(j, i, f"{val:.0f}", ha="center", va="center",
                             fontsize=6, color="white", alpha=0.8)

        plt.colorbar(im, ax=ax3, label="IV (%)")
        ax3.set_xlabel("Strike"); ax3.set_ylabel("Expiry")
        ax3.set_title(f"{ticker} IV Heatmap")
        st.pyplot(fig3); plt.close()

        # ── 3D Surface ────────────────────────────────────────────────────────
        st.markdown("### 3D Implied Volatility Surface")
        pivot_3d = pivot.dropna(axis=1, thresh=max(1, int(len(pivot) * 0.5)))
        if not pivot_3d.empty and pivot_3d.shape[1] >= 3:
            strikes    = pivot_3d.columns.values.astype(float)
            expiry_idx = np.arange(len(pivot_3d))
            SG, EG     = np.meshgrid(strikes, expiry_idx)
            IVG        = pivot_3d.values

            fig4 = plt.figure(figsize=(11, 6))
            ax4  = fig4.add_subplot(111, projection="3d")
            surf = ax4.plot_surface(SG, EG, IVG, cmap="plasma", alpha=0.88, edgecolor="none")
            fig4.colorbar(surf, ax=ax4, shrink=0.5, label="IV (%)")
            ax4.set_xlabel("Strike ($)")
            ax4.set_ylabel("Expiry Index")
            ax4.set_zlabel("IV (%)")
            ax4.set_yticks(expiry_idx)
            ax4.set_yticklabels(pivot_3d.index, fontsize=7)
            ax4.set_title(f"{ticker} Implied Volatility Surface")
            st.pyplot(fig4); plt.close()
        else:
            st.info("Need at least 3 strikes per expiry to render the 3D surface.")
else:
    st.warning("No vol surface data available with the current filters. Try lowering the minimum OI/volume thresholds.")

# ── Put/Call IV Skew ──────────────────────────────────────────────────────────
if exps:
    st.markdown("### Put vs Call IV Skew (first expiry)")
    exp0    = exps[0]
    chain0  = load_option_chain(ticker, exp0)
    calls_0 = clean_chain(chain0, "calls", spot, 0, 0, band_lo, band_hi)
    puts_0  = clean_chain(chain0, "puts",  spot, 0, 0, band_lo, band_hi)

    if not calls_0.empty and not puts_0.empty:
        fig5, ax5 = plt.subplots(figsize=(10, 4))
        ax5.scatter(calls_0["moneyness"], calls_0["iv_pct"],
                    color=GREEN, s=22, alpha=0.75, label="Calls", zorder=3)
        ax5.scatter(puts_0["moneyness"],  puts_0["iv_pct"],
                    color=RED,   s=22, alpha=0.75, label="Puts",  zorder=3)
        ax5.axvline(1.0, color=YELLOW, ls="--", lw=1, label="ATM")
        ax5.set_xlabel("Moneyness (K/S)"); ax5.set_ylabel("IV (%)")
        ax5.set_title(f"{ticker} — Put vs Call IV Skew ({exp0})")
        ax5.legend(); ax5.grid(True, alpha=0.3)
        st.pyplot(fig5); plt.close()
