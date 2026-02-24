"""Technical indicators: MACD, Bollinger Bands, ATR, Fibonacci, Follow-Through Day detection."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Internal import: analysis-utils via importlib (kebab-case filename)
# ---------------------------------------------------------------------------
_utils_path = Path(__file__).parent / "analysis-utils.py"
_spec = importlib.util.spec_from_file_location("analysis_utils", _utils_path)
_utils = importlib.util.module_from_spec(_spec)
sys.modules["analysis_utils"] = _utils
_spec.loader.exec_module(_utils)

sma = _utils.sma
ema = _utils.ema


def compute_macd(
    df: pd.DataFrame,
    price_col: str = "close",
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """MACD line, signal line, and histogram.

    MACD line  = EMA(fast) - EMA(slow)
    Signal     = EMA(signal) of MACD line
    Histogram  = MACD - Signal

    Args:
        df: OHLCV DataFrame with a price column.
        price_col: Column to use (default 'close').
        fast: Fast EMA period (default 12).
        slow: Slow EMA period (default 26).
        signal: Signal EMA period (default 9).

    Returns:
        Input DataFrame + columns: macd, signal_line, histogram.
    """
    out = df.copy()
    ema_fast = ema(out[price_col], fast)
    ema_slow = ema(out[price_col], slow)
    out["macd"] = ema_fast - ema_slow
    out["signal_line"] = ema(out["macd"], signal)
    out["histogram"] = out["macd"] - out["signal_line"]
    return out


def compute_bollinger_bands(
    df: pd.DataFrame,
    price_col: str = "close",
    period: int = 20,
    std_dev: float = 2.0,
) -> pd.DataFrame:
    """Bollinger Bands: middle (SMA), upper, and lower bands.

    bb_middle = SMA(period)
    bb_upper  = bb_middle + std_dev * rolling_std(period)
    bb_lower  = bb_middle - std_dev * rolling_std(period)

    Args:
        df: OHLCV DataFrame.
        price_col: Column to use (default 'close').
        period: Rolling window (default 20).
        std_dev: Number of standard deviations (default 2).

    Returns:
        Input DataFrame + columns: bb_middle, bb_upper, bb_lower.
    """
    out = df.copy()
    mid = sma(out[price_col], period)
    std = out[price_col].rolling(window=period).std()
    out["bb_middle"] = mid
    out["bb_upper"] = mid + std_dev * std
    out["bb_lower"] = mid - std_dev * std
    return out


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Average True Range via SMA of True Range.

    True Range = max(high-low, |high-prev_close|, |low-prev_close|)
    ATR        = SMA(True Range, period)

    Args:
        df: DataFrame with 'high', 'low', 'close' columns.
        period: ATR period (default 14).

    Returns:
        Input DataFrame + column: atr.
    """
    out = df.copy()
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr"] = sma(tr, period)
    return out


def compute_fibonacci_retracement(high: float, low: float) -> dict:
    """Fibonacci retracement levels between a swing high and swing low.

    Levels: 0.236, 0.382, 0.5, 0.618, 0.786 applied to price range.
    Level price = high - ratio * (high - low)

    Args:
        high: Swing high price.
        low: Swing low price.

    Returns:
        Dict mapping ratio -> price level.
    """
    diff = high - low
    ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
    return {r: round(high - r * diff, 6) for r in ratios}


def detect_ftd(df: pd.DataFrame, volume_avg_period: int = 20) -> pd.Series:
    """Follow-Through Day (FTD) detection per IBD definition.

    Conditions on each bar:
    - Day index within a rally attempt is 4-7 (counted from a local trough reset)
    - Close is up >= 1.25% from previous close
    - Volume > 20-day average volume

    A trough reset occurs whenever close < previous close (rally broken).
    Day count restarts from 1 on the day after a new trough is set.

    Args:
        df: DataFrame with 'close' and 'volume' columns.
        volume_avg_period: Period for volume moving average (default 20).

    Returns:
        Boolean Series, True where FTD conditions are met.
    """
    close = df["close"]
    volume = df["volume"]

    pct_change = close.pct_change() * 100.0
    vol_avg = volume.rolling(window=volume_avg_period).mean()

    # Track rally day count using a vectorizable loop (state machine)
    n = len(close)
    day_count = np.zeros(n, dtype=int)
    count = 0

    for i in range(1, n):
        if pct_change.iloc[i] > 0:
            count += 1
        else:
            count = 0  # reset on flat/down day (trough reset)
        day_count[i] = count

    day_count_series = pd.Series(day_count, index=df.index)

    ftd = (
        (day_count_series >= 4)
        & (day_count_series <= 7)
        & (pct_change >= 1.25)
        & (volume > vol_avg)
    )
    return ftd
