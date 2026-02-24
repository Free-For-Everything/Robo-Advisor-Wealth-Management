"""Shared math helpers for quantitative analysis - vectorized numpy/pandas implementations."""

import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average using pandas rolling window.

    Args:
        series: Price series (e.g., close prices).
        period: Lookback window size.

    Returns:
        Rolling SMA series with same index.
    """
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average using pandas ewm with span.

    Args:
        series: Price series.
        period: Span parameter (equivalent to N-period EMA).

    Returns:
        EMA series - more weight on recent values than SMA.
    """
    return series.ewm(span=period, adjust=False).mean()


def roc(series: pd.Series, period: int) -> pd.Series:
    """Rate of Change: percentage change over N periods.

    Formula: (current - prev_n) / prev_n * 100

    Args:
        series: Price series.
        period: Number of periods to look back.

    Returns:
        ROC series as percentage (not decimal).
    """
    prev = series.shift(period)
    return (series - prev) / prev * 100.0


def rolling_std(series: pd.Series, period: int) -> pd.Series:
    """Rolling Standard Deviation using pandas rolling window.

    Args:
        series: Input series (prices, returns, etc.).
        period: Lookback window size.

    Returns:
        Rolling standard deviation series (ddof=1 by default).
    """
    return series.rolling(window=period).std()
