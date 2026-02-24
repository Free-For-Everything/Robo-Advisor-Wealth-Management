"""Value at Risk (VaR) calculations: parametric, historical, portfolio, CVaR."""

import numpy as np
import pandas as pd
from scipy import stats


def parametric_var(
    returns: pd.Series,
    confidence: float = 0.95,
    holding_period: int = 1,
) -> float:
    """Parametric (Gaussian) VaR.

    Formula: VaR = -(mu - z * sigma * sqrt(T))
    Returns a positive number representing the loss threshold.
    """
    mu = returns.mean()
    sigma = returns.std()
    z = stats.norm.ppf(1 - confidence)
    # z is negative for confidence > 0.5, so -(mu + z*sigma*sqrt(T)) is positive
    return -(mu + z * sigma * np.sqrt(holding_period))


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical simulation VaR using percentile method.

    Returns a positive number representing the loss threshold.
    """
    percentile = (1 - confidence) * 100
    return -np.percentile(returns.dropna(), percentile)


def portfolio_var(
    weights: np.ndarray,
    cov_matrix: np.ndarray,
    confidence: float = 0.95,
    portfolio_value: float = 1.0,
) -> float:
    """Portfolio VaR using covariance matrix.

    Formula: VaR = z * sqrt(w^T * Sigma * w) * portfolio_value
    """
    z = stats.norm.ppf(1 - confidence)
    portfolio_std = np.sqrt(weights @ cov_matrix @ weights)
    return z * portfolio_std * portfolio_value


def conditional_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Conditional VaR (Expected Shortfall): average loss beyond VaR.

    Returns a positive number.
    """
    var_threshold = -historical_var(returns, confidence)  # negative loss
    tail_losses = returns[returns <= var_threshold]
    if tail_losses.empty:
        return historical_var(returns, confidence)
    return -tail_losses.mean()
