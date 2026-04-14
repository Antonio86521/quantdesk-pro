import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=600)
def load_price_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Return full OHLCV DataFrame for a ticker."""
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_close_series(ticker: str, period: str = "1y") -> pd.Series:
    """Return adjusted close price series."""
    df = load_price_history(ticker, period=period)
    if df.empty:
        return pd.Series(dtype=float)
    return df["Close"]


@st.cache_data(ttl=600)
def load_option_expiries(ticker: str) -> list:
    """Return list of available expiry date strings."""
    try:
        return list(yf.Ticker(ticker).options)
    except Exception:
        return []


@st.cache_data(ttl=600)
def load_option_chain(ticker: str, expiry: str) -> dict:
    """
    Return dict with 'calls' and 'puts' DataFrames.
    Always returns a dict — never raises on empty data.
    """
    try:
        chain = yf.Ticker(ticker).option_chain(expiry)
        return {"calls": chain.calls.copy(), "puts": chain.puts.copy()}
    except Exception:
        empty = pd.DataFrame(columns=[
            "strike", "lastPrice", "bid", "ask",
            "volume", "openInterest", "impliedVolatility",
        ])
        return {"calls": empty, "puts": empty.copy()}


@st.cache_data(ttl=600)
def load_news(ticker: str, n: int = 3) -> list:
    """Return up to n news items as list of {title, url} dicts."""
    try:
        raw = yf.Ticker(ticker).news or []
        results = []
        for item in raw[:n]:
            title = (
                item.get("content", {}).get("title", "")
                or item.get("title", "")
            )
            url = (
                item.get("content", {}).get("canonicalUrl", {}).get("url", "")
                or item.get("link", "")
            )
            if title:
                results.append({"title": title, "url": url})
        return results
    except Exception:
        return []


@st.cache_data(ttl=600)
def load_spot_price(ticker: str) -> float:
    """Return latest closing price."""
    s = load_close_series(ticker, period="5d")
    if s.empty:
        return float("nan")
    return float(s.iloc[-1])
