import pandas as pd
import streamlit as st

from auth import sidebar_user_widget
from database import create_profile_if_needed
from portfolio_service import (
    add_position,
    create_portfolio,
    delete_portfolio,
    delete_position,
    get_portfolios,
    get_positions,
    rename_portfolio,
    update_position,
)
from utils import apply_responsive_layout, apply_theme, get_active_plan, page_header, app_footer

st.set_page_config(page_title="Portfolio Manager", layout="wide", page_icon="📊")
apply_theme()
apply_responsive_layout()

user = getattr(st, "user", None)
if not user or not user.get("is_logged_in"):
    st.markdown("## 🔐 Login Required")
    st.markdown("Sign in to create, edit, and manage your saved portfolios.")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Continue with Google", use_container_width=True):
            st.login()
    st.stop()

sidebar_user_widget()
page_header("Portfolio Manager", "Create portfolios, edit holdings and manage a simple fund workspace")

user_id = user.get("sub") if user else None
user_email = user.get("email") if user else None
user_name = user.get("name") if user else None
if not user_id:
    st.error("User not found. Please log in again.")
    st.stop()
create_profile_if_needed(user_id, user_email, user_name)


def clean_ticker(x: str) -> str:
    return str(x).strip().upper()


def ensure_fund_state():
    st.session_state.setdefault(
        "fund_investors",
        [
            {"Investor": "Founder Capital", "Commitment": 150000.0, "Mgmt Fee %": 2.0},
            {"Investor": "Friends & Family", "Commitment": 85000.0, "Mgmt Fee %": 1.5},
        ],
    )


st.caption(f"Workspace plan: {get_active_plan().upper()}")

st.markdown("### Create Portfolio")
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
portfolios = get_portfolios(user_id)
if not portfolios:
    st.info("No portfolios yet. Create one above to get started.")
    st.stop()

portfolio_map = {p["name"]: p["id"] for p in portfolios}
portfolio_names = list(portfolio_map.keys())
st.session_state.setdefault("selected_portfolio_manager", portfolio_names[0])
selected_name = st.selectbox(
    "Select Portfolio",
    options=portfolio_names,
    index=portfolio_names.index(st.session_state["selected_portfolio_manager"]) if st.session_state["selected_portfolio_manager"] in portfolio_map else 0,
)
st.session_state["selected_portfolio_manager"] = selected_name
portfolio_id = portfolio_map[selected_name]
positions = get_positions(portfolio_id)
st.session_state["analysis_selected_portfolio"] = selected_name

action1, action2 = st.columns(2)
with action1:
    st.markdown("### Portfolio Actions")
    new_portfolio_name = st.text_input("Rename Portfolio", value=selected_name, key="rename_portfolio_input")
    if st.button("Rename Portfolio", use_container_width=True):
        cleaned_name = new_portfolio_name.strip()
        if not cleaned_name:
            st.warning("Please enter a valid portfolio name.")
        else:
            try:
                rename_portfolio(portfolio_id, cleaned_name)
                st.success(f'Portfolio renamed to "{cleaned_name}".')
                st.session_state["selected_portfolio_manager"] = cleaned_name
                st.rerun()
            except Exception as e:
                st.error(f"Could not rename portfolio: {e}")
    st.page_link("pages/9_portfolio_analysis.py", label="Analyze This Portfolio", icon="📈")

with action2:
    st.markdown("### Delete Portfolio")
    confirm_delete = st.checkbox(f'I confirm I want to delete "{selected_name}"', key="confirm_delete_portfolio")
    if st.button("Delete Portfolio", use_container_width=True):
        if not confirm_delete:
            st.warning("Please confirm deletion first.")
        else:
            try:
                delete_portfolio(portfolio_id)
                st.success(f'Portfolio "{selected_name}" deleted.')
                st.session_state.pop("selected_portfolio_manager", None)
                st.rerun()
            except Exception as e:
                st.error(f"Could not delete portfolio: {e}")

st.divider()

if positions:
    pos_df = pd.DataFrame(positions).copy()
    pos_df["shares"] = pd.to_numeric(pos_df["shares"], errors="coerce").fillna(0.0)
    pos_df["buy_price"] = pd.to_numeric(pos_df["buy_price"], errors="coerce").fillna(0.0)
    total_positions = len(pos_df)
    total_shares = pos_df["shares"].sum()
    total_cost = (pos_df["shares"] * pos_df["buy_price"]).sum()
else:
    pos_df = pd.DataFrame(columns=["ticker", "shares", "buy_price"])
    total_positions = 0
    total_shares = 0.0
    total_cost = 0.0

s1, s2, s3 = st.columns(3)
s1.metric("Positions", f"{total_positions}")
s2.metric("Total Shares", f"{total_shares:,.2f}")
s3.metric("Total Cost Basis", f"${total_cost:,.2f}")

st.divider()
st.markdown("### Add Position")
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
st.markdown("### Positions")
positions = get_positions(portfolio_id)
if not positions:
    st.info("No positions yet in this portfolio.")
else:
    pos_df = pd.DataFrame(positions).copy()
    pos_df["ticker"] = pos_df["ticker"].astype(str).str.upper()
    pos_df["shares"] = pd.to_numeric(pos_df["shares"], errors="coerce").fillna(0.0)
    pos_df["buy_price"] = pd.to_numeric(pos_df["buy_price"], errors="coerce").fillna(0.0)
    pos_df["cost_basis"] = pos_df["shares"] * pos_df["buy_price"]

    header = st.columns([2, 1.2, 1.2, 1.2, 1, 1])
    header[0].markdown("**Ticker**")
    header[1].markdown("**Shares**")
    header[2].markdown("**Buy Price**")
    header[3].markdown("**Cost Basis**")
    header[4].markdown("**Save**")
    header[5].markdown("**Delete**")

    for _, pos in pos_df.iterrows():
        row = st.columns([2, 1.2, 1.2, 1.2, 1, 1])
        row[0].write(pos["ticker"])
        new_shares = row[1].number_input(
            f"Shares {pos['id']}", min_value=0.0, value=float(pos["shares"]), step=1.0, key=f"shares_{pos['id']}", label_visibility="collapsed"
        )
        new_buy_price = row[2].number_input(
            f"Buy Price {pos['id']}", min_value=0.0, value=float(pos["buy_price"]), step=1.0, key=f"buy_price_{pos['id']}", label_visibility="collapsed"
        )
        row[3].write(f"${new_shares * new_buy_price:,.2f}")
        if row[4].button("Save", key=f"save_{pos['id']}"):
            try:
                update_position(pos["id"], new_shares, new_buy_price)
                st.success(f"Updated {pos['ticker']}.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not update position: {e}")
        if row[5].button("Delete", key=f"del_{pos['id']}"):
            try:
                delete_position(pos["id"])
                st.success(f"Deleted {pos['ticker']}.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not delete position: {e}")

st.divider()
st.markdown("### Fund Mode")
st.caption("Simple investor and NAV monitor so the app feels more like a real fund workspace.")
ensure_fund_state()

fund_left, fund_right = st.columns([1.05, 0.95])
with fund_left:
    inv_name = st.text_input("Investor Name", placeholder="Institutional LP")
    inv_commit = st.number_input("Commitment", min_value=0.0, value=0.0, step=1000.0)
    inv_fee = st.number_input("Management Fee %", min_value=0.0, max_value=5.0, value=2.0, step=0.25)
    if st.button("Add Investor", use_container_width=True):
        if not inv_name.strip() or inv_commit <= 0:
            st.warning("Enter an investor name and positive commitment.")
        else:
            investors = st.session_state["fund_investors"]
            investors.append({"Investor": inv_name.strip(), "Commitment": float(inv_commit), "Mgmt Fee %": float(inv_fee)})
            st.session_state["fund_investors"] = investors
            st.rerun()

with fund_right:
    nav = st.number_input("Current NAV", min_value=0.0, value=max(total_cost, 100000.0), step=5000.0)
    perf_fee = st.number_input("Performance Fee %", min_value=0.0, max_value=40.0, value=20.0, step=1.0)
    hurdle = st.number_input("Hurdle Rate %", min_value=0.0, max_value=20.0, value=5.0, step=0.5)

investor_df = pd.DataFrame(st.session_state["fund_investors"])
if investor_df.empty:
    st.info("No investors yet.")
else:
    total_commitment = investor_df["Commitment"].sum()
    avg_mgmt = investor_df["Mgmt Fee %"].mean()
    gross_return = (nav / total_commitment - 1) if total_commitment > 0 else 0.0
    mgmt_fee_revenue = total_commitment * avg_mgmt / 100
    incentive_base = max(gross_return - hurdle / 100, 0.0)
    performance_fee_value = incentive_base * total_commitment * perf_fee / 100

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Committed Capital", f"${total_commitment:,.0f}")
    f2.metric("Current NAV", f"${nav:,.0f}")
    f3.metric("Gross Return", f"{gross_return:.2%}")
    f4.metric("Mgmt Fee Revenue", f"${mgmt_fee_revenue:,.0f}")
    st.metric("Estimated Performance Fee", f"${performance_fee_value:,.0f}")

    alloc = investor_df.copy()
    alloc["Ownership %"] = alloc["Commitment"] / total_commitment if total_commitment > 0 else 0.0
    alloc["NAV Allocation"] = alloc["Ownership %"] * nav
    st.dataframe(
        alloc.style.format({"Commitment": "${:,.0f}", "Mgmt Fee %": "{:.2f}%", "Ownership %": "{:.2%}", "NAV Allocation": "${:,.0f}"}),
        use_container_width=True,
        hide_index=True,
    )

app_footer()

