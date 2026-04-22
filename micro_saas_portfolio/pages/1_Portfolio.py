"""1_Portfolio.py — Portfolio Analytics"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker

from auth import require_login, sidebar_user_widget
from utils import (
    apply_theme, apply_responsive_layout, page_header, section_header,
    metric_row, stat_table, chart_card, chart_card_close, info_panel, empty_state,
    PALETTE, ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEAL,
    TEXT, TEXT2, TEXT3, BG2, BG3, BG4, BG5, MPL_BORDER,
    app_footer, safe_pct, safe_num, fmt_dollar, colour_pct,
)
from data_loader import load_close_series, load_price_history, load_news
from analytics import (
    annualized_return, annualized_vol, max_drawdown_from_returns,
    sortino_ratio, calmar_ratio, omega_ratio, gain_to_pain,
    return_skew, return_kurtosis,
    historical_var, cvar, parametric_var,
    compute_alpha_beta, tracking_stats,
    covariance_matrix, marginal_vol_contribution,
    sma, ema, rsi, macd, bollinger_bands, atr, obv, rolling_vol,
)

st.set_page_config(page_title="Portfolio Analytics — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Portfolio Analytics", "Performance · Attribution · Risk · Technicals")
sidebar_user_widget()


def _set_clicked():
    st.session_state["analyze_portfolio_clicked"] = True


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Portfolio Inputs")
tickers_input    = st.sidebar.text_input("Tickers (comma-separated)", "AAPL,MSFT,NVDA,GOOGL,SPY")
shares_input     = st.sidebar.text_input("Shares", "20,15,10,25,50")
buy_prices_input = st.sidebar.text_input("Buy Prices ($)", "182,380,650,160,490")
period           = st.sidebar.selectbox("Lookback Period", ["3mo","6mo","1y","2y","5y"], index=2)
risk_free_rate   = st.sidebar.number_input("Risk-Free Rate (%)", 0.0, 15.0, 2.0, 0.1)
benchmark_ticker = st.sidebar.selectbox("Benchmark", ["SPY","QQQ","DIA","IWM"])
st.sidebar.button("Analyze Portfolio", use_container_width=True, on_click=_set_clicked)

if not st.session_state.get("analyze_portfolio_clicked", False):
    empty_state("📈", "Portfolio Analytics",
                "Enter your tickers, shares and buy prices in the sidebar, then click <strong>Analyze Portfolio</strong> to begin.")
    st.stop()

# ── Parse ──────────────────────────────────────────────────────────────────────
try:
    tickers    = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    shares     = [float(x) for x in shares_input.split(",") if x.strip()]
    buy_prices = [float(x) for x in buy_prices_input.split(",") if x.strip()]
except ValueError:
    st.error("Could not parse inputs — check shares and buy prices are numbers.")
    st.stop()

if not (len(tickers) == len(shares) == len(buy_prices)):
    st.error("Tickers, shares and buy prices must have the same number of entries.")
    st.stop()

# ── Load ───────────────────────────────────────────────────────────────────────
with st.spinner("Loading market data…"):
    prices = pd.DataFrame()
    for t in tickers:
        s = load_close_series(t, period=period, source="auto")
        if s is None or s.empty:
            st.error(f"No price data for **{t}**."); st.stop()
        prices[t] = s
    prices = prices.dropna()
    if prices.empty:
        st.error("No aligned price data."); st.stop()
    bench_series = load_close_series(benchmark_ticker, period=period, source="auto")
    bench_series = pd.Series(bench_series).reindex(prices.index).dropna() if bench_series is not None else pd.Series()

# ── Compute ────────────────────────────────────────────────────────────────────
latest   = prices.iloc[-1]
sh       = np.array(shares[:len(tickers)])
bp       = np.array(buy_prices[:len(tickers)])
pos_val  = latest.values * sh
cost     = bp * sh
upnl     = pos_val - cost
upnl_pct = upnl / cost
total_v  = pos_val.sum()
total_c  = cost.sum()
total_u  = upnl.sum()
weights  = pos_val / total_v

ret      = prices.pct_change().dropna()
port_ret = ret.dot(weights)
total_r  = (1 + port_ret).prod() - 1
ann_r    = annualized_return(port_ret)
ann_v    = annualized_vol(port_ret)
rf       = risk_free_rate / 100
sharpe   = (ann_r - rf) / ann_v if ann_v else np.nan
max_dd, drawdown = max_drawdown_from_returns(port_ret)
sortino  = sortino_ratio(ann_r, rf, port_ret)
calmar   = calmar_ratio(ann_r, max_dd)
omega    = omega_ratio(port_ret)
gtp      = gain_to_pain(port_ret)
sk       = return_skew(port_ret)
kurt     = return_kurtosis(port_ret)

hist_v95 = historical_var(port_ret, 0.95)
hist_cv  = cvar(port_ret, hist_v95)
param_v  = parametric_var(port_ret, 0.95)

bench_ret = bench_series.pct_change().dropna() if not bench_series.empty else pd.Series()
alpha, beta, r2, aligned = compute_alpha_beta(port_ret, bench_ret) if not bench_ret.empty else (np.nan,np.nan,np.nan,None)
te, ir = tracking_stats(aligned) if aligned is not None and not aligned.empty else (np.nan,np.nan)

asset_ret   = (prices.iloc[-1] / prices.iloc[0]) - 1
contrib_ret = weights * asset_ret.reindex(tickers).values
cov_ann     = covariance_matrix(ret)
vol_contrib = marginal_vol_contribution(weights, cov_ann.values)

norm_port  = (prices * sh).sum(axis=1); norm_port /= norm_port.iloc[0]
norm_bench = bench_series / bench_series.iloc[0] if not bench_series.empty else pd.Series()


# ── OVERVIEW METRICS ──────────────────────────────────────────────────────────
section_header("Portfolio Overview")

# Row 1 — value metrics
pnl_pos = total_u >= 0
st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:12px;">
  <div class="qd-metric">
    <div class="qd-metric-label">Portfolio Value</div>
    <div class="qd-metric-value">{fmt_dollar(total_v)}</div>
    <div class="qd-metric-delta {'up' if pnl_pos else 'dn'}" style="font-size:11.5px;margin-top:6px;">
      {'+' if pnl_pos else ''}{fmt_dollar(total_u)} unrealised P&L
    </div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">Total Return</div>
    <div class="qd-metric-value" style="color:{'#0ec97d' if total_r>=0 else '#f5415a'};">{safe_pct(total_r)}</div>
    <div class="qd-metric-delta nu">{period} lookback</div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">Ann. Return</div>
    <div class="qd-metric-value" style="color:{'#0ec97d' if ann_r>=0 else '#f5415a'};">{safe_pct(ann_r)}</div>
    <div class="qd-metric-delta nu">Annualised</div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">Invested Capital</div>
    <div class="qd-metric-value">{fmt_dollar(total_c)}</div>
    <div class="qd-metric-delta {'up' if pnl_pos else 'dn'}">{safe_pct(total_u/total_c if total_c else 0)} return on cost</div>
  </div>
</div>

<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:12px;">
  <div class="qd-metric">
    <div class="qd-metric-label">Sharpe Ratio</div>
    <div class="qd-metric-value" style="color:{'#0ec97d' if not np.isnan(sharpe) and sharpe>1 else '#e2eaf6'};">{safe_num(sharpe)}</div>
    <div class="qd-metric-delta {'up' if not np.isnan(sharpe) and sharpe>1 else 'nu'}">{'Above 1.0 threshold' if not np.isnan(sharpe) and sharpe>1 else 'Risk-adjusted return'}</div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">Sortino Ratio</div>
    <div class="qd-metric-value">{safe_num(sortino)}</div>
    <div class="qd-metric-delta nu">Downside-adjusted</div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">Max Drawdown</div>
    <div class="qd-metric-value" style="color:#f5415a;">{safe_pct(max_dd)}</div>
    <div class="qd-metric-delta dn">Peak to trough</div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">Ann. Volatility</div>
    <div class="qd-metric-value">{safe_pct(ann_v)}</div>
    <div class="qd-metric-delta nu">Realised vol</div>
  </div>
</div>

<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
  <div class="qd-metric">
    <div class="qd-metric-label">Alpha (Ann.)</div>
    <div class="qd-metric-value" style="color:{'#0ec97d' if not np.isnan(alpha) and alpha>0 else '#f5415a'};">{safe_pct(alpha)}</div>
    <div class="qd-metric-delta nu">vs {benchmark_ticker}</div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">Beta</div>
    <div class="qd-metric-value">{safe_num(beta)}</div>
    <div class="qd-metric-delta nu">Market sensitivity</div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">VaR 95%</div>
    <div class="qd-metric-value" style="color:#f5415a;">{safe_pct(hist_v95)}</div>
    <div class="qd-metric-delta nu">Historical daily</div>
  </div>
  <div class="qd-metric">
    <div class="qd-metric-label">CVaR 95%</div>
    <div class="qd-metric-value" style="color:#f5415a;">{safe_pct(hist_cv)}</div>
    <div class="qd-metric-delta nu">Expected shortfall</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Extended stats expander
with st.expander("Extended Risk Statistics"):
    cols = st.columns(4)
    ext_stats = [
        ("Calmar Ratio", safe_num(calmar)), ("Omega Ratio", safe_num(omega)),
        ("Gain / Pain", safe_num(gtp)), ("R² vs Bench", safe_num(r2, 3)),
        ("Skewness", safe_num(sk, 3)), ("Excess Kurtosis", safe_num(kurt, 3)),
        ("Param VaR 95%", safe_pct(param_v)), ("Tracking Error", safe_pct(te)),
        ("Info Ratio", safe_num(ir)), ("Calmar", safe_num(calmar)),
    ]
    for i, (label, val) in enumerate(ext_stats):
        cols[i % 4].metric(label, val)

st.divider()

# ── PERFORMANCE CHARTS ─────────────────────────────────────────────────────────
section_header("Performance")

left_c, right_c = st.columns([3, 1.1])

with left_c:
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(norm_port.index, norm_port.values, color=ACCENT, lw=2.2, label="Portfolio", zorder=4)
    if not norm_bench.empty:
        bench_aligned = norm_bench.reindex(norm_port.index).ffill()
        ax.plot(bench_aligned.index, bench_aligned.values, color="#344d68", lw=1.4, ls="--", label=benchmark_ticker, zorder=3)
        ax.fill_between(norm_port.index, norm_port.values, bench_aligned.values,
                        where=norm_port.values >= bench_aligned.values, alpha=0.09, color=GREEN)
        ax.fill_between(norm_port.index, norm_port.values, bench_aligned.values,
                        where=norm_port.values < bench_aligned.values, alpha=0.09, color=RED)
    ax.axhline(1, color="#1a2535", lw=0.8, ls=":")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.2f}x"))
    ax.set_title("Growth of $1", loc="left")
    ax.legend(framealpha=0.8, loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

with right_c:
    fig2, ax2 = plt.subplots(figsize=(4.5, 4.5))
    wedges, texts, autotexts = ax2.pie(
        weights, labels=tickers, autopct="%1.1f%%",
        colors=PALETTE[:len(tickers)],
        startangle=90,
        wedgeprops=dict(edgecolor="#0d1117", linewidth=2, width=0.65),
        pctdistance=0.8,
    )
    for at in autotexts:
        at.set_fontsize(9); at.set_color("#e2eaf6")
    for t in texts:
        t.set_fontsize(9); t.set_color("#8ba3bd")
    ax2.set_title("Allocation", loc="left")
    circle = plt.Circle((0, 0), 0.35, fc="#0d1117")
    ax2.add_patch(circle)
    fig2.tight_layout()
    st.pyplot(fig2, use_container_width=True)
    plt.close()

# Drawdown + Distribution
dd_col, dist_col = st.columns(2)
with dd_col:
    fig3, ax3 = plt.subplots(figsize=(7.5, 3.2))
    ax3.fill_between(drawdown.index, drawdown.values * 100, 0, color=RED, alpha=0.2)
    ax3.plot(drawdown.index, drawdown.values * 100, color=RED, lw=1.5)
    ax3.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax3.set_title("Portfolio Drawdown", loc="left")
    ax3.grid(True, alpha=0.3)
    fig3.tight_layout()
    st.pyplot(fig3, use_container_width=True)
    plt.close()

with dist_col:
    fig4, ax4 = plt.subplots(figsize=(7.5, 3.2))
    n_bins = min(50, len(port_ret) // 3)
    ax4.hist(port_ret * 100, bins=n_bins, color=ACCENT, alpha=0.75, edgecolor="#0d1117")
    ax4.axvline(hist_v95 * 100, color=RED, lw=1.6, ls="--", label=f"VaR 95%: {hist_v95:.2%}")
    ax4.axvline(hist_cv * 100,  color=AMBER, lw=1.6, ls="--", label=f"CVaR: {hist_cv:.2%}")
    ax4.xaxis.set_major_formatter(mticker.PercentFormatter())
    ax4.set_title("Daily Return Distribution", loc="left")
    ax4.legend(framealpha=0.8)
    ax4.grid(True, alpha=0.3)
    fig4.tight_layout()
    st.pyplot(fig4, use_container_width=True)
    plt.close()

st.divider()

# ── ROLLING METRICS ────────────────────────────────────────────────────────────
section_header("Rolling Analysis")
rol1, rol2 = st.columns(2)

with rol1:
    from analytics import rolling_sharpe, rolling_beta, rolling_corr
    roll_v = rolling_vol(port_ret, 20) * 100
    roll_s = rolling_sharpe(port_ret, rf=rf, window=20)

    fig5, (ax5a, ax5b) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    ax5a.plot(roll_v.index, roll_v.values, color=AMBER, lw=1.6)
    ax5a.fill_between(roll_v.index, roll_v.values, alpha=0.12, color=AMBER)
    ax5a.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax5a.set_title("Rolling 20D Volatility", loc="left")
    ax5a.grid(True, alpha=0.3)

    ax5b.plot(roll_s.index, roll_s.values, color=ACCENT, lw=1.6)
    ax5b.axhline(0, color="#1a2535", lw=0.8)
    ax5b.axhline(1, color=GREEN, lw=0.8, ls="--", alpha=0.5)
    ax5b.set_title("Rolling 20D Sharpe", loc="left")
    ax5b.grid(True, alpha=0.3)
    fig5.tight_layout()
    st.pyplot(fig5, use_container_width=True)
    plt.close()

with rol2:
    if not bench_ret.empty:
        roll_b = rolling_beta(port_ret, bench_ret, 20)
        roll_c = rolling_corr(port_ret, bench_ret, 20)

        fig6, (ax6a, ax6b) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
        ax6a.plot(roll_b.index, roll_b.values, color=PURPLE, lw=1.6)
        ax6a.axhline(1, color="#344d68", lw=0.8, ls="--")
        ax6a.set_title(f"Rolling Beta vs {benchmark_ticker}", loc="left")
        ax6a.grid(True, alpha=0.3)

        ax6b.plot(roll_c.index, roll_c.values, color=TEAL, lw=1.6)
        ax6b.set_ylim(-1, 1)
        ax6b.axhline(0, color="#1a2535", lw=0.8)
        ax6b.set_title("Rolling Correlation", loc="left")
        ax6b.grid(True, alpha=0.3)
        fig6.tight_layout()
        st.pyplot(fig6, use_container_width=True)
        plt.close()
    else:
        st.info("Benchmark data unavailable for rolling metrics.")

st.divider()

# ── CORRELATION + CONTRIBUTION ─────────────────────────────────────────────────
section_header("Risk Attribution")
corr_c, contrib_c = st.columns(2)

with corr_c:
    if len(tickers) > 1:
        corr = ret.corr()
        fig7, ax7 = plt.subplots(figsize=(max(5, len(tickers)*1.4), max(4, len(tickers)*1.1)))
        cmap = mcolors.LinearSegmentedColormap.from_list("rg", [RED, "#131920", ACCENT])
        im = ax7.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1, aspect="auto")
        ax7.set_xticks(range(len(tickers))); ax7.set_xticklabels(tickers, rotation=45, ha="right")
        ax7.set_yticks(range(len(tickers))); ax7.set_yticklabels(tickers)
        for i in range(len(tickers)):
            for j in range(len(tickers)):
                ax7.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center",
                         color="white", fontsize=9.5, fontweight="600")
        plt.colorbar(im, ax=ax7, fraction=0.04, pad=0.03)
        ax7.set_title("Asset Correlation Matrix", loc="left")
        fig7.tight_layout()
        st.pyplot(fig7, use_container_width=True)
        plt.close()

with contrib_c:
    hdf = pd.DataFrame({
        "Ticker":       tickers,
        "Weight":       weights * 100,
        "Asset Return": asset_ret.reindex(tickers).values * 100,
        "Contribution": contrib_ret * 100,
        "Vol Contrib":  vol_contrib * 100,
    })

    fig8, axes8 = plt.subplots(1, 2, figsize=(8, max(3.5, len(tickers)*0.7)))
    axes8[0].barh(hdf["Ticker"], hdf["Weight"], color=PALETTE[:len(tickers)], edgecolor="#0d1117", height=0.65)
    axes8[0].set_title("Weight (%)", loc="left"); axes8[0].grid(True, alpha=0.3, axis="x")

    colors_ret = [GREEN if v >= 0 else RED for v in hdf["Asset Return"]]
    axes8[1].barh(hdf["Ticker"], hdf["Asset Return"], color=colors_ret, edgecolor="#0d1117", height=0.65)
    axes8[1].axvline(0, color="#1a2535", lw=0.8)
    axes8[1].set_title(f"Return {period} (%)", loc="left"); axes8[1].grid(True, alpha=0.3, axis="x")
    fig8.tight_layout()
    st.pyplot(fig8, use_container_width=True)
    plt.close()

st.divider()

# ── TECHNICAL SNAPSHOT ─────────────────────────────────────────────────────────
section_header("Technical Analysis")

tech_t = st.selectbox("Select ticker", tickers)
tech_df = load_price_history(tech_t, period=period, source="auto")

if not tech_df.empty and "Close" in tech_df.columns:
    tc = tech_df["Close"]
    sma20_v = sma(tc, 20); sma50_v = sma(tc, 50)
    rsi14   = rsi(tc, 14)
    macd_l, macd_s, macd_h = macd(tc)
    bb_mid, bb_up, bb_lo   = bollinger_bands(tc)

    rsi_now = float(rsi14.iloc[-1]) if not rsi14.empty else np.nan
    rsi_col = RED if not np.isnan(rsi_now) and rsi_now > 70 else (GREEN if not np.isnan(rsi_now) and rsi_now < 30 else TEXT)

    # RSI badge
    st.markdown(
        f"""<div style="display:flex;gap:10px;margin-bottom:14px;align-items:center;">
        <span style="font-family:'DM Mono',monospace;font-size:15px;font-weight:500;color:#e2eaf6;">{tech_t}</span>
        <span style="font-family:'DM Mono',monospace;font-size:13px;color:#8ba3bd;">${float(tc.iloc[-1]):,.2f}</span>
        <span style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);
                     border-radius:5px;padding:3px 9px;font-size:11px;color:{rsi_col};">
          RSI {rsi_now:.1f}
        </span>
      </div>""",
        unsafe_allow_html=True,
    )

    fig9, ax9 = plt.subplots(figsize=(13, 4.5))
    ax9.plot(tc.index,       tc.values,       color=ACCENT,  lw=2,   label="Close",    zorder=4)
    ax9.plot(sma20_v.index,  sma20_v.values,  color=AMBER,   lw=1.3, label="SMA 20",   zorder=3)
    ax9.plot(sma50_v.index,  sma50_v.values,  color=ACCENT2, lw=1.3, label="SMA 50",   zorder=3)
    ax9.plot(bb_up.index,    bb_up.values,    color=GREEN,   lw=1,   ls="--", alpha=0.7, label="BB Upper")
    ax9.plot(bb_lo.index,    bb_lo.values,    color=RED,     lw=1,   ls="--", alpha=0.7, label="BB Lower")
    ax9.fill_between(bb_up.index, bb_up.values, bb_lo.values, alpha=0.04, color=ACCENT)
    ax9.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax9.set_title(f"{tech_t} — Price & Bollinger Bands", loc="left")
    ax9.legend(framealpha=0.85, ncol=5, fontsize=8.5)
    ax9.grid(True, alpha=0.3)
    fig9.tight_layout()
    st.pyplot(fig9, use_container_width=True)
    plt.close()

    ta1, ta2 = st.columns(2)
    with ta1:
        fig10, ax10 = plt.subplots(figsize=(7.5, 3))
        ax10.plot(rsi14.index, rsi14.values, color=ACCENT, lw=1.8)
        ax10.axhline(70, color=RED,   ls="--", lw=1.2, label="Overbought 70")
        ax10.axhline(30, color=GREEN, ls="--", lw=1.2, label="Oversold 30")
        ax10.fill_between(rsi14.index, rsi14.values, 70, where=rsi14.values >= 70, alpha=0.12, color=RED)
        ax10.fill_between(rsi14.index, rsi14.values, 30, where=rsi14.values <= 30, alpha=0.12, color=GREEN)
        ax10.set_ylim(0, 100); ax10.set_title("RSI (14)", loc="left")
        ax10.legend(framealpha=0.8); ax10.grid(True, alpha=0.3)
        fig10.tight_layout()
        st.pyplot(fig10, use_container_width=True)
        plt.close()

    with ta2:
        fig11, ax11 = plt.subplots(figsize=(7.5, 3))
        ax11.plot(macd_l.index, macd_l.values,  color=ACCENT, lw=1.8, label="MACD")
        ax11.plot(macd_s.index, macd_s.values,  color=AMBER,  lw=1.5, label="Signal")
        clrs = [GREEN if v >= 0 else RED for v in macd_h.values]
        ax11.bar(macd_h.index, macd_h.values, color=clrs, alpha=0.5, width=1)
        ax11.axhline(0, color="#1a2535", lw=0.8)
        ax11.set_title("MACD", loc="left"); ax11.legend(framealpha=0.8)
        ax11.grid(True, alpha=0.3)
        fig11.tight_layout()
        st.pyplot(fig11, use_container_width=True)
        plt.close()

    if "Volume" in tech_df.columns and tech_df["Volume"].sum() > 0:
        v1, v2 = st.columns(2)
        with v1:
            fig12, ax12 = plt.subplots(figsize=(7.5, 2.5))
            vol_s = tech_df["Volume"]
            clrs_v = [GREEN if tech_df["Close"].iloc[i] >= tech_df["Close"].iloc[i-1] else RED
                      for i in range(1, len(vol_s))]
            clrs_v = [TEXT2] + clrs_v
            ax12.bar(tech_df.index, vol_s, color=clrs_v, alpha=0.7, width=1)
            avg_vol = float(vol_s.mean())
            ax12.axhline(avg_vol, color=AMBER, lw=1, ls="--", label=f"Avg {avg_vol/1e6:.1f}M")
            ax12.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
            ax12.set_title("Volume", loc="left"); ax12.legend(); ax12.grid(True, alpha=0.3, axis="y")
            fig12.tight_layout()
            st.pyplot(fig12, use_container_width=True)
            plt.close()
        with v2:
            obv_s = obv(tech_df["Close"], tech_df["Volume"])
            fig13, ax13 = plt.subplots(figsize=(7.5, 2.5))
            ax13.plot(obv_s.index, obv_s.values, color=GREEN, lw=1.8)
            ax13.fill_between(obv_s.index, obv_s.values, alpha=0.1, color=GREEN)
            ax13.set_title("On-Balance Volume (OBV)", loc="left"); ax13.grid(True, alpha=0.3)
            fig13.tight_layout()
            st.pyplot(fig13, use_container_width=True)
            plt.close()

st.divider()

# ── HOLDINGS TABLE ─────────────────────────────────────────────────────────────
section_header("Holdings Breakdown")

hdf_display = pd.DataFrame({
    "Ticker":          tickers,
    "Shares":          sh,
    "Avg Cost":        bp,
    "Current Price":   latest.values,
    "Market Value":    pos_val,
    "Unrealised P&L":  upnl,
    "P&L %":           upnl_pct * 100,
    "Weight %":        weights * 100,
    "Period Return %": asset_ret.reindex(tickers).values * 100,
    "Vol Contrib %":   vol_contrib * 100,
})

st.dataframe(
    hdf_display.style
    .format({
        "Avg Cost":        "${:,.2f}",
        "Current Price":   "${:,.2f}",
        "Market Value":    "${:,.0f}",
        "Unrealised P&L":  "${:+,.0f}",
        "P&L %":           "{:+.2f}%",
        "Weight %":        "{:.2f}%",
        "Period Return %": "{:+.2f}%",
        "Vol Contrib %":   "{:.3f}%",
    })
    .background_gradient(subset=["P&L %","Period Return %"], cmap="RdYlGn", vmin=-20, vmax=20)
    .bar(subset=["Weight %"], color=[f"rgba(45,127,249,0.35)"])
    ,
    use_container_width=True, hide_index=True,
)

csv = hdf_display.to_csv(index=False).encode()
st.download_button("⬇ Download Holdings CSV", csv, "holdings.csv", "text/csv")

# ── NEWS ───────────────────────────────────────────────────────────────────────
st.divider()
section_header("Latest News")

news_cols = st.columns(len(tickers[:4]))
for i, t in enumerate(tickers[:4]):
    with news_cols[i]:
        news = load_news(t, 3)
        st.markdown(
            f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#5b9ef5;'
            f'letter-spacing:0.5px;text-transform:uppercase;margin-bottom:8px;">{t}</div>',
            unsafe_allow_html=True,
        )
        if news:
            for item in news:
                st.markdown(
                    f'<div style="font-size:12px;color:#8ba3bd;margin-bottom:8px;line-height:1.5;">'
                    f'<a href="{item["url"]}" style="color:#5b9ef5;text-decoration:none;"'
                    f' target="_blank">{item["title"]}</a></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(f'<div style="font-size:11px;color:#344d68;">No news available.</div>',
                        unsafe_allow_html=True)

app_footer()
