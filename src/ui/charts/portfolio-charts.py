"""Portfolio-level charts: allocation pie, P&L bar, equity curve."""

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
BG_PRIMARY = _theme.BG_PRIMARY
BG_SECONDARY = _theme.BG_SECONDARY
BG_TERTIARY = _theme.BG_TERTIARY
TEXT_PRIMARY = _theme.TEXT_PRIMARY
TEXT_SECONDARY = _theme.TEXT_SECONDARY
CHART_COLORS = _theme.CHART_COLORS


def create_allocation_pie(
    labels: list[str],
    values: list[float],
    title: str = "Portfolio Allocation",
) -> go.Figure:
    """Donut pie chart showing portfolio weight by asset / sector.

    Args:
        labels: Asset or sector names.
        values: Corresponding weights or market values (will be normalised).
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker={"colors": CHART_COLORS, "line": {"color": BG_PRIMARY, "width": 2}},
        textinfo="label+percent",
        textfont={"color": TEXT_PRIMARY, "size": 11},
        hovertemplate="%{label}<br>Value: %{value:,.0f}<br>Weight: %{percent}<extra></extra>",
    ))
    fig.update_layout(
        title={"text": title, "x": 0.5},
        height=380,
        paper_bgcolor=BG_PRIMARY,
        font={"color": TEXT_PRIMARY},
        legend={"font": {"color": TEXT_PRIMARY}, "bgcolor": BG_SECONDARY},
        margin={"t": 50, "b": 20, "l": 20, "r": 20},
        annotations=[{
            "text": "Allocation",
            "x": 0.5, "y": 0.5,
            "font_size": 13,
            "font_color": TEXT_SECONDARY,
            "showarrow": False,
        }],
    )
    return fig


def create_pnl_bar(
    dates: list,
    pnl_values: list[float],
    title: str = "Daily P&L",
) -> go.Figure:
    """Signed bar chart of daily realised or unrealised P&L.

    Args:
        dates: List of date labels (str or datetime).
        pnl_values: Corresponding P&L values (positive = green, negative = red).
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    colors = [BULLISH if v >= 0 else BEARISH for v in pnl_values]

    fig = go.Figure(go.Bar(
        x=dates,
        y=pnl_values,
        marker_color=colors,
        hovertemplate="%{x|%Y-%m-%d}<br>P&L: %{y:+,.0f}<extra></extra>",
        name="Daily P&L",
    ))
    fig.add_hline(y=0, line={"color": BG_TERTIARY, "width": 1})
    fig.update_layout(
        title={"text": title, "x": 0.5},
        yaxis={"title": "P&L (VND)"},
        height=300,
        showlegend=False,
    )
    _theme.apply_theme(fig)
    return fig


def create_equity_curve(
    equity_series: pd.Series,
    benchmark_series: pd.Series | None = None,
    title: str = "Equity Curve",
) -> go.Figure:
    """Line chart of portfolio NAV with optional benchmark overlay.

    Args:
        equity_series: Portfolio value series indexed by datetime.
        benchmark_series: Optional benchmark (e.g. VN-Index) also indexed by datetime.
                          Will be rebased to match portfolio starting value.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    # Portfolio line
    fig.add_trace(go.Scatter(
        x=equity_series.index,
        y=equity_series.values,
        mode="lines",
        line={"color": ACCENT_BLUE, "width": 2},
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
        name="Portfolio",
        hovertemplate="%{x|%Y-%m-%d}<br>NAV: %{y:,.0f}<extra></extra>",
    ))

    # Benchmark overlay rebased to same start
    if benchmark_series is not None and not benchmark_series.empty:
        rebase_factor = equity_series.iloc[0] / benchmark_series.iloc[0]
        rebased = benchmark_series * rebase_factor
        fig.add_trace(go.Scatter(
            x=rebased.index,
            y=rebased.values,
            mode="lines",
            line={"color": ACCENT_AMBER, "width": 1.5, "dash": "dot"},
            name="Benchmark (rebased)",
            hovertemplate="%{x|%Y-%m-%d}<br>Benchmark: %{y:,.0f}<extra></extra>",
        ))

    fig.update_layout(
        title={"text": title, "x": 0.5},
        yaxis={"title": "Portfolio Value (VND)"},
        height=360,
        legend={"orientation": "h", "y": -0.15},
    )
    _theme.apply_theme(fig)
    return fig
