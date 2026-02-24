"""Kelly Criterion position sizing with Half-Kelly safety margin."""

import pandas as pd


def kelly_fraction(win_prob: float, win_loss_ratio: float) -> float:
    """Full Kelly fraction: f* = p - (1-p)/b.

    Args:
        win_prob: Probability of winning (0 < p < 1).
        win_loss_ratio: Average win / average loss (b > 0).

    Returns:
        Optimal fraction of capital to risk. Can be negative (don't bet).
    """
    if win_loss_ratio <= 0:
        raise ValueError("win_loss_ratio must be positive")
    return win_prob - (1 - win_prob) / win_loss_ratio


def half_kelly(win_prob: float, win_loss_ratio: float) -> float:
    """Half-Kelly for reduced volatility: f*/2."""
    return kelly_fraction(win_prob, win_loss_ratio) / 2


def optimal_position_size(
    capital: float,
    kelly_frac: float,
    max_position_pct: float = 0.25,
) -> float:
    """Position size in currency, capped at max_position_pct.

    Args:
        capital: Total portfolio capital.
        kelly_frac: Kelly fraction (from kelly_fraction or half_kelly).
        max_position_pct: Maximum percentage of capital per position.

    Returns:
        Dollar amount to allocate to the position.
    """
    effective_frac = max(0.0, min(kelly_frac, max_position_pct))
    return capital * effective_frac


def estimate_win_stats(trade_history_df: pd.DataFrame) -> tuple[float, float]:
    """Estimate win probability and win/loss ratio from trade history.

    Args:
        trade_history_df: DataFrame with 'pnl' column (profit/loss per trade).

    Returns:
        Tuple of (win_probability, win_loss_ratio).
    """
    pnl = trade_history_df["pnl"]
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]

    if len(pnl) == 0:
        return 0.0, 1.0

    win_prob = len(wins) / len(pnl)

    avg_win = wins.mean() if len(wins) > 0 else 0.0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 1.0

    win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1.0
    return win_prob, win_loss_ratio
