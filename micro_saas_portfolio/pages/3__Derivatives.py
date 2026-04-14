import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from utils import apply_theme, page_header, ACCENT, ACCENT2, GREEN, RED, YELLOW, MUTED
from data_loader import load_option_expiries, load_option_chain, load_spot_price
from options_models import (
    black_scholes_with_greeks, bs_price_only,
    implied_volatility_newton,
    binomial_option_price, monte_carlo_option_price,
    put_call_parity_gap, option_breakeven,
)

st.set_page_config(page_title="Derivatives", layout="wide", page_icon="📊")
apply_theme()
page_header("Derivatives", "Black-Scholes · Binomial · Monte Carlo · Live Chain")

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

# ── Live Options Chain ────────────────────────────────────────────────────────
st.markdown("### Live Options Chain")

col_tk, col_btn = st.columns([3, 1])
with col_tk:
    chain_ticker = st.text_input("Ticker", value="AAPL", key="chain_ticker")
with col_btn:
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    load_chain_btn = st.button("Load Chain", use_container_width=True)

if load_chain_btn:
    with st.spinner("Fetching options data…"):
        expiries = load_option_expiries(chain_ticker.upper())

    if not expiries:
        st.warning(f"No option expiries found for **{chain_ticker.upper()}**.")
    else:
        spot = load_spot_price(chain_ticker.upper())
        st.markdown(f"**Spot: ${spot:.2f}** &nbsp;|&nbsp; {len(expiries)} expiries available")

        selected_exp = st.selectbox("Select expiry", expiries, key="chain_expiry")

        with st.spinner("Loading chain…"):
            chain = load_option_chain(chain_ticker.upper(), selected_exp)

        calls_df = chain["calls"]
        puts_df  = chain["puts"]

        cols_show = ["strike", "lastPrice", "bid", "ask", "volume", "openInterest", "impliedVolatility"]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Calls**")
            df = calls_df[cols_show].copy()
            df["impliedVolatility"] = (df["impliedVolatility"] * 100).round(2)
            # Highlight ITM rows
            df["ITM"] = df["strike"] < spot
            st.dataframe(
                df.drop(columns=["ITM"]).style
                .format({
                    "strike": "${:.2f}", "lastPrice": "${:.2f}",
                    "bid": "${:.2f}", "ask": "${:.2f}",
                    "impliedVolatility": "{:.2f}%",
                })
                .apply(lambda row: ["background-color:#00e67618" if df.loc[row.name, "ITM"]
                                    else "" for _ in row], axis=1),
                use_container_width=True, height=320,
            )

        with c2:
            st.markdown("**Puts**")
            df2 = puts_df[cols_show].copy()
            df2["impliedVolatility"] = (df2["impliedVolatility"] * 100).round(2)
            df2["ITM"] = df2["strike"] > spot
            st.dataframe(
                df2.drop(columns=["ITM"]).style
                .format({
                    "strike": "${:.2f}", "lastPrice": "${:.2f}",
                    "bid": "${:.2f}", "ask": "${:.2f}",
                    "impliedVolatility": "{:.2f}%",
                })
                .apply(lambda row: ["background-color:#ff174418" if df2.loc[row.name, "ITM"]
                                    else "" for _ in row], axis=1),
                use_container_width=True, height=320,
            )

        # Open interest bar chart
        if not calls_df.empty and "openInterest" in calls_df.columns:
            st.markdown("**Open Interest by Strike**")
            oi_calls = calls_df[["strike", "openInterest"]].dropna().copy()
            oi_puts  = puts_df[["strike",  "openInterest"]].dropna().copy()

            fig_oi, ax_oi = plt.subplots(figsize=(10, 3))
            ax_oi.bar(oi_calls["strike"], oi_calls["openInterest"],
                      width=0.8, alpha=0.7, color=GREEN, label="Call OI")
            ax_oi.bar(oi_puts["strike"], -oi_puts["openInterest"],
                      width=0.8, alpha=0.7, color=RED, label="Put OI")
            ax_oi.axvline(spot, color=YELLOW, lw=1.5, ls="--", label=f"Spot ${spot:.0f}")
            ax_oi.axhline(0, color="white", lw=0.6)
            ax_oi.set_xlabel("Strike"); ax_oi.set_ylabel("Open Interest")
            ax_oi.set_title("Open Interest (Calls ↑ / Puts ↓)")
            ax_oi.legend(fontsize=8); ax_oi.grid(True, alpha=0.3, axis="y")
            st.pyplot(fig_oi); plt.close()

st.markdown("---")

# ── BS / Binomial / MC Pricing ────────────────────────────────────────────────
st.markdown("### Option Pricing — BS · Binomial · Monte Carlo")

if calc_option:
    S = option_S; K = option_K; T = option_T
    r = option_r / 100; sigma = option_sigma / 100

    res = black_scholes_with_greeks(S, K, T, r, sigma)
    call_p, put_p, cdelta, pdelta, gamma, vega, ctheta, ptheta, crho, prho, pitm_c, pitm_p = res

    with st.spinner("Running Binomial & Monte Carlo…"):
        bin_call = binomial_option_price(S, K, T, r, sigma, 150, "call", False)
        bin_put  = binomial_option_price(S, K, T, r, sigma, 150, "put",  False)
        bin_call_am = binomial_option_price(S, K, T, r, sigma, 150, "call", True)
        bin_put_am  = binomial_option_price(S, K, T, r, sigma, 150, "put",  True)
        mc_call, _, _ = monte_carlo_option_price(S, K, T, r, sigma, "call", 10_000)
        mc_put,  _, _ = monte_carlo_option_price(S, K, T, r, sigma, "put",  10_000)

    parity = put_call_parity_gap(call_p, put_p, S, K, T, r)
    be_call = option_breakeven("call", K, call_p)
    be_put  = option_breakeven("put",  K, put_p)

    st.markdown("#### Model Comparison")
    models_df = pd.DataFrame({
        "Model":   ["Black-Scholes", "Binomial (Eur)", "Binomial (Am)", "Monte Carlo"],
        "Call":    [call_p, bin_call, bin_call_am, mc_call],
        "Put":     [put_p,  bin_put,  bin_put_am,  mc_put],
    })
    st.dataframe(
        models_df.style.format({"Call": "${:.4f}", "Put": "${:.4f}"}),
        use_container_width=True,
    )

    st.markdown("#### Greeks & Probabilities")
    g1, g2, g3, g4, g5, g6 = st.columns(6)
    g1.metric("Call Δ", f"{cdelta:.4f}")
    g2.metric("Put Δ",  f"{pdelta:.4f}")
    g3.metric("Γ Gamma", f"{gamma:.6f}")
    g4.metric("ν Vega",  f"{vega:.4f}")
    g5.metric("Call Θ", f"{ctheta:.4f}")
    g6.metric("Put Θ",  f"{ptheta:.4f}")

    g7, g8, g9, g10, g11, g12 = st.columns(6)
    g7.metric("Call ρ",     f"{crho:.4f}")
    g8.metric("Put ρ",      f"{prho:.4f}")
    g9.metric("P(Call ITM)",  f"{pitm_c*100:.2f}%")
    g10.metric("P(Put ITM)",  f"{pitm_p*100:.2f}%")
    g11.metric("Call B/E",   f"${be_call:.2f}")
    g12.metric("Put B/E",    f"${be_put:.2f}")

    parity_color = "green" if abs(parity) < 0.01 else "red"
    st.markdown(
        f"Put-Call Parity gap: "
        f"<span style='color:{'#00e676' if abs(parity)<0.01 else '#ff1744'}; font-weight:700;'>"
        f"{parity:.6f}</span>",
        unsafe_allow_html=True,
    )

    # ── Option price vs S ─────────────────────────────────────────────────────
    st.markdown("#### Option Prices vs Stock Price")
    sp = np.linspace(max(1, S * 0.5), S * 1.5, 200)
    cp2 = [bs_price_only(s, K, T, r, sigma, "call") for s in sp]
    pp2 = [bs_price_only(s, K, T, r, sigma, "put")  for s in sp]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(sp, cp2, color=ACCENT,  label="Call", lw=2)
    ax.plot(sp, pp2, color=ACCENT2, label="Put",  lw=2)
    ax.plot(sp, np.maximum(sp - K, 0), color=ACCENT,  lw=1, ls=":", alpha=0.5, label="Call intrinsic")
    ax.plot(sp, np.maximum(K - sp, 0), color=ACCENT2, lw=1, ls=":", alpha=0.5, label="Put intrinsic")
    ax.axvline(K, color=YELLOW, ls="--", lw=1.2, label="Strike")
    ax.axvline(S, color=GREEN,  ls="--", lw=1.2, label="Spot")
    ax.set_xlabel("Stock Price"); ax.set_ylabel("Option Price")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    st.pyplot(fig); plt.close()

    # ── P&L Heatmap ───────────────────────────────────────────────────────────
    st.markdown("#### P&L Heatmap — Call Option")
    stock_range = np.linspace(S * 0.6, S * 1.4, 50)
    time_range  = np.linspace(T, 0.01, 25)
    pnl_grid    = np.zeros((len(time_range), len(stock_range)))
    for i, t_val in enumerate(time_range):
        for j, s_val in enumerate(stock_range):
            pnl_grid[i, j] = bs_price_only(s_val, K, t_val, r, sigma, "call") - call_p

    fig6, ax6 = plt.subplots(figsize=(10, 4))
    cmap2   = mcolors.LinearSegmentedColormap.from_list("pnl", [RED, "#111827", GREEN])
    max_abs = np.abs(pnl_grid).max()
    im = ax6.imshow(
        pnl_grid, cmap=cmap2, aspect="auto",
        extent=[stock_range[0], stock_range[-1], 0, T],
        vmin=-max_abs, vmax=max_abs, origin="upper",
    )
    ax6.axvline(K, color=YELLOW, ls="--", lw=1.5, label="Strike")
    ax6.axvline(S, color="white", ls="--", lw=1,  label="Spot")
    plt.colorbar(im, ax=ax6, label="P&L ($)")
    ax6.set_xlabel("Stock Price"); ax6.set_ylabel("Time to Expiry (yrs)")
    ax6.set_title("Call Option P&L Heatmap"); ax6.legend(fontsize=8)
    st.pyplot(fig6); plt.close()

    # ── Greeks Curves ─────────────────────────────────────────────────────────
    st.markdown("#### Greeks Curves vs Stock Price")
    delta_c, delta_p, gamma_c, vega_c, theta_c = [], [], [], [], []
    for s in sp:
        rr = black_scholes_with_greeks(s, K, T, r, sigma)
        delta_c.append(rr[2]); delta_p.append(rr[3])
        gamma_c.append(rr[4]); vega_c.append(rr[5]); theta_c.append(rr[6])

    col1, col2 = st.columns(2)
    with col1:
        fig2, ax2 = plt.subplots(figsize=(10, 3))
        ax2.plot(sp, delta_c, color=ACCENT,  label="Call Δ", lw=1.8)
        ax2.plot(sp, delta_p, color=ACCENT2, label="Put Δ",  lw=1.8)
        ax2.axhline(0, color="white", lw=0.6, ls="--")
        ax2.axvline(K, color=YELLOW, lw=1, ls=":")
        ax2.set_title("Delta"); ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)
        st.pyplot(fig2); plt.close()

    with col2:
        fig3, ax3 = plt.subplots(figsize=(10, 3))
        ax3.plot(sp, gamma_c, color=YELLOW)
        ax3.axvline(K, color=YELLOW, lw=1, ls=":")
        ax3.set_title("Gamma"); ax3.grid(True, alpha=0.3)
        st.pyplot(fig3); plt.close()

    col3, col4 = st.columns(2)
    with col3:
        fig4, ax4 = plt.subplots(figsize=(10, 3))
        ax4.plot(sp, vega_c, color=ACCENT2)
        ax4.axvline(K, color=YELLOW, lw=1, ls=":")
        ax4.set_title("Vega"); ax4.grid(True, alpha=0.3)
        st.pyplot(fig4); plt.close()

    with col4:
        fig5, ax5 = plt.subplots(figsize=(10, 3))
        ax5.plot(sp, theta_c, color=RED)
        ax5.axhline(0, color="white", lw=0.6, ls="--")
        ax5.axvline(K, color=YELLOW, lw=1, ls=":")
        ax5.set_title("Call Theta"); ax5.grid(True, alpha=0.3)
        st.pyplot(fig5); plt.close()

    # ── 3D Surface ────────────────────────────────────────────────────────────
    st.markdown("#### 3D Call Price Surface")
    from mpl_toolkits.mplot3d import Axes3D  # noqa
    sr = np.linspace(max(1, S * 0.5), S * 1.5, 30)
    vr = np.linspace(0.05, max(0.6, sigma * 1.5), 30)
    SG, VG = np.meshgrid(sr, vr)
    CS = np.vectorize(lambda s, v: bs_price_only(s, K, T, r, v))(SG, VG)
    fig7 = plt.figure(figsize=(10, 6))
    ax7  = fig7.add_subplot(111, projection="3d")
    surf = ax7.plot_surface(SG, VG * 100, CS, cmap="cool", alpha=0.85, edgecolor="none")
    fig7.colorbar(surf, ax=ax7, shrink=0.5, label="Call Price ($)")
    ax7.set_xlabel("Stock Price"); ax7.set_ylabel("Volatility (%)"); ax7.set_zlabel("Call Price")
    ax7.set_title("Call Price Surface")
    st.pyplot(fig7); plt.close()

else:
    st.info("Enter pricing inputs in the sidebar and click **Calculate Option**.")

# ── IV Calculator ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Implied Volatility Calculator")

if calc_iv:
    iv = implied_volatility_newton(mkt_price, option_S, option_K, option_T, option_r / 100, iv_type)
    if np.isnan(iv):
        st.error("Could not converge. Try a different market price or wider bounds.")
    else:
        col_iv1, col_iv2, col_iv3 = st.columns(3)
        col_iv1.metric("Implied Volatility", f"{iv*100:.2f}%")
        col_iv2.metric("Option Type", iv_type.capitalize())
        col_iv3.metric("Market Price", f"${mkt_price:.2f}")
        st.success(
            f"IV of **{iv*100:.2f}%** makes the BS model price match the observed market price of **${mkt_price:.2f}**."
        )

        # IV sensitivity: how IV changes with market price
        prices_range = np.linspace(max(0.01, mkt_price * 0.5), mkt_price * 2, 80)
        iv_range = [
            implied_volatility_newton(p, option_S, option_K, option_T, option_r / 100, iv_type)
            for p in prices_range
        ]
        iv_range = [v * 100 if not np.isnan(v) else np.nan for v in iv_range]

        fig_iv, ax_iv = plt.subplots(figsize=(10, 3))
        ax_iv.plot(prices_range, iv_range, color=ACCENT, lw=2)
        ax_iv.axvline(mkt_price, color=YELLOW, ls="--", lw=1.2, label=f"Current ${mkt_price:.2f}")
        ax_iv.set_xlabel("Market Option Price"); ax_iv.set_ylabel("Implied Volatility (%)")
        ax_iv.set_title("IV vs Market Price")
        ax_iv.legend(); ax_iv.grid(True, alpha=0.3)
        st.pyplot(fig_iv); plt.close()
else:
    st.info("Enter a market price and click **Calculate IV**.")