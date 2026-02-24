"""Reward function for RL trading agent: Sharpe-based with cost and penalty deductions."""

from __future__ import annotations

from typing import List

import numpy as np

# Vietnam market constants from config/trading.yaml
_TAX_RATE = 0.001       # 0.1% selling tax
_BROKER_FEE = 0.003     # 0.3% broker commission
_TOTAL_COST_RATE = _TAX_RATE + _BROKER_FEE  # 0.4% per trade

# Violation penalty magnitudes
_PENALTY_T_PLUS = -10.0   # T+2.5 settlement violation
_PENALTY_VAR = -5.0       # VaR breach violation

_EPSILON = 1e-8  # avoid division by zero in Sharpe


def compute_reward(
    portfolio_returns: List[float] | np.ndarray,
    risk_free_rate: float = 0.0,
) -> float:
    """Compute Sharpe-ratio-based reward over a return series.

    Sharpe = (mean_return - risk_free_rate) / std_return

    Args:
        portfolio_returns: Sequence of period returns (e.g. daily log-returns).
        risk_free_rate: Per-period risk-free rate (default 0).

    Returns:
        Sharpe ratio as float. Returns 0.0 for empty or zero-std series.
    """
    arr = np.asarray(portfolio_returns, dtype=float)
    arr = np.nan_to_num(arr, nan=0.0)
    if arr.size == 0:
        return 0.0
    excess = arr - risk_free_rate
    std = float(np.std(excess))
    if std < _EPSILON:
        return 0.0
    return float(np.mean(excess) / std)


def apply_transaction_costs(reward: float, trade_value: float) -> float:
    """Deduct transaction cost impact from reward.

    Cost = (tax_rate + broker_fee) * |trade_value|.
    Reward is reduced proportionally to trade value.

    Args:
        reward: Current reward signal.
        trade_value: Gross trade value (absolute VND amount).

    Returns:
        Reward reduced by cost fraction.
    """
    cost = _TOTAL_COST_RATE * abs(trade_value)
    return reward - cost


def apply_penalty(reward: float, violation_type: str) -> float:
    """Apply a hard penalty for rule violations.

    Args:
        reward: Current reward value.
        violation_type: One of 't_plus' or 'var'.

    Returns:
        Reward after penalty applied.

    Raises:
        ValueError: If violation_type is unknown.
    """
    penalties = {
        "t_plus": _PENALTY_T_PLUS,
        "var": _PENALTY_VAR,
    }
    if violation_type not in penalties:
        raise ValueError(f"Unknown violation_type '{violation_type}'. "
                         f"Expected one of {list(penalties)}")
    return reward + penalties[violation_type]


def total_reward(
    portfolio_returns: List[float] | np.ndarray,
    trades: List[dict],
    violations: List[str],
    risk_free_rate: float = 0.0,
) -> float:
    """Compute full reward: Sharpe minus costs and penalties.

    Args:
        portfolio_returns: Period return series.
        trades: List of trade dicts with key 'value' (float, gross amount).
        violations: List of violation type strings ('t_plus', 'var').
        risk_free_rate: Per-period risk-free rate.

    Returns:
        Final scalar reward.
    """
    reward = compute_reward(portfolio_returns, risk_free_rate)

    # Deduct transaction costs for each trade
    for trade in trades:
        trade_value = float(trade.get("value", 0.0))
        reward = apply_transaction_costs(reward, trade_value)

    # Apply hard penalties for violations
    for violation in violations:
        reward = apply_penalty(reward, violation)

    return reward
