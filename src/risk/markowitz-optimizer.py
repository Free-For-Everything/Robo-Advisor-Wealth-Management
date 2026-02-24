"""Markowitz mean-variance portfolio optimization with efficient frontier."""

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def _portfolio_stats(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
) -> tuple[float, float]:
    """Compute annualized return and volatility for given weights."""
    port_return = np.dot(weights, mean_returns) * 252
    port_vol = np.sqrt(weights @ cov_matrix @ weights) * np.sqrt(252)
    return port_return, port_vol


def minimum_variance_portfolio(returns_df: pd.DataFrame) -> dict:
    """Find the minimum variance portfolio (long-only).

    Returns:
        dict with keys: weights, risk, return (annualized).
    """
    n = returns_df.shape[1]
    mean_ret = returns_df.mean().values
    cov = returns_df.cov().values

    def objective(w):
        return w @ cov @ w

    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    bounds = [(0, 1)] * n
    w0 = np.ones(n) / n

    result = minimize(objective, w0, method="SLSQP", bounds=bounds, constraints=constraints)
    ret, vol = _portfolio_stats(result.x, mean_ret, cov)
    return {"weights": result.x.tolist(), "risk": vol, "return": ret}


def maximum_sharpe_portfolio(
    returns_df: pd.DataFrame,
    risk_free: float = 0.0,
) -> dict:
    """Find the maximum Sharpe ratio portfolio (long-only)."""
    n = returns_df.shape[1]
    mean_ret = returns_df.mean().values
    cov = returns_df.cov().values

    def neg_sharpe(w):
        ret, vol = _portfolio_stats(w, mean_ret, cov)
        if vol == 0:
            return 0
        return -(ret - risk_free) / vol

    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    bounds = [(0, 1)] * n
    w0 = np.ones(n) / n

    result = minimize(neg_sharpe, w0, method="SLSQP", bounds=bounds, constraints=constraints)
    ret, vol = _portfolio_stats(result.x, mean_ret, cov)
    return {"weights": result.x.tolist(), "risk": vol, "return": ret}


def target_return_portfolio(returns_df: pd.DataFrame, target: float) -> dict:
    """Find minimum variance portfolio achieving target annualized return."""
    n = returns_df.shape[1]
    mean_ret = returns_df.mean().values
    cov = returns_df.cov().values

    def objective(w):
        return w @ cov @ w

    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1},
        {"type": "eq", "fun": lambda w: np.dot(w, mean_ret) * 252 - target},
    ]
    bounds = [(0, 1)] * n
    w0 = np.ones(n) / n

    result = minimize(objective, w0, method="SLSQP", bounds=bounds, constraints=constraints)
    ret, vol = _portfolio_stats(result.x, mean_ret, cov)
    return {"weights": result.x.tolist(), "risk": vol, "return": ret}


def compute_efficient_frontier(
    returns_df: pd.DataFrame,
    n_points: int = 50,
) -> pd.DataFrame:
    """Compute efficient frontier as DataFrame of (risk, return, weights)."""
    min_port = minimum_variance_portfolio(returns_df)
    max_port = maximum_sharpe_portfolio(returns_df)

    min_ret = min_port["return"]
    max_ret = max(max_port["return"], min_ret + 0.01)
    target_returns = np.linspace(min_ret, max_ret * 1.5, n_points)

    results = []
    for t in target_returns:
        try:
            port = target_return_portfolio(returns_df, t)
            results.append({"risk": port["risk"], "return": port["return"], "weights": port["weights"]})
        except Exception:
            continue

    return pd.DataFrame(results)
