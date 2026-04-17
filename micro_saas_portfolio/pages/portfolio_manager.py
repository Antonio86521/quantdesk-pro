import streamlit as st
from portfolio_service import *

user_id = st.user.get("sub")  # or your auth method

st.title("📊 Portfolio Manager")

# ─────────────────────────────
# CREATE NEW PORTFOLIO
# ─────────────────────────────
st.subheader("Create Portfolio")

portfolio_name = st.text_input("Portfolio Name")

if st.button("Create"):
    portfolio_id = create_portfolio(user_id, portfolio_name)
    st.success("Portfolio created!")

# ─────────────────────────────
# LOAD PORTFOLIOS
# ─────────────────────────────
portfolios = get_portfolios(user_id)

if portfolios:
    portfolio_names = [p["name"] for p in portfolios]
    selected_name = st.selectbox("Select Portfolio", portfolio_names)

    selected_portfolio = next(p for p in portfolios if p["name"] == selected_name)
    portfolio_id = selected_portfolio["id"]

    # ─────────────────────────────
    # ADD POSITION
    # ─────────────────────────────
    st.subheader("Add Position")

    col1, col2, col3 = st.columns(3)

    ticker = col1.text_input("Ticker")
    shares = col2.number_input("Shares", min_value=0.0)
    price = col3.number_input("Buy Price", min_value=0.0)

    if st.button("Add Position"):
        add_position(portfolio_id, ticker, shares, price)
        st.success("Added!")

    # ─────────────────────────────
    # SHOW POSITIONS
    # ─────────────────────────────
    st.subheader("Positions")

    positions = get_positions(portfolio_id)

    for pos in positions:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        col1.write(pos["ticker"])
        col2.write(pos["shares"])
        col3.write(pos["buy_price"])

        if col4.button("❌", key=pos["id"]):
            delete_position(pos["id"])
            st.rerun()