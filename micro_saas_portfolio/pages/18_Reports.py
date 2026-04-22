"""
14_Reports.py — QuantDesk Pro
Professional report generator: portfolio summaries, risk digests,
macro snapshots. Export as CSV packs or HTML reports.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime
import io

from utils import (
    apply_theme, apply_responsive_layout, page_header, section_header,
    ACCENT, ACCENT2, GREEN, RED, AMBER, PURPLE, TEAL, TEXT2, BG2, BG3,
    MPL_BORDER, MPL_GRID, PALETTE, app_footer, safe_pct, safe_num,
    html_report, make_download_zip,
)
from data_loader import load_close_series, load_macro_snapshot
from analytics import (
    annualized_return, annualized_vol, max_drawdown_from_returns,
    historical_var, cvar, compute_alpha_beta, rolling_vol,
)
from auth import sidebar_user_widget

st.set_page_config(page_title="Reports — QuantDesk Pro", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
page_header("Reports", "Generate portfolio summaries · Risk digests · Macro snapshots")
sidebar_user_widget()

REPORT_TYPES = {
    "📈 Portfolio Performance Report": "portfolio",
    "⚡ Risk Digest": "risk",
    "🌍 Macro Snapshot": "macro",
    "📊 Multi-Asset Summary": "multi",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## Report Settings")
report_type   = st.sidebar.selectbox("Report Type", list(REPORT_TYPES.keys()))
period        = st.sidebar.selectbox("Period", ["1mo","3mo","6mo","1y","2y"], index=3)
benchmark     = st.sidebar.selectbox("Benchmark", ["SPY","QQQ","DIA","IWM"], index=0)
risk_free     = st.sidebar.number_input("Risk-Free Rate (%)", 0.0, 10.0, 2.0, 0.5)
generate_btn  = st.sidebar.button("🔄 Generate Report", use_container_width=True)

rtype = REPORT_TYPES[report_type]


# ── Report type inputs ────────────────────────────────────────────────────────
section_header("Report Configuration")

if rtype == "portfolio":
    col1, col2, col3 = st.columns(3)
    tickers_input = col1.text_input("Tickers", value="AAPL,MSFT,NVDA,GOOGL,SPY")
    shares_input  = col2.text_input("Shares",  value="20,15,10,25,50")
    prices_input  = col3.text_input("Buy Prices", value="182,380,650,160,490")
    report_title  = st.text_input("Report Title", value=f"Portfolio Performance Report — {datetime.date.today()}")

elif rtype == "risk":
    col1, col2 = st.columns(2)
    tickers_input = col1.text_input("Tickers", value="AAPL,MSFT,NVDA,SPY")
    shares_input  = col2.text_input("Shares",  value="20,15,10,50")
    prices_input  = "0,0,0,0"  # not used for risk
    report_title  = st.text_input("Report Title", value=f"Risk Digest — {datetime.date.today()}")

elif rtype == "macro":
    report_title = st.text_input("Report Title", value=f"Macro Snapshot — {datetime.date.today()}")

elif rtype == "multi":
    col1, col2 = st.columns(2)
    tickers_input = col1.text_input("Tickers to compare", value="SPY,QQQ,IWM,GLD,TLT,BTC-USD")
    report_title  = st.text_input("Report Title", value=f"Multi-Asset Summary — {datetime.date.today()}")

if not generate_btn:
    st.markdown(
        f'<div style="background:{BG3};border:1px solid rgba(255,255,255,0.06);'
        f'border-radius:10px;padding:24px;text-align:center;margin-top:12px;">'
        f'<div style="font-size:24px;margin-bottom:10px;">📄</div>'
        f'<div style="font-size:13px;font-weight:600;margin-bottom:4px;">Ready to generate</div>'
        f'<div style="font-size:12px;color:{TEXT2};">'
        f'Configure settings in the sidebar and click <strong>Generate Report</strong>.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    app_footer()
    st.stop()

# ── GENERATE ──────────────────────────────────────────────────────────────────
st.divider()
section_header(f"Report: {report_title}")

with st.spinner("Building report…"):

    # ── PORTFOLIO PERFORMANCE REPORT ─────────────────────────────────────────
    if rtype == "portfolio":
        try:
            tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
            shares  = [float(x) for x in shares_input.split(",") if x.strip()]
            bp      = [float(x) for x in prices_input.split(",") if x.strip()]
        except ValueError:
            st.error("Could not parse inputs."); st.stop()

        if not (len(tickers) == len(shares) == len(bp)):
            st.error("Tickers, shares and buy prices must match in length."); st.stop()

        prices = pd.DataFrame()
        for t in tickers:
            s = load_close_series(t, period=period, source="auto")
            if s is not None and not s.empty:
                prices[t] = s
        prices = prices.dropna()
        if prices.empty:
            st.error("No price data loaded."); st.stop()

        latest   = prices.iloc[-1]
        sh       = np.array(shares[:len(tickers)])
        bp_arr   = np.array(bp[:len(tickers)])
        pos_val  = latest.values * sh
        cost     = bp_arr * sh
        total_v  = pos_val.sum()
        total_c  = cost.sum()
        weights  = pos_val / total_v
        ret      = prices.pct_change().dropna()
        port_ret = ret.dot(weights)

        ann_r    = annualized_return(port_ret)
        ann_v    = annualized_vol(port_ret)
        rf       = risk_free / 100
        sharpe   = (ann_r - rf) / ann_v if ann_v else np.nan
        max_dd, _ = max_drawdown_from_returns(port_ret)
        var95    = historical_var(port_ret)
        cvar95   = cvar(port_ret, var95)

        bench_s  = load_close_series(benchmark, period=period, source="auto")
        bench_r  = pd.Series(bench_s).pct_change().dropna() if bench_s is not None else pd.Series()
        alpha, beta, r2, _ = compute_alpha_beta(port_ret, bench_r) if not bench_r.empty else (np.nan, np.nan, np.nan, None)

        # Metrics row
        m = st.columns(5)
        m[0].metric("Portfolio Value", f"${total_v:,.0f}")
        m[1].metric("Ann. Return",     safe_pct(ann_r))
        m[2].metric("Sharpe Ratio",    safe_num(sharpe))
        m[3].metric("Max Drawdown",    safe_pct(max_dd))
        m[4].metric("VaR 95%",         safe_pct(var95))

        m2 = st.columns(5)
        m2[0].metric("Invested",  f"${total_c:,.0f}")
        m2[1].metric("Unrealised P&L", f"${total_v - total_c:+,.0f}")
        m2[2].metric("Ann. Vol",  safe_pct(ann_v))
        m2[3].metric("Alpha",     safe_pct(alpha))
        m2[4].metric("Beta",      safe_num(beta))

        # Charts
        fig = plt.figure(figsize=(14, 8))
        gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)

        ax1 = fig.add_subplot(gs[0, :2])
        cum  = (1 + port_ret).cumprod()
        ax1.plot(cum.index, cum.values, color=ACCENT, lw=2, label="Portfolio")
        if not bench_r.empty:
            bench_cum = (1 + bench_r.reindex(port_ret.index).dropna()).cumprod()
            ax1.plot(bench_cum.index, bench_cum.values, color="#3d5068", lw=1.4, ls="--", label=benchmark)
        ax1.set_title("Growth of $1"); ax1.legend(fontsize=8); ax1.grid(True, alpha=0.2)

        ax2 = fig.add_subplot(gs[0, 2])
        ax2.pie(weights, labels=tickers, autopct="%1.1f%%",
                colors=PALETTE[:len(tickers)],
                wedgeprops=dict(edgecolor="#0d1117", linewidth=1.5))
        ax2.set_title("Allocation")

        ax3 = fig.add_subplot(gs[1, :2])
        _, dd = max_drawdown_from_returns(port_ret)
        ax3.fill_between(dd.index, dd.values, 0, color=RED, alpha=0.3)
        ax3.plot(dd.index, dd.values, color=RED, lw=1.2)
        ax3.set_title("Drawdown"); ax3.grid(True, alpha=0.2)

        ax4 = fig.add_subplot(gs[1, 2])
        ax4.hist(port_ret, bins=40, color=ACCENT, alpha=0.75, edgecolor="#0d1117")
        ax4.axvline(var95, color=RED, lw=1.5, ls="--", label=f"VaR {var95:.2%}")
        ax4.set_title("Return Distribution"); ax4.legend(fontsize=8); ax4.grid(True, alpha=0.2)

        fig.patch.set_facecolor("#080b10")
        st.pyplot(fig, use_container_width=True)
        plt.close()

        # Holdings table
        hdf = pd.DataFrame({
            "Ticker":  tickers,
            "Price":   latest.values,
            "Shares":  sh,
            "Value":   pos_val,
            "Weight":  weights,
        })
        st.dataframe(
            hdf.style.format({"Price": "${:,.2f}", "Value": "${:,.0f}", "Weight": "{:.2%}"}),
            use_container_width=True, hide_index=True,
        )

        # Export
        summary_data = {
            "Metric": ["Ann. Return","Ann. Vol","Sharpe","Max DD","VaR 95%","Alpha","Beta","R²"],
            "Value":  [ann_r, ann_v, sharpe, max_dd, var95, alpha, beta, r2],
        }
        smdf  = pd.DataFrame(summary_data)
        rpt   = html_report(report_title, [
            ("Summary", smdf.to_html(index=False)),
            ("Holdings", hdf.to_html(index=False)),
        ])
        zipped = make_download_zip({"summary.csv": smdf, "holdings.csv": hdf, "report.html": rpt})
        st.download_button("⬇ Download Report Pack (.zip)", data=zipped,
                           file_name="portfolio_report.zip", mime="application/zip")

    # ── RISK DIGEST ────────────────────────────────────────────────────────────
    elif rtype == "risk":
        try:
            tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
            shares  = np.array([float(x) for x in shares_input.split(",") if x.strip()])
        except ValueError:
            st.error("Could not parse inputs."); st.stop()

        prices = pd.DataFrame()
        for t in tickers:
            s = load_close_series(t, period=period, source="auto")
            if s is not None and not s.empty:
                prices[t] = s
        prices = prices.dropna()

        latest  = prices.iloc[-1]
        pos_val = latest.values * shares[:len(tickers)]
        weights = pos_val / pos_val.sum()
        ret     = prices.pct_change().dropna()
        port_ret = ret.dot(weights)

        var95  = historical_var(port_ret, 0.95)
        var99  = historical_var(port_ret, 0.99)
        cvar95 = cvar(port_ret, var95)
        max_dd, _ = max_drawdown_from_returns(port_ret)
        ann_vol = annualized_vol(port_ret)

        section_header("Risk Metrics")
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Ann. Volatility", safe_pct(ann_vol))
        c2.metric("Max Drawdown",    safe_pct(max_dd))
        c3.metric("VaR 95%",         safe_pct(var95))
        c4.metric("VaR 99%",         safe_pct(var99))
        c5.metric("CVaR 95%",        safe_pct(cvar95))

        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        axes[0].hist(port_ret, bins=50, color=ACCENT, alpha=0.75, edgecolor="#0d1117")
        axes[0].axvline(var95, color=RED, lw=1.5, ls="--", label="VaR 95%")
        axes[0].axvline(cvar95, color=AMBER, lw=1.5, ls="--", label="CVaR 95%")
        axes[0].set_title("Return Distribution"); axes[0].legend(fontsize=8)

        _, dd = max_drawdown_from_returns(port_ret)
        axes[1].fill_between(dd.index, dd.values, 0, color=RED, alpha=0.3)
        axes[1].plot(dd.index, dd.values, color=RED, lw=1.2)
        axes[1].set_title("Drawdown Profile")

        roll_v = rolling_vol(port_ret, 20) * 100
        axes[2].plot(roll_v.index, roll_v.values, color=AMBER, lw=1.8)
        axes[2].set_title("Rolling 20D Volatility (%)")
        axes[2].grid(True, alpha=0.2)

        for ax in axes:
            ax.grid(True, alpha=0.2)
        fig.patch.set_facecolor("#080b10")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    # ── MACRO SNAPSHOT ─────────────────────────────────────────────────────────
    elif rtype == "macro":
        MACRO_UNIVERSE = {
            "S&P 500": "SPY", "NASDAQ": "QQQ", "US 10Y": "^TNX",
            "Gold": "GC=F", "WTI": "CL=F", "DXY": "DX-Y.NYB",
            "EUR/USD": "EURUSD=X", "Bitcoin": "BTC-USD",
            "VIX": "^VIX", "TLT": "TLT", "HYG": "HYG",
        }
        snap = load_macro_snapshot(MACRO_UNIVERSE, period=period)
        if snap.empty:
            st.error("Macro data unavailable."); st.stop()

        section_header("Macro Overview")
        st.dataframe(
            snap.style.format({
                "Last": "{:,.2f}", "1D %": "{:+.2f}%", "5D %": "{:+.2f}%",
                "1M %": "{:+.2f}%", "3M %": "{:+.2f}%", "YTD %": "{:+.2f}%",
                "20D Vol %": "{:.1f}%",
            }, na_rep="—"),
            use_container_width=True, hide_index=True,
        )
        csv = snap.to_csv(index=False).encode()
        st.download_button("⬇ Download Macro CSV", csv, "macro_snapshot.csv", "text/csv")

    # ── MULTI-ASSET SUMMARY ─────────────────────────────────────────────────────
    elif rtype == "multi":
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        rows = []
        for t in tickers:
            try:
                s = load_close_series(t, period=period, source="auto")
                if s is None or len(s) < 22: continue
                s = s.dropna()
                r = s.pct_change().dropna()
                rows.append({
                    "Asset": t,
                    "Last":  float(s.iloc[-1]),
                    "1M %":  (float(s.iloc[-1]) / float(s.iloc[-22]) - 1) * 100,
                    "Ann. Return %": annualized_return(r) * 100,
                    "Ann. Vol %":    annualized_vol(r) * 100,
                    "Sharpe":        (annualized_return(r) - risk_free/100) / annualized_vol(r) if annualized_vol(r) else np.nan,
                    "Max DD %":      max_drawdown_from_returns(r)[0] * 100,
                })
            except Exception:
                continue

        if rows:
            mdf = pd.DataFrame(rows)
            st.dataframe(
                mdf.style.format({
                    "Last": "{:,.3f}", "1M %": "{:+.2f}%",
                    "Ann. Return %": "{:+.2f}%", "Ann. Vol %": "{:.2f}%",
                    "Sharpe": "{:.2f}", "Max DD %": "{:.2f}%",
                }, na_rep="—"),
                use_container_width=True, hide_index=True,
            )

            fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
            clrs = [GREEN if v >= 0 else RED for v in mdf["Ann. Return %"]]
            axes[0].bar(mdf["Asset"], mdf["Ann. Return %"], color=clrs, edgecolor="#0d1117")
            axes[0].axhline(0, color="#3d5068", lw=0.8, ls="--")
            axes[0].set_title("Annualised Return (%)"); axes[0].grid(True, alpha=0.2, axis="y")

            sv = mdf["Sharpe"].fillna(0)
            clrs_s = [GREEN if v >= 1 else (AMBER if v >= 0 else RED) for v in sv]
            axes[1].bar(mdf["Asset"], sv, color=clrs_s, edgecolor="#0d1117")
            axes[1].axhline(1, color=GREEN, lw=0.8, ls="--", label="Sharpe=1")
            axes[1].axhline(0, color="#3d5068", lw=0.8, ls=":")
            axes[1].set_title("Sharpe Ratio"); axes[1].legend(fontsize=8); axes[1].grid(True, alpha=0.2, axis="y")

            fig.patch.set_facecolor("#080b10")
            st.pyplot(fig, use_container_width=True)
            plt.close()

            csv = mdf.to_csv(index=False).encode()
            st.download_button("⬇ Download CSV", csv, "multi_asset.csv", "text/csv")

app_footer()
