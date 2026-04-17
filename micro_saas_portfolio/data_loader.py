import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import requests
import datetime


# ── Alpha Vantage helpers ─────────────────────────────────────────────────────

def _get_alpha_key() -> str:
    return st.secrets.get("ALPHA_VANTAGE_API_KEY", "").strip()


@st.cache_data(ttl=600)
def load_alpha_daily(ticker: str, outputsize: str = "compact") -> pd.DataFrame:
    """
    Alpha Vantage daily adjusted OHLCV.
    Returns columns aligned to your yfinance structure:
    Open, High, Low, Close, Volume
    """
    ticker = str(ticker).strip().upper()
    api_key = _get_alpha_key()

    if not api_key:
        return pd.DataFrame()

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "outputsize": outputsize,   # compact or full
        "apikey": api_key,
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        ts = data.get("Time Series (Daily)")
        if not ts:
            return pd.DataFrame()

        df = pd.DataFrame.from_dict(ts, orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        rename_map = {
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "5. adjusted close": "Close",
            "6. volume": "Volume",
        }
        df = df.rename(columns=rename_map)

        keep_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
        df = df[keep_cols].apply(pd.to_numeric, errors="coerce").dropna(how="all")

        return df

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_alpha_fx_daily(from_symbol: str, to_symbol: str) -> pd.Series:
    """
    Alpha Vantage FX daily series.
    Example: load_alpha_fx_daily("EUR", "USD")
    """
    from_symbol = str(from_symbol).strip().upper()
    to_symbol = str(to_symbol).strip().upper()
    api_key = _get_alpha_key()

    if not api_key:
        return pd.Series(dtype=float)

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "FX_DAILY",
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "outputsize": "compact",
        "apikey": api_key,
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        ts = data.get("Time Series FX (Daily)")
        if not ts:
            return pd.Series(dtype=float)

        df = pd.DataFrame.from_dict(ts, orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        if "4. close" not in df.columns:
            return pd.Series(dtype=float)

        s = pd.to_numeric(df["4. close"], errors="coerce").dropna()
        s.name = f"{from_symbol}{to_symbol}=X"
        return s

    except Exception:
        return pd.Series(dtype=float)


# ── Core price loaders ────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_price_history(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    source: str = "auto",
) -> pd.DataFrame:
    """
    Return full OHLCV DataFrame for a ticker.

    source:
        - "auto"          -> try yfinance first, then Alpha Vantage fallback
        - "yfinance"      -> force yfinance only
        - "alpha_vantage" -> force Alpha Vantage only (daily only)
    """
    ticker = str(ticker).strip().upper()
    source = str(source).strip().lower()

    # ── Force Alpha Vantage
    if source == "alpha_vantage":
        if interval != "1d":
            return pd.DataFrame()
        outputsize = "full" if period in {"5y", "10y", "max"} else "compact"
        return load_alpha_daily(ticker, outputsize=outputsize)

    # ── Try yfinance first
    if source in {"auto", "yfinance"}:
        try:
            df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
            if df is not None and not df.empty:
                return df
        except Exception:
            pass

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
        except Exception:
            pass

    # ── Fallback to Alpha Vantage only if daily data
    if source == "auto" and interval == "1d":
        outputsize = "full" if period in {"5y", "10y", "max"} else "compact"
        df_alpha = load_alpha_daily(ticker, outputsize=outputsize)
        if not df_alpha.empty:
            return df_alpha

    if source == "yfinance":
        st.warning(f"Yahoo data failed for {ticker}.")
    elif source == "alpha_vantage":
        st.warning(f"Alpha Vantage data failed for {ticker}.")
    else:
        st.warning(f"All data sources failed for {ticker}.")

    return pd.DataFrame()


@st.cache_data(ttl=600)
def load_close_series(
    ticker: str,
    period: str = "1y",
    source: str = "auto",
) -> pd.Series:
    """
    Return adjusted close / close price series.
    """
    df = load_price_history(ticker, period=period, interval="1d", source=source)

    if df.empty:
        return pd.Series(dtype=float)

    if "Close" in df.columns:
        s = pd.to_numeric(df["Close"], errors="coerce").dropna()
        s.name = ticker
        return s

    return pd.Series(dtype=float)


@st.cache_data(ttl=600)
def load_spot_price(ticker: str, source: str = "auto") -> float:
    s = load_close_series(ticker, period="5d", source=source)
    if s.empty:
        return float("nan")
    return float(s.iloc[-1])


# ── Options / news (still yfinance only) ─────────────────────────────────────

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


# ── Macro helpers ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_macro_dataset(universe: dict, period: str = "1y", source: str = "auto") -> pd.DataFrame:
    """
    Load close prices for a {label: yf_ticker} universe.
    Returns a DataFrame with label columns aligned on a common date index.
    """
    frames = {}
    for label, sym in universe.items():
        s = load_close_series(sym, period=period, source=source)
        if not s.empty:
            frames[label] = s

    if not frames:
        return pd.DataFrame()

    df = pd.DataFrame(frames)
    df = df.sort_index().ffill().dropna(how="all")
    return df


@st.cache_data(ttl=600)
def load_macro_snapshot(universe: dict, period: str = "1y", source: str = "auto") -> pd.DataFrame:
    """
    Build a snapshot table with Last price and multi-period returns + volatility.
    Returns a DataFrame with columns:
        Asset, Ticker, Last, 1D %, 5D %, 1M %, 3M %, YTD %, 20D Vol %
    """
    records = []

    for label, sym in universe.items():
        try:
            df = load_price_history(sym, period=period, source=source)
            if df is None or df.empty or "Close" not in df.columns:
                continue

            close = pd.to_numeric(df["Close"], errors="coerce").dropna()
            if len(close) < 2:
                continue

            last = float(close.iloc[-1])

            def _pct(n):
                if len(close) > n:
                    return (last / float(close.iloc[-n - 1]) - 1) * 100
                return np.nan

            year_start = datetime.date.today().replace(month=1, day=1)
            ytd_series = close[close.index.date >= year_start]  # type: ignore
            ytd = (last / float(ytd_series.iloc[0]) - 1) * 100 if len(ytd_series) > 1 else np.nan

            ret = close.pct_change().dropna()
            vol_20 = float(ret.tail(20).std() * np.sqrt(252) * 100) if len(ret) >= 20 else np.nan

            records.append({
                "Asset": label,
                "Ticker": sym,
                "Last": last,
                "1D %": _pct(1),
                "5D %": _pct(5),
                "1M %": _pct(21),
                "3M %": _pct(63),
                "YTD %": ytd,
                "20D Vol %": vol_20,
            })

        except Exception:
            continue

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records).reset_index(drop=True)
