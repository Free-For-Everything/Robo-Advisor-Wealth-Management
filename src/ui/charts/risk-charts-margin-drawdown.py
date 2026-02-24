"""Risk charts: margin monitor bar chart and drawdown area chart."""

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
ACCENT_AMBER = _theme.ACCENT_AMBER
BG_TERTIARY = _theme.BG_TERTIARY


def create_margin_monitor(
    used_margin: float,
    total_margin: float,
    maintenance_margin: float,
    title: str = "Margin Monitor",
) -> go.Figure:
    """Horizontal bar chart showing margin utilisation with call threshold.

    Args:
        used_margin: Current margin in use (currency).
        total_margin: Total available margin (currency).
        maintenance_margin: Maintenance margin level (currency).
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    if total_margin <= 0:
        # Return empty figure with warning annotation
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient margin data",
            showarrow=False,
            font={"size": 14, "color": BEARISH},
            xref="paper", yref="paper",
            x=0.5, y=0.5,
        )
        fig.update_layout(
            title={"text": title, "x": 0.5},
            height=160,
            xaxis={"visible": False},
            yaxis={"visible": False},
        )
        _theme.apply_theme(fig)
        return fig

    used_pct = used_margin / total_margin * 100
    maint_pct = maintenance_margin / total_margin * 100
    free_pct = max(0.0, 100 - used_pct)

    bar_color = BULLISH if used_pct < maint_pct * 0.8 else ACCENT_AMBER if used_pct < maint_pct else BEARISH

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[used_pct], y=["Margin"],
        orientation="h",
        marker_color=bar_color,
        name="Used",
        text=[f"{used_pct:.1f}%"],
        textposition="inside",
    ))
    fig.add_trace(go.Bar(
        x=[free_pct], y=["Margin"],
        orientation="h",
        marker_color=BG_TERTIARY,
        name="Free",
        opacity=0.4,
    ))
    # Maintenance line
    fig.add_vline(
        x=maint_pct,
        line={"color": BEARISH, "width": 2, "dash": "dash"},
        annotation_text="Maintenance",
        annotation_font_color=BEARISH,
    )
    fig.update_layout(
        title={"text": title, "x": 0.5},
        barmode="stack",
        xaxis={"range": [0, 105], "title": "% of Total Margin", "ticksuffix": "%"},
        height=160,
        showlegend=True,
        legend={"orientation": "h", "y": -0.4},
        margin={"t": 40, "b": 60, "l": 60, "r": 20},
    )
    _theme.apply_theme(fig)
    return fig


def create_drawdown_chart(
    equity_series: pd.Series,
    title: str = "Drawdown",
) -> go.Figure:
    """Plot portfolio drawdown over time as a filled area chart.

    Args:
        equity_series: Series of portfolio values indexed by datetime.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown.values,
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(239,68,68,0.2)",
        line={"color": BEARISH, "width": 1.5},
        name="Drawdown",
        hovertemplate="%{x|%Y-%m-%d}<br>Drawdown: %{y:.2f}%<extra></extra>",
    ))
    max_dd = drawdown.min()
    max_dd_date = drawdown.idxmin()
    fig.add_annotation(
        x=max_dd_date, y=max_dd,
        text=f"Max DD: {max_dd:.1f}%",
        showarrow=True, arrowhead=2,
        font={"color": BEARISH, "size": 11},
        arrowcolor=BEARISH,
    )
    fig.update_layout(
        title={"text": title, "x": 0.5},
        yaxis={"title": "Drawdown (%)", "ticksuffix": "%"},
        height=300,
        showlegend=False,
    )
    _theme.apply_theme(fig)
    return fig
