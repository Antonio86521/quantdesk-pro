import streamlit as st
import pandas as pd

from auth import require_login, sidebar_user_widget
from utils import apply_theme, page_header
from portfolio_service import (
    create_portfolio,
    get_portfolios,
    get_positions,
    add_position,
    delete_position,
)
from database import create_profile_if_needed


# ─────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Manager",
    layout="wide",
    page_icon="📊"
)

apply_theme()
require_login()
sidebar_user_widget()

st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1350px;
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 12px 14px;
}
.section-title {
    font-size: 1.45rem;
    font-weight: 700;
    margin-top: 0.3rem;
    margin-bottom: 0.8rem;
}
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

page_header(
    "Portfolio Manager",
    "Create portfolios, add positions, and manage saved holdings."
)

user = st.user
user_id = user.get("sub") if user else None
user_email = user.get("email") if user else None
user_name = user.get("name") if user else None

if not user_id:
    st.error("User not found. Please log in again.")
    st.stop()

# ensure profile exists before any inserts
create_profile_if_needed(user_id, user_email, user_name)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def clean_ticker(x: str) -> str:
    return str(x).strip().upper()


# ─────────────────────────────────────────────
# CREATE NEW PORTFOLIO
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Create Portfolio</div>', unsafe_allow_html=True)

c1, c2 = st.columns([4, 1])

with c1:
    portfolio_name = st.text_input("Portfolio Name", placeholder="e.g. Growth Portfolio")

with c2:
    st.write("")
    st.write("")
    create_clicked = st.button("Create Portfolio", use_container_width=True)

if create_clicked:
    portfolio_name = portfolio_name.strip()

    if not portfolio_name:
        st.warning("Please enter a portfolio name.")
    else:
        try:
            create_portfolio(user_id, portfolio_name)
            st.success(f'Portfolio "{portfolio_name}" created.')
            st.rerun()
        except Exception as e:
            st.error(f"Could not create portfolio: {e}")

st.divider()


# ─────────────────────────────────────────────
# LOAD PORTFOLIOS
# ─────────────────────────────────────────────
portfolios = get_portfolios(user_id)

if not portfolios:
    st.info("No portfolios yet. Create one above to get started.")
    st.stop()

portfolio_map = {p["name"]: p["id"] for p in portfolios}
portfolio_names = list(portfolio_map.keys())

if "selected_portfolio_manager" not in st.session_state:
    st.session_state.selected_portfolio_manager = portfolio_names[0]

selected_name = st.selectbox(
    "Select Portfolio",
    options=portfolio_names,
    index=portfolio_names.index(st.session_state.selected_portfolio_manager)
    if st.session_state.selected_portfolio_manager in portfolio_map
    else 0,
)

st.session_state.selected_portfolio_manager = selected_name
portfolio_id = portfolio_map[selected_name]

positions = get_positions(portfolio_id)


# ─────────────────────────────────────────────
# PORTFOLIO SUMMARY
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Portfolio Summary</div>', unsafe_allow_html=True)

if positions:
    pos_df = pd.DataFrame(positions)

    total_positions = len(pos_df)
    total_shares = pd.to_numeric(pos_df["shares"], errors="coerce").fillna(0).sum()
    total_cost = (
        pd.to_numeric(pos_df["shares"], errors="coerce").fillna(0) *
        pd.to_numeric(pos_df["buy_price"], errors="coerce").fillna(0)
    ).sum()

    s1, s2, s3 = st.columns(3)
    s1.metric("Positions", f"{total_positions}")
    s2.metric("Total Shares", f"{total_shares:,.2f}")
    s3.metric("Total Cost Basis", f"${total_cost:,.2f}")
else:
    s1, s2, s3 = st.columns(3)
    s1.metric("Positions", "0")
    s2.metric("Total Shares", "0.00")
    s3.metric("Total Cost Basis", "$0.00")

st.divider()


# ─────────────────────────────────────────────
# ADD POSITION
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Add Position</div>', unsafe_allow_html=True)

a1, a2, a3, a4 = st.columns([2, 1, 1, 1])

with a1:
    ticker = st.text_input("Ticker", placeholder="AAPL")
with a2:
    shares = st.number_input("Shares", min_value=0.0, step=1.0, value=0.0)
with a3:
    buy_price = st.number_input("Buy Price", min_value=0.0, step=1.0, value=0.0)
with a4:
    st.write("")
    st.write("")
    add_clicked = st.button("Add Position", use_container_width=True)

if add_clicked:
    ticker = clean_ticker(ticker)

    if not ticker:
        st.warning("Please enter a ticker.")
    elif shares <= 0:
        st.warning("Shares must be greater than 0.")
    elif buy_price <= 0:
        st.warning("Buy price must be greater than 0.")
    else:
        try:
            add_position(portfolio_id, ticker, shares, buy_price)
            st.success(f"Added {ticker} to {selected_name}.")
            st.rerun()
        except Exception as e:
            st.error(f"Could not add position: {e}")

st.divider()


# ─────────────────────────────────────────────
# SHOW POSITIONS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Positions</div>', unsafe_allow_html=True)

positions = get_positions(portfolio_id)

if not positions:
    st.info("No positions yet in this portfolio.")
else:
    pos_df = pd.DataFrame(positions).copy()

    pos_df["ticker"] = pos_df["ticker"].astype(str).str.upper()
    pos_df["shares"] = pd.to_numeric(pos_df["shares"], errors="coerce").fillna(0.0)
    pos_df["buy_price"] = pd.to_numeric(pos_df["buy_price"], errors="coerce").fillna(0.0)
    pos_df["cost_basis"] = pos_df["shares"] * pos_df["buy_price"]

    display_df = pos_df[["ticker", "shares", "buy_price", "cost_basis"]].rename(columns={
        "ticker": "Ticker",
        "shares": "Shares",
        "buy_price": "Buy Price",
        "cost_basis": "Cost Basis"
    }).copy()

    display_df["Shares"] = display_df["Shares"].map(lambda x: f"{x:,.2f}")
    display_df["Buy Price"] = display_df["Buy Price"].map(lambda x: f"${x:,.2f}")
    display_df["Cost Basis"] = display_df["Cost Basis"].map(lambda x: f"${x:,.2f}")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Delete Position")

    for _, pos in pos_df.iterrows():
        d1, d2, d3, d4, d5 = st.columns([2, 1, 1, 1, 1])

        d1.write(pos["ticker"])
        d2.write(f'{pos["shares"]:,.2f}')
        d3.write(f'${pos["buy_price"]:,.2f}')
        d4.write(f'${pos["cost_basis"]:,.2f}')

        if d5.button("Delete", key=f'del_{pos["id"]}'):
            try:
                delete_position(pos["id"])
                st.success(f'Deleted {pos["ticker"]}.')
                st.rerun()
            except Exception as e:
                st.error(f"Could not delete position: {e}")
