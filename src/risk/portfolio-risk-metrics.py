"""Portfolio risk metrics: returns, Sharpe ratio, max drawdown, volatility, beta."""

import numpy as np
import pandas as pd


def compute_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """Compute daily percentage returns from a prices DataFrame.

    Args:
        prices_df: DataFrame with asset price columns (one column per asset).

    Returns:
        DataFrame of daily returns (first row is NaN-dropped).
    """
    return prices_df.pct_change().dropna()


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Annualized Sharpe ratio: (mean_daily - rf_daily) / std_daily * sqrt(252).

    Args:
        returns: Daily return series.
        risk_free_rate: Annualized risk-free rate (default 0.0).

    Returns:
        Sharpe ratio as float. Returns 0.0 if std is zero.
    """
    rf_daily = risk_free_rate / 252.0
    excess = returns - rf_daily
    std = excess.std(ddof=1)
    if std == 0.0 or np.isnan(std):
        return 0.0
    return float((excess.mean() / std) * np.sqrt(252))


def max_drawdown(equity_curve: pd.Series) -> float:
    """Maximum peak-to-trough drawdown of an equity curve.

    Args:
        equity_curve: Series of portfolio values over time.

    Returns:
        Max drawdown as a negative float (e.g. -0.30 means -30%).
    """
    cumulative_max = equity_curve.cummax()
    drawdowns = (equity_curve - cumulative_max) / cumulative_max
    return float(drawdowns.min())


def portfolio_volatility(returns: pd.Series) -> float:
    """Annualized volatility: std(daily_returns) * sqrt(252).

    Args:
        returns: Daily return series.

    Returns:
        Annualized volatility as float.
    """
    return float(returns.std(ddof=1) * np.sqrt(252))


def portfolio_beta(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Portfolio beta relative to benchmark: cov(r, r_bm) / var(r_bm).

    Args:
        returns: Portfolio daily returns.
        benchmark_returns: Benchmark daily returns (same length/index).

    Returns:
        Beta as float. Returns 0.0 if benchmark variance is zero.
    """
    aligned = pd.concat([returns, benchmark_returns], axis=1).dropna()
    if aligned.empty or len(aligned) < 2:
        return 0.0
    r = aligned.iloc[:, 0]
    bm = aligned.iloc[:, 1]
    bm_var = bm.var(ddof=1)
    if bm_var == 0.0:
        return 0.0
    cov = r.cov(bm)
    return float(cov / bm_var)
