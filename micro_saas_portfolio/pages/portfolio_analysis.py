import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from auth import require_login, sidebar_user_widget
from utils import apply_theme, page_header
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
    cvar,
)

# ─────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Saved Portfolio Analysis",
    layout="wide",
    page_icon="📊"
)

apply_theme()

# ─────────────────────────────────────────────
# INLINE LOGIN HANDLING
# ─────────────────────────────────────────────
if not user or not user.get("is_logged_in"):

    st.markdown("""
    <div style="text-align:center; padding:60px 0;">
        <h2>🔐 Access Your Portfolio</h2>
        <p style="color:rgba(255,255,255,0.7);">
            Sign in to view and analyze your saved portfolios
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        if st.button("Continue with Google", use_container_width=True):
            st.login()

    st.stop()

sidebar_user_widget()

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 14px 16px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.88rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.75rem;
    }

    .section-title {
        font-size: 1.55rem;
        font-weight: 700;
        margin-top: 0.2rem;
        margin-bottom: 0.9rem;
    }

    .subtle-note {
        color: rgba(255,255,255,0.65);
        font-size: 0.9rem;
        margin-top: -0.35rem;
        margin-bottom: 1rem;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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


def compute_portfolio_returns(price_df: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    rets = price_df.pct_change().dropna()
    if rets.empty:
        return pd.Series(dtype=float)
    return rets.mul(weights, axis=1).sum(axis=1)


def latest_valid_prices(price_df: pd.DataFrame) -> pd.Series:
    if price_df.empty:
        return pd.Series(dtype=float)
    return price_df.ffill().iloc[-1]


def fmt_pct_or_dash(x):
    return "—" if pd.isna(x) else f"{x:.2%}"


def fmt_num_or_dash(x, decimals=2):
    return "—" if pd.isna(x) else f"{x:.{decimals}f}"


# ─────────────────────────────────────────────
# LOAD PORTFOLIOS
# ─────────────────────────────────────────────
portfolios = get_portfolios(user_id)

if not portfolios:
    st.warning("No saved portfolios found yet.")
    st.stop()

portfolio_map = {p["name"]: p["id"] for p in portfolios}
portfolio_names = list(portfolio_map.keys())

if "selected_saved_portfolio" not in st.session_state:
    st.session_state.selected_saved_portfolio = portfolio_names[0]

top_left, top_right = st.columns([3, 1])

with top_left:
    selected_name = st.selectbox(
        "Select Portfolio",
        options=portfolio_names,
        index=portfolio_names.index(st.session_state.selected_saved_portfolio)
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

pos_df = (
    pos_df.groupby("ticker", as_index=False)
    .agg({
        "shares": "sum",
        "buy_price": "mean"
    })
)

tickers = pos_df["ticker"].tolist()


# ─────────────────────────────────────────────
# SIDEBAR SETTINGS
# ─────────────────────────────────────────────
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
        s = load_close_series(ticker, period=lookback, source="auto")
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
# COMPUTE WEIGHTS / RETURNS
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
# OVERVIEW METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Portfolio Overview</div>', unsafe_allow_html=True)

row1 = st.columns(5)
row1[0].metric("Portfolio Value", f"${total_value:,.0f}")
row1[1].metric("Ann Return", fmt_pct_or_dash(ann_ret))
row1[2].metric("Volatility", fmt_pct_or_dash(ann_vol))
row1[3].metric("Sharpe", fmt_num_or_dash(sharpe))
row1[4].metric("Max Drawdown", fmt_pct_or_dash(max_dd))

row2 = st.columns(4)
row2[0].metric("Sortino", fmt_num_or_dash(sortino))
row2[1].metric("Calmar", fmt_num_or_dash(calmar))
row2[2].metric("Omega", fmt_num_or_dash(omega))
row2[3].metric("Gain/Pain", fmt_num_or_dash(gtp))

row3 = st.columns(3)
row3[0].metric("Positions", f"{num_positions}")
row3[1].metric("Unrealized P&L", f"${unrealized_pnl:,.2f}")
row3[2].metric("Unrealized P&L %", fmt_pct_or_dash(unrealized_pnl_pct))

st.divider()


# ─────────────────────────────────────────────
# HOLDINGS TABLE
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Holdings Overview</div>', unsafe_allow_html=True)

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

display_df["Shares"] = display_df["Shares"].map(lambda x: f"{x:,.2f}")
display_df["Avg Buy Price"] = display_df["Avg Buy Price"].map(lambda x: f"${x:,.2f}")
display_df["Current Price"] = display_df["Current Price"].map(lambda x: f"${x:,.2f}")
display_df["Market Value"] = display_df["Market Value"].map(lambda x: f"${x:,.2f}")
display_df["Weight (%)"] = display_df["Weight (%)"].map(lambda x: f"{x:.2f}%")

st.dataframe(
    display_df.sort_values("Ticker"),
    use_container_width=True,
    hide_index=True,
)

st.divider()


# ─────────────────────────────────────────────
# PERFORMANCE + ALLOCATION
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Performance & Allocation</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("### Cumulative Return")
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(cum_returns.index, cum_returns.values, linewidth=2)
    ax.set_ylabel("Growth of $1")
    ax.set_xlabel("")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

with col2:
    st.markdown("### Allocation")
    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    ax.pie(
        pos_df["market_value"],
        labels=pos_df["ticker"],
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.72,
        labeldistance=1.05
    )
    ax.axis("equal")
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

st.divider()


# ─────────────────────────────────────────────
# RISK VISUALS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Risk Visuals</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("### Rolling Volatility (30D)")
    rolling = rolling_vol(portfolio_returns, window=30)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(rolling.index, rolling.values, linewidth=2)
    ax.set_ylabel("Volatility")
    ax.set_xlabel("")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

with col4:
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


# ─────────────────────────────────────────────
# ADVANCED RISK METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Advanced Risk Metrics</div>', unsafe_allow_html=True)

risk_row = st.columns(3)
risk_row[0].metric("Parametric VaR (95%)", fmt_pct_or_dash(var_param))
risk_row[1].metric("Historical VaR (95%)", fmt_pct_or_dash(var_hist))
risk_row[2].metric("CVaR", fmt_pct_or_dash(cvar_val))

dist_row = st.columns(2)
dist_row[0].metric("Skewness", fmt_num_or_dash(sk))
dist_row[1].metric("Kurtosis", fmt_num_or_dash(kt))

st.divider()


# ─────────────────────────────────────────────
# DAILY RETURNS TABLE
# ─────────────────────────────────────────────
with st.expander("Show Daily Portfolio Returns"):
    dr = portfolio_returns.rename("Portfolio Return").to_frame()
    dr["Portfolio Return"] = dr["Portfolio Return"].map(lambda x: f"{x:.4%}")
    st.dataframe(dr, use_container_width=True)

st.caption(
    f"Analysis based on {lookback} historical prices for available tickers only. "
    f"Risk-free rate used for Sharpe ratio: {risk_free_rate:.2%}."
)
