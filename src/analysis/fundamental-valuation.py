"""Fundamental valuation models: Graham, Black-Scholes, Bond FV, ETF tracking error."""

import math

import pandas as pd
from scipy.stats import norm


def graham_intrinsic_value(eps: float, growth_rate: float) -> float:
    """Graham Number intrinsic value formula.

    Formula: EPS * (8.5 + 2 * g)
    where g = expected annual growth rate in percentage points (e.g., 7.5 for 7.5%).

    Benjamin Graham's original formula from The Intelligent Investor.

    Args:
        eps: Trailing twelve-month earnings per share.
        growth_rate: Expected 7-10 year EPS growth rate (percentage, not decimal).

    Returns:
        Intrinsic value estimate as float.
    """
    return float(eps * (8.5 + 2.0 * growth_rate))


def black_scholes_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes European call option price.

    Formula:
        d1 = (ln(S/K) + (r + sigma^2/2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        C  = S * N(d1) - K * exp(-r*T) * N(d2)

    Args:
        S: Current underlying asset price.
        K: Option strike price.
        T: Time to expiration in years.
        r: Risk-free interest rate (annual, decimal, e.g. 0.05 for 5%).
        sigma: Annualized volatility (decimal, e.g. 0.20 for 20%).

    Returns:
        Call option fair value as float.
    """
    if T <= 0 or sigma <= 0:
        return max(S - K, 0.0)
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    return float(S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2))


def black_scholes_put(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes European put option price via put-call parity.

    Formula:
        P = C - S + K * exp(-r * T)
    which is equivalent to:
        P = K * exp(-r*T) * N(-d2) - S * N(-d1)

    Args:
        S: Current underlying asset price.
        K: Option strike price.
        T: Time to expiration in years.
        r: Risk-free interest rate (annual, decimal).
        sigma: Annualized volatility (decimal).

    Returns:
        Put option fair value as float.
    """
    if T <= 0 or sigma <= 0:
        return max(K - S, 0.0)
    call = black_scholes_call(S, K, T, r, sigma)
    # Put-call parity: P = C - S + K * e^(-rT)
    return float(call - S + K * math.exp(-r * T))


def bond_future_value(
    pv: float,
    rate: float,
    n_periods: float,
    compounding_freq: int,
) -> float:
    """Compound interest future value for bonds / fixed income instruments.

    Formula: FV = PV * (1 + r/n)^(n * t)

    Args:
        pv: Present value (principal).
        rate: Annual interest rate (decimal, e.g. 0.06 for 6%).
        n_periods: Total time in years.
        compounding_freq: Number of compounding periods per year
                          (1=annual, 2=semi-annual, 4=quarterly, 12=monthly).

    Returns:
        Future value as float.
    """
    return float(pv * (1.0 + rate / compounding_freq) ** (compounding_freq * n_periods))


def etf_tracking_error(
    etf_returns: pd.Series,
    index_returns: pd.Series,
) -> float:
    """ETF tracking error: annualized standard deviation of return differences.

    Tracking Error = std(etf_returns - index_returns) * sqrt(252)
    Uses daily returns; annualizes by sqrt(252) convention.

    Args:
        etf_returns: Daily return series of the ETF (decimal, e.g. 0.01 = 1%).
        index_returns: Daily return series of the target index (same length/index).

    Returns:
        Annualized tracking error as float (decimal).
    """
    diff = etf_returns - index_returns
    return float(diff.std() * math.sqrt(252))
