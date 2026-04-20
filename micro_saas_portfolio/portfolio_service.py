from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ─────────────────────────────
# CREATE PORTFOLIO
# ─────────────────────────────
def create_portfolio(user_id, name, benchmark="SPY", risk_free_rate=0.02):
    res = supabase.table("portfolios").insert({
        "user_id": user_id,
        "name": str(name).strip(),
        "benchmark": str(benchmark).strip().upper(),
        "risk_free_rate": float(risk_free_rate),
    }).execute()
    return res.data[0]["id"]


# ─────────────────────────────
# GET PORTFOLIOS
# ─────────────────────────────
def get_portfolios(user_id):
    res = (
        supabase.table("portfolios")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def get_portfolio(portfolio_id):
    res = (
        supabase.table("portfolios")
        .select("*")
        .eq("id", portfolio_id)
        .limit(1)
        .execute()
    )
    rows = res.data or []
    return rows[0] if rows else None


# ─────────────────────────────
# UPDATE PORTFOLIO
# ─────────────────────────────
def rename_portfolio(portfolio_id, new_name):
    res = supabase.table("portfolios").update({
        "name": str(new_name).strip()
    }).eq("id", portfolio_id).execute()
    return res.data or []


def update_portfolio_settings(portfolio_id, benchmark=None, risk_free_rate=None, name=None):
    payload = {}

    if benchmark is not None:
        payload["benchmark"] = str(benchmark).strip().upper()

    if risk_free_rate is not None:
        payload["risk_free_rate"] = float(risk_free_rate)

    if name is not None and str(name).strip():
        payload["name"] = str(name).strip()

    if not payload:
        return []

    res = supabase.table("portfolios").update(payload).eq("id", portfolio_id).execute()
    return res.data or []


def delete_portfolio(portfolio_id):
    res = supabase.table("portfolios").delete().eq("id", portfolio_id).execute()
    return res.data or []


# ─────────────────────────────
# POSITIONS
# ─────────────────────────────
def add_position(portfolio_id, ticker, shares, buy_price):
    res = supabase.table("portfolio_positions").insert({
        "portfolio_id": portfolio_id,
        "ticker": str(ticker).strip().upper(),
        "shares": float(shares),
        "buy_price": float(buy_price)
    }).execute()
    return res.data or []


def get_positions(portfolio_id):
    res = (
        supabase.table("portfolio_positions")
        .select("*")
        .eq("portfolio_id", portfolio_id)
        .order("created_at", desc=False)
        .execute()
    )
    return res.data or []


def update_position(position_id, shares, buy_price):
    res = supabase.table("portfolio_positions").update({
        "shares": float(shares),
        "buy_price": float(buy_price)
    }).eq("id", position_id).execute()
    return res.data or []


def delete_position(position_id):
    supabase.table("portfolio_positions").delete().eq("id", position_id).execute()


# ─────────────────────────────
# PROFILE HELPERS
# ─────────────────────────────
def set_last_selected_portfolio(user_id, portfolio_id):
    res = supabase.table("profiles").update({
        "last_selected_portfolio": portfolio_id
    }).eq("id", user_id).execute()
    return res.data or []


def get_last_selected_portfolio(user_id):
    res = (
        supabase.table("profiles")
        .select("last_selected_portfolio")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    rows = res.data or []
    if not rows:
        return None
    return rows[0].get("last_selected_portfolio")
