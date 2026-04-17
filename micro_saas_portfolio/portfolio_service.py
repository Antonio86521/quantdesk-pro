from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ─────────────────────────────
# CREATE PORTFOLIO
# ─────────────────────────────
def create_portfolio(user_id, name):
    res = supabase.table("portfolios").insert({
        "user_id": user_id,
        "name": name
    }).execute()
    return res.data[0]["id"]


# ─────────────────────────────
# ADD POSITION
# ─────────────────────────────
def add_position(portfolio_id, ticker, shares, buy_price):
    supabase.table("portfolio_positions").insert({
        "portfolio_id": portfolio_id,
        "ticker": ticker,
        "shares": shares,
        "buy_price": buy_price
    }).execute()


# ─────────────────────────────
# GET USER PORTFOLIOS
# ─────────────────────────────
def get_portfolios(user_id):
    res = supabase.table("portfolios").select("*").eq("user_id", user_id).execute()
    return res.data


# ─────────────────────────────
# GET POSITIONS
# ─────────────────────────────
def get_positions(portfolio_id):
    res = supabase.table("portfolio_positions").select("*").eq("portfolio_id", portfolio_id).execute()
    return res.data


# ─────────────────────────────
# DELETE POSITION
# ─────────────────────────────
def delete_position(position_id):
    supabase.table("portfolio_positions").delete().eq("id", position_id).execute()
