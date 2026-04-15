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


@st.cache_data(ttl=600)
def load_macro_dataset(symbols: dict[str, str], period: str = "1y") -> pd.DataFrame:
    """
    Load a panel of macro / cross-asset close series.

    Parameters
    ----------
    symbols : dict[str, str]
        Mapping of display name -> yfinance ticker.
    period : str
        yfinance history period.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by date with one column per display name.
    """
    frames = {}
    for label, ticker in symbols.items():
        series = load_close_series(ticker, period=period)
        if not series.empty:
            frames[label] = series
    if not frames:
        return pd.DataFrame()
    return pd.DataFrame(frames).dropna(how="all")


@st.cache_data(ttl=600)
def load_macro_snapshot(symbols: dict[str, str], period: str = "6mo") -> pd.DataFrame:
    """Return latest macro snapshot with price and momentum statistics."""
    records = []
    for label, ticker in symbols.items():
        df = load_price_history(ticker, period=period)
        if df.empty or "Close" not in df.columns or len(df) < 2:
            continue

        close = df["Close"].dropna()
        if len(close) < 2:
            continue

        latest = float(close.iloc[-1])
        prev = float(close.iloc[-2])
        chg_1d = (latest - prev) / prev * 100 if prev != 0 else float("nan")
        chg_5d = (latest / float(close.iloc[-6]) - 1) * 100 if len(close) >= 6 else float("nan")
        chg_1m = (latest / float(close.iloc[-22]) - 1) * 100 if len(close) >= 22 else float("nan")
        chg_3m = (latest / float(close.iloc[-64]) - 1) * 100 if len(close) >= 64 else float("nan")
        vol_20d = close.pct_change().dropna().tail(20).std() * (252 ** 0.5) * 100 if len(close) >= 21 else float("nan")

        records.append({
            "Asset": label,
            "Ticker": ticker,
            "Last": latest,
            "1D %": chg_1d,
            "5D %": chg_5d,
            "1M %": chg_1m,
            "3M %": chg_3m,
            "20D Vol %": vol_20d,
        })

    return pd.DataFrame(records)

        return float("nan")
    return float(s.iloc[-1])
