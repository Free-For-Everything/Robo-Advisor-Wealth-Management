"""Risk metric charts: VaR gauge, efficient frontier, margin monitor, drawdown."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# Load theme side-effect
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
BG_PRIMARY = _theme.BG_PRIMARY
BG_SECONDARY = _theme.BG_SECONDARY
BG_TERTIARY = _theme.BG_TERTIARY
TEXT_PRIMARY = _theme.TEXT_PRIMARY
TEXT_SECONDARY = _theme.TEXT_SECONDARY
NEUTRAL = _theme.NEUTRAL


def create_var_gauge(
    var_pct: float,
    limit_pct: float = 5.0,
    confidence: float = 0.95,
    title: str = "Value at Risk",
) -> go.Figure:
    """Render a gauge chart showing current VaR vs limit.

    Args:
        var_pct: Current 1-day VaR as positive percentage (e.g. 2.3 = 2.3%).
        limit_pct: Maximum allowed VaR percentage.
        confidence: VaR confidence level for subtitle.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    utilisation = min(var_pct / limit_pct, 1.0) * 100

    # Color zones: green < 60%, amber 60-85%, red > 85%
    bar_color = (
        BULLISH if utilisation < 60
        else ACCENT_AMBER if utilisation < 85
        else BEARISH
    )

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=var_pct,
        delta={"reference": limit_pct, "valueformat": ".2f", "suffix": "%"},
        number={"suffix": "%", "font": {"color": TEXT_PRIMARY, "size": 28}},
        title={"text": f"{title}<br><span style='font-size:11px;color:{TEXT_SECONDARY}'>"
                       f"{int(confidence*100)}% confidence, 1-day</span>"},
        gauge={
            "axis": {"range": [0, limit_pct * 1.2], "ticksuffix": "%",
                     "tickcolor": TEXT_SECONDARY},
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": BG_SECONDARY,
            "bordercolor": BG_TERTIARY,
            "steps": [
                {"range": [0, limit_pct * 0.6], "color": "rgba(16,185,129,0.12)"},
                {"range": [limit_pct * 0.6, limit_pct * 0.85], "color": "rgba(245,158,11,0.12)"},
                {"range": [limit_pct * 0.85, limit_pct * 1.2], "color": "rgba(239,68,68,0.12)"},
            ],
            "threshold": {
                "line": {"color": BEARISH, "width": 2},
                "thickness": 0.75,
                "value": limit_pct,
            },
        },
    ))
    fig.update_layout(height=260, paper_bgcolor=BG_PRIMARY,
                      font={"color": TEXT_PRIMARY}, margin={"t": 60, "b": 10})
    return fig


def create_efficient_frontier(
    portfolios_df: pd.DataFrame,
    current_point: tuple[float, float] | None = None,
    title: str = "Efficient Frontier",
) -> go.Figure:
    """Plot the efficient frontier scatter.

    Args:
        portfolios_df: DataFrame with columns [volatility, returns, sharpe].
                       Each row represents a simulated or analytical portfolio.
        current_point: (volatility, returns) of the live portfolio (optional).
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=portfolios_df["volatility"],
        y=portfolios_df["returns"],
        mode="markers",
        marker={
            "size": 4,
            "color": portfolios_df["sharpe"],
            "colorscale": [[0, BEARISH], [0.5, ACCENT_AMBER], [1, BULLISH]],
            "colorbar": {"title": "Sharpe", "thickness": 12,
                         "tickfont": {"color": TEXT_SECONDARY}},
            "opacity": 0.7,
        },
        name="Simulated Portfolios",
        hovertemplate="Vol: %{x:.2f}%<br>Return: %{y:.2f}%<br>Sharpe: %{marker.color:.2f}<extra></extra>",
    ))

    if current_point is not None:
        fig.add_trace(go.Scatter(
            x=[current_point[0]],
            y=[current_point[1]],
            mode="markers",
            marker={"size": 14, "color": ACCENT_BLUE,
                    "symbol": "star", "line": {"color": "white", "width": 1.5}},
            name="Current Portfolio",
        ))

    fig.update_layout(
        title={"text": title, "x": 0.5},
        xaxis={"title": "Annualised Volatility (%)"},
        yaxis={"title": "Annualised Return (%)"},
        height=400,
        legend={"orientation": "h", "y": -0.15},
    )
    _theme.apply_theme(fig)
    return fig
