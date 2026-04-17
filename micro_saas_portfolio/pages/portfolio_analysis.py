import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from auth import require_login, sidebar_user_widget
from utils import apply_theme, page_header, MUTED
from portfolio_service import get_portfolios, get_positions
from data_loader import load_close_series
from analytics import (
    annualized_return,
    annualized_vol,
    correlation_matrix,
    rolling_vol,
    max_drawdown_from_returns,
    sortino_ratio,
    calmar_ratio,
    omega_ratio,
    gain_to_pain,
    return_skew,
    return_kurtosis,
    parametric_var,
    historical_var,
    cvar
)

# ─────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────
st.set_page_config(page_title="Saved Portfolio Analysis", layout="wide", page_icon="📊")
apply_theme()
require_login()
sidebar_user_widget()

page_header(
    "Saved Portfolio Analysis",
    "Load a saved portfolio from Supabase and run full analytics."
)

user = st.user
user_id = user.get("sub") if user else None

if not user_id:
    st.error("User not found. Please log in again.")
    st.stop()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def max_drawdown_from_returns(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    wealth = (1 + returns).cumprod()
    peak = wealth.cummax()
    dd = wealth / peak - 1
    return float(dd.min())


def sharpe_ratio(returns: pd.Series, rf: float = 0.0) -> float:
    if returns.empty:
        return 0.0
    ann_ret = annualized_return(returns)
    ann_vol = annualized_vol(returns)
    if ann_vol == 0 or pd.isna(ann_vol):
        return 0.0
    return float((ann_ret - rf) / ann_vol)


def compute_portfolio_returns(price_df: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    rets = price_df.pct_change().dropna()
    if rets.empty:
        return pd.Series(dtype=float)
    port_rets = rets.mul(weights, axis=1).sum(axis=1)
    return port_rets


def latest_valid_prices(price_df: pd.DataFrame) -> pd.Series:
    if price_df.empty:
        return pd.Series(dtype=float)
    return price_df.ffill().iloc[-1]


# ─────────────────────────────────────────────
# LOAD PORTFOLIOS
# ─────────────────────────────────────────────
portfolios = get_portfolios(user_id)

if not portfolios:
    st.warning("No saved portfolios found yet.")
    st.stop()

portfolio_map = {p["name"]: p["id"] for p in portfolios}

if "selected_saved_portfolio" not in st.session_state:
    st.session_state.selected_saved_portfolio = list(portfolio_map.keys())[0]

selected_name = st.selectbox(
    "Select Portfolio",
    options=list(portfolio_map.keys()),
    index=list(portfolio_map.keys()).index(st.session_state.selected_saved_portfolio)
    if st.session_state.selected_saved_portfolio in portfolio_map
    else 0,
)

st.session_state.selected_saved_portfolio = selected_name
selected_portfolio_id = portfolio_map[selected_name]

positions = get_positions(selected_portfolio_id)

if not positions:
    st.warning("This portfolio has no positions yet.")
    st.stop()


# ─────────────────────────────────────────────
# CLEAN POSITIONS
# ─────────────────────────────────────────────
pos_df = pd.DataFrame(positions).copy()

required_cols = ["ticker", "shares", "buy_price"]
for col in required_cols:
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

# Optional: combine duplicate tickers
pos_df = (
    pos_df.groupby("ticker", as_index=False)
    .agg({
        "shares": "sum",
        "buy_price": "mean"
    })
)

tickers = pos_df["ticker"].tolist()

# Sidebar controls
st.sidebar.markdown("### Analysis Settings")
lookback = st.sidebar.selectbox(
    "Lookback Period",
    ["6mo", "1y", "2y", "5y"],
    index=1
)
risk_free_rate = st.sidebar.number_input(
    "Risk-Free Rate",
    min_value=0.0,
    max_value=0.20,
    value=0.02,
    step=0.005
)

# ─────────────────────────────────────────────
# LOAD MARKET DATA
# ─────────────────────────────────────────────
price_data = {}

for ticker in tickers:
    try:
        s = load_close_series(ticker, period=lookback)
        if s is not None and not s.empty:
            s = pd.Series(s).dropna()
            s.name = ticker
            price_data[ticker] = s
    except Exception:
        pass

if not price_data:
    st.error("No market data could be loaded for this portfolio.")
    st.stop()

price_df = pd.concat(price_data.values(), axis=1, join="inner").dropna(how="all")

if price_df.empty or price_df.shape[1] == 0:
    st.error("Not enough overlapping price data to analyze this portfolio.")
    st.stop()

available_tickers = price_df.columns.tolist()
pos_df = pos_df[pos_df["ticker"].isin(available_tickers)].copy()

if pos_df.empty:
    st.error("None of the saved tickers have valid price history.")
    st.stop()

price_df = price_df[pos_df["ticker"].tolist()].copy()


# ─────────────────────────────────────────────
# COMPUTE WEIGHTS
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# ADVANCED METRICS
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# TOP METRICS
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Portfolio Value", f"${total_value:,.0f}")
c2.metric("Ann Return", f"{ann_ret:.2%}")
c3.metric("Volatility", f"{ann_vol:.2%}")
c4.metric("Sharpe", f"{sharpe:.2f}")
c5.metric("Max Drawdown", f"{max_dd:.2%}")

c6, c7, c8, c9 = st.columns(4)
c6.metric("Sortino", f"{sortino:.2f}")
c7.metric("Calmar", f"{calmar:.2f}")
c8.metric("Omega", f"{omega:.2f}")
c9.metric("Gain/Pain", f"{gtp:.2f}")

st.markdown("### Risk Metrics")
c10, c11, c12 = st.columns(3)
c10.metric("Parametric VaR (95%)", f"{var_param:.2%}")
c11.metric("Historical VaR (95%)", f"{var_hist:.2%}")
c12.metric("CVaR", f"{cvar_val:.2%}")

st.markdown("### Return Distribution")
c13, c14 = st.columns(2)
c13.metric("Skewness", f"{sk:.2f}")
c14.metric("Kurtosis", f"{kt:.2f}")

c15, c16, c17 = st.columns(3)
c15.metric("Positions", f"{num_positions}")
c16.metric("Unrealized P&L", f"${unrealized_pnl:,.2f}")
c17.metric("Unrealized P&L %", f"{unrealized_pnl_pct:.2%}")


# ─────────────────────────────────────────────
# POSITIONS TABLE
# ─────────────────────────────────────────────
st.markdown("### Holdings Overview")

display_df = pos_df.copy()
display_df["weight"] = display_df["weight"] * 100

display_df = display_df[[
    "ticker",
    "shares",
    "buy_price",
    "current_price",
    "market_value",
    "weight"
]].rename(columns={
    "ticker": "Ticker",
    "shares": "Shares",
    "buy_price": "Avg Buy Price",
    "current_price": "Current Price",
    "market_value": "Market Value",
    "weight": "Weight (%)"
})

st.dataframe(
    display_df.sort_values("Market Value", ascending=False),
    use_container_width=True,
    hide_index=True,
)


# ─────────────────────────────────────────────
# CHARTS ROW 1
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Cumulative Return")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(cum_returns.index, cum_returns.values)
    ax.set_ylabel("Growth of $1")
    ax.set_xlabel("")
    ax.grid(True, alpha=0.25)
    st.pyplot(fig, clear_figure=True)

with col2:
    st.markdown("### Allocation")
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        pos_df["market_value"],
        labels=pos_df["ticker"],
        autopct="%1.1f%%",
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig, clear_figure=True)


# ─────────────────────────────────────────────
# CHARTS ROW 2
# ─────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("### Rolling Volatility (30D)")
    rolling = rolling_vol(portfolio_returns, window=30)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(rolling.index, rolling.values)
    ax.set_ylabel("Volatility")
    ax.set_xlabel("")
    ax.grid(True, alpha=0.25)
    st.pyplot(fig, clear_figure=True)

with col4:
    st.markdown("### Correlation Matrix")
    asset_returns = price_df.pct_change().dropna()
    corr = correlation_matrix(asset_returns)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr.values)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.index)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    st.pyplot(fig, clear_figure=True)


# ─────────────────────────────────────────────
# DAILY RETURNS TABLE
# ─────────────────────────────────────────────
with st.expander("Show Daily Portfolio Returns"):
    dr = portfolio_returns.rename("Portfolio Return").to_frame()
    st.dataframe(dr, use_container_width=True)


# ─────────────────────────────────────────────
# NOTES
# ─────────────────────────────────────────────
st.caption(
    f"Analysis based on {lookback} historical prices for available tickers only. "
    f"Risk-free rate used for Sharpe ratio: {risk_free_rate:.2%}."
)
