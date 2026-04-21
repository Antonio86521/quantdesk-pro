import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from auth import require_login, sidebar_user_widget
from utils import (
    apply_theme, apply_responsive_layout, page_header,
    PALETTE, ACCENT, ACCENT2, GREEN, RED, AMBER, TEXT2, BG3, BORDER,
    app_footer, safe_pct, safe_num,
)
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

st.set_page_config(page_title="Portfolio — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Portfolio Analytics", "Performance · Attribution · Risk · Technicals")


def _set_clicked():
    st.session_state["analyze_portfolio_clicked"] = True


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Inputs")
tickers_input    = st.sidebar.text_input("Tickers (comma-separated)", "AAPL,MSFT,SPY")
shares_input     = st.sidebar.text_input("Shares", "2,1,3")
buy_prices_input = st.sidebar.text_input("Buy prices", "180,350,500")
period           = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
risk_free_rate   = st.sidebar.number_input("Risk-free rate (%)", 0.0, 15.0, 2.0, 0.1)
benchmark_ticker = st.sidebar.selectbox("Benchmark", ["SPY", "QQQ", "DIA", "IWM"])
st.sidebar.button("Analyze Portfolio", use_container_width=True, on_click=_set_clicked)
sidebar_user_widget()

if not st.session_state.get("analyze_portfolio_clicked", False):
    st.markdown(
        f"""
        <div style="background:{BG3};border:1px solid {BORDER};border-radius:10px;
                    padding:24px;text-align:center;margin-top:24px;">
          <div style="font-size:28px;margin-bottom:12px;">📈</div>
          <div style="font-size:15px;font-weight:600;margin-bottom:6px;">Portfolio Analytics</div>
          <div style="font-size:12px;color:{TEXT2};">
            Enter tickers, shares and buy prices in the sidebar, then click
            <strong>Analyze Portfolio</strong>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── Parse ──────────────────────────────────────────────────────────────────────
try:
    tickers    = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    shares     = [float(x.strip()) for x in shares_input.split(",") if x.strip()]
    buy_prices = [float(x.strip()) for x in buy_prices_input.split(",") if x.strip()]
except ValueError:
    st.error("Could not parse inputs. Check that shares and buy prices are numbers.")
    st.stop()

if not (len(tickers) == len(shares) == len(buy_prices)):
    st.error("Tickers, shares, and buy prices must have the same number of entries.")
    st.stop()
if any(s <= 0 for s in shares) or any(p <= 0 for p in buy_prices):
    st.error("Shares and buy prices must all be positive.")
    st.stop()

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading market data…"):
    prices = pd.DataFrame()
    for t in tickers:
        s = load_close_series(t, period=period, source="auto")
        if s.empty:
            st.error(f"No price data for **{t}**.")
            st.stop()
        prices[t] = s
    prices = prices.dropna()
    if prices.empty:
        st.error("No aligned price data across the selected tickers.")
        st.stop()
    bench_series = load_close_series(benchmark_ticker, period=period, source="auto").reindex(prices.index).dropna()

# ── Compute ────────────────────────────────────────────────────────────────────
latest   = prices.iloc[-1]
sh       = np.array(shares)
bp       = np.array(buy_prices)
pos_val  = latest.values * sh
cost     = bp * sh
upnl     = pos_val - cost
upnl_pct = upnl / cost
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
sharpe     = (ann_ret - rf) / ann_vol if ann_vol else np.nan
max_dd, drawdown = max_drawdown_from_returns(port_ret)
sortino_r  = sortino_ratio(ann_ret, rf, port_ret)
calmar_r   = calmar_ratio(ann_ret, max_dd)
omega_r    = omega_ratio(port_ret)
gtp        = gain_to_pain(port_ret)
sk         = return_skew(port_ret)
kurt       = return_kurtosis(port_ret)

hist_var95   = historical_var(port_ret, 0.95)
hist_cvar95  = cvar(port_ret, hist_var95)
param_var95  = parametric_var(port_ret, 0.95)

bench_ret_s = bench_series.pct_change().dropna()
alpha_ann, beta, r2, aligned = compute_alpha_beta(port_ret, bench_ret_s)
tracking_error, info_ratio = tracking_stats(aligned)

asset_total_returns   = (prices.iloc[-1] / prices.iloc[0]) - 1
contribution_return   = weights * asset_total_returns.reindex(tickers).values
cov_ann               = covariance_matrix(ret)
vol_contrib           = marginal_vol_contribution(weights, cov_ann.values)

norm_port  = (prices * sh).sum(axis=1);   norm_port  /= norm_port.iloc[0]
norm_bench = bench_series / bench_series.iloc[0] if not bench_series.empty else pd.Series()


# ── METRICS ROW ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="font-size:9.5px;color:#3d5068;letter-spacing:1px;
                text-transform:uppercase;font-weight:600;margin-bottom:10px;">
      Overview
    </div>
    """,
    unsafe_allow_html=True,
)

r1 = st.columns(4)
r1[0].metric("Portfolio Value",  f"${total_val:,.2f}")
r1[1].metric("Invested Capital", f"${total_cost:,.2f}")
r1[2].metric("Unrealized P&L",  f"${total_upnl:,.2f}", delta=f"{total_upnl_p:.2%}")
r1[3].metric("Total Return",     safe_pct(total_ret))

r2 = st.columns(4)
r2[0].metric("Ann. Return",    safe_pct(ann_ret))
r2[1].metric("Ann. Volatility",safe_pct(ann_vol))
r2[2].metric("Sharpe Ratio",   safe_num(sharpe))
r2[3].metric("Max Drawdown",   safe_pct(max_dd))

r3 = st.columns(4)
r3[0].metric("Sortino",        safe_num(sortino_r))
r3[1].metric("Calmar",         safe_num(calmar_r))
r3[2].metric("Beta",           safe_num(beta))
r3[3].metric("Alpha (ann.)",   safe_pct(alpha_ann))

with st.expander("Extended Statistics"):
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Omega Ratio",    safe_num(omega_r))
    e2.metric("Gain/Pain",      safe_num(gtp))
    e3.metric("Skewness",       safe_num(sk, 3))
    e4.metric("Excess Kurtosis",safe_num(kurt, 3))

    e5, e6, e7, e8 = st.columns(4)
    e5.metric("Param. VaR 95%",safe_pct(param_var95))
    e6.metric("Hist. VaR 95%", safe_pct(hist_var95))
    e7.metric("CVaR 95%",      safe_pct(hist_cvar95))
    e8.metric("R² vs Bench",   safe_num(r2, 3))

st.divider()

# ── PERFORMANCE CHARTS ────────────────────────────────────────────────────────
st.markdown(
    '<div style="font-size:9.5px;color:#3d5068;letter-spacing:1px;'
    'text-transform:uppercase;font-weight:600;margin-bottom:10px;">Performance</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([3, 1])
with left:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(norm_port.index, norm_port.values, color=ACCENT, label="Portfolio", lw=2)
    if not norm_bench.empty:
        ax.plot(norm_bench.index, norm_bench.values, color="#3d5068",
                label=benchmark_ticker, ls="--", lw=1.4)
        ax.fill_between(norm_port.index, norm_port.values, norm_bench.values,
                        where=norm_port.values >= norm_bench.values, alpha=0.08, color=GREEN)
        ax.fill_between(norm_port.index, norm_port.values, norm_bench.values,
                        where=norm_port.values < norm_bench.values, alpha=0.08, color=RED)
    ax.set_title("Growth of $1")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.25)
    st.pyplot(fig); plt.close()

with right:
    fig2, ax2 = plt.subplots(figsize=(4.2, 4.2))
    ax2.pie(
        weights, labels=tickers,
        autopct="%1.1f%%", colors=PALETTE[:len(tickers)],
        startangle=90, wedgeprops=dict(edgecolor="#0d1117", linewidth=2),
    )
    ax2.set_title("Allocation", pad=10)
    st.pyplot(fig2); plt.close()

# Drawdown + distribution side by side
col_dd, col_dist = st.columns(2)
with col_dd:
    fig3, ax3 = plt.subplots(figsize=(7, 3))
    ax3.fill_between(drawdown.index, drawdown.values, 0, color=RED, alpha=0.25)
    ax3.plot(drawdown.index, drawdown.values, color=RED, lw=1.3)
    ax3.set_title("Portfolio Drawdown"); ax3.grid(True, alpha=0.25)
    st.pyplot(fig3); plt.close()

with col_dist:
    fig4, ax4 = plt.subplots(figsize=(7, 3))
    ax4.hist(port_ret, bins=45, color=ACCENT, alpha=0.7, edgecolor="#0d1117")
    ax4.axvline(hist_var95,  color=RED,  lw=1.5, ls="--", label=f"VaR 95% {hist_var95:.2%}")
    ax4.axvline(hist_cvar95, color=AMBER, lw=1.5, ls="--", label=f"CVaR {hist_cvar95:.2%}")
    ax4.set_title("Return Distribution"); ax4.legend(fontsize=8); ax4.grid(True, alpha=0.25)
    st.pyplot(fig4); plt.close()

st.divider()

# ── CORRELATION ───────────────────────────────────────────────────────────────
st.markdown(
    '<div style="font-size:9.5px;color:#3d5068;letter-spacing:1px;'
    'text-transform:uppercase;font-weight:600;margin-bottom:10px;">Correlation Matrix</div>',
    unsafe_allow_html=True,
)
corr = ret.corr()
fig5, ax5 = plt.subplots(figsize=(max(5, len(tickers) * 1.5), max(4, len(tickers) * 1.2)))
cmap_c = mcolors.LinearSegmentedColormap.from_list("rg", [RED, "#131920", ACCENT])
im = ax5.imshow(corr.values, cmap=cmap_c, vmin=-1, vmax=1)
ax5.set_xticks(range(len(tickers))); ax5.set_xticklabels(tickers)
ax5.set_yticks(range(len(tickers))); ax5.set_yticklabels(tickers)
for i in range(len(tickers)):
    for j in range(len(tickers)):
        ax5.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center",
                 color="white", fontsize=10, fontweight="bold")
plt.colorbar(im, ax=ax5); ax5.set_title("Asset Correlation")
st.pyplot(fig5); plt.close()

st.divider()

# ── TECHNICAL SNAPSHOT ────────────────────────────────────────────────────────
st.markdown(
    '<div style="font-size:9.5px;color:#3d5068;letter-spacing:1px;'
    'text-transform:uppercase;font-weight:600;margin-bottom:10px;">Technical Snapshot</div>',
    unsafe_allow_html=True,
)

tech_ticker = st.selectbox("Select ticker for technicals", tickers)
tech_df     = load_price_history(tech_ticker, period=period, source="auto")

if not tech_df.empty:
    tc = tech_df["Close"]
    sma20 = sma(tc, 20); sma50 = sma(tc, 50)
    rsi14 = rsi(tc, 14)
    macd_l, macd_sig, macd_hist = macd(tc)
    bb_mid, bb_up, bb_lo = bollinger_bands(tc)

    fig6, ax6 = plt.subplots(figsize=(10, 4))
    ax6.plot(tc.index,    tc.values,    color=ACCENT,  lw=2,   label="Close")
    ax6.plot(sma20.index, sma20.values, color=AMBER,   lw=1.2, label="SMA 20")
    ax6.plot(sma50.index, sma50.values, color=ACCENT2, lw=1.2, label="SMA 50")
    ax6.plot(bb_up.index, bb_up.values, color=GREEN,   lw=1,   ls="--", label="BB Upper")
    ax6.plot(bb_lo.index, bb_lo.values, color=RED,     lw=1,   ls="--", label="BB Lower")
    ax6.fill_between(bb_up.index, bb_up.values, bb_lo.values, alpha=0.05, color=ACCENT)
    ax6.set_title(f"{tech_ticker} — Price & Indicators")
    ax6.legend(fontsize=8); ax6.grid(True, alpha=0.25)
    st.pyplot(fig6); plt.close()

    col_a, col_b = st.columns(2)
    with col_a:
        fig7, ax7 = plt.subplots(figsize=(7, 3))
        ax7.plot(rsi14.index, rsi14.values, color=ACCENT)
        ax7.axhline(70, color=RED,   ls="--", lw=1, label="OB 70")
        ax7.axhline(30, color=GREEN, ls="--", lw=1, label="OS 30")
        ax7.fill_between(rsi14.index, rsi14.values, 70, where=rsi14.values >= 70, alpha=0.12, color=RED)
        ax7.fill_between(rsi14.index, rsi14.values, 30, where=rsi14.values <= 30, alpha=0.12, color=GREEN)
        ax7.set_ylim(0, 100); ax7.set_title("RSI (14)")
        ax7.legend(fontsize=8); ax7.grid(True, alpha=0.25)
        st.pyplot(fig7); plt.close()

    with col_b:
        fig8, ax8 = plt.subplots(figsize=(7, 3))
        ax8.plot(macd_l.index,   macd_l.values,   color=ACCENT, label="MACD",   lw=1.5)
        ax8.plot(macd_sig.index, macd_sig.values, color=AMBER,  label="Signal", lw=1.5)
        colors_h = [GREEN if v >= 0 else RED for v in macd_hist.values]
        ax8.bar(macd_hist.index, macd_hist.values, color=colors_h, alpha=0.45, width=1)
        ax8.axhline(0, color="white", lw=0.6, ls="--")
        ax8.set_title("MACD"); ax8.legend(fontsize=8); ax8.grid(True, alpha=0.25)
        st.pyplot(fig8); plt.close()

    if "Volume" in tech_df.columns and tech_df["Volume"].sum() > 0:
        col_c, col_d = st.columns(2)
        with col_c:
            fig9, ax9 = plt.subplots(figsize=(7, 2.5))
            ax9.bar(tech_df.index, tech_df["Volume"], color=ACCENT2, alpha=0.55, width=1)
            ax9.set_title("Volume"); ax9.grid(True, alpha=0.25)
            st.pyplot(fig9); plt.close()
        with col_d:
            obv_s = obv(tech_df["Close"], tech_df["Volume"])
            fig10, ax10 = plt.subplots(figsize=(7, 2.5))
            ax10.plot(obv_s.index, obv_s.values, color=GREEN)
            ax10.set_title("OBV"); ax10.grid(True, alpha=0.25)
            st.pyplot(fig10); plt.close()

st.divider()

# ── HOLDINGS TABLE ────────────────────────────────────────────────────────────
st.markdown(
    '<div style="font-size:9.5px;color:#3d5068;letter-spacing:1px;'
    'text-transform:uppercase;font-weight:600;margin-bottom:10px;">Holdings Breakdown</div>',
    unsafe_allow_html=True,
)

hdf = pd.DataFrame({
    "Ticker":            tickers,
    "Shares":            sh,
    "Avg Buy Price":     bp,
    "Latest Price":      latest.values,
    "Cost Basis":        cost,
    "Market Value":      pos_val,
    "Unrealized P&L":    upnl,
    "P&L %":             upnl_pct * 100,
    "Weight %":          weights * 100,
    "Asset Return %":    asset_total_returns.reindex(tickers).values * 100,
    "Return Contrib. %": contribution_return * 100,
    "Vol Contribution":  vol_contrib,
})
st.dataframe(
    hdf.style.format({
        "Avg Buy Price":    "${:,.2f}",
        "Latest Price":     "${:,.2f}",
        "Cost Basis":       "${:,.2f}",
        "Market Value":     "${:,.2f}",
        "Unrealized P&L":   "${:,.2f}",
        "P&L %":            "{:.2f}%",
        "Weight %":         "{:.2f}%",
        "Asset Return %":   "{:.2f}%",
        "Return Contrib. %":"{:.2f}%",
        "Vol Contribution": "{:.4f}",
    }).background_gradient(subset=["P&L %", "Asset Return %"], cmap="RdYlGn"),
    use_container_width=True, hide_index=True,
)

csv = hdf.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download Holdings CSV", csv, "holdings.csv", "text/csv")

# ── NEWS ──────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<div style="font-size:9.5px;color:#3d5068;letter-spacing:1px;'
    'text-transform:uppercase;font-weight:600;margin-bottom:10px;">Latest News</div>',
    unsafe_allow_html=True,
)
for t in tickers:
    news = load_news(t, 2)
    for item in news:
        st.markdown(f"**{t}** — [{item['title']}]({item['url']})")

app_footer()
