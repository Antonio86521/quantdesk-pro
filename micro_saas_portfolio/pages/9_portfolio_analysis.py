import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from auth import sidebar_user_widget
from portfolio_service import get_portfolios, get_positions
from data_loader import load_close_series
from analytics import (
    annualized_return,
    annualized_vol,
    calmar_ratio,
    compute_alpha_beta,
    correlation_matrix,
    cvar,
    gain_to_pain,
    historical_var,
    max_drawdown_from_returns,
    omega_ratio,
    parametric_var,
    return_kurtosis,
    return_skew,
    rolling_vol,
    sortino_ratio,
    tracking_stats,
)
from utils import (
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
    glossary_expander,
)

st.set_page_config(page_title="Saved Portfolio Analysis", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()

user = getattr(st, "user", None)
if not user or not user.get("is_logged_in"):
    st.markdown("## 🔐 Login Required")
    st.markdown("Access your saved portfolios and analytics.")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Continue with Google", use_container_width=True):
            st.login()
    st.stop()

sidebar_user_widget()
page_header("Saved Portfolio Analysis", "Benchmark diagnostics · export packs · reporting")
section_intro("This page analyzes a saved portfolio from the database and compares it against a benchmark using performance, risk, allocation, and reporting views.")

user_id = user.get("sub") if user else None
if not user_id:
    st.error("User not found. Please log in again.")
    st.stop()


def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def compute_portfolio_returns(price_df: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    rets = price_df.pct_change().dropna()
    if rets.empty:
        return pd.Series(dtype=float)
    return rets.mul(weights, axis=1).sum(axis=1)


def latest_valid_prices(price_df: pd.DataFrame) -> pd.Series:
    if price_df.empty:
        return pd.Series(dtype=float)
    return price_df.ffill().iloc[-1]


def compute_capture_ratios(port: pd.Series, bench: pd.Series):
    aligned = pd.concat([port.rename("p"), bench.rename("b")], axis=1).dropna()
    if aligned.empty:
        return np.nan, np.nan
    up = aligned[aligned["b"] > 0]
    down = aligned[aligned["b"] < 0]
    upside = up["p"].mean() / up["b"].mean() if not up.empty and up["b"].mean() != 0 else np.nan
    downside = down["p"].mean() / down["b"].mean() if not down.empty and down["b"].mean() != 0 else np.nan
    return upside, downside


portfolios = get_portfolios(user_id)
if not portfolios:
    st.warning("No saved portfolios found yet.")
    st.stop()

portfolio_map = {p["name"]: p["id"] for p in portfolios}
portfolio_names = list(portfolio_map.keys())
default_portfolio = st.session_state.get("analysis_selected_portfolio", portfolio_names[0])
if default_portfolio not in portfolio_map:
    default_portfolio = portfolio_names[0]

selected_name = st.selectbox("Select Portfolio", options=portfolio_names, index=portfolio_names.index(default_portfolio))
glossary_expander("How to read the saved analysis metrics", ["Portfolio Value", "Ann. Return", "Ann. Volatility", "Sharpe Ratio", "Sortino", "Calmar", "Max Drawdown", "Tracking Error", "Alpha", "Beta", "R²"])
st.session_state["analysis_selected_portfolio"] = selected_name
selected_portfolio_id = portfolio_map[selected_name]
positions = get_positions(selected_portfolio_id)
if not positions:
    st.warning("This portfolio has no positions yet.")
    st.stop()

pos_df = pd.DataFrame(positions).copy()
for col in ["ticker", "shares", "buy_price"]:
    if col not in pos_df.columns:
        st.error(f"Missing required field in portfolio_positions: {col}")
        st.stop()

pos_df["ticker"] = pos_df["ticker"].astype(str).str.upper().str.strip()
pos_df["shares"] = pos_df["shares"].apply(safe_float)
pos_df["buy_price"] = pos_df["buy_price"].apply(safe_float)
pos_df = pos_df[(pos_df["ticker"] != "") & (pos_df["shares"] > 0)].copy()
if pos_df.empty:
    st.warning("No valid positions found in this portfolio.")
    st.stop()

pos_df = pos_df.groupby("ticker", as_index=False).agg({"shares": "sum", "buy_price": "mean"})
tickers = pos_df["ticker"].tolist()

st.sidebar.markdown("### Analysis Settings")
lookback = st.sidebar.selectbox("Lookback Period", ["6mo", "1y", "2y", "5y"], index=1)
risk_free_rate = st.sidebar.number_input("Risk-Free Rate", min_value=0.0, max_value=0.20, value=0.02, step=0.005)
benchmark_ticker = st.sidebar.text_input("Benchmark Ticker", value="SPY").strip().upper()
plan = get_active_plan()
st.sidebar.caption(f"Plan: {plan.upper()}")

price_data = {}
for ticker in tickers:
    try:
        s = load_close_series(ticker, period=lookback, source="auto")
        if s is not None and not s.empty:
            price_data[ticker] = pd.Series(s).dropna()
    except Exception:
        pass
if not price_data:
    st.error("No market data could be loaded for this portfolio.")
    st.stop()

price_df = pd.concat(price_data.values(), axis=1, join="inner")
price_df.columns = list(price_data.keys())
price_df = price_df.dropna(how="all")
if price_df.empty:
    st.error("Not enough overlapping price data to analyze this portfolio.")
    st.stop()

available_tickers = price_df.columns.tolist()
pos_df = pos_df[pos_df["ticker"].isin(available_tickers)].copy()
price_df = price_df[pos_df["ticker"].tolist()].copy()
benchmark_prices = pd.Series(dtype=float)
if benchmark_ticker:
    try:
        benchmark_prices = pd.Series(load_close_series(benchmark_ticker, period=lookback, source="auto")).dropna()
    except Exception:
        benchmark_prices = pd.Series(dtype=float)

latest_prices = latest_valid_prices(price_df)
pos_df["current_price"] = pos_df["ticker"].map(latest_prices)
pos_df["market_value"] = pos_df["shares"] * pos_df["current_price"]
total_value = float(pos_df["market_value"].sum())
if total_value <= 0:
    st.error("Total portfolio market value is zero.")
    st.stop()

pos_df["weight"] = pos_df["market_value"] / total_value
weights = pos_df["weight"].values
portfolio_returns = compute_portfolio_returns(price_df, weights)
if portfolio_returns.empty:
    st.error("Portfolio returns could not be computed.")
    st.stop()

cum_returns = (1 + portfolio_returns).cumprod()
benchmark_returns = pd.Series(dtype=float)
benchmark_cum_returns = pd.Series(dtype=float)
alpha_annual = beta = r2 = tracking_error = information_ratio = np.nan
aligned_pb = pd.DataFrame()
if not benchmark_prices.empty:
    benchmark_returns = benchmark_prices.reindex(portfolio_returns.index.union(benchmark_prices.index)).pct_change().dropna()
    benchmark_returns = benchmark_returns.reindex(portfolio_returns.index).dropna()
    aligned = pd.concat([portfolio_returns.rename("portfolio"), benchmark_returns.rename("benchmark")], axis=1).dropna()
    if not aligned.empty:
        portfolio_returns = aligned["portfolio"]
        benchmark_returns = aligned["benchmark"]
        cum_returns = (1 + portfolio_returns).cumprod()
        benchmark_cum_returns = (1 + benchmark_returns).cumprod()
        alpha_annual, beta, r2, aligned_pb = compute_alpha_beta(portfolio_returns, benchmark_returns)
        tracking_error, information_ratio = tracking_stats(aligned_pb)

ann_ret = annualized_return(portfolio_returns)
ann_vol = annualized_vol(portfolio_returns)
sharpe = (ann_ret - risk_free_rate) / ann_vol if ann_vol and not pd.isna(ann_vol) else np.nan
max_dd, drawdown_series = max_drawdown_from_returns(portfolio_returns)
sortino = sortino_ratio(ann_ret, risk_free_rate, portfolio_returns)
calmar = calmar_ratio(ann_ret, max_dd)
omega = omega_ratio(portfolio_returns)
gtp = gain_to_pain(portfolio_returns)
sk = return_skew(portfolio_returns)
kt = return_kurtosis(portfolio_returns)
var_param = parametric_var(portfolio_returns)
var_hist = historical_var(portfolio_returns)
cvar_val = cvar(portfolio_returns, var_hist)
num_positions = len(pos_df)
portfolio_cost = float((pos_df["shares"] * pos_df["buy_price"]).sum())
unrealized_pnl = total_value - portfolio_cost
unrealized_pnl_pct = (unrealized_pnl / portfolio_cost) if portfolio_cost > 0 else 0.0
up_cap, down_cap = compute_capture_ratios(portfolio_returns, benchmark_returns) if not benchmark_returns.empty else (np.nan, np.nan)

row1 = st.columns(5)
row1[0].metric("Portfolio Value", f"${total_value:,.0f}")
row1[1].metric("Ann Return", safe_pct(ann_ret))
row1[2].metric("Volatility", safe_pct(ann_vol))
row1[3].metric("Sharpe", safe_num(sharpe))
row1[4].metric("Max Drawdown", safe_pct(max_dd))

row2 = st.columns(5)
row2[0].metric("Sortino", safe_num(sortino))
row2[1].metric("Calmar", safe_num(calmar))
row2[2].metric("Omega", safe_num(omega))
row2[3].metric("Gain/Pain", safe_num(gtp))
row2[4].metric("Unrealized P&L", f"${unrealized_pnl:,.0f}", delta=f"{unrealized_pnl_pct:+.2%}")

bench_row = st.columns(5)
bench_row[0].metric("Benchmark", benchmark_ticker if benchmark_ticker else "—")
bench_row[1].metric("Alpha", safe_pct(alpha_annual))
bench_row[2].metric("Beta", safe_num(beta))
bench_row[3].metric("R²", safe_num(r2))
bench_row[4].metric("Tracking Error", safe_pct(tracking_error))

st.divider()

with st.expander("Download portfolio report pack"):
    holdings_export = pos_df[["ticker", "shares", "buy_price", "current_price", "market_value", "weight"]].copy()
    returns_export = pd.DataFrame({"portfolio": portfolio_returns})
    if not benchmark_returns.empty:
        returns_export[benchmark_ticker] = benchmark_returns
    summary_df = pd.DataFrame(
        {
            "Metric": ["Portfolio Value", "Ann Return", "Ann Vol", "Sharpe", "Alpha", "Beta", "Tracking Error", "Information Ratio", "Upside Capture", "Downside Capture"],
            "Value": [total_value, ann_ret, ann_vol, sharpe, alpha_annual, beta, tracking_error, information_ratio, up_cap, down_cap],
        }
    )
    report_html = html_report(
        f"QuantDesk Pro - {selected_name}",
        [
            ("Portfolio summary", summary_df.to_html(index=False)),
            ("Commentary", f"Portfolio analysed versus {benchmark_ticker or 'no benchmark'} over {lookback}."),
        ],
    )
    zip_bytes = make_download_zip(
        {"summary.csv": summary_df, "holdings.csv": holdings_export, "returns.csv": returns_export, "portfolio_report.html": report_html}
    )
    st.download_button("Download report pack (.zip)", data=zip_bytes, file_name=f"{selected_name.lower().replace(' ', '_')}_report_pack.zip", mime="application/zip")

st.markdown("### Holdings Overview")
section_intro("The holdings table reconciles saved position sizes with current prices to show current market value, weights, and embedded gains or losses.", title="Holdings explanation")
display_df = pos_df[["ticker", "shares", "buy_price", "current_price", "market_value", "weight"]].copy()
display_df.columns = ["Ticker", "Shares", "Avg Buy Price", "Current Price", "Market Value", "Weight"]
st.dataframe(
    display_df.style.format({"Shares": "{:,.2f}", "Avg Buy Price": "${:,.2f}", "Current Price": "${:,.2f}", "Market Value": "${:,.2f}", "Weight": "{:.2%}"}),
    use_container_width=True,
    hide_index=True,
)

st.divider()
perf_col, alloc_col = st.columns([1.2, 1])
with perf_col:
    st.markdown("### Cumulative Return vs Benchmark")
    section_intro("This chart shows how one dollar would have grown in the portfolio versus the benchmark over the same period.", title="Return path")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(cum_returns.index, cum_returns.values, linewidth=2, label="Portfolio")
    if not benchmark_cum_returns.empty:
        ax.plot(benchmark_cum_returns.index, benchmark_cum_returns.values, linewidth=2, label=benchmark_ticker)
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)
with alloc_col:
    st.markdown("### Allocation")
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.pie(pos_df["market_value"], labels=pos_df["ticker"], autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

st.divider()
risk_col, corr_col = st.columns(2)
with risk_col:
    st.markdown("### Rolling Volatility")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(rolling_vol(portfolio_returns, window=30), linewidth=2)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)
with corr_col:
    st.markdown("### Correlation Matrix")
    asset_returns = price_df.pct_change().dropna()
    corr = correlation_matrix(asset_returns)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(corr.values, aspect="auto")
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.index)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

st.divider()
st.markdown("### Benchmark Comparison")
section_intro("Benchmark comparison is useful for understanding whether returns came from broad market exposure or from portfolio-specific sources such as stock selection and concentration.", title="Relative performance context")
if benchmark_returns.empty:
    st.info("Enter a valid benchmark ticker to unlock alpha, tracking and capture diagnostics.")
else:
    benchmark_ann_ret = annualized_return(benchmark_returns)
    benchmark_ann_vol = annualized_vol(benchmark_returns)
    benchmark_dd = max_drawdown_from_returns(benchmark_returns)[0]
    comparison_df = pd.DataFrame(
        {
            "Metric": [
                "Annualized Return",
                "Annualized Volatility",
                "Max Drawdown",
                "Alpha",
                "Beta",
                "Tracking Error",
                "Information Ratio",
                "Upside Capture",
                "Downside Capture",
            ],
            "Portfolio": [ann_ret, ann_vol, max_dd, alpha_annual, beta, tracking_error, information_ratio, up_cap, down_cap],
            benchmark_ticker: [benchmark_ann_ret, benchmark_ann_vol, benchmark_dd, np.nan, 1.0, np.nan, np.nan, 1.0, 1.0],
        }
    )
    st.dataframe(comparison_df.style.format({"Portfolio": "{:.2%}", benchmark_ticker: "{:.2%}"}, na_rep="—"), use_container_width=True, hide_index=True)

st.divider()
st.markdown("### Advanced Risk Metrics")
section_intro("These statistics go beyond simple return and volatility to describe drawdown quality, tail risk, asymmetry, and benchmark tracking behavior.", title="Risk interpretation")
r1, r2c, r3 = st.columns(3)
r1.metric("Parametric VaR (95%)", safe_pct(var_param))
r2c.metric("Historical VaR (95%)", safe_pct(var_hist))
r3.metric("CVaR", safe_pct(cvar_val))
r4, r5 = st.columns(2)
r4.metric("Skewness", safe_num(sk))
r5.metric("Kurtosis", safe_num(kt))

st.divider()
st.markdown("### Manager Notes")
section_intro("Manager notes summarize the portfolio in plain English so the main takeaways are visible without reading every chart and table individually.", title="Narrative summary")
notes = []
if not benchmark_returns.empty and information_ratio > 0.4:
    notes.append("Active return efficiency is strong relative to the benchmark.")
if max_dd < -0.20:
    notes.append("Drawdown profile is elevated and may need tighter risk controls.")
if down_cap > 1.0:
    notes.append("Portfolio tends to lose more than the benchmark on negative benchmark days.")
if plan != "pro":
    premium_notice("Extra report commentary and advanced comparison modules")
else:
    if ann_ret > benchmark_ann_ret:
        notes.append("Portfolio is outperforming the selected benchmark on an annualized basis.")
for note in notes or ["Portfolio diagnostics loaded successfully."]:
    st.markdown(f"- {note}")

with st.expander("Show Daily Portfolio Returns"):
    dr = portfolio_returns.rename("Portfolio Return").to_frame()
    dr["Portfolio Return"] = dr["Portfolio Return"].map(lambda x: f"{x:.4%}")
    st.dataframe(dr, use_container_width=True)

st.caption(f"Analysis based on {lookback} history. Risk-free rate for ratio calculations: {risk_free_rate:.2%}.")

