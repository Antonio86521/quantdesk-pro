"""
database.py — Supabase integration for QuantDesk Pro.

Requires .streamlit/secrets.toml with:
    SUPABASE_URL = "https://..."
    SUPABASE_KEY = "..."

Tables needed in Supabase:
    profiles            (id text PK, email text, full_name text, created_at timestamptz default now())
    portfolios          (id uuid PK default gen_random_uuid(), user_id text, name text,
                         benchmark text, risk_free_rate float8, created_at timestamptz default now())
    portfolio_positions (id uuid PK default gen_random_uuid(), portfolio_id uuid FK portfolios.id,
                         ticker text, shares float8, buy_price float8)
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any

import streamlit as st


# ── Client ────────────────────────────────────────────────────────────────────

@st.cache_resource
def get_supabase():
    """Return a cached Supabase client. Raises a clear error if secrets are missing."""
    try:
        from supabase import create_client, Client  # type: ignore
    except ImportError:
        st.error(
            "The `supabase` package is not installed. "
            "Run: `pip install supabase`"
        )
        st.stop()

    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")

    if not url or not key or url.startswith("https://YOUR_"):
        st.error(
            "Supabase credentials not configured. "
            "Add SUPABASE_URL and SUPABASE_KEY to `.streamlit/secrets.toml`."
        )
        st.stop()

    return create_client(url, key)


# ── Profiles ──────────────────────────────────────────────────────────────────

def create_profile_if_needed(
    user_id: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
) -> None:
    """Upsert a user profile row in Supabase."""
    try:
        supabase = get_supabase()
        existing = (
            supabase.table("profiles")
            .select("id")
            .eq("id", user_id)
            .execute()
        )
        if not existing.data:
            supabase.table("profiles").insert(
                {"id": user_id, "email": email, "full_name": full_name}
            ).execute()
    except Exception as e:
        # Non-fatal — log but don't crash the app
        st.warning(f"Could not sync user profile: {e}")


# ── Portfolios ────────────────────────────────────────────────────────────────

def save_portfolio(
    user_id: str,
    name: str,
    benchmark: str,
    risk_free_rate: float,
    positions: List[Dict[str, Any]],
) -> Optional[str]:
    """
    Persist a portfolio + its positions to Supabase.
    Returns the new portfolio_id or None on failure.
    """
    try:
        supabase = get_supabase()

        resp = supabase.table("portfolios").insert({
            "user_id":        user_id,
            "name":           name,
            "benchmark":      benchmark,
            "risk_free_rate": risk_free_rate,
        }).execute()

        portfolio_id = resp.data[0]["id"]

        rows = [
            {
                "portfolio_id": portfolio_id,
                "ticker":       p["ticker"],
                "shares":       p["shares"],
                "buy_price":    p["buy_price"],
            }
            for p in positions
        ]
        if rows:
            supabase.table("portfolio_positions").insert(rows).execute()

        return portfolio_id

    except Exception as e:
        st.error(f"Could not save portfolio: {e}")
        return None


def load_portfolios(user_id: str) -> List[Dict[str, Any]]:
    """Return all saved portfolios for a user, newest first."""
    try:
        supabase = get_supabase()
        return (
            supabase.table("portfolios")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
            .data
        ) or []
    except Exception as e:
        st.warning(f"Could not load portfolios: {e}")
        return []


def load_portfolio_positions(portfolio_id: str) -> List[Dict[str, Any]]:
    """Return all positions for a given portfolio."""
    try:
        supabase = get_supabase()
        return (
            supabase.table("portfolio_positions")
            .select("*")
            .eq("portfolio_id", portfolio_id)
            .execute()
            .data
        ) or []
    except Exception as e:
        st.warning(f"Could not load positions: {e}")
        return []


def delete_portfolio(portfolio_id: str) -> bool:
    """Delete a portfolio and its positions. Returns True on success."""
    try:
        supabase = get_supabase()
        supabase.table("portfolio_positions").delete().eq("portfolio_id", portfolio_id).execute()
        supabase.table("portfolios").delete().eq("id", portfolio_id).execute()
        return True
    except Exception as e:
        st.error(f"Could not delete portfolio: {e}")
        return False
