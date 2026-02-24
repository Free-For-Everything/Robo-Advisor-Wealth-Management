"""Candlestick chart with volume, SMA/Bollinger overlays and MACD subplot."""

from __future__ import annotations

# Load theme via direct import (kebab loader not needed inside same package tree
# since this file is exec'd by importlib; we import plotly template by side-effect)
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_THEME_PATH = Path(__file__).parent.parent / "theme" / "chart-theme.py"
if "chart_theme" not in sys.modules:
    import importlib.util
    _spec = importlib.util.spec_from_file_location("chart_theme", _THEME_PATH)
    _mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
    sys.modules["chart_theme"] = _mod
    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
_theme = sys.modules["chart_theme"]

BULLISH = _theme.BULLISH
BEARISH = _theme.BEARISH
ACCENT_BLUE = _theme.ACCENT_BLUE
ACCENT_AMBER = _theme.ACCENT_AMBER
ACCENT_PURPLE = _theme.ACCENT_PURPLE
BG_TERTIARY = _theme.BG_TERTIARY


# ── Technical indicator helpers ────────────────────────────────────────────────

def _sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def _bollinger(series: pd.Series, window: int = 20, std: float = 2.0):
    mid = _sma(series, window)
    sigma = series.rolling(window).std()
    return mid - std * sigma, mid, mid + std * sigma


def _macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


# ── Public API ─────────────────────────────────────────────────────────────────

def create_candlestick(
    ohlcv_df: pd.DataFrame,
    symbol: str = "",
    sma_periods: list[int] | None = None,
    show_bollinger: bool = True,
    show_macd: bool = True,
) -> go.Figure:
    """Build a candlestick chart with optional overlays and MACD subplot.

    Args:
        ohlcv_df: DataFrame with columns [open, high, low, close, volume]
                  and a DatetimeIndex or 'date'/'datetime' column.
        symbol: Ticker label shown in title.
        sma_periods: SMA windows to overlay, defaults to [20, 50].
        show_bollinger: Whether to draw Bollinger Bands.
        show_macd: Whether to add MACD subplot below price.

    Returns:
        Plotly Figure object.
    """
    df = ohlcv_df.copy()

    # Normalise index to datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        date_col = next((c for c in df.columns if c.lower() in ("date", "datetime", "time")), None)
        if date_col:
            df = df.set_index(pd.to_datetime(df[date_col])).drop(columns=[date_col])
        else:
            df.index = pd.to_datetime(df.index)

    # Normalise column names to lowercase
    df.columns = [c.lower() for c in df.columns]

    sma_periods = sma_periods or [20, 50]
    sma_colors = [ACCENT_BLUE, ACCENT_AMBER, ACCENT_PURPLE]

    row_heights = [0.55, 0.2, 0.25] if show_macd else [0.7, 0.3]
    rows = 3 if show_macd else 2
    subplot_titles = [f"{symbol} Price", "Volume", "MACD"] if show_macd else [f"{symbol} Price", "Volume"]

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        row_heights=row_heights,
        vertical_spacing=0.03,
        subplot_titles=subplot_titles,
    )

    # ── Candlestick ──
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        increasing_line_color=BULLISH,
        decreasing_line_color=BEARISH,
        name="OHLC",
        showlegend=False,
    ), row=1, col=1)

    # ── SMA overlays ──
    for i, period in enumerate(sma_periods):
        sma = _sma(df["close"], period)
        fig.add_trace(go.Scatter(
            x=df.index, y=sma,
            mode="lines",
            line={"color": sma_colors[i % len(sma_colors)], "width": 1.2},
            name=f"SMA{period}",
        ), row=1, col=1)

    # ── Bollinger Bands ──
    if show_bollinger:
        bb_low, bb_mid, bb_high = _bollinger(df["close"])
        fig.add_trace(go.Scatter(
            x=df.index, y=bb_high,
            mode="lines", line={"color": ACCENT_PURPLE, "width": 1, "dash": "dot"},
            name="BB Upper", showlegend=True,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=bb_low,
            mode="lines", line={"color": ACCENT_PURPLE, "width": 1, "dash": "dot"},
            fill="tonexty", fillcolor="rgba(168,85,247,0.07)",
            name="BB Lower", showlegend=True,
        ), row=1, col=1)

    # ── Volume bars ──
    vol_colors = [BULLISH if c >= o else BEARISH
                  for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["volume"],
        marker_color=vol_colors,
        name="Volume", showlegend=False,
        opacity=0.7,
    ), row=2, col=1)

    # ── MACD ──
    if show_macd:
        macd_line, signal_line, histogram = _macd(df["close"])
        hist_colors = [BULLISH if v >= 0 else BEARISH for v in histogram.fillna(0)]
        fig.add_trace(go.Bar(
            x=df.index, y=histogram,
            marker_color=hist_colors,
            name="MACD Hist", showlegend=False, opacity=0.8,
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=macd_line,
            mode="lines", line={"color": ACCENT_BLUE, "width": 1.5},
            name="MACD",
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=signal_line,
            mode="lines", line={"color": ACCENT_AMBER, "width": 1.5},
            name="Signal",
        ), row=3, col=1)

    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        legend={"orientation": "h", "y": 1.02, "x": 0},
        title={"text": f"{symbol} — Technical Analysis", "x": 0.5},
    )
    _theme.apply_theme(fig)
    return fig
