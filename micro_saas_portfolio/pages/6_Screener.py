import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from auth import require_login, sidebar_user_widget
from utils import apply_theme, page_header, PALETTE, ACCENT, ACCENT2, GREEN, RED, YELLOW, MUTED
from data_loader import load_close_series, load_price_history
from analytics import (
    annualized_return, annualized_vol, rsi, sma,
    historical_var, max_drawdown_from_returns,
)

st.set_page_config(page_title="Screener & Watchlist", layout="wide", page_icon="📊")
apply_theme()
require_login()
sidebar_user_widget()
page_header("Screener & Watchlist", "Multi-ticker snapshot · Signals · Momentum")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Screener Inputs")
default_tickers = "AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,SPY,QQQ,BRK-B"
tickers_input   = st.sidebar.text_area("Tickers (one per line or comma-separated)",
                                        value=default_tickers, height=160)
period          = st.sidebar.selectbox("Lookback period", ["1mo", "3mo", "6mo", "1y"], index=2)
rsi_ob          = st.sidebar.slider("RSI overbought threshold", 60, 90, 70, 5)
rsi_os          = st.sidebar.slider("RSI oversold threshold",  10, 40, 30, 5)
run_screen      = st.sidebar.button("Run Screener", use_container_width=True)

if not run_screen:
    st.info("Enter tickers in the sidebar and click **Run Screener**.")
    st.stop()

# ── Parse tickers ─────────────────────────────────────────────────────────────
raw = tickers_input.replace("\n", ",")
tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
if not tickers:
    st.error("Enter at least one ticker.")
    st.stop()

# ── Fetch data ────────────────────────────────────────────────────────────────
records = []
failed  = []

progress = st.progress(0, text="Fetching data…")
for i, t in enumerate(tickers):
    progress.progress((i + 1) / len(tickers), text=f"Loading {t}…")
    try:
        close = load_close_series(t, period=period)
        df_full = load_price_history(t, period=period)
        if close.empty or len(close) < 15:
            failed.append(t)
            continue

        ret   = close.pct_change().dropna()
        ann_r = annualized_return(ret)
        ann_v = annualized_vol(ret)
        sharpe = (ann_r - 0.02) / ann_v if ann_v > 0 else np.nan
        max_dd, _ = max_drawdown_from_returns(ret)
        var95   = historical_var(ret, 0.95)

        rsi_val = float(rsi(close, 14).iloc[-1]) if len(close) >= 15 else np.nan
        sma20   = float(sma(close, 20).iloc[-1]) if len(close) >= 20 else np.nan
        sma50   = float(sma(close, 50).iloc[-1]) if len(close) >= 50 else np.nan
        price   = float(close.iloc[-1])
        prev    = float(close.iloc[-2]) if len(close) >= 2 else price
        chg_pct = (price - prev) / prev * 100

        # 52-week high/low (use all available data)
        close_1y = load_close_series(t, period="1y")
        high52  = float(close_1y.max()) if not close_1y.empty else np.nan
        low52   = float(close_1y.min()) if not close_1y.empty else np.nan
        pct_off_high = (price - high52) / high52 * 100 if not np.isnan(high52) else np.nan

        # Volume (if available)
        avg_vol = float(df_full["Volume"].mean()) if "Volume" in df_full.columns else np.nan
        last_vol = float(df_full["Volume"].iloc[-1]) if "Volume" in df_full.columns else np.nan
        vol_ratio = last_vol / avg_vol if avg_vol > 0 and not np.isnan(last_vol) else np.nan

        # Signal
        signal = "—"
        if not np.isnan(rsi_val):
            if rsi_val >= rsi_ob:
                signal = "🔴 Overbought"
            elif rsi_val <= rsi_os:
                signal = "🟢 Oversold"
            elif not np.isnan(sma20) and not np.isnan(sma50):
                if price > sma20 > sma50:
                    signal = "📈 Uptrend"
                elif price < sma20 < sma50:
                    signal = "📉 Downtrend"
                else:
                    signal = "➡️ Neutral"

        records.append({
            "Ticker":      t,
            "Price":       price,
            "1D Chg %":    chg_pct,
            "Ann. Return %": ann_r * 100,
            "Ann. Vol %":  ann_v * 100,
            "Sharpe":      sharpe,
            "Max DD %":    max_dd * 100,
            "VaR 95%":     var95 * 100,
            "RSI (14)":    rsi_val,
            "vs SMA20":    (price - sma20) / sma20 * 100 if not np.isnan(sma20) else np.nan,
            "% off 52W Hi": pct_off_high,
            "Vol Ratio":   vol_ratio,
            "Signal":      signal,
        })
    except Exception:
        failed.append(t)

progress.empty()

if failed:
    st.warning(f"Could not load: {', '.join(failed)}")
if not records:
    st.error("No data loaded.")
    st.stop()

df = pd.DataFrame(records)

# ── Summary Cards ─────────────────────────────────────────────────────────────
st.markdown("### Market Snapshot")
n_up   = (df["1D Chg %"] > 0).sum()
n_down = (df["1D Chg %"] < 0).sum()
avg_rsi = df["RSI (14)"].mean()
overbought = (df["RSI (14)"] >= rsi_ob).sum()
oversold   = (df["RSI (14)"] <= rsi_os).sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Tickers Loaded",  f"{len(df)}")
c2.metric("Up Today",        f"{n_up}", delta=f"{n_up - n_down}")
c3.metric("Average RSI",     f"{avg_rsi:.1f}")
c4.metric("Overbought",      f"{overbought}")
c5.metric("Oversold",        f"{oversold}")

# ── Main Table ────────────────────────────────────────────────────────────────
st.markdown("### Screener Table")

fmt = {
    "Price":          "${:.2f}",
    "1D Chg %":       "{:.2f}%",
    "Ann. Return %":  "{:.1f}%",
    "Ann. Vol %":     "{:.1f}%",
    "Sharpe":         "{:.2f}",
    "Max DD %":       "{:.1f}%",
    "VaR 95%":        "{:.2f}%",
    "RSI (14)":       "{:.1f}",
    "vs SMA20":       "{:.2f}%",
    "% off 52W Hi":   "{:.1f}%",
    "Vol Ratio":      "{:.2f}",
}

def highlight_signal(row):
    colors = []
    for col in row.index:
        if col == "1D Chg %":
            colors.append(f"color: {'#00e676' if row[col] >= 0 else '#ff1744'}")
        elif col == "RSI (14)":
            if row[col] >= rsi_ob:
                colors.append("color: #ff1744")
            elif row[col] <= rsi_os:
                colors.append("color: #00e676")
            else:
                colors.append("")
        elif col == "Ann. Return %":
            colors.append(f"color: {'#00e676' if row[col] >= 0 else '#ff1744'}")
        else:
            colors.append("")
    return colors

st.dataframe(
    df.style.format(fmt).apply(highlight_signal, axis=1),
    use_container_width=True,
    height=420,
)

# ── Charts ────────────────────────────────────────────────────────────────────
st.markdown("### Visual Comparison")

tab1, tab2, tab3 = st.tabs(["Returns & Sharpe", "RSI Heatmap", "Price History"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        fig, ax = plt.subplots(figsize=(8, 4))
        colors_bar = [GREEN if v >= 0 else RED for v in df["Ann. Return %"]]
        bars = ax.bar(df["Ticker"], df["Ann. Return %"], color=colors_bar,
                      edgecolor="#0a0e1a", linewidth=1)
        ax.axhline(0, color="white", lw=0.8, ls="--")
        ax.set_title("Annualised Return (%)"); ax.grid(True, alpha=0.3, axis="y")
        st.pyplot(fig); plt.close()

    with col_b:
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        sharpe_vals = df["Sharpe"].fillna(0)
        colors_sh = [GREEN if v >= 1 else (YELLOW if v >= 0 else RED) for v in sharpe_vals]
        bars2 = ax2.bar(df["Ticker"], sharpe_vals, color=colors_sh,
                        edgecolor="#0a0e1a", linewidth=1)
        ax2.axhline(1, color=GREEN, lw=0.8, ls="--", label="Sharpe=1")
        ax2.axhline(0, color="white", lw=0.6, ls=":")
        ax2.set_title("Sharpe Ratio"); ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3, axis="y")
        st.pyplot(fig2); plt.close()

with tab2:
    rsi_vals = df[["Ticker", "RSI (14)"]].set_index("Ticker")
    fig3, ax3 = plt.subplots(figsize=(max(6, len(df) * 0.6), 2.5))
    import matplotlib.colors as mcolors
    cmap_rsi = mcolors.LinearSegmentedColormap.from_list("rsi", [GREEN, YELLOW, RED])
    im = ax3.imshow(rsi_vals.T.values, cmap=cmap_rsi, vmin=0, vmax=100, aspect="auto")
    ax3.set_xticks(range(len(df))); ax3.set_xticklabels(df["Ticker"], rotation=45, ha="right")
    ax3.set_yticks([0]); ax3.set_yticklabels(["RSI"])
    for j, val in enumerate(rsi_vals["RSI (14)"].values):
        ax3.text(j, 0, f"{val:.0f}", ha="center", va="center", color="black",
                 fontsize=9, fontweight="bold")
    plt.colorbar(im, ax=ax3, label="RSI")
    ax3.set_title("RSI Heatmap")
    st.pyplot(fig3); plt.close()

with tab3:
    selected = st.multiselect("Select tickers to compare", df["Ticker"].tolist(),
                               default=df["Ticker"].tolist()[:4])
    if selected:
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        for i, t in enumerate(selected):
            s = load_close_series(t, period=period)
            if not s.empty:
                norm = s / s.iloc[0]
                ax4.plot(norm.index, norm.values, color=PALETTE[i % len(PALETTE)],
                         label=t, lw=1.8)
        ax4.set_title("Normalised Price Performance")
        ax4.axhline(1, color="white", lw=0.6, ls="--")
        ax4.legend(fontsize=8); ax4.grid(True, alpha=0.3)
        st.pyplot(fig4); plt.close()

# ── Signal Summary ────────────────────────────────────────────────────────────
st.markdown("### Signal Summary")
signal_counts = df["Signal"].value_counts()
for signal, count in signal_counts.items():
    tickers_with = df[df["Signal"] == signal]["Ticker"].tolist()
    st.markdown(f"{signal}: **{', '.join(tickers_with)}**")

# ── Export ────────────────────────────────────────────────────────────────────
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download Screener CSV", csv, "screener.csv", "text/csv")
