import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from utils import apply_theme, page_header, PALETTE, ACCENT, ACCENT2, GREEN, RED, YELLOW, MUTED
from data_loader import load_close_series
from analytics import (
    rolling_sharpe, rolling_beta, rolling_corr, rolling_vol,
    historical_var, cvar, parametric_var,
    compute_alpha_beta, covariance_matrix, marginal_vol_contribution,
    annualized_return, annualized_vol, max_drawdown_from_returns,
)

st.set_page_config(page_title="Risk & Attribution", layout="wide", page_icon="📊")
apply_theme()
page_header("Risk & Attribution", "Rolling Metrics · VaR · Stress Test · Factor Analysis")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Inputs")
tickers_input    = st.sidebar.text_input("Tickers", "AAPL,MSFT,SPY")
shares_input     = st.sidebar.text_input("Shares", "2,1,3")
period           = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
benchmark_ticker = st.sidebar.selectbox("Benchmark", ["SPY", "QQQ", "DIA", "IWM"])
risk_free_rate   = st.sidebar.number_input("Risk-free rate (%)", 0.0, 15.0, 2.0, 0.1)
roll_window      = st.sidebar.slider("Rolling window (days)", 10, 60, 20, 5)
market_shock     = st.sidebar.slider("Uniform market shock (%)", -50, 20, -10, 1)
run_page         = st.sidebar.button("Run Risk Analysis", use_container_width=True)

if not run_page:
    st.info("Fill in the sidebar and click **Run Risk Analysis**.")
    st.stop()

# ── Parse & load ──────────────────────────────────────────────────────────────
try:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    shares  = np.array([float(x.strip()) for x in shares_input.split(",") if x.strip()])
except ValueError:
    st.error("Check that shares are numeric.")
    st.stop()

if len(tickers) != len(shares):
    st.error("Tickers and shares must have the same length.")
    st.stop()

with st.spinner("Loading data…"):
    prices = pd.DataFrame()
    for t in tickers:
        s = load_close_series(t, period=period)
        if s.empty:
            st.error(f"No data for {t}")
            st.stop()
        prices[t] = s
    prices = prices.dropna()

    bench = load_close_series(benchmark_ticker, period=period).reindex(prices.index).dropna()

latest   = prices.iloc[-1]
pos_val  = latest.values * shares
weights  = pos_val / pos_val.sum()
ret      = prices.pct_change().dropna()
port_ret = ret.dot(weights)
bench_ret_s = bench.pct_change().dropna()

ann_ret = annualized_return(port_ret)
ann_vol = annualized_vol(port_ret)
rf      = risk_free_rate / 100
max_dd, _ = max_drawdown_from_returns(port_ret)
alpha_ann, beta, r2, aligned = compute_alpha_beta(port_ret, bench_ret_s)

# ── Summary ───────────────────────────────────────────────────────────────────
st.markdown("### Risk Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ann. Volatility",  f"{ann_vol*100:.2f}%")
c2.metric("Max Drawdown",     f"{max_dd*100:.2f}%")
c3.metric("Beta",             f"{beta:.2f}"       if not np.isnan(beta)  else "N/A")
c4.metric("Alpha (ann.)",     f"{alpha_ann*100:.2f}%" if not np.isnan(alpha_ann) else "N/A")

var95    = historical_var(port_ret, 0.95)
cvar95   = cvar(port_ret, var95)
pvar95   = parametric_var(port_ret, 0.95)
var99    = historical_var(port_ret, 0.99)
cvar99   = cvar(port_ret, var99)

c5, c6, c7, c8 = st.columns(4)
c5.metric("Hist. VaR 95%",  f"{var95*100:.2f}%")
c6.metric("CVaR 95%",       f"{cvar95*100:.2f}%")
c7.metric("Hist. VaR 99%",  f"{var99*100:.2f}%")
c8.metric("CVaR 99%",       f"{cvar99*100:.2f}%")

# ── Rolling metrics ───────────────────────────────────────────────────────────
st.markdown("### Rolling Risk Metrics")

roll_v  = rolling_vol(port_ret, window=roll_window)
roll_sh = rolling_sharpe(port_ret, rf=rf, window=roll_window)
roll_b  = rolling_beta(port_ret, bench_ret_s, window=roll_window)
roll_c  = rolling_corr(port_ret, bench_ret_s, window=roll_window)

c1, c2 = st.columns(2)
with c1:
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(roll_v.index, roll_v.values, color=ACCENT)
    ax.fill_between(roll_v.index, roll_v.values, alpha=0.15, color=ACCENT)
    ax.set_title(f"Rolling {roll_window}-Day Volatility (Ann.)")
    ax.grid(True, alpha=0.3); st.pyplot(fig); plt.close()

with c2:
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(roll_sh.index, roll_sh.values, color=ACCENT2)
    ax.axhline(0, color="white", lw=0.8, ls="--")
    ax.fill_between(roll_sh.index, roll_sh.values, 0,
                    where=roll_sh.values >= 0, alpha=0.15, color=GREEN)
    ax.fill_between(roll_sh.index, roll_sh.values, 0,
                    where=roll_sh.values < 0, alpha=0.15, color=RED)
    ax.set_title(f"Rolling {roll_window}-Day Sharpe")
    ax.grid(True, alpha=0.3); st.pyplot(fig); plt.close()

c3, c4 = st.columns(2)
with c3:
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(roll_b.index, roll_b.values, color=YELLOW)
    ax.axhline(1.0, color="white", lw=0.8, ls="--", label="β=1")
    ax.axhline(0.0, color=MUTED,   lw=0.6, ls=":")
    ax.set_title(f"Rolling {roll_window}-Day Beta")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    st.pyplot(fig); plt.close()

with c4:
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(roll_c.index, roll_c.values, color=GREEN)
    ax.axhline(0.0, color="white", lw=0.8, ls="--")
    ax.set_ylim(-1, 1)
    ax.set_title(f"Rolling {roll_window}-Day Correlation vs {benchmark_ticker}")
    ax.grid(True, alpha=0.3); st.pyplot(fig); plt.close()

# ── Correlation Matrix ────────────────────────────────────────────────────────
st.markdown("### Correlation Matrix")
corr = ret.corr()
fig2, ax2 = plt.subplots(figsize=(max(5, len(tickers)*1.5), max(4, len(tickers)*1.2)))
cmap_c = mcolors.LinearSegmentedColormap.from_list("rg", [RED, "#111827", ACCENT])
im = ax2.imshow(corr.values, cmap=cmap_c, vmin=-1, vmax=1)
ax2.set_xticks(range(len(tickers))); ax2.set_xticklabels(tickers)
ax2.set_yticks(range(len(tickers))); ax2.set_yticklabels(tickers)
for i in range(len(tickers)):
    for j in range(len(tickers)):
        ax2.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center",
                 color="white", fontsize=10, fontweight="bold")
plt.colorbar(im, ax=ax2)
st.pyplot(fig2); plt.close()

# ── Return Distribution ───────────────────────────────────────────────────────
st.markdown("### Return Distribution")
fig3, ax3 = plt.subplots(figsize=(10, 3))
ax3.hist(port_ret, bins=50, color=ACCENT, alpha=0.7, edgecolor="#0a0e1a")
ax3.axvline(var95,  color=RED,    lw=1.5, ls="--", label=f"VaR 95% {var95*100:.2f}%")
ax3.axvline(cvar95, color=YELLOW, lw=1.5, ls="--", label=f"CVaR 95% {cvar95*100:.2f}%")
ax3.axvline(var99,  color="#ff6e40", lw=1.2, ls=":",  label=f"VaR 99% {var99*100:.2f}%")
ax3.legend(); ax3.grid(True, alpha=0.3)
st.pyplot(fig3); plt.close()

# ── Vol Contribution ──────────────────────────────────────────────────────────
st.markdown("### Volatility Contribution by Asset")
cov_ann    = covariance_matrix(ret)
vol_contrib = marginal_vol_contribution(weights, cov_ann.values)

fig_vc, ax_vc = plt.subplots(figsize=(8, 3))
bars = ax_vc.bar(tickers, vol_contrib, color=PALETTE[:len(tickers)], edgecolor="#0a0e1a", linewidth=1.5)
for bar, val in zip(bars, vol_contrib):
    ax_vc.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
               f"{val:.4f}", ha="center", va="bottom", fontsize=9, color="white")
ax_vc.set_title("Marginal Volatility Contribution")
ax_vc.grid(True, alpha=0.3, axis="y")
st.pyplot(fig_vc); plt.close()

# ── Stress Test ───────────────────────────────────────────────────────────────
st.markdown("### Stress Test — Uniform Shock")
shocked_prices = latest * (1 + market_shock / 100)
shocked_values = shocked_prices.values * shares
scenario_pnl   = shocked_values - pos_val

s1, s2, s3 = st.columns(3)
s1.metric("Current Value",  f"${pos_val.sum():,.2f}")
s2.metric("Shocked Value",  f"${shocked_values.sum():,.2f}")
s3.metric("Scenario P&L",   f"${scenario_pnl.sum():,.2f}")

shock_df = pd.DataFrame({
    "Ticker":       tickers,
    "Current Price":  latest.values,
    "Shocked Price":  shocked_prices.values,
    "Current Value":  pos_val,
    "Shocked Value":  shocked_values,
    "Scenario P&L":   scenario_pnl,
})
st.dataframe(
    shock_df.style.format({
        "Current Price":  "${:,.2f}",
        "Shocked Price":  "${:,.2f}",
        "Current Value":  "${:,.2f}",
        "Shocked Value":  "${:,.2f}",
        "Scenario P&L":   "${:,.2f}",
    }).background_gradient(subset=["Scenario P&L"], cmap="RdYlGn"),
    use_container_width=True,
)

# ── Custom Scenario ───────────────────────────────────────────────────────────
st.markdown("### Custom Scenario — Per-Asset Shocks")
st.caption("Set individual shock percentages for each asset and see the portfolio impact.")

custom_shocks = {}
cols = st.columns(min(len(tickers), 5))
for i, t in enumerate(tickers):
    with cols[i % 5]:
        custom_shocks[t] = st.number_input(
            f"{t} shock %", value=0.0, step=1.0, key=f"cshock_{t}"
        )

custom_shocked = np.array([latest[t] * (1 + custom_shocks[t] / 100) for t in tickers])
custom_vals    = custom_shocked * shares
custom_pnl     = custom_vals - pos_val

ca1, ca2, ca3 = st.columns(3)
ca1.metric("Current Value", f"${pos_val.sum():,.2f}")
ca2.metric("Scenario Value", f"${custom_vals.sum():,.2f}")
ca3.metric("Scenario P&L",  f"${custom_pnl.sum():,.2f}")

custom_df = pd.DataFrame({
    "Ticker":         tickers,
    "Current Price":  latest.values,
    "Shock %":        [custom_shocks[t] for t in tickers],
    "Scenario Price": custom_shocked,
    "Scenario Value": custom_vals,
    "Scenario P&L":   custom_pnl,
})
st.dataframe(
    custom_df.style.format({
        "Current Price":  "${:,.2f}",
        "Shock %":        "{:.2f}%",
        "Scenario Price": "${:,.2f}",
        "Scenario Value": "${:,.2f}",
        "Scenario P&L":   "${:,.2f}",
    }).background_gradient(subset=["Scenario P&L"], cmap="RdYlGn"),
    use_container_width=True,
)

# ── Multi-scenario sweep ──────────────────────────────────────────────────────
st.markdown("### Scenario Sweep — Portfolio Value vs Market Move")
sweep_range = np.arange(-40, 41, 5)
sweep_vals  = [(latest.values * (1 + s/100) * shares).sum() for s in sweep_range]

fig_sw, ax_sw = plt.subplots(figsize=(10, 3))
colors_sw = [RED if v < pos_val.sum() else GREEN for v in sweep_vals]
ax_sw.bar(sweep_range, sweep_vals, width=3.5, color=colors_sw, alpha=0.75, edgecolor="#0a0e1a")
ax_sw.axhline(pos_val.sum(), color="white", lw=1.2, ls="--", label="Current Value")
ax_sw.axhline(total_cost if True else 0, color=YELLOW, lw=1, ls=":", label="Cost Basis")
ax_sw.set_xlabel("Market Move (%)"); ax_sw.set_ylabel("Portfolio Value ($)")
ax_sw.set_title("Portfolio Value Across Market Scenarios")
ax_sw.legend(); ax_sw.grid(True, alpha=0.3, axis="y")
st.pyplot(fig_sw); plt.close()

total_cost = (np.array(buy_prices_input if False else [float(x.strip())
              for x in "180,350,500".split(",")]) * shares).sum()