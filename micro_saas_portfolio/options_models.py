import numpy as np
from scipy.stats import norm


# ── Black-Scholes ──────────────────────────────────────────────────────────────

def black_scholes_with_greeks(S, K, T, r, sigma):
    """
    Full Black-Scholes pricing + all Greeks for European options.

    Returns 12-tuple:
        call_price, put_price,
        call_delta, put_delta,
        gamma, vega,
        call_theta, put_theta,
        call_rho, put_rho,
        prob_call_itm, prob_put_itm
    """
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return (np.nan,) * 12

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put_price  = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    call_delta = norm.cdf(d1)
    put_delta  = norm.cdf(d1) - 1

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega  = S * norm.pdf(d1) * np.sqrt(T) / 100          # per 1% vol move

    call_theta = (
        -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * norm.cdf(d2)
    ) / 365

    put_theta = (
        -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
        + r * K * np.exp(-r * T) * norm.cdf(-d2)
    ) / 365

    call_rho =  K * T * np.exp(-r * T) * norm.cdf(d2)  / 100
    put_rho  = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    prob_call_itm = norm.cdf(d2)
    prob_put_itm  = norm.cdf(-d2)

    return (
        call_price, put_price,
        call_delta, put_delta,
        gamma, vega,
        call_theta, put_theta,
        call_rho, put_rho,
        prob_call_itm, prob_put_itm,
    )


def bs_price_only(S, K, T, r, sigma, option_type: str = "call") -> float:
    res = black_scholes_with_greeks(S, K, T, r, sigma)
    return float(res[0] if option_type == "call" else res[1])


# ── Implied Volatility ─────────────────────────────────────────────────────────

def implied_volatility_newton(
    market_price, S, K, T, r,
    option_type: str = "call",
    tol: float = 1e-7,
    max_iter: int = 300,
) -> float:
    """Newton-Raphson IV solver with bisection fallback."""
    if market_price <= 0 or S <= 0 or K <= 0 or T <= 0:
        return np.nan

    # ── Newton-Raphson
    sigma = 0.3
    for _ in range(max_iter):
        res = black_scholes_with_greeks(S, K, T, r, sigma)
        model_price = res[0] if option_type == "call" else res[1]
        true_vega   = res[5] * 100          # convert back from per-1%
        diff        = model_price - market_price
        if abs(diff) < tol:
            return sigma
        if true_vega <= 1e-12:
            break
        sigma -= diff / true_vega
        if sigma <= 0:
            break

    # ── Bisection fallback
    lo, hi = 1e-6, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        res = black_scholes_with_greeks(S, K, T, r, mid)
        price = res[0] if option_type == "call" else res[1]
        if np.isnan(price):
            return np.nan
        if abs(price - market_price) < tol:
            return mid
        if price < market_price:
            lo = mid
        else:
            hi = mid

    return (lo + hi) / 2.0


# ── Binomial Tree ──────────────────────────────────────────────────────────────

def binomial_option_price(
    S, K, T, r, sigma,
    steps: int = 150,
    option_type: str = "call",
    american: bool = False,
) -> float:
    """CRR binomial tree for European and American options."""
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0 or steps <= 0:
        return np.nan

    dt = T / steps
    u  = np.exp(sigma * np.sqrt(dt))
    d  = 1.0 / u
    p  = (np.exp(r * dt) - d) / (u - d)

    if not (0 < p < 1):
        return np.nan

    # Terminal stock prices
    j_arr   = np.arange(steps + 1)
    prices  = S * (u ** j_arr) * (d ** (steps - j_arr))

    if option_type == "call":
        values = np.maximum(prices - K, 0.0)
    else:
        values = np.maximum(K - prices, 0.0)

    disc = np.exp(-r * dt)
    for i in range(steps - 1, -1, -1):
        j_arr_i  = np.arange(i + 1)
        prices_i = S * (u ** j_arr_i) * (d ** (i - j_arr_i))
        values   = disc * (p * values[1:i + 2] + (1 - p) * values[0:i + 1])
        if american:
            intrinsic = (np.maximum(prices_i - K, 0.0) if option_type == "call"
                         else np.maximum(K - prices_i, 0.0))
            values = np.maximum(values, intrinsic)

    return float(values[0])


# ── Monte Carlo ────────────────────────────────────────────────────────────────

def monte_carlo_paths(
    S, T, r, sigma,
    n_paths: int = 1000,
    n_steps: int = 252,
) -> np.ndarray:
    """GBM simulation. Returns (n_steps+1, n_paths) array."""
    dt    = T / n_steps
    paths = np.zeros((n_steps + 1, n_paths))
    paths[0] = S
    Z = np.random.standard_normal((n_steps, n_paths))
    for t in range(1, n_steps + 1):
        paths[t] = paths[t - 1] * np.exp(
            (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z[t - 1]
        )
    return paths


def monte_carlo_option_price(
    S, K, T, r, sigma,
    option_type: str = "call",
    n_paths: int = 10_000,
    n_steps: int = 252,
    antithetic: bool = True,
) -> tuple:
    """
    Monte Carlo option price with optional antithetic variates.
    Returns (price, terminal_prices, all_paths).
    """
    np.random.seed(42)
    if antithetic:
        half = n_paths // 2
        paths1 = monte_carlo_paths(S, T, r, sigma, half, n_steps)
        # Antithetic: negate the same random draws
        dt = T / n_steps
        Z  = np.random.standard_normal((n_steps, half))
        paths2 = np.zeros((n_steps + 1, half))
        paths2[0] = S
        for t in range(1, n_steps + 1):
            paths2[t] = paths2[t - 1] * np.exp(
                (r - 0.5 * sigma ** 2) * dt - sigma * np.sqrt(dt) * Z[t - 1]
            )
        paths    = np.concatenate([paths1, paths2], axis=1)
    else:
        paths = monte_carlo_paths(S, T, r, sigma, n_paths, n_steps)

    terminal = paths[-1]
    if option_type == "call":
        payoff = np.maximum(terminal - K, 0.0)
    else:
        payoff = np.maximum(K - terminal, 0.0)

    price = float(np.exp(-r * T) * payoff.mean())
    return price, terminal, paths


# ── Utilities ──────────────────────────────────────────────────────────────────

def put_call_parity_gap(call_price, put_price, S, K, T, r) -> float:
    """Deviation from put-call parity (should be ~0 for European)."""
    lhs = call_price - put_price
    rhs = S - K * np.exp(-r * T)
    return float(lhs - rhs)


def option_breakeven(option_type: str, K: float, premium: float) -> float:
    if option_type == "call":
        return K + premium
    return K - premium
