"""Chart theme constants and Plotly template factory for the Robo-Advisor dashboard."""

import plotly.graph_objects as go
import plotly.io as pio

# ── Color palette ──────────────────────────────────────────────────────────────
BG_PRIMARY = "#0f172a"       # main dark background
BG_SECONDARY = "#1e293b"     # card / panel background
BG_TERTIARY = "#334155"      # borders, dividers

BULLISH = "#10b981"          # green – price up / profit
BEARISH = "#ef4444"          # red   – price down / loss
NEUTRAL = "#94a3b8"          # grey  – flat / label

ACCENT_BLUE = "#3b82f6"
ACCENT_AMBER = "#f59e0b"
ACCENT_PURPLE = "#a855f7"
ACCENT_CYAN = "#06b6d4"

TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"

# Quadrant colors for RRG
QUAD_LEADING = "#10b981"     # top-right
QUAD_WEAKENING = "#f59e0b"   # top-left
QUAD_LAGGING = "#ef4444"     # bottom-left
QUAD_IMPROVING = "#3b82f6"   # bottom-right

CHART_COLORS = [
    ACCENT_BLUE, BULLISH, ACCENT_AMBER, ACCENT_PURPLE,
    ACCENT_CYAN, BEARISH, "#ec4899", "#84cc16",
]


def create_plotly_template() -> go.layout.Template:
    """Return a dark Plotly template matching the dashboard palette."""
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_SECONDARY,
        font={"color": TEXT_PRIMARY, "family": "Inter, sans-serif", "size": 12},
        title={"font": {"color": TEXT_PRIMARY, "size": 14}},
        xaxis=dict(
            gridcolor=BG_TERTIARY,
            zerolinecolor=BG_TERTIARY,
            tickcolor=TEXT_SECONDARY,
            linecolor=BG_TERTIARY,
        ),
        yaxis=dict(
            gridcolor=BG_TERTIARY,
            zerolinecolor=BG_TERTIARY,
            tickcolor=TEXT_SECONDARY,
            linecolor=BG_TERTIARY,
        ),
        legend=dict(
            bgcolor=BG_SECONDARY,
            bordercolor=BG_TERTIARY,
            borderwidth=1,
            font={"color": TEXT_PRIMARY},
        ),
        colorway=CHART_COLORS,
        margin={"l": 50, "r": 20, "t": 40, "b": 40},
        hoverlabel=dict(
            bgcolor=BG_SECONDARY,
            font_color=TEXT_PRIMARY,
            bordercolor=BG_TERTIARY,
        ),
    )
    return template


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply the robo-advisor dark theme to an existing Plotly figure."""
    fig.update_layout(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_SECONDARY,
        font={"color": TEXT_PRIMARY, "family": "Inter, sans-serif"},
        xaxis=dict(gridcolor=BG_TERTIARY, zerolinecolor=BG_TERTIARY),
        yaxis=dict(gridcolor=BG_TERTIARY, zerolinecolor=BG_TERTIARY),
        legend=dict(bgcolor=BG_SECONDARY, bordercolor=BG_TERTIARY, borderwidth=1),
        hoverlabel=dict(bgcolor=BG_SECONDARY, font_color=TEXT_PRIMARY),
        margin={"l": 50, "r": 20, "t": 40, "b": 40},
    )
    return fig


# Register template globally so all charts can reference it by name
_template = create_plotly_template()
pio.templates["robo_dark"] = _template
pio.templates.default = "robo_dark"
