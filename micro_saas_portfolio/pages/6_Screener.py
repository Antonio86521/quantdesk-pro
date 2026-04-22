import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from auth import require_login, sidebar_user_widget
from utils import (
    apply_theme, apply_responsive_layout, page_header,
    PALETTE, ACCENT, ACCENT2, GREEN, RED, AMBER, MUTED, TEXT2, BG3, BORDER,
    app_footer,
    section_header,)
from data_loader import load_close_series, load_price_history
from analytics import annualized_return, annualized_vol, rsi, sma, historical_var, max_drawdown_from_returns

st.set_page_config(page_title="Screener — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Screener & Watchlist", "Multi-ticker snapshot · Signals · Momentum")
sidebar_user_widget()


def _set_clicked():
    st.session_state["run_screener_clicked"] = True



# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Screener Inputs")
default_tickers = "AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,SPY,QQQ,BRK-B"
tickers_input   = st.sidebar.text_area("Tickers (one per line or comma-separated)",
                                        value=default_tickers, height=160)
period  = st.sidebar.selectbox("Lookback period", ["1mo","3mo","6mo","1y"], index=2)
rsi_ob  = st.sidebar.slider("RSI overbought", 60, 90, 70, 5)
rsi_os  = st.sidebar.slider("RSI oversold",   10, 40, 30, 5)
st.sidebar.button("Run Screener", use_container_width=True, on_click=_set_clicked)

if not st.session_state.get("run_screener_clicked", False):
    st.markdown(
        f'<div style="background:{BG3};border:1px solid {BORDER};border-radius:10px;'
        f'padding:22px;text-align:center;margin:10px 0;">'
        f'<div style="font-size:24px;margin-bottom:10px;">🔍</div>'
        f'<div style="font-size:13px;font-weight:600;margin-bottom:5px;">Stock Screener</div>'
        f'<div style="font-size:12px;color:{TEXT2};">Enter tickers in the sidebar and click <strong>Run Screener</strong>.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.stop()

raw     = tickers_input.replace("\n", ",")
tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
if not tickers:
    st.error("Enter at least one ticker."); st.stop()

# ── Fetch ──────────────────────────────────────────────────────────────────────
records = []
failed  = []
progress = st.progress(0, text="Fetching data…")
for i, t in enumerate(tickers):
    progress.progress((i + 1) / len(tickers), text=f"Loading {t}…")
    try:
        close   = load_close_series(t, period=period, source="auto")
        df_full = load_price_history(t, period=period, source="auto")
        if close.empty or len(close) < 15:
            failed.append(t); continue

        ret    = close.pct_change().dropna()
        ann_r  = annualized_return(ret)
        ann_v  = annualized_vol(ret)
        sharpe = (ann_r - 0.02) / ann_v if ann_v > 0 else np.nan
        max_dd, _ = max_drawdown_from_returns(ret)
        var95  = historical_var(ret, 0.95)

        rsi_val = float(rsi(close, 14).iloc[-1]) if len(close) >= 15 else np.nan
        sma20   = float(sma(close, 20).iloc[-1]) if len(close) >= 20 else np.nan
        sma50   = float(sma(close, 50).iloc[-1]) if len(close) >= 50 else np.nan
        price   = float(close.iloc[-1])
        prev    = float(close.iloc[-2]) if len(close) >= 2 else price
        chg_pct = (price - prev) / prev * 100

        close_1y = load_close_series(t, period="1y", source="auto")
        high52   = float(close_1y.max()) if not close_1y.empty else np.nan
        low52    = float(close_1y.min()) if not close_1y.empty else np.nan
        pct_off_high = (price - high52) / high52 * 100 if not np.isnan(high52) else np.nan

        avg_vol  = float(df_full["Volume"].mean()) if "Volume" in df_full.columns else np.nan
        last_vol = float(df_full["Volume"].iloc[-1]) if "Volume" in df_full.columns else np.nan
        vol_ratio = last_vol / avg_vol if avg_vol > 0 and not np.isnan(last_vol) else np.nan

        if not np.isnan(rsi_val):
            if rsi_val >= rsi_ob:
                signal = "🔴 Overbought"
            elif rsi_val <= rsi_os:
                signal = "🟢 Oversold"
            elif not np.isnan(sma20) and not np.isnan(sma50):
                if price > sma20 > sma50:   signal = "📈 Uptrend"
                elif price < sma20 < sma50: signal = "📉 Downtrend"
                else:                        signal = "➡️ Neutral"
            else:
                signal = "—"
        else:
            signal = "—"

        records.append({
            "Ticker":       t, "Price": price,
            "1D Chg %":     chg_pct, "Ann. Return %": ann_r * 100,
            "Ann. Vol %":   ann_v * 100, "Sharpe":    sharpe,
            "Max DD %":     max_dd * 100, "VaR 95%":  var95 * 100,
            "RSI (14)":     rsi_val, "vs SMA20":       (price - sma20) / sma20 * 100 if not np.isnan(sma20) else np.nan,
            "% off 52W Hi": pct_off_high, "Vol Ratio": vol_ratio,
            "Signal":       signal,
        })
    except Exception:
        failed.append(t)

progress.empty()
if failed:
    st.warning(f"Could not load: {', '.join(failed)}")
if not records:
    st.error("No data loaded."); st.stop()

df = pd.DataFrame(records)

# ── SNAPSHOT CARDS ────────────────────────────────────────────────────────────
section_header("Market Snapshot")
n_up   = (df["1D Chg %"] > 0).sum()
n_down = (df["1D Chg %"] < 0).sum()

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Tickers Loaded",  f"{len(df)}")
c2.metric("Up Today",        f"{n_up}", delta=f"{n_up - n_down:+d}")
c3.metric("Average RSI",     f"{df['RSI (14)'].mean():.1f}")
c4.metric("Overbought",      f"{(df['RSI (14)'] >= rsi_ob).sum()}")
c5.metric("Oversold",        f"{(df['RSI (14)'] <= rsi_os).sum()}")

# ── SCREENER TABLE ────────────────────────────────────────────────────────────
section_header("Screener Table")

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
    out = []
    for col in row.index:
        if col == "1D Chg %":
            out.append(f"color: {'#0ecb81' if row[col] >= 0 else '#f6465d'}")
        elif col == "RSI (14)":
            if row[col] >= rsi_ob:     out.append("color: #f6465d")
            elif row[col] <= rsi_os:   out.append("color: #0ecb81")
            else:                       out.append("")
        elif col == "Ann. Return %":
            out.append(f"color: {'#0ecb81' if row[col] >= 0 else '#f6465d'}")
        else:
            out.append("")
    return out

st.dataframe(
    df.style.format(fmt).apply(highlight_signal, axis=1),
    use_container_width=True, height=420,
)

# ── CHARTS ────────────────────────────────────────────────────────────────────
section_header("Visual Comparison")
tab1, tab2, tab3 = st.tabs(["Returns & Sharpe", "RSI Heatmap", "Price History"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        fig, ax = plt.subplots(figsize=(8, 4))
        clrs = [GREEN if v >= 0 else RED for v in df["Ann. Return %"]]
        ax.bar(df["Ticker"], df["Ann. Return %"], color=clrs, edgecolor="#0d1117", linewidth=1)
        ax.axhline(0, color="white", lw=0.8, ls="--")
        ax.set_title("Annualised Return (%)"); ax.grid(True, alpha=0.25, axis="y")
        st.pyplot(fig); plt.close()
    with col_b:
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        sv = df["Sharpe"].fillna(0)
        clrs_s = [GREEN if v >= 1 else (AMBER if v >= 0 else RED) for v in sv]
        ax2.bar(df["Ticker"], sv, color=clrs_s, edgecolor="#0d1117", linewidth=1)
        ax2.axhline(1, color=GREEN, lw=0.8, ls="--", label="Sharpe=1")
        ax2.axhline(0, color="white", lw=0.6, ls=":")
        ax2.set_title("Sharpe Ratio"); ax2.legend(fontsize=8); ax2.grid(True, alpha=0.25, axis="y")
        st.pyplot(fig2); plt.close()

with tab2:
    rsi_vals = df[["Ticker","RSI (14)"]].set_index("Ticker")
    fig3, ax3 = plt.subplots(figsize=(max(6, len(df) * 0.6), 2.5))
    cmap_rsi = mcolors.LinearSegmentedColormap.from_list("rsi", [GREEN, AMBER, RED])
    im = ax3.imshow(rsi_vals.T.values, cmap=cmap_rsi, vmin=0, vmax=100, aspect="auto")
    ax3.set_xticks(range(len(df))); ax3.set_xticklabels(df["Ticker"], rotation=45, ha="right")
    ax3.set_yticks([0]); ax3.set_yticklabels(["RSI"])
    for j, val in enumerate(rsi_vals["RSI (14)"].values):
        ax3.text(j, 0, f"{val:.0f}", ha="center", va="center", color="black", fontsize=9, fontweight="bold")
    plt.colorbar(im, ax=ax3, label="RSI"); ax3.set_title("RSI Heatmap")
    st.pyplot(fig3); plt.close()

with tab3:
    selected = st.multiselect("Select tickers to compare", df["Ticker"].tolist(),
                               default=df["Ticker"].tolist()[:4])
    if selected:
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        for i, t in enumerate(selected):
            s = load_close_series(t, period=period, source="auto")
            if not s.empty:
                ax4.plot(s.index, s / s.iloc[0], color=PALETTE[i % len(PALETTE)], label=t, lw=1.8)
        ax4.set_title("Normalised Price Performance")
        ax4.axhline(1, color="white", lw=0.6, ls="--")
        ax4.legend(fontsize=8); ax4.grid(True, alpha=0.25)
        st.pyplot(fig4); plt.close()

# ── SIGNAL SUMMARY ────────────────────────────────────────────────────────────
section_header("Signal Summary")
for signal, count in df["Signal"].value_counts().items():
    tickers_w = df[df["Signal"] == signal]["Ticker"].tolist()
    st.markdown(f"{signal}: **{', '.join(tickers_w)}**")

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download Screener CSV", csv, "screener.csv", "text/csv")

app_footer()
