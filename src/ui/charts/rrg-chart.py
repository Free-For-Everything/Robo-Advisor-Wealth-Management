"""Relative Rotation Graph (RRG) chart for momentum analysis."""

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

QUAD_LEADING = _theme.QUAD_LEADING
QUAD_WEAKENING = _theme.QUAD_WEAKENING
QUAD_LAGGING = _theme.QUAD_LAGGING
QUAD_IMPROVING = _theme.QUAD_IMPROVING
BG_SECONDARY = _theme.BG_SECONDARY
BG_TERTIARY = _theme.BG_TERTIARY
TEXT_SECONDARY = _theme.TEXT_SECONDARY

# Quadrant labels and fill colours (low alpha rectangles)
_QUADS = [
    # (x0, x1, y0, y1, fill_color, label, label_x, label_y)
    (100, None, 100, None, "rgba(16,185,129,0.07)", "LEADING", 102, 102),
    (None, 100, 100, None, "rgba(245,158,11,0.07)", "WEAKENING", 96, 102),
    (None, 100, None, 100, "rgba(239,68,68,0.07)", "LAGGING", 96, 98),
    (100, None, None, 100, "rgba(59,130,246,0.07)", "IMPROVING", 102, 98),
]


def _quad_color(rs_ratio: float, rs_momentum: float) -> str:
    """Return scatter marker color based on quadrant position."""
    if rs_ratio >= 100 and rs_momentum >= 100:
        return QUAD_LEADING
    if rs_ratio < 100 and rs_momentum >= 100:
        return QUAD_WEAKENING
    if rs_ratio < 100 and rs_momentum < 100:
        return QUAD_LAGGING
    return QUAD_IMPROVING


def create_rrg_chart(
    rrg_data_df: pd.DataFrame,
    tail_length: int = 5,
    title: str = "Relative Rotation Graph",
) -> go.Figure:
    """Create an interactive RRG scatter chart.

    Args:
        rrg_data_df: DataFrame with columns:
            symbol, rs_ratio, rs_momentum, [period] (optional tail sequence)
        tail_length: Number of historical points to draw as tail lines.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    df = rrg_data_df.copy()
    required = {"symbol", "rs_ratio", "rs_momentum"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"RRG data missing columns: {missing}")

    fig = go.Figure()

    # ── Quadrant shading ──────────────────────────────────────────────────────
    axis_range_x = [94, 106]
    axis_range_y = [94, 106]

    for x0, x1, y0, y1, color, label, lx, ly in _QUADS:
        x0_ = x0 or axis_range_x[0]
        x1_ = x1 or axis_range_x[1]
        y0_ = y0 or axis_range_y[0]
        y1_ = y1 or axis_range_y[1]
        fig.add_shape(
            type="rect",
            x0=x0_, x1=x1_, y0=y0_, y1=y1_,
            fillcolor=color,
            line_width=0,
            layer="below",
        )
        fig.add_annotation(
            x=lx, y=ly,
            text=f"<b>{label}</b>",
            showarrow=False,
            font={"size": 11, "color": TEXT_SECONDARY},
            opacity=0.6,
        )

    # ── Centre lines at 100/100 ───────────────────────────────────────────────
    for axis, val in [("x", 100), ("y", 100)]:
        line_kw = dict(type="line", line={"color": BG_TERTIARY, "width": 1, "dash": "dot"})
        if axis == "x":
            fig.add_shape(**line_kw, x0=val, x1=val, y0=axis_range_y[0], y1=axis_range_y[1])
        else:
            fig.add_shape(**line_kw, x0=axis_range_x[0], x1=axis_range_x[1], y0=val, y1=val)

    # ── Per-symbol scatter + tail ─────────────────────────────────────────────
    has_period = "period" in df.columns

    for symbol in df["symbol"].unique():
        sym_df = df[df["symbol"] == symbol].copy()
        if has_period:
            sym_df = sym_df.sort_values("period")

        latest = sym_df.iloc[-1]
        color = _quad_color(latest["rs_ratio"], latest["rs_momentum"])

        # Tail line (historical path)
        if has_period and len(sym_df) > 1:
            tail = sym_df.tail(tail_length)
            fig.add_trace(go.Scatter(
                x=tail["rs_ratio"],
                y=tail["rs_momentum"],
                mode="lines",
                line={"color": color, "width": 1.5, "dash": "dot"},
                showlegend=False,
                hoverinfo="skip",
                opacity=0.5,
            ))

        # Current dot
        fig.add_trace(go.Scattergl(
            x=[latest["rs_ratio"]],
            y=[latest["rs_momentum"]],
            mode="markers+text",
            marker={"size": 14, "color": color, "line": {"color": "white", "width": 1.5}},
            text=[symbol],
            textposition="top center",
            textfont={"size": 10, "color": "white"},
            name=symbol,
            hovertemplate=(
                f"<b>{symbol}</b><br>"
                "RS-Ratio: %{x:.2f}<br>"
                "RS-Momentum: %{y:.2f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        title={"text": title, "x": 0.5},
        xaxis={"title": "RS-Ratio", "range": axis_range_x, "showgrid": True},
        yaxis={"title": "RS-Momentum", "range": axis_range_y, "showgrid": True},
        height=520,
        showlegend=True,
        legend={"orientation": "h", "y": -0.12},
    )
    _theme.apply_theme(fig)
    return fig
