import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from auth import require_login, sidebar_user_widget
from data_loader import load_close_series
from analytics import (
    annualized_return,
    annualized_vol,
    compute_alpha_beta,
    covariance_matrix,
    cvar,
    historical_var,
    marginal_vol_contribution,
    max_drawdown_from_returns,
    parametric_var,
    rolling_beta,
    rolling_corr,
    rolling_sharpe,
    rolling_vol,
)
from utils import (
    ACCENT,
    GREEN,
    RED,
    apply_responsive_layout,
    apply_theme,
    get_active_plan,
    html_report,
    make_download_zip,
    page_header,
    premium_notice,
    safe_num,
    safe_pct,
    section_intro,
    glossary_expander
)

st.set_page_config(page_title="Risk & Attribution", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()
require_login()
sidebar_user_widget()
page_header("Risk & Attribution", "Rolling Metrics · VaR · Stress Test · Factor Analysis")
section_intro("This page focuses on how the portfolio behaves under volatility, benchmark-relative movement, concentration effects, and simple macro shock assumptions. Start with the summary cards, then move into rolling diagnostics and scenario analysis.")


FACTOR_MAP = {
    "Market (SPY)": "SPY",
    "Size (IWM)": "IWM",
    "Value (IWD)": "IWD",
    "Momentum (MTUM)": "MTUM",
}


if "risk_analysis_clicked" not in st.session_state:
    st.session_state["risk_analysis_clicked"] = False


def _set_risk_analysis_clicked():
    st.session_state["risk_analysis_clicked"] = True


def parse_csv_numbers(text: str) -> np.ndarray:
    return np.array([float(x.strip()) for x in text.split(",") if x.strip()])


def compute_capture_ratios(port: pd.Series, bench: pd.Series):
    aligned = pd.concat([port.rename("p"), bench.rename("b")], axis=1).dropna()
    if aligned.empty:
        return np.nan, np.nan
    up = aligned[aligned["b"] > 0]
    down = aligned[aligned["b"] < 0]
    upside = up["p"].mean() / up["b"].mean() if not up.empty and up["b"].mean() != 0 else np.nan
    downside = down["p"].mean() / down["b"].mean() if not down.empty and down["b"].mean() != 0 else np.nan
    return upside, downside


def factor_regression(port_ret: pd.Series) -> pd.DataFrame:
    data = pd.DataFrame({"portfolio": port_ret})
    for label, ticker in FACTOR_MAP.items():
        s = load_close_series(ticker, period=period, source="auto")
        if s is not None and not s.empty:
            data[label] = pd.Series(s).pct_change()
    data = data.dropna()
    if data.shape[0] < 20 or data.shape[1] < 3:
        return pd.DataFrame()
    y = data["portfolio"].values
    X = data.drop(columns=["portfolio"]).values
    X_design = np.column_stack([np.ones(len(X)), X])
    coeffs, *_ = np.linalg.lstsq(X_design, y, rcond=None)
    y_hat = X_design @ coeffs
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan
    cols = ["Intercept"] + list(data.drop(columns=["portfolio"]).columns)
    out = pd.DataFrame({"Factor": cols, "Exposure": coeffs})
    out["Exposure"] = out["Exposure"].astype(float)
    out.loc[len(out)] = ["R²", r2]
    return out


st.sidebar.markdown("## Inputs")
tickers_input = st.sidebar.text_input("Tickers", "AAPL,MSFT,SPY")
shares_input = st.sidebar.text_input("Shares", "2,1,3")
buy_prices_input = st.sidebar.text_input("Buy prices", "180,350,500")
period = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
benchmark_ticker = st.sidebar.selectbox("Benchmark", ["SPY", "QQQ", "DIA", "IWM"], index=0)
risk_free_rate = st.sidebar.number_input("Risk-free rate (%)", 0.0, 15.0, 2.0, 0.1)
roll_window = st.sidebar.slider("Rolling window (days)", 10, 90, 20, 5)
market_shock = st.sidebar.slider("Uniform market shock (%)", -50, 20, -10, 1)
rate_shock = st.sidebar.slider("Rates shock (bp)", -200, 300, 50, 25)
sector_shock = st.sidebar.slider("Tech concentration shock (%)", -40, 10, -12, 1)
run_page = st.sidebar.button("Run Risk Analysis", use_container_width=True, on_click=_set_risk_analysis_clicked)

plan = get_active_plan()
st.sidebar.caption(f"Workspace plan: {plan.upper()}")

if not st.session_state.get("risk_analysis_clicked", False):
    st.info("Fill in the sidebar and click **Run Risk Analysis**.")
    st.stop()

try:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    shares = parse_csv_numbers(shares_input)
    buy_prices = parse_csv_numbers(buy_prices_input)
except ValueError:
    st.error("Check that shares and buy prices are numeric.")
    st.stop()

if len(tickers) != len(shares) or len(tickers) != len(buy_prices):
    st.error("Tickers, shares, and buy prices must all have the same length.")
    st.stop()

with st.spinner("Loading data…"):
    prices = pd.DataFrame()
    for t in tickers:
        s = load_close_series(t, period=period, source="auto")
        if s is None or s.empty:
            st.error(f"No data for {t}")
            st.stop()
        prices[t] = pd.Series(s)
    prices = prices.dropna()
    bench = load_close_series(benchmark_ticker, period=period, source="auto")
    if bench is None or bench.empty:
        st.error(f"No data for benchmark {benchmark_ticker}")
        st.stop()
    bench = pd.Series(bench).reindex(prices.index).dropna()
    prices = prices.reindex(bench.index).dropna()

latest = prices.iloc[-1]
pos_val = latest.values * shares
cost = buy_prices * shares
weights = pos_val / pos_val.sum()
ret = prices.pct_change().dropna()
port_ret = ret.dot(weights)
bench_ret_s = bench.pct_change().dropna()

ann_ret = annualized_return(port_ret)
ann_vol = annualized_vol(port_ret)
rf = risk_free_rate / 100
max_dd, drawdown = max_drawdown_from_returns(port_ret)
alpha_ann, beta, r2, aligned = compute_alpha_beta(port_ret, bench_ret_s)
var95 = historical_var(port_ret, 0.95)
pvar95 = parametric_var(port_ret, 0.95)
cvar95 = cvar(port_ret, var95)
up_cap, down_cap = compute_capture_ratios(port_ret, bench_ret_s)

st.markdown("### Risk Summary")
glossary_expander("What do these risk summary metrics mean?", ["Ann. Return", "Ann. Volatility", "Max Drawdown", "Beta", "Alpha", "Historical VaR 95%", "Parametric VaR 95%", "CVaR 95%", "R²"])
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Ann. Return", safe_pct(ann_ret))
c2.metric("Ann. Volatility", safe_pct(ann_vol))
c3.metric("Max Drawdown", safe_pct(max_dd))
c4.metric("Beta", safe_num(beta))
c5.metric("Alpha", safe_pct(alpha_ann))

c6, c7, c8, c9 = st.columns(4)
c6.metric("Historical VaR 95%", safe_pct(var95))
c7.metric("Parametric VaR 95%", safe_pct(pvar95))
c8.metric("CVaR 95%", safe_pct(cvar95))
c9.metric("R²", safe_num(r2))

with st.expander("Export risk pack"):
    summary_df = pd.DataFrame(
        {
            "Metric": ["Ann Return", "Ann Vol", "Max Drawdown", "Alpha", "Beta", "R2", "VaR95", "CVaR95"],
            "Value": [ann_ret, ann_vol, max_dd, alpha_ann, beta, r2, var95, cvar95],
        }
    )
    report_html = html_report(
        "QuantDesk Pro - Risk Pack",
        [
            ("Summary", summary_df.to_html(index=False)),
            ("Stress setup", f"Market shock: {market_shock}%<br>Rates shock: {rate_shock} bp<br>Tech concentration shock: {sector_shock}%"),
        ],
    )
    zip_bytes = make_download_zip(
        {
            "risk_summary.csv": summary_df,
            "returns.csv": pd.DataFrame({"portfolio": port_ret, "benchmark": bench_ret_s}),
            "risk_pack.html": report_html,
        }
    )
    st.download_button("Download risk pack (.zip)", data=zip_bytes, file_name="quantdesk_risk_pack.zip", mime="application/zip")

st.divider()

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("### Rolling Metrics")
    section_intro("Rolling statistics help you see whether the portfolio risk profile is stable or changing over time. Sudden jumps can signal regime shifts, concentration issues, or benchmark divergence.", title="Rolling diagnostics")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(rolling_vol(port_ret, roll_window), label="Rolling Vol")
    ax.plot(rolling_sharpe(port_ret, rf=rf, window=roll_window), label="Rolling Sharpe")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

with col_b:
    st.markdown("### Benchmark Diagnostics")
    section_intro("These series show how tightly the portfolio has tracked the chosen benchmark through time. Beta measures sensitivity; rolling correlation shows co-movement strength.", title="Benchmark context")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(rolling_beta(port_ret, bench_ret_s, roll_window), label="Rolling Beta")
    ax.plot(rolling_corr(port_ret, bench_ret_s, roll_window), label="Rolling Corr")
    ax.axhline(1.0, linestyle="--", linewidth=1)
    ax.axhline(0.0, linestyle="--", linewidth=1)
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

st.divider()

st.markdown("### Risk Contribution")
section_intro("Risk contribution splits total portfolio volatility into holding-level components. Large weights do not always mean largest risk, but they often do when correlations are high.", title="Contribution view")
cov_ann = covariance_matrix(ret)
contr = marginal_vol_contribution(weights, cov_ann.values)
risk_df = pd.DataFrame({"Ticker": tickers, "Weight": weights, "Risk Contribution": contr}).sort_values("Risk Contribution", ascending=False)

r1, r2c = st.columns([1.1, 0.9])
with r1:
    st.dataframe(risk_df.style.format({"Weight": "{:.2%}", "Risk Contribution": "{:.2%}"}), use_container_width=True, hide_index=True)
with r2c:
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.bar(risk_df["Ticker"], risk_df["Risk Contribution"])
    ax.axhline(0, linewidth=1)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

st.divider()

st.markdown("### Stress Test Lab")
section_intro("This is a rule-based scenario engine, not a full institutional risk model. It is designed to illustrate how concentrated portfolios may respond to broad market, rates, or tech-specific shocks.", title="Scenario assumptions")
st.caption("A simple rule-based engine to approximate portfolio behavior under macro and concentration shocks.")

stress_df = pd.DataFrame({
    "Ticker": tickers,
    "Weight": weights,
    "Market Shock": market_shock / 100,
})
stress_df["Base Impact"] = stress_df["Weight"] * stress_df["Market Shock"]
stress_df["Rate Sensitivity"] = np.where(stress_df["Ticker"].isin(["QQQ", "IWM", "ARKK", "NVDA", "AAPL", "MSFT", "META", "AMZN"]), -0.35, -0.10)
stress_df["Rate Impact"] = stress_df["Weight"] * stress_df["Rate Sensitivity"] * (rate_shock / 10000)
stress_df["Tech Shock Impact"] = np.where(
    stress_df["Ticker"].isin(["AAPL", "MSFT", "NVDA", "META", "AMZN", "GOOGL", "TSLA"]),
    stress_df["Weight"] * (sector_shock / 100),
    0.0,
)
stress_df["Estimated Impact"] = stress_df[["Base Impact", "Rate Impact", "Tech Shock Impact"]].sum(axis=1)
portfolio_stress = stress_df["Estimated Impact"].sum()

s1, s2, s3 = st.columns(3)
s1.metric("Scenario Loss / Gain", safe_pct(portfolio_stress), delta=None)
s2.metric("Upside Capture", safe_num(up_cap))
s3.metric("Downside Capture", safe_num(down_cap))

sleft, sright = st.columns([1.1, 0.9])
with sleft:
    st.dataframe(
        stress_df[["Ticker", "Weight", "Base Impact", "Rate Impact", "Tech Shock Impact", "Estimated Impact"]].style.format(
            {"Weight": "{:.2%}", "Base Impact": "{:.2%}", "Rate Impact": "{:.2%}", "Tech Shock Impact": "{:.2%}", "Estimated Impact": "{:.2%}"}
        ),
        use_container_width=True,
        hide_index=True,
    )
with sright:
    fig, ax = plt.subplots(figsize=(8, 4.4))
    colors = [GREEN if x >= 0 else RED for x in stress_df["Estimated Impact"]]
    ax.bar(stress_df["Ticker"], stress_df["Estimated Impact"], color=colors)
    ax.axhline(0, linewidth=1)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

st.divider()

st.markdown("### Factor Exposure")
section_intro("Factor exposure estimates whether the portfolio behaves mainly like broad beta, small caps, value, or momentum. It helps explain why performance may differ from a simple benchmark view.", title="Factor interpretation")
if plan != "pro":
    premium_notice("Factor regression")
else:
    factor_df = factor_regression(port_ret)
    if factor_df.empty:
        st.warning("Not enough overlapping factor data to estimate exposures for this window.")
    else:
        display = factor_df.copy()
        st.dataframe(display.style.format({"Exposure": "{:.4f}"}), use_container_width=True, hide_index=True)
        fac_plot = factor_df[factor_df["Factor"].ne("R²") & factor_df["Factor"].ne("Intercept")].copy()
        fig, ax = plt.subplots(figsize=(8.8, 4.2))
        ax.bar(fac_plot["Factor"], fac_plot["Exposure"])
        ax.axhline(0, linewidth=1)
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()
        st.pyplot(fig, clear_figure=True)

st.divider()

st.markdown("### Desk Notes")
section_intro("These notes summarize the most important risk takeaways in plain English. They are rule-based portfolio commentary rather than investment recommendations.", title="Desk note purpose")
messages = []
if beta > 1.1:
    messages.append("Portfolio beta is above 1, so it is likely to amplify broad market moves.")
if portfolio_stress < -0.08:
    messages.append("Current stress settings imply a material drawdown. Consider reducing concentration or adding defensives.")
if down_cap > 1.0:
    messages.append("Downside capture is above 1, which means the portfolio tends to fall more than the benchmark on weak days.")
if not messages:
    messages.append("Risk profile is broadly balanced under the current assumptions.")
for msg in messages:
    st.markdown(f"- {msg}")
