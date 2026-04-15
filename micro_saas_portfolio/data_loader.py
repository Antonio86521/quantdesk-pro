import pandas as pd
import streamlit as st


@st.cache_data(ttl=600)
def load_price_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Return full OHLCV DataFrame for a ticker."""
    """Return full OHLCV DataFrame for a ticker with fallback logic."""
    ticker = str(ticker).strip().upper()

    # First attempt: Ticker().history()
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
        return df
    except Exception:
        return pd.DataFrame()
        df = yf.Ticker(ticker).history(
            period=period,
            interval=interval,
            auto_adjust=True
        )
        if df is not None and not df.empty:
            return df
    except Exception as e1:
        first_error = str(e1)
    else:
        first_error = "Ticker().history() returned empty data"

    # Second attempt: yf.download()
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=False,
        )
        if df is not None and not df.empty:
            return df
    except Exception as e2:
        second_error = str(e2)
    else:
        second_error = "yf.download() returned empty data"

    st.warning(
        f"Yahoo data failed for {ticker}. "
        f"history() -> {first_error} | download() -> {second_error}"
    )
    return pd.DataFrame()


@st.cache_data(ttl=600)
@@ -18,15 +52,25 @@ def load_close_series(ticker: str, period: str = "1y") -> pd.Series:
    df = load_price_history(ticker, period=period)
    if df.empty:
        return pd.Series(dtype=float)
    return df["Close"]

    if "Close" in df.columns:
        s = df["Close"].copy()
        s.name = ticker
        return s.dropna()

    return pd.Series(dtype=float)


@st.cache_data(ttl=600)
def load_option_expiries(ticker: str) -> list:
    """Return list of available expiry date strings."""
    ticker = str(ticker).strip().upper()

    try:
        return list(yf.Ticker(ticker).options)
    except Exception:
        expiries = list(yf.Ticker(ticker).options)
        return expiries if expiries else []
    except Exception as e:
        st.warning(f"Could not load option expiries for {ticker}: {e}")
        return []


@@ -36,10 +80,13 @@ def load_option_chain(ticker: str, expiry: str) -> dict:
    Return dict with 'calls' and 'puts' DataFrames.
    Always returns a dict — never raises on empty data.
    """
    ticker = str(ticker).strip().upper()

    try:
        chain = yf.Ticker(ticker).option_chain(expiry)
        return {"calls": chain.calls.copy(), "puts": chain.puts.copy()}
    except Exception:
    except Exception as e:
        st.warning(f"Could not load option chain for {ticker} {expiry}: {e}")
        empty = pd.DataFrame(columns=[
            "strike", "lastPrice", "bid", "ask",
            "volume", "openInterest", "impliedVolatility",
@@ -50,6 +97,8 @@ def load_option_chain(ticker: str, expiry: str) -> dict:
@st.cache_data(ttl=600)
def load_news(ticker: str, n: int = 3) -> list:
    """Return up to n news items as list of {title, url} dicts."""
    ticker = str(ticker).strip().upper()

    try:
        raw = yf.Ticker(ticker).news or []
        results = []
@@ -65,7 +114,8 @@ def load_news(ticker: str, n: int = 3) -> list:
            if title:
                results.append({"title": title, "url": url})
        return results
    except Exception:
    except Exception as e:
        st.warning(f"Could not load news for {ticker}: {e}")
        return []
