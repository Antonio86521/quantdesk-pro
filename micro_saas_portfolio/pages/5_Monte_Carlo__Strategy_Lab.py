import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from auth import require_login, sidebar_user_widget
from utils import (
    apply_theme, apply_responsive_layout, page_header,
    ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEXT2, BG3, BORDER,
    app_footer,
    section_header,)
from options_models import monte_carlo_paths, bs_price_only, monte_carlo_option_price
from strategies import (
    payoff_long_call, payoff_short_call, payoff_long_put, payoff_short_put,
    payoff_covered_call, payoff_protective_put,
    payoff_bull_call_spread, payoff_bear_put_spread,
    payoff_bull_put_spread, payoff_bear_call_spread,
    payoff_straddle, payoff_strangle,
    payoff_long_butterfly, payoff_iron_condor,
    strategy_summary,
)

st.set_page_config(page_title="Monte Carlo & Strategy Lab — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Monte Carlo & Strategy Lab", "GBM Simulation · Option Pricing · Payoff Diagrams")
sidebar_user_widget()



# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Simulation Inputs")
option_S     = st.sidebar.number_input("Spot Price (S)",     0.01, value=100.0, step=1.0)
option_K     = st.sidebar.number_input("Strike (K)",         0.01, value=100.0, step=1.0)
option_r     = st.sidebar.number_input("Risk-Free Rate (%)", 0.0,  20.0, 2.0,   0.1)
option_sigma = st.sidebar.number_input("Volatility (%)",     0.01, 300.0, 20.0, 1.0)
mc_horizon   = st.sidebar.number_input("Horizon (years)",    0.1,  5.0,  1.0,   0.1)
mc_paths_n   = st.sidebar.slider("Number of paths", 100, 10_000, 3_000, 100)
run_mc       = st.sidebar.button("Run Monte Carlo", use_container_width=True)

# ── MONTE CARLO ───────────────────────────────────────────────────────────────
section_header("Monte Carlo Price Simulation")

if run_mc:
    sigma_mc = option_sigma / 100
    r_mc     = option_r / 100
    np.random.seed(42)

    with st.spinner(f"Simulating {mc_paths_n:,} paths…"):
        paths  = monte_carlo_paths(option_S, mc_horizon, r_mc, sigma_mc, mc_paths_n)
        t_axis = np.linspace(0, mc_horizon, paths.shape[0])
        final_prices     = paths[-1]
        mc_call_payoff   = np.exp(-r_mc * mc_horizon) * np.maximum(final_prices - option_K, 0)
        mc_put_payoff    = np.exp(-r_mc * mc_horizon) * np.maximum(option_K - final_prices, 0)
        bs_call = bs_price_only(option_S, option_K, mc_horizon, r_mc, sigma_mc, "call")
        bs_put  = bs_price_only(option_S, option_K, mc_horizon, r_mc, sigma_mc, "put")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("MC Call Price",  f"${mc_call_payoff.mean():.4f}")
    c2.metric("BS Call Price",  f"${bs_call:.4f}")
    c3.metric("MC Put Price",   f"${mc_put_payoff.mean():.4f}")
    c4.metric("BS Put Price",   f"${bs_put:.4f}")

    call_err = abs(mc_call_payoff.mean() - bs_call) / max(bs_call, 1e-9) * 100
    put_err  = abs(mc_put_payoff.mean()  - bs_put)  / max(bs_put,  1e-9) * 100
    st.caption(f"MC error vs BS — Call: {call_err:.2f}%  ·  Put: {put_err:.2f}%  ({mc_paths_n:,} paths, antithetic variates)")

    # Path chart
    fig, ax = plt.subplots(figsize=(10, 5))
    n_show = min(mc_paths_n, 150)
    for i in range(n_show):
        ax.plot(t_axis, paths[:, i], lw=0.4, alpha=0.15, color=ACCENT)
    p5  = np.percentile(paths,  5, axis=1)
    p25 = np.percentile(paths, 25, axis=1)
    p50 = np.percentile(paths, 50, axis=1)
    p75 = np.percentile(paths, 75, axis=1)
    p95 = np.percentile(paths, 95, axis=1)
    ax.fill_between(t_axis, p5,  p95, alpha=0.06, color=ACCENT)
    ax.fill_between(t_axis, p25, p75, alpha=0.10, color=ACCENT)
    ax.plot(t_axis, p50, color="white",  lw=2,   label="Median",   zorder=4)
    ax.plot(t_axis, p5,  color=RED,      lw=1.5, ls="--", label="5th pct",  zorder=4)
    ax.plot(t_axis, p95, color=GREEN,    lw=1.5, ls="--", label="95th pct", zorder=4)
    ax.axhline(option_K, color=AMBER, ls=":", lw=1.5, label=f"Strike ${option_K:.0f}")
    ax.set_title(f"Monte Carlo — {mc_paths_n:,} paths  ·  {mc_horizon:.1f} yr(s)")
    ax.set_xlabel("Time (years)"); ax.set_ylabel("Price ($)")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.25)
    st.pyplot(fig); plt.close()

    section_header("Final Price Distribution")
    fig2, ax2 = plt.subplots(figsize=(10, 3))
    ax2.hist(final_prices, bins=70, color=ACCENT2, alpha=0.75, edgecolor="#0d1117")
    ax2.axvline(option_K,                  color=AMBER,  lw=1.5, ls="--", label=f"Strike ${option_K:.0f}")
    ax2.axvline(np.mean(final_prices),     color="white",lw=1.5,          label=f"Mean ${np.mean(final_prices):.2f}")
    ax2.axvline(np.percentile(final_prices, 5),  color=RED,   lw=1.2, ls=":", label="5th pct")
    ax2.axvline(np.percentile(final_prices, 95), color=GREEN, lw=1.2, ls=":", label="95th pct")
    ax2.set_xlabel("Final Price ($)"); ax2.set_title("Distribution of Final Prices")
    ax2.legend(fontsize=8); ax2.grid(True, alpha=0.25)
    st.pyplot(fig2); plt.close()

    s1,s2,s3,s4,s5,s6 = st.columns(6)
    s1.metric("Mean Final",  f"${np.mean(final_prices):.2f}")
    s2.metric("Median",      f"${np.median(final_prices):.2f}")
    s3.metric("Std Dev",     f"${np.std(final_prices):.2f}")
    s4.metric("5th Pct",     f"${np.percentile(final_prices, 5):.2f}")
    s5.metric("95th Pct",    f"${np.percentile(final_prices, 95):.2f}")
    s6.metric("P(above K)",  f"{(final_prices > option_K).mean()*100:.1f}%")

    section_header("MC Convergence")
    sample_sizes = np.unique(np.linspace(100, mc_paths_n, 40).astype(int))
    conv_prices  = [np.exp(-r_mc * mc_horizon) * np.maximum(paths[-1, :n] - option_K, 0).mean()
                    for n in sample_sizes]
    fig3, ax3 = plt.subplots(figsize=(10, 3))
    ax3.plot(sample_sizes, conv_prices, color=ACCENT, lw=1.5)
    ax3.axhline(bs_call, color=AMBER, lw=1.2, ls="--", label=f"BS Price ${bs_call:.4f}")
    ax3.set_xlabel("Number of Paths"); ax3.set_ylabel("Call Price ($)")
    ax3.set_title("MC Convergence to BS Price"); ax3.legend(fontsize=8); ax3.grid(True, alpha=0.25)
    st.pyplot(fig3); plt.close()

else:
    st.markdown(
        f'<div style="background:{BG3};border:1px solid {BORDER};border-radius:10px;'
        f'padding:22px;text-align:center;margin:10px 0;">'
        f'<div style="font-size:24px;margin-bottom:10px;">🎲</div>'
        f'<div style="font-size:13px;font-weight:600;margin-bottom:5px;">Monte Carlo Simulator</div>'
        f'<div style="font-size:12px;color:{TEXT2};">Set parameters in the sidebar and click <strong>Run Monte Carlo</strong>.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ── STRATEGY LAB ──────────────────────────────────────────────────────────────
section_header("Strategy Lab — Expiry Payoff Diagrams")

STRATEGIES = [
    "Long Call","Short Call","Long Put","Short Put",
    "Covered Call","Protective Put",
    "Bull Call Spread","Bear Put Spread","Bull Put Spread","Bear Call Spread",
    "Straddle","Strangle","Long Butterfly","Iron Condor",
]
DESCRIPTIONS = {
    "Long Call":       "Bullish. Unlimited upside, loss capped at premium paid.",
    "Short Call":      "Bearish/neutral. Premium collected, unlimited upside risk.",
    "Long Put":        "Bearish. Profits as stock falls, loss capped at premium.",
    "Short Put":       "Bullish/neutral. Premium collected, significant downside risk.",
    "Covered Call":    "Neutral/mild bullish. Own stock, sell call to generate income.",
    "Protective Put":  "Bullish with downside hedge. Long stock + long put.",
    "Bull Call Spread":"Moderately bullish. Capped profit and capped loss.",
    "Bear Put Spread": "Moderately bearish. Capped profit and capped loss.",
    "Bull Put Spread": "Bullish/neutral. Credit spread — sell higher, buy lower put.",
    "Bear Call Spread":"Bearish/neutral. Credit spread — sell lower, buy higher call.",
    "Straddle":        "Volatility bet. Profits from large move in either direction.",
    "Strangle":        "Cheaper vol bet. Wider strikes than straddle, needs bigger move.",
    "Long Butterfly":  "Low vol bet. Max profit at middle strike, limited risk.",
    "Iron Condor":     "Low vol / range-bound. Profit from time decay in a sideways market.",
}

strategy = st.selectbox("Choose strategy", STRATEGIES)
S_range  = np.linspace(option_S * 0.5, option_S * 1.5, 300)
pnl = None

if strategy == "Long Call":
    premium = st.number_input("Call premium ($)", value=max(0.01, round(option_S*0.08,2)), step=0.5)
    pnl = payoff_long_call(S_range, option_K, premium)
elif strategy == "Short Call":
    premium = st.number_input("Call premium ($)", value=max(0.01, round(option_S*0.08,2)), step=0.5)
    pnl = payoff_short_call(S_range, option_K, premium)
elif strategy == "Long Put":
    premium = st.number_input("Put premium ($)", value=max(0.01, round(option_S*0.08,2)), step=0.5)
    pnl = payoff_long_put(S_range, option_K, premium)
elif strategy == "Short Put":
    premium = st.number_input("Put premium ($)", value=max(0.01, round(option_S*0.08,2)), step=0.5)
    pnl = payoff_short_put(S_range, option_K, premium)
elif strategy == "Covered Call":
    stock_cost = st.number_input("Stock cost basis ($)", value=float(option_S), step=1.0)
    premium    = st.number_input("Call premium ($)", value=max(0.01, round(option_S*0.05,2)), step=0.5)
    pnl = payoff_covered_call(S_range, stock_cost, option_K, premium)
elif strategy == "Protective Put":
    stock_cost = st.number_input("Stock cost basis ($)", value=float(option_S), step=1.0)
    premium    = st.number_input("Put premium ($)", value=max(0.01, round(option_S*0.05,2)), step=0.5)
    pnl = payoff_protective_put(S_range, stock_cost, option_K, premium)
elif strategy == "Bull Call Spread":
    K2    = st.number_input("Short call strike ($)", value=float(option_K+10), step=1.0)
    prem1 = st.number_input("Long call premium ($)", value=8.0, step=0.5)
    prem2 = st.number_input("Short call premium ($)", value=3.0, step=0.5)
    pnl = payoff_bull_call_spread(S_range, option_K, prem1, K2, prem2)
elif strategy == "Bear Put Spread":
    K2    = st.number_input("Short put strike ($)", value=max(1.0, float(option_K-10)), step=1.0)
    prem1 = st.number_input("Long put premium ($)", value=8.0, step=0.5)
    prem2 = st.number_input("Short put premium ($)", value=3.0, step=0.5)
    pnl = payoff_bear_put_spread(S_range, option_K, prem1, K2, prem2)
elif strategy == "Bull Put Spread":
    K2    = st.number_input("Lower put strike ($)", value=max(1.0, float(option_K-10)), step=1.0)
    prem1 = st.number_input("Higher put premium ($)", value=8.0, step=0.5)
    prem2 = st.number_input("Lower put premium ($)",  value=3.0, step=0.5)
    pnl = payoff_bull_put_spread(S_range, option_K, prem1, K2, prem2)
elif strategy == "Bear Call Spread":
    K2    = st.number_input("Higher call strike ($)", value=float(option_K+10), step=1.0)
    prem1 = st.number_input("Lower call premium ($)", value=8.0, step=0.5)
    prem2 = st.number_input("Higher call premium ($)", value=3.0, step=0.5)
    pnl = payoff_bear_call_spread(S_range, option_K, prem1, K2, prem2)
elif strategy == "Straddle":
    call_p = st.number_input("Call premium ($)", value=8.0, step=0.5)
    put_p  = st.number_input("Put premium ($)",  value=7.0, step=0.5)
    pnl = payoff_straddle(S_range, option_K, call_p, put_p)
elif strategy == "Strangle":
    k_put  = st.number_input("Put strike ($)",   value=max(1.0, float(option_K-10)), step=1.0)
    put_p  = st.number_input("Put premium ($)",  value=4.0, step=0.5)
    k_call = st.number_input("Call strike ($)",  value=float(option_K+10), step=1.0)
    call_p = st.number_input("Call premium ($)", value=4.0, step=0.5)
    pnl = payoff_strangle(S_range, k_put, put_p, k_call, call_p)
elif strategy == "Long Butterfly":
    K1 = st.number_input("Lower strike ($)",  value=max(1.0, float(option_K-10)), step=1.0)
    K2 = st.number_input("Middle strike ($)", value=float(option_K), step=1.0)
    K3 = st.number_input("Upper strike ($)",  value=float(option_K+10), step=1.0)
    p1 = st.number_input("Lower call prem ($)",  value=12.0, step=0.5)
    p2 = st.number_input("Middle call prem ($)", value=6.0,  step=0.5)
    p3 = st.number_input("Upper call prem ($)",  value=2.0,  step=0.5)
    pnl = payoff_long_butterfly(S_range, K1, K2, K3, p1, p2, p3)
elif strategy == "Iron Condor":
    K1 = st.number_input("Long put strike ($)",   value=max(1.0, float(option_K-20)), step=1.0)
    K2 = st.number_input("Short put strike ($)",  value=max(1.0, float(option_K-10)), step=1.0)
    K3 = st.number_input("Short call strike ($)", value=float(option_K+10), step=1.0)
    K4 = st.number_input("Long call strike ($)",  value=float(option_K+20), step=1.0)
    p1 = st.number_input("Long put prem ($)",   value=2.0, step=0.5, key="ic_p1")
    p2 = st.number_input("Short put prem ($)",  value=5.0, step=0.5, key="ic_p2")
    p3 = st.number_input("Short call prem ($)", value=5.0, step=0.5, key="ic_p3")
    p4 = st.number_input("Long call prem ($)",  value=2.0, step=0.5, key="ic_p4")
    pnl = payoff_iron_condor(S_range, K1, K2, K3, K4, p1, p2, p3, p4)

if pnl is not None:
    summary = strategy_summary(S_range, pnl)

    fig_s, ax_s = plt.subplots(figsize=(10, 4))
    ax_s.plot(S_range, pnl, color=ACCENT, lw=2.5, zorder=3)
    ax_s.fill_between(S_range, pnl, 0, where=pnl >= 0, alpha=0.14, color=GREEN, label="Profit zone")
    ax_s.fill_between(S_range, pnl, 0, where=pnl <  0, alpha=0.14, color=RED,   label="Loss zone")
    ax_s.axhline(0,       color="white", ls="--", lw=1)
    ax_s.axvline(option_S, color=GREEN,  ls="--", lw=1, label=f"Spot ${option_S:.0f}")
    ax_s.axvline(option_K, color=AMBER,  ls="--", lw=1, label=f"Strike ${option_K:.0f}")
    for be in summary["breakevens"]:
        ax_s.axvline(be, color=PURPLE, ls=":", lw=1.2)
        ax_s.annotate(f"B/E\n${be:.1f}", (be, ax_s.get_ylim()[0]),
                      fontsize=7, color=PURPLE, ha="center", va="bottom")
    ax_s.set_xlabel("Stock Price at Expiry ($)"); ax_s.set_ylabel("P&L ($)")
    ax_s.set_title(f"{strategy} — Expiry Payoff")
    ax_s.legend(fontsize=8); ax_s.grid(True, alpha=0.25)
    st.pyplot(fig_s); plt.close()

    m1,m2,m3 = st.columns(3)
    m1.metric("Max Profit",  f"${summary['max_profit']:,.2f}" if not np.isinf(summary['max_profit']) else "Unlimited")
    m2.metric("Max Loss",    f"${summary['max_loss']:,.2f}"   if not np.isinf(summary['max_loss'])   else "Unlimited")
    m3.metric("Breakeven(s)",", ".join([f"${b:.1f}" for b in summary["breakevens"]]) if summary["breakevens"] else "None in range")

    desc = DESCRIPTIONS.get(strategy, "")
    if desc:
        st.markdown(
            f'<div style="background:{BG3};border:1px solid {BORDER};border-radius:8px;'
            f'padding:12px 14px;font-size:12px;color:{TEXT2};margin-top:8px;">'
            f'<strong style="color:#dde4f0;">{strategy}</strong> — {desc}</div>',
            unsafe_allow_html=True,
        )

app_footer()
