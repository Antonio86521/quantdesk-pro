import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D  # noqa

from auth import require_login, sidebar_user_widget
from utils import (
    apply_theme, apply_responsive_layout, page_header,
    ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEXT2, BG3, BORDER,
    app_footer,
)
from data_loader import load_option_expiries, load_option_chain, load_spot_price
from options_models import (
    black_scholes_with_greeks, bs_price_only,
    implied_volatility_newton,
    binomial_option_price, monte_carlo_option_price,
    put_call_parity_gap, option_breakeven,
)

st.set_page_config(page_title="Derivatives — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Derivatives Pricer", "Black-Scholes · Binomial · Monte Carlo · Live Chain")
sidebar_user_widget()


def _slbl(text):
    st.markdown(
        f'<div style="font-size:9.5px;color:#3d5068;letter-spacing:1px;'
        f'text-transform:uppercase;font-weight:600;margin:18px 0 10px;">{text}</div>',
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Pricing Inputs")
option_S     = st.sidebar.number_input("Stock Price (S)",        0.01, value=100.0, step=1.0)
option_K     = st.sidebar.number_input("Strike Price (K)",       0.01, value=100.0, step=1.0)
option_T     = st.sidebar.number_input("Time to Maturity (yrs)", 0.01, value=1.0,   step=0.1)
option_r     = st.sidebar.number_input("Risk-Free Rate (%)",     0.0,  20.0, 2.0,   0.1)
option_sigma = st.sidebar.number_input("Volatility (%)",         0.01, 300.0, 20.0, 1.0)
calc_option  = st.sidebar.button("Calculate Option", use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.markdown("## Implied Volatility")
mkt_price = st.sidebar.number_input("Market Option Price", 0.01, value=10.0, step=0.1)
iv_type   = st.sidebar.selectbox("Option Type", ["call", "put"])
calc_iv   = st.sidebar.button("Calculate IV", use_container_width=True)

# ── LIVE CHAIN ────────────────────────────────────────────────────────────────
_slbl("Live Options Chain")
col_tk, col_btn = st.columns([3, 1])
with col_tk:
    chain_ticker = st.text_input("Ticker", value="AAPL")
with col_btn:
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    load_chain_btn = st.button("Load Chain", use_container_width=True)

if load_chain_btn:
    with st.spinner("Fetching options data…"):
        expiries = load_option_expiries(chain_ticker.upper())
    if not expiries:
        st.warning(f"No option expiries found for **{chain_ticker.upper()}**.")
    else:
        spot = load_spot_price(chain_ticker.upper(), source="auto")
        st.markdown(
            f'<div style="font-size:12px;color:{TEXT2};margin-bottom:10px;">'
            f'Spot: <strong style="color:#dde4f0;">${spot:.2f}</strong>&nbsp;·&nbsp;'
            f'{len(expiries)} expiries available</div>',
            unsafe_allow_html=True,
        )
        selected_exp = st.selectbox("Select expiry", expiries)
        with st.spinner("Loading chain…"):
            chain = load_option_chain(chain_ticker.upper(), selected_exp)
        cols_show = ["strike","lastPrice","bid","ask","volume","openInterest","impliedVolatility"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div style="font-size:10px;color:{GREEN};letter-spacing:.5px;text-transform:uppercase;margin-bottom:6px;">Calls</div>', unsafe_allow_html=True)
            df = chain["calls"][cols_show].copy()
            df["impliedVolatility"] = (df["impliedVolatility"] * 100).round(2)
            df["ITM"] = df["strike"] < spot
            st.dataframe(
                df.drop(columns=["ITM"]).style
                .format({"strike":"${:.2f}","lastPrice":"${:.2f}","bid":"${:.2f}","ask":"${:.2f}","impliedVolatility":"{:.2f}%"})
                .apply(lambda row: ["background-color:rgba(14,203,129,0.08)" if df.loc[row.name,"ITM"] else "" for _ in row], axis=1),
                use_container_width=True, height=300,
            )
        with c2:
            st.markdown(f'<div style="font-size:10px;color:{RED};letter-spacing:.5px;text-transform:uppercase;margin-bottom:6px;">Puts</div>', unsafe_allow_html=True)
            df2 = chain["puts"][cols_show].copy()
            df2["impliedVolatility"] = (df2["impliedVolatility"] * 100).round(2)
            df2["ITM"] = df2["strike"] > spot
            st.dataframe(
                df2.drop(columns=["ITM"]).style
                .format({"strike":"${:.2f}","lastPrice":"${:.2f}","bid":"${:.2f}","ask":"${:.2f}","impliedVolatility":"{:.2f}%"})
                .apply(lambda row: ["background-color:rgba(246,70,93,0.08)" if df2.loc[row.name,"ITM"] else "" for _ in row], axis=1),
                use_container_width=True, height=300,
            )
        if "openInterest" in chain["calls"].columns:
            _slbl("Open Interest by Strike")
            oi_c = chain["calls"][["strike","openInterest"]].dropna()
            oi_p = chain["puts"][["strike","openInterest"]].dropna()
            fig_oi, ax_oi = plt.subplots(figsize=(10, 3))
            ax_oi.bar(oi_c["strike"],  oi_c["openInterest"], width=0.8, alpha=0.7, color=GREEN, label="Call OI")
            ax_oi.bar(oi_p["strike"], -oi_p["openInterest"], width=0.8, alpha=0.7, color=RED,   label="Put OI")
            ax_oi.axvline(spot, color=AMBER, lw=1.5, ls="--", label=f"Spot ${spot:.0f}")
            ax_oi.axhline(0, color="white", lw=0.6)
            ax_oi.set_title("Open Interest  (Calls ↑  /  Puts ↓)")
            ax_oi.legend(fontsize=8); ax_oi.grid(True, alpha=0.25, axis="y")
            st.pyplot(fig_oi); plt.close()

st.divider()

# ── PRICING ────────────────────────────────────────────────────────────────────
_slbl("Option Pricing — Black-Scholes · Binomial · Monte Carlo")

if calc_option:
    S = option_S; K = option_K; T = option_T
    r = option_r / 100; sigma = option_sigma / 100
    res = black_scholes_with_greeks(S, K, T, r, sigma)
    call_p, put_p, cdelta, pdelta, gamma, vega, ctheta, ptheta, crho, prho, pitm_c, pitm_p = res
    with st.spinner("Running Binomial & Monte Carlo…"):
        bin_call    = binomial_option_price(S, K, T, r, sigma, 150, "call", False)
        bin_put     = binomial_option_price(S, K, T, r, sigma, 150, "put",  False)
        bin_call_am = binomial_option_price(S, K, T, r, sigma, 150, "call", True)
        bin_put_am  = binomial_option_price(S, K, T, r, sigma, 150, "put",  True)
        mc_call, _, _ = monte_carlo_option_price(S, K, T, r, sigma, "call", 10_000)
        mc_put,  _, _ = monte_carlo_option_price(S, K, T, r, sigma, "put",  10_000)
    parity  = put_call_parity_gap(call_p, put_p, S, K, T, r)
    be_call = option_breakeven("call", K, call_p)
    be_put  = option_breakeven("put",  K, put_p)

    st.dataframe(
        pd.DataFrame({
            "Model":  ["Black-Scholes", "Binomial (European)", "Binomial (American)", "Monte Carlo"],
            "Call":   [call_p, bin_call, bin_call_am, mc_call],
            "Put":    [put_p,  bin_put,  bin_put_am,  mc_put],
        }).style.format({"Call": "${:.4f}", "Put": "${:.4f}"}),
        use_container_width=True, hide_index=True,
    )

    _slbl("Greeks & Probabilities")
    g1,g2,g3,g4,g5,g6 = st.columns(6)
    g1.metric("Call Δ",      f"{cdelta:.4f}")
    g2.metric("Put Δ",       f"{pdelta:.4f}")
    g3.metric("Γ Gamma",     f"{gamma:.6f}")
    g4.metric("ν Vega",      f"{vega:.4f}")
    g5.metric("Call Θ",      f"{ctheta:.4f}")
    g6.metric("Put Θ",       f"{ptheta:.4f}")
    g7,g8,g9,g10,g11,g12 = st.columns(6)
    g7.metric("Call ρ",      f"{crho:.4f}")
    g8.metric("Put ρ",       f"{prho:.4f}")
    g9.metric("P(Call ITM)", f"{pitm_c*100:.2f}%")
    g10.metric("P(Put ITM)", f"{pitm_p*100:.2f}%")
    g11.metric("Call B/E",   f"${be_call:.2f}")
    g12.metric("Put B/E",    f"${be_put:.2f}")

    parity_c = GREEN if abs(parity) < 0.01 else RED
    st.markdown(f'<div style="font-size:12px;margin:8px 0;">Put-Call Parity gap: <strong style="color:{parity_c};">{parity:.6f}</strong></div>', unsafe_allow_html=True)

    _slbl("Option Price vs Stock Price")
    sp = np.linspace(max(1, S * 0.5), S * 1.5, 200)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(sp, [bs_price_only(s, K, T, r, sigma, "call") for s in sp], color=ACCENT, label="Call", lw=2)
    ax.plot(sp, [bs_price_only(s, K, T, r, sigma, "put")  for s in sp], color=PURPLE, label="Put",  lw=2)
    ax.plot(sp, np.maximum(sp-K,0), color=ACCENT, lw=1, ls=":", alpha=0.4, label="Call intrinsic")
    ax.plot(sp, np.maximum(K-sp,0), color=PURPLE, lw=1, ls=":", alpha=0.4, label="Put intrinsic")
    ax.axvline(K, color=AMBER, ls="--", lw=1.2, label="Strike")
    ax.axvline(S, color=GREEN, ls="--", lw=1.2, label="Spot")
    ax.set_xlabel("Stock Price ($)"); ax.set_ylabel("Option Price ($)")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.25)
    st.pyplot(fig); plt.close()

    _slbl("P&L Heatmap — Call Option")
    stock_r = np.linspace(S*0.6, S*1.4, 50); time_r = np.linspace(T, 0.01, 25)
    pnl_grid = np.array([[bs_price_only(sv, K, tv, r, sigma, "call") - call_p
                          for sv in stock_r] for tv in time_r])
    fig6, ax6 = plt.subplots(figsize=(10, 4))
    cmap2 = mcolors.LinearSegmentedColormap.from_list("pnl", [RED, "#131920", GREEN])
    max_abs = max(np.abs(pnl_grid).max(), 1e-6)
    im = ax6.imshow(pnl_grid, cmap=cmap2, aspect="auto",
                    extent=[stock_r[0], stock_r[-1], 0, T],
                    vmin=-max_abs, vmax=max_abs, origin="upper")
    ax6.axvline(K, color=AMBER, ls="--", lw=1.5, label="Strike")
    ax6.axvline(S, color="white", ls="--", lw=1, label="Spot")
    plt.colorbar(im, ax=ax6, label="P&L ($)")
    ax6.set_xlabel("Stock Price ($)"); ax6.set_ylabel("Time to Expiry (yrs)")
    ax6.set_title("Call Option P&L Heatmap"); ax6.legend(fontsize=8)
    st.pyplot(fig6); plt.close()

    _slbl("Greeks Curves")
    delta_c, delta_p, gamma_c, vega_c, theta_c = [], [], [], [], []
    for s in sp:
        rr = black_scholes_with_greeks(s, K, T, r, sigma)
        delta_c.append(rr[2]); delta_p.append(rr[3])
        gamma_c.append(rr[4]); vega_c.append(rr[5]); theta_c.append(rr[6])

    c1,c2 = st.columns(2)
    with c1:
        fig2, ax2 = plt.subplots(figsize=(7,3))
        ax2.plot(sp, delta_c, color=ACCENT, label="Call Δ", lw=1.8)
        ax2.plot(sp, delta_p, color=PURPLE, label="Put Δ",  lw=1.8)
        ax2.axhline(0, color="white", lw=0.6, ls="--"); ax2.axvline(K, color=AMBER, lw=1, ls=":")
        ax2.set_title("Delta"); ax2.legend(fontsize=8); ax2.grid(True, alpha=0.25)
        st.pyplot(fig2); plt.close()
    with c2:
        fig3, ax3 = plt.subplots(figsize=(7,3))
        ax3.plot(sp, gamma_c, color=AMBER, lw=1.8); ax3.axvline(K, color=AMBER, lw=1, ls=":")
        ax3.set_title("Gamma"); ax3.grid(True, alpha=0.25)
        st.pyplot(fig3); plt.close()
    c3,c4 = st.columns(2)
    with c3:
        fig4, ax4 = plt.subplots(figsize=(7,3))
        ax4.plot(sp, vega_c, color=ACCENT2, lw=1.8); ax4.axvline(K, color=AMBER, lw=1, ls=":")
        ax4.set_title("Vega"); ax4.grid(True, alpha=0.25)
        st.pyplot(fig4); plt.close()
    with c4:
        fig5, ax5 = plt.subplots(figsize=(7,3))
        ax5.plot(sp, theta_c, color=RED, lw=1.8)
        ax5.axhline(0, color="white", lw=0.6, ls="--"); ax5.axvline(K, color=AMBER, lw=1, ls=":")
        ax5.set_title("Call Theta"); ax5.grid(True, alpha=0.25)
        st.pyplot(fig5); plt.close()

    _slbl("3D Call Price Surface")
    sr = np.linspace(max(1, S*0.5), S*1.5, 30)
    vr = np.linspace(0.05, max(0.6, sigma*1.5), 30)
    SG, VG = np.meshgrid(sr, vr)
    CS = np.vectorize(lambda s, v: bs_price_only(s, K, T, r, v))(SG, VG)
    fig7 = plt.figure(figsize=(10, 6))
    ax7  = fig7.add_subplot(111, projection="3d")
    surf = ax7.plot_surface(SG, VG*100, CS, cmap="cool", alpha=0.85, edgecolor="none")
    fig7.colorbar(surf, ax=ax7, shrink=0.5, label="Call Price ($)")
    ax7.set_xlabel("Stock Price"); ax7.set_ylabel("Volatility (%)"); ax7.set_zlabel("Call Price")
    ax7.set_title("Call Price Surface")
    st.pyplot(fig7); plt.close()

else:
    st.markdown(
        f'<div style="background:{BG3};border:1px solid {BORDER};border-radius:10px;'
        f'padding:22px;text-align:center;margin:10px 0;">'
        f'<div style="font-size:24px;margin-bottom:10px;">⚙</div>'
        f'<div style="font-size:13px;font-weight:600;margin-bottom:5px;">Option Pricer</div>'
        f'<div style="font-size:12px;color:{TEXT2};">Set inputs in the sidebar and click <strong>Calculate Option</strong>.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.divider()
_slbl("Implied Volatility Calculator")
if calc_iv:
    iv = implied_volatility_newton(mkt_price, option_S, option_K, option_T, option_r/100, iv_type)
    if np.isnan(iv):
        st.error("Could not converge. Try a different market price.")
    else:
        c1,c2,c3 = st.columns(3)
        c1.metric("Implied Volatility", f"{iv*100:.2f}%")
        c2.metric("Option Type", iv_type.capitalize())
        c3.metric("Market Price", f"${mkt_price:.2f}")
        st.success(f"IV of **{iv*100:.2f}%** replicates the observed market price of **${mkt_price:.2f}**.")
        prices_range = np.linspace(max(0.01, mkt_price*0.5), mkt_price*2, 80)
        iv_range = [implied_volatility_newton(p, option_S, option_K, option_T, option_r/100, iv_type) for p in prices_range]
        iv_pct = [v*100 if not np.isnan(v) else np.nan for v in iv_range]
        fig_iv, ax_iv = plt.subplots(figsize=(10, 3))
        ax_iv.plot(prices_range, iv_pct, color=ACCENT, lw=2)
        ax_iv.axvline(mkt_price, color=AMBER, ls="--", lw=1.2, label=f"Current ${mkt_price:.2f}")
        ax_iv.set_xlabel("Market Option Price ($)"); ax_iv.set_ylabel("Implied Volatility (%)")
        ax_iv.set_title("IV vs Market Price"); ax_iv.legend(); ax_iv.grid(True, alpha=0.25)
        st.pyplot(fig_iv); plt.close()
else:
    st.info("Enter a market price in the sidebar and click **Calculate IV**.")

app_footer()

