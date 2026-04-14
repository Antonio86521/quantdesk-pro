import numpy as np


# ── Single-leg ─────────────────────────────────────────────────────────────────

def payoff_long_call(S_range, K, premium):
    return np.maximum(S_range - K, 0) - premium


def payoff_short_call(S_range, K, premium):
    return premium - np.maximum(S_range - K, 0)


def payoff_long_put(S_range, K, premium):
    return np.maximum(K - S_range, 0) - premium


def payoff_short_put(S_range, K, premium):
    return premium - np.maximum(K - S_range, 0)


# ── Two-leg ────────────────────────────────────────────────────────────────────

def payoff_covered_call(S_range, stock_cost, K, premium):
    return (S_range - stock_cost) + (premium - np.maximum(S_range - K, 0))


def payoff_protective_put(S_range, stock_cost, K, premium):
    return (S_range - stock_cost) + (np.maximum(K - S_range, 0) - premium)


def payoff_bull_call_spread(S_range, K1, prem1, K2, prem2):
    return (np.maximum(S_range - K1, 0) - prem1) + (prem2 - np.maximum(S_range - K2, 0))


def payoff_bear_put_spread(S_range, K1, prem1, K2, prem2):
    return (np.maximum(K1 - S_range, 0) - prem1) + (prem2 - np.maximum(K2 - S_range, 0))


def payoff_bull_put_spread(S_range, K1, prem1, K2, prem2):
    """Sell higher-strike put, buy lower-strike put."""
    return (prem1 - np.maximum(K1 - S_range, 0)) + (np.maximum(K2 - S_range, 0) - prem2)


def payoff_bear_call_spread(S_range, K1, prem1, K2, prem2):
    """Sell lower-strike call, buy higher-strike call."""
    return (prem1 - np.maximum(S_range - K1, 0)) + (np.maximum(S_range - K2, 0) - prem2)


# ── Volatility strategies ──────────────────────────────────────────────────────

def payoff_straddle(S_range, K, call_prem, put_prem):
    return (np.maximum(S_range - K, 0) - call_prem) + (np.maximum(K - S_range, 0) - put_prem)


def payoff_strangle(S_range, K_put, put_prem, K_call, call_prem):
    return (np.maximum(K_put - S_range, 0) - put_prem) + (np.maximum(S_range - K_call, 0) - call_prem)


def payoff_long_butterfly(S_range, K1, K2, K3, prem1, prem2, prem3):
    """Long K1 call, short 2× K2 calls, long K3 call."""
    return (
        (np.maximum(S_range - K1, 0) - prem1)
        - 2 * (np.maximum(S_range - K2, 0) - prem2)
        + (np.maximum(S_range - K3, 0) - prem3)
    )


def payoff_iron_condor(S_range, K1, K2, K3, K4, p1, p2, p3, p4):
    """
    Bull put spread (K1/K2) + Bear call spread (K3/K4).
    K1 < K2 < K3 < K4.
    """
    bull_put  = payoff_bull_put_spread(S_range, K2, p2, K1, p1)
    bear_call = payoff_bear_call_spread(S_range, K3, p3, K4, p4)
    return bull_put + bear_call


# ── Utility ────────────────────────────────────────────────────────────────────

def find_breakevens(S_range: np.ndarray, pnl: np.ndarray) -> list:
    """Return approximate breakeven stock prices."""
    idx = np.where(np.diff(np.sign(pnl)) != 0)[0]
    return [float(S_range[i]) for i in idx]


def strategy_summary(S_range: np.ndarray, pnl: np.ndarray) -> dict:
    return {
        "max_profit":   float(np.max(pnl)),
        "max_loss":     float(np.min(pnl)),
        "breakevens":   find_breakevens(S_range, pnl),
    }