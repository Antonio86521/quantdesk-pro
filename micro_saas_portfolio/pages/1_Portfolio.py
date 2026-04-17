import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from auth import require_login, sidebar_user_widget
from utils import apply_theme, page_header, PALETTE, ACCENT, ACCENT2, GREEN, RED, YELLOW
from data_loader import load_close_series, load_price_history, load_news
from analytics import (
    annualized_return, annualized_vol, max_drawdown_from_returns,
    sortino_ratio, calmar_ratio, omega_ratio, gain_to_pain,
    return_skew, return_kurtosis,
    historical_var, cvar, parametric_var,
    compute_alpha_beta, tracking_stats,
    covariance_matrix, marginal_vol_contribution,
    sma, ema, rsi, macd, bollinger_bands, atr, obv,
)

st.set_page_config(page_title="Portfolio", layout="wide", page_icon="📊")
apply_theme()
require_login()
sidebar_user_widget()
page_header("Portfolio Analytics", "Performance · Attribution · Technicals")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Portfolio Inputs")
tickers_input    = st.sidebar.text_input("Tickers (comma-separated)", "AAPL,MSFT,SPY")
shares_input     = st.sidebar.text_input("Shares (comma-separated)", "2,1,3")
buy_prices_input = st.sidebar.text_input("Buy prices (comma-separated)", "180,350,500")
period           = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
risk_free_rate   = st.sidebar.number_input("Risk-free rate (%)", 0.0, 15.0, 2.0, 0.1)
benchmark_ticker = st.sidebar.selectbox("Benchmark", ["SPY", "QQQ", "DIA", "IWM"])
run_page         = st.sidebar.button("Analyze Portfolio", use_container_width=True)

if not run_page:
    st.info("Fill in the sidebar and click **Analyze Portfolio** to begin.")
    st.stop()

# ── Parse inputs ──────────────────────────────────────────────────────────────
try:
    tickers    = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    shares     = [float(x.strip()) for x in shares_input.split(",") if x.strip()]
    buy_prices = [float(x.strip()) for x in buy_prices_input.split(",") if x.strip()]
except ValueError:
    st.error("Could not parse inputs. Check that shares and buy prices are numbers.")
    st.stop()

if len(tickers) != len(shares) or len(tickers) != len(buy_prices):
    st.error("Tickers, shares, and buy prices must have the same number of entries.")
    st.stop()
if any(s <= 0 for s in shares) or any(p <= 0 for p in buy_prices):
    st.error("Shares and buy prices must all be positive.")
    st.stop()
if len(tickers) == 0:
    st.error("Enter at least one ticker.")
    st.stop()

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading market data…"):
    prices = pd.DataFrame()
    for t in tickers:
        s = load_close_series(t, period=period)
        if s.empty:
            st.error(f"No price data found for **{t}**. Check the ticker symbol.")
            st.stop()
        prices[t] = s
    prices = prices.dropna()
    if prices.empty:
        st.error("No aligned price data across the selected tickers.")
        st.stop()

    bench_series = load_close_series(benchmark_ticker, period=period).reindex(prices.index).dropna()

# ── Computations ──────────────────────────────────────────────────────────────
latest  = prices.iloc[-1]
sh      = np.array(shares)
bp      = np.array(buy_prices)

pos_val      = latest.values * sh
cost         = bp * sh
upnl         = pos_val - cost
upnl_pct     = upnl / cost
total_val    = pos_val.sum()
total_cost   = cost.sum()
total_upnl   = upnl.sum()
total_upnl_p = total_upnl / total_cost
weights      = pos_val / total_val

ret        = prices.pct_change().dropna()
port_ret   = ret.dot(weights)
total_ret  = (1 + port_ret).prod() - 1
ann_ret    = annualized_return(port_ret)
ann_vol    = annualized_vol(port_ret)
rf         = risk_free_rate / 100
sharpe     = (ann_ret - rf) / ann_vol if ann_vol != 0 else np.nan
max_dd, drawdown = max_drawdown_from_returns(port_ret)
sortino    = sortino_ratio(ann_ret, rf, port_ret)
calmar     = calmar_ratio(ann_ret, max_dd)
omega      = omega_ratio(port_ret)
gtp        = gain_to_pain(port_ret)
sk         = return_skew(port_ret)
kurt       = return_kurtosis(port_ret)

hist_var95   = historical_var(port_ret, 0.95)
hist_cvar95  = cvar(port_ret, hist_var95)
param_var95  = parametric_var(port_ret, 0.95)
var99        = historical_var(port_ret, 0.99)
cvar99       = cvar(port_ret, var99)

bench_ret_s = bench_series.pct_change().dropna()
alpha_ann, beta, r2, aligned = compute_alpha_beta(port_ret, bench_ret_s)
tracking_error, info_ratio = tracking_stats(aligned)

asset_total_returns = (prices.iloc[-1] / prices.iloc[0]) - 1
contribution_return  = weights * asset_total_returns.reindex(tickers).values

cov_ann  = covariance_matrix(ret)
vol_contrib = marginal_vol_contribution(weights, cov_ann.values)

norm_port  = (prices * sh).sum(axis=1)
norm_port  = norm_port / norm_port.iloc[0]
norm_bench = bench_series / bench_series.iloc[0]

# ── Overview metrics ──────────────────────────────────────────────────────────
st.markdown("### Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio Value",   f"${total_val:,.2f}")
c2.metric("Invested Capital",  f"${total_cost:,.2f}")
c3.metric("Unrealized P&L",    f"${total_upnl:,.2f}")
c4.metric("Unrealized P&L %",  f"{total_upnl_p*100:.2f}%")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Total Return",   f"{total_ret*100:.2f}%")
c6.metric("Ann. Return",    f"{ann_ret*100:.2f}%")
c7.metric("Ann. Volatility",f"{ann_vol*100:.2f}%")
c8.metric("Sharpe Ratio",   f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A")

c9, c10, c11, c12 = st.columns(4)
c9.metric("Sortino",          f"{sortino:.2f}"    if not np.isnan(sortino)    else "N/A")
c10.metric("Calmar",          f"{calmar:.2f}"     if not np.isnan(calmar)     else "N/A")
c11.metric("Max Drawdown",    f"{max_dd*100:.2f}%")
c12.metric("Info. Ratio",     f"{info_ratio:.2f}" if not np.isnan(info_ratio) else "N/A")

c13, c14, c15, c16 = st.columns(4)
c13.metric("Beta",            f"{beta:.2f}"       if not np.isnan(beta)       else "N/A")
c14.metric("Alpha (ann.)",    f"{alpha_ann*100:.2f}%" if not np.isnan(alpha_ann) else "N/A")
c15.metric("Hist. VaR 95%",   f"{hist_var95*100:.2f}%")
c16.metric("CVaR 95%",        f"{hist_cvar95*100:.2f}%")

with st.expander("Extended Statistics"):
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Omega Ratio",    f"{omega:.2f}"  if not np.isnan(omega) else "N/A")
    e2.metric("Gain/Pain",      f"{gtp:.2f}"    if not np.isnan(gtp)   else "N/A")
    e3.metric("Skewness",       f"{sk:.3f}")
    e4.metric("Excess Kurtosis",f"{kurt:.3f}")

    e5, e6, e7, e8 = st.columns(4)
    e5.metric("Param. VaR 95%", f"{param_var95*100:.2f}%")
    e6.metric("Hist. VaR 99%",  f"{var99*100:.2f}%")
    e7.metric("CVaR 99%",       f"{cvar99*100:.2f}%")
    e8.metric("R² vs Bench",    f"{r2:.3f}"     if not np.isnan(r2)    else "N/A")

# ── Charts ────────────────────────────────────────────────────────────────────
st.markdown("### Performance")

left, right = st.columns([3, 1])
with left:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(norm_port.index, norm_port.values, color=ACCENT, label="Portfolio", lw=2)
    ax.plot(norm_bench.index, norm_bench.values, color=ACCENT2, label=benchmark_ticker, ls="--", lw=1.6)
    ax.fill_between(norm_port.index, norm_port.values, norm_bench.values,
                    where=norm_port.values >= norm_bench.values, alpha=0.12, color=GREEN)
    ax.fill_between(norm_port.index, norm_port.values, norm_bench.values,
                    where=norm_port.values < norm_bench.values, alpha=0.12, color=RED)
    ax.set_title("Growth of $1")
    ax.legend(); ax.grid(True, alpha=0.3)
    st.pyplot(fig); plt.close()

with right:
    fig2, ax2 = plt.subplots(figsize=(4, 4))
    ax2.pie(
        weights, labels=tickers,
        autopct="%1.1f%%",
        colors=PALETTE[:len(tickers)],
        startangle=90,
        wedgeprops=dict(edgecolor="#0a0e1a", linewidth=2),
    )
    ax2.set_title("Allocation", pad=12)
    st.pyplot(fig2); plt.close()

# Drawdown
fig3, ax3 = plt.subplots(figsize=(10, 3))
ax3.fill_between(drawdown.index, drawdown.values, 0, color=RED, alpha=0.35)
ax3.plot(drawdown.index, drawdown.values, color=RED, lw=1.2)
ax3.set_title("Portfolio Drawdown"); ax3.grid(True, alpha=0.3)
st.pyplot(fig3); plt.close()

# Return distribution
fig4, ax4 = plt.subplots(figsize=(10, 3))
ax4.hist(port_ret, bins=50, color=ACCENT, alpha=0.7, edgecolor="#0a0e1a")
ax4.axvline(hist_var95, color=RED,    lw=1.5, ls="--", label=f"VaR 95% {hist_var95*100:.2f}%")
ax4.axvline(hist_cvar95, color=YELLOW, lw=1.5, ls="--", label=f"CVaR 95% {hist_cvar95*100:.2f}%")
ax4.set_title("Daily Return Distribution"); ax4.legend(); ax4.grid(True, alpha=0.3)
st.pyplot(fig4); plt.close()

# Correlation matrix
st.markdown("### Correlation Matrix")
corr = ret.corr()
fig5, ax5 = plt.subplots(figsize=(max(5, len(tickers) * 1.5), max(4, len(tickers) * 1.2)))
cmap_c = mcolors.LinearSegmentedColormap.from_list("rg", [RED, "#111827", ACCENT])
im = ax5.imshow(corr.values, cmap=cmap_c, vmin=-1, vmax=1)
ax5.set_xticks(range(len(tickers))); ax5.set_xticklabels(tickers)
ax5.set_yticks(range(len(tickers))); ax5.set_yticklabels(tickers)
for i in range(len(tickers)):
    for j in range(len(tickers)):
        ax5.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center",
                 color="white", fontsize=10, fontweight="bold")
plt.colorbar(im, ax=ax5); ax5.set_title("Asset Correlation")
st.pyplot(fig5); plt.close()

# ── Technical Snapshot ────────────────────────────────────────────────────────
st.markdown("### Technical Snapshot")

tech_ticker = st.selectbox("Select ticker for technical analysis", tickers)
tech_df     = load_price_history(tech_ticker, period=period)

if not tech_df.empty:
    tc = tech_df["Close"]
    sma20 = sma(tc, 20); sma50 = sma(tc, 50)
    rsi14 = rsi(tc, 14)
    macd_l, macd_sig, macd_hist = macd(tc)
    bb_mid, bb_up, bb_lo = bollinger_bands(tc)

    # Price + indicators
    fig6, ax6 = plt.subplots(figsize=(10, 4))
    ax6.plot(tc.index, tc.values,       color=ACCENT,  lw=2,   label="Close")
    ax6.plot(sma20.index, sma20.values, color=YELLOW,  lw=1.2, label="SMA 20")
    ax6.plot(sma50.index, sma50.values, color=ACCENT2, lw=1.2, label="SMA 50")
    ax6.plot(bb_up.index, bb_up.values, color=GREEN,   lw=1,   ls="--", label="BB Upper")
    ax6.plot(bb_lo.index, bb_lo.values, color=RED,     lw=1,   ls="--", label="BB Lower")
    ax6.fill_between(bb_up.index, bb_up.values, bb_lo.values, alpha=0.05, color=ACCENT)
    ax6.set_title(f"{tech_ticker} — Price & Indicators")
    ax6.legend(fontsize=8); ax6.grid(True, alpha=0.3)
    st.pyplot(fig6); plt.close()

    col_a, col_b = st.columns(2)
    with col_a:
        fig7, ax7 = plt.subplots(figsize=(10, 3))
        ax7.plot(rsi14.index, rsi14.values, color=ACCENT)
        ax7.axhline(70, color=RED,   ls="--", lw=1, label="Overbought 70")
        ax7.axhline(30, color=GREEN, ls="--", lw=1, label="Oversold 30")
        ax7.axhline(50, color="white", ls=":", lw=0.6, alpha=0.5)
        ax7.fill_between(rsi14.index, rsi14.values, 70,
                         where=rsi14.values >= 70, alpha=0.15, color=RED)
        ax7.fill_between(rsi14.index, rsi14.values, 30,
                         where=rsi14.values <= 30, alpha=0.15, color=GREEN)
        ax7.set_ylim(0, 100); ax7.set_title("RSI (14)")
        ax7.legend(fontsize=8); ax7.grid(True, alpha=0.3)
        st.pyplot(fig7); plt.close()

    with col_b:
        fig8, ax8 = plt.subplots(figsize=(10, 3))
        ax8.plot(macd_l.index, macd_l.values,   color=ACCENT,  label="MACD", lw=1.5)
        ax8.plot(macd_sig.index, macd_sig.values, color=YELLOW, label="Signal", lw=1.5)
        colors_hist = [GREEN if v >= 0 else RED for v in macd_hist.values]
        ax8.bar(macd_hist.index, macd_hist.values, color=colors_hist, alpha=0.5, width=1)
        ax8.axhline(0, color="white", lw=0.6, ls="--")
        ax8.set_title("MACD"); ax8.legend(fontsize=8); ax8.grid(True, alpha=0.3)
        st.pyplot(fig8); plt.close()

    # Volume & OBV
    if "Volume" in tech_df.columns and tech_df["Volume"].sum() > 0:
        col_c, col_d = st.columns(2)
        with col_c:
            fig9, ax9 = plt.subplots(figsize=(10, 2.5))
            ax9.bar(tech_df.index, tech_df["Volume"], color=ACCENT2, alpha=0.6, width=1)
            ax9.set_title("Volume"); ax9.grid(True, alpha=0.3)
            st.pyplot(fig9); plt.close()

        with col_d:
            obv_series = obv(tech_df["Close"], tech_df["Volume"])
            fig10, ax10 = plt.subplots(figsize=(10, 2.5))
            ax10.plot(obv_series.index, obv_series.values, color=GREEN)
            ax10.set_title("OBV"); ax10.grid(True, alpha=0.3)
            st.pyplot(fig10); plt.close()

# ── Holdings Breakdown ────────────────────────────────────────────────────────
st.markdown("### Holdings Breakdown")

hdf = pd.DataFrame({
    "Ticker":             tickers,
    "Shares":             sh,
    "Avg Buy Price":      bp,
    "Latest Price":       latest.values,
    "Cost Basis":         cost,
    "Position Value":     pos_val,
    "Unrealized P&L":     upnl,
    "P&L %":              upnl_pct * 100,
    "Weight %":           weights * 100,
    "Asset Return %":     asset_total_returns.reindex(tickers).values * 100,
    "Return Contrib. %":  contribution_return * 100,
    "Vol Contribution":   vol_contrib,
})

st.dataframe(
    hdf.style.format({
        "Avg Buy Price":     "${:,.2f}",
        "Latest Price":      "${:,.2f}",
        "Cost Basis":        "${:,.2f}",
        "Position Value":    "${:,.2f}",
        "Unrealized P&L":    "${:,.2f}",
        "P&L %":             "{:.2f}%",
        "Weight %":          "{:.2f}%",
        "Asset Return %":    "{:.2f}%",
        "Return Contrib. %": "{:.2f}%",
        "Vol Contribution":  "{:.4f}",
    }).background_gradient(subset=["P&L %", "Asset Return %"], cmap="RdYlGn"),
    use_container_width=True,
)

# ── News ──────────────────────────────────────────────────────────────────────
st.markdown("### Latest News")
for t in tickers:
    news = load_news(t, 2)
    for item in news:
        st.markdown(f"**{t}** — [{item['title']}]({item['url']})")

# ── Export ────────────────────────────────────────────────────────────────────
csv = hdf.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download Holdings CSV", csv, "holdings_breakdown.csv", "text/csv")

