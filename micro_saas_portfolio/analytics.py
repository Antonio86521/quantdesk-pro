import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis


# ── Return metrics ────────────────────────────────────────────────────────────

def annualized_return(returns: pd.Series) -> float:
    if len(returns) == 0:
        return np.nan
    return (1 + returns.mean()) ** 252 - 1


def annualized_vol(returns: pd.Series) -> float:
    if len(returns) == 0:
        return np.nan
    return returns.std() * np.sqrt(252)


def max_drawdown_from_returns(returns: pd.Series):
    if len(returns) == 0:
        return np.nan, pd.Series(dtype=float)
    cum = (1 + returns).cumprod()
    dd = (cum / cum.cummax()) - 1
    return dd.min(), dd


def downside_deviation(returns: pd.Series) -> float:
    downside = returns[returns < 0]
    if len(downside) == 0:
        return np.nan
    return downside.std() * np.sqrt(252)


def sortino_ratio(ann_ret: float, rf: float, returns: pd.Series) -> float:
    dd = downside_deviation(returns)
    if pd.isna(dd) or dd == 0:
        return np.nan
    return (ann_ret - rf) / dd


def calmar_ratio(ann_ret: float, max_dd: float) -> float:
    if pd.isna(max_dd) or max_dd == 0:
        return np.nan
    return ann_ret / abs(max_dd)


def omega_ratio(returns: pd.Series, threshold: float = 0.0) -> float:
    gains = returns[returns > threshold] - threshold
    losses = threshold - returns[returns < threshold]
    if losses.sum() == 0:
        return np.nan
    return gains.sum() / losses.sum()


def gain_to_pain(returns: pd.Series) -> float:
    total_gains = returns[returns > 0].sum()
    total_losses = abs(returns[returns < 0].sum())
    if total_losses == 0:
        return np.nan
    return total_gains / total_losses


def return_skew(returns: pd.Series) -> float:
    return float(skew(returns.dropna()))


def return_kurtosis(returns: pd.Series) -> float:
    return float(kurtosis(returns.dropna()))


# ── Risk / VaR ────────────────────────────────────────────────────────────────

def parametric_var(returns: pd.Series, confidence: float = 0.95) -> float:
    mu = returns.mean()
    sigma = returns.std()
    z = norm.ppf(1 - confidence)
    return mu + z * sigma


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    return float(np.percentile(returns, (1 - confidence) * 100))


def cvar(returns: pd.Series, var_level: float) -> float:
    tail = returns[returns <= var_level]
    return float(tail.mean()) if len(tail) > 0 else np.nan


def conditional_var_99(returns: pd.Series) -> float:
    var99 = historical_var(returns, 0.99)
    return cvar(returns, var99)


# ── Benchmark metrics ─────────────────────────────────────────────────────────

def compute_alpha_beta(port_ret: pd.Series, bench_ret: pd.Series):
    aligned = pd.concat([port_ret, bench_ret], axis=1).dropna()
    aligned.columns = ["portfolio", "benchmark"]
    if len(aligned) < 2 or aligned["benchmark"].var() == 0:
        return np.nan, np.nan, np.nan, aligned
    beta = aligned["portfolio"].cov(aligned["benchmark"]) / aligned["benchmark"].var()
    alpha_daily = aligned["portfolio"].mean() - beta * aligned["benchmark"].mean()
    alpha_annual = alpha_daily * 252
    r2 = aligned.corr().iloc[0, 1] ** 2
    return alpha_annual, beta, r2, aligned


def tracking_stats(aligned: pd.DataFrame):
    if len(aligned) == 0:
        return np.nan, np.nan
    active = aligned["portfolio"] - aligned["benchmark"]
    te = active.std() * np.sqrt(252)
    ir = (active.mean() * 252) / te if te != 0 else np.nan
    return te, ir


# ── Rolling metrics ───────────────────────────────────────────────────────────

def rolling_sharpe(returns: pd.Series, rf: float = 0.0, window: int = 20) -> pd.Series:
    roll_mean = returns.rolling(window).mean() * 252
    roll_vol = returns.rolling(window).std() * np.sqrt(252)
    return (roll_mean - rf) / roll_vol


def rolling_beta(port_ret: pd.Series, bench_ret: pd.Series, window: int = 20) -> pd.Series:
    aligned = pd.concat([port_ret, bench_ret], axis=1).dropna()
    aligned.columns = ["portfolio", "benchmark"]
    cov_ = aligned["portfolio"].rolling(window).cov(aligned["benchmark"])
    var_ = aligned["benchmark"].rolling(window).var()
    return cov_ / var_


def rolling_corr(port_ret: pd.Series, bench_ret: pd.Series, window: int = 20) -> pd.Series:
    aligned = pd.concat([port_ret, bench_ret], axis=1).dropna()
    aligned.columns = ["portfolio", "benchmark"]
    return aligned["portfolio"].rolling(window).corr(aligned["benchmark"])


def rolling_vol(returns: pd.Series, window: int = 20) -> pd.Series:
    return returns.rolling(window).std() * np.sqrt(252)


# ── Technical indicators ──────────────────────────────────────────────────────

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = pd.Series(np.where(delta > 0, delta, 0.0), index=series.index)
    down = pd.Series(np.where(delta < 0, -delta, 0.0), index=series.index)
    rs = up.rolling(window).mean() / down.rolling(window).mean()
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    fast_ema = ema(series, fast)
    slow_ema = ema(series, slow)
    line = fast_ema - slow_ema
    sig = ema(line, signal)
    hist = line - sig
    return line, sig, hist


def bollinger_bands(series: pd.Series, window: int = 20, n_std: float = 2.0):
    mid = sma(series, window)
    std = series.rolling(window).std()
    upper = mid + n_std * std
    lower = mid - n_std * std
    return mid, upper, lower


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(window).mean()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff())
    return (direction * volume).fillna(0).cumsum()


# ── Correlation / covariance ──────────────────────────────────────────────────

def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()


def covariance_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.cov() * 252


def portfolio_variance(weights: np.ndarray, cov_ann: np.ndarray) -> float:
    return float(weights.T @ cov_ann @ weights)


def marginal_vol_contribution(weights: np.ndarray, cov_ann: np.ndarray) -> np.ndarray:
    port_var = portfolio_variance(weights, cov_ann)
    if port_var <= 0:
        return np.full(len(weights), np.nan)
    marginal = cov_ann @ weights
    return weights * marginal / np.sqrt(port_var)

        return np.full(len(weights), np.nan)
    marginal = cov_ann @ weights
    return weights * marginal / np.sqrt(port_var)

