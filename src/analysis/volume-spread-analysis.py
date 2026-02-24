"""Volume Spread Analysis (VSA): active volume, spring/upthrust detection, signal classification."""

import numpy as np
import pandas as pd


def compute_active_volume(df: pd.DataFrame) -> pd.Series:
    """Active volume: volume weighted by directional price body within bar range.

    Formula: (close - open) / (high - low) * volume
    When high == low (doji bar), result is 0 to avoid division by zero.

    Args:
        df: DataFrame with 'open', 'high', 'low', 'close', 'volume' columns.

    Returns:
        Series of active volume values (positive = bullish, negative = bearish).
    """
    bar_range = df["high"] - df["low"]
    body = df["close"] - df["open"]
    # Compute ratio safely: where range != 0, divide; where range == 0, use 0
    ratio = body / bar_range.replace(0, np.nan)  # NaN where range==0
    active = (ratio * df["volume"]).fillna(0.0)   # 0 on doji bars
    return active


def detect_spring(df: pd.DataFrame, support_level: float) -> pd.Series:
    """Detect Spring: price dips below support but closes back above it (bullish reversal).

    Spring conditions per bar:
    - Low penetrates below support_level
    - Close is above support_level (rejection of breakdown)
    - Volume is below 20-bar average (lack of supply on test)

    Args:
        df: DataFrame with 'low', 'close', 'volume' columns.
        support_level: Horizontal support price level to test.

    Returns:
        Boolean Series, True on Spring bars.
    """
    vol_avg = df["volume"].rolling(window=20, min_periods=1).mean()
    spring = (
        (df["low"] < support_level)
        & (df["close"] > support_level)
        & (df["volume"] < vol_avg)
    )
    return spring


def detect_upthrust(df: pd.DataFrame, resistance_level: float) -> pd.Series:
    """Detect Upthrust: price spikes above resistance but closes back below it (bearish reversal).

    Upthrust conditions per bar:
    - High penetrates above resistance_level
    - Close is below resistance_level (rejection of breakout)
    - Volume is above 20-bar average (supply overwhelming demand)

    Args:
        df: DataFrame with 'high', 'close', 'volume' columns.
        resistance_level: Horizontal resistance price level to test.

    Returns:
        Boolean Series, True on Upthrust bars.
    """
    vol_avg = df["volume"].rolling(window=20, min_periods=1).mean()
    upthrust = (
        (df["high"] > resistance_level)
        & (df["close"] < resistance_level)
        & (df["volume"] > vol_avg)
    )
    return upthrust


def classify_vsa_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Classify VSA signals for each bar into labeled categories.

    Signal hierarchy (first match wins):
    - 'stopping_volume': Very high volume (> 2x 20-bar avg), small spread (< 0.5x avg range)
    - 'effort_no_result': High volume (> 1.5x avg), small price move (< 0.3x avg range)
    - 'no_supply': Low volume (< 0.7x avg), down bar (close < open)
    - 'no_demand': Low volume (< 0.7x avg), up bar (close > open)
    - 'wide_spread_up': Large spread (> 1.5x avg range), close >= open
    - 'wide_spread_down': Large spread (> 1.5x avg range), close < open
    - 'neutral': Everything else

    Args:
        df: DataFrame with 'open', 'high', 'low', 'close', 'volume' columns.

    Returns:
        Input DataFrame + column 'vsa_signal' with string labels.
    """
    out = df.copy()
    vol_avg = df["volume"].rolling(window=20, min_periods=1).mean()
    bar_range = (df["high"] - df["low"]).abs()
    range_avg = bar_range.rolling(window=20, min_periods=1).mean()

    high_vol = df["volume"] > (1.5 * vol_avg)
    very_high_vol = df["volume"] > (2.0 * vol_avg)
    low_vol = df["volume"] < (0.7 * vol_avg)
    small_spread = bar_range < (0.5 * range_avg)
    tiny_move = bar_range < (0.3 * range_avg)
    wide_spread = bar_range > (1.5 * range_avg)
    up_bar = df["close"] >= df["open"]
    down_bar = df["close"] < df["open"]

    conditions = [
        very_high_vol & small_spread,
        high_vol & tiny_move,
        low_vol & down_bar,
        low_vol & up_bar,
        wide_spread & up_bar,
        wide_spread & down_bar,
    ]
    choices = [
        "stopping_volume",
        "effort_no_result",
        "no_supply",
        "no_demand",
        "wide_spread_up",
        "wide_spread_down",
    ]
    out["vsa_signal"] = np.select(conditions, choices, default="neutral")
    return out
