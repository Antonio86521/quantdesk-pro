import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data(ttl=600)
def load_price_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Return full OHLCV DataFrame for a ticker."""
    ticker = str(ticker).strip().upper()

    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
        if df is not None and not df.empty:
            return df
    except Exception:
        pass

    try:
        df = yf.download(
            ticker, period=period, interval=interval,
            auto_adjust=True, progress=False, threads=False,
        )
        if df is not None and not df.empty:
            return df
    except Exception:
        pass

    st.warning(f"Yahoo data failed for {ticker}.")
    return pd.DataFrame()


@st.cache_data(ttl=600)
def load_close_series(ticker: str, period: str = "1y") -> pd.Series:
    """Return adjusted close price series."""
    df = load_price_history(ticker, period=period)
    if df.empty:
        return pd.Series(dtype=float)
    if "Close" in df.columns:
        s = df["Close"].copy()
        s.name = ticker
        return s.dropna()
    return pd.Series(dtype=float)


@st.cache_data(ttl=600)
def load_option_expiries(ticker: str) -> list:
    ticker = str(ticker).strip().upper()
    try:
        expiries = list(yf.Ticker(ticker).options)
        return expiries if expiries else []
    except Exception as e:
        st.warning(f"Could not load option expiries for {ticker}: {e}")
        return []


@st.cache_data(ttl=600)
def load_option_chain(ticker: str, expiry: str) -> dict:
    ticker = str(ticker).strip().upper()
    try:
        chain = yf.Ticker(ticker).option_chain(expiry)
        return {"calls": chain.calls.copy(), "puts": chain.puts.copy()}
    except Exception as e:
        st.warning(f"Could not load option chain for {ticker} {expiry}: {e}")
        empty = pd.DataFrame(columns=[
            "strike", "lastPrice", "bid", "ask",
            "volume", "openInterest", "impliedVolatility",
        ])
        return {"calls": empty, "puts": empty.copy()}


@st.cache_data(ttl=600)
def load_news(ticker: str, n: int = 3) -> list:
    ticker = str(ticker).strip().upper()
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
    except Exception as e:
        st.warning(f"Could not load news for {ticker}: {e}")
        return []


@st.cache_data(ttl=600)
def load_spot_price(ticker: str) -> float:
    s = load_close_series(ticker, period="5d")
    if s.empty:
        return float("nan")
    return float(s.iloc[-1])


# ── Macro helpers ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_macro_dataset(universe: dict, period: str = "1y") -> pd.DataFrame:
    """
    Load close prices for a {label: yf_ticker} universe.
    Returns a DataFrame with label columns aligned on a common date index.
    """
    frames = {}
    for label, sym in universe.items():
        s = load_close_series(sym, period=period)
        if not s.empty:
            frames[label] = s
    if not frames:
        return pd.DataFrame()
    df = pd.DataFrame(frames)
    df = df.sort_index().ffill().dropna(how="all")
    return df


@st.cache_data(ttl=600)
def load_macro_snapshot(universe: dict, period: str = "1y") -> pd.DataFrame:
    """
    Build a snapshot table with Last price and multi-period returns + volatility.
    Returns a DataFrame with columns:
        Asset, Ticker, Last, 1D %, 5D %, 1M %, 3M %, YTD %, 20D Vol %
    """
    records = []
    for label, sym in universe.items():
        try:
            df = load_price_history(sym, period=period)
            if df is None or df.empty or "Close" not in df.columns:
                continue
            close = df["Close"].dropna()
            if len(close) < 2:
                continue

            last = float(close.iloc[-1])

            def _pct(n):
                if len(close) > n:
                    return (last / float(close.iloc[-n - 1]) - 1) * 100
                return np.nan

            # YTD
            import datetime
            year_start = datetime.date.today().replace(month=1, day=1)
            ytd_series = close[close.index.date >= year_start]  # type: ignore
            ytd = (last / float(ytd_series.iloc[0]) - 1) * 100 if len(ytd_series) > 1 else np.nan

            # 20D vol
            ret = close.pct_change().dropna()
            vol_20 = float(ret.tail(20).std() * np.sqrt(252) * 100) if len(ret) >= 20 else np.nan

            records.append({
                "Asset":     label,
                "Ticker":    sym,
                "Last":      last,
                "1D %":      _pct(1),
                "5D %":      _pct(5),
                "1M %":      _pct(21),
                "3M %":      _pct(63),
                "YTD %":     ytd,
                "20D Vol %": vol_20,
            })
        except Exception:
            continue

    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records).reset_index(drop=True)
