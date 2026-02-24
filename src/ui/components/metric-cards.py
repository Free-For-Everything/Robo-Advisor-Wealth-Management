"""Metric card components for portfolio KPIs on the Robo-Advisor dashboard."""

import streamlit as st

# ── Internal helpers ───────────────────────────────────────────────────────────

def _delta_color(value: float) -> str:
    """Return 'normal' (green/red auto) for st.metric delta coloring."""
    return "normal"


def _fmt_currency(value: float, currency: str = "VND") -> str:
    if currency == "VND":
        return f"{value:,.0f} ₫"
    return f"{value:,.2f} {currency}"


def _fmt_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


# ── Public API ─────────────────────────────────────────────────────────────────

def render_metric_card(
    label: str,
    value: str,
    delta: str | None = None,
    help_text: str | None = None,
) -> None:
    """Render a single st.metric card.

    Args:
        label: Card title.
        value: Formatted value string.
        delta: Optional delta string (positive = green, negative = red).
        help_text: Optional tooltip text.
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)


def render_portfolio_summary(
    total_value: float,
    daily_pnl: float,
    daily_pnl_pct: float,
    total_return_pct: float,
    sharpe: float,
    max_drawdown_pct: float,
    currency: str = "VND",
) -> None:
    """Render a row of 6 portfolio-level KPI metric cards.

    Args:
        total_value: Current portfolio NAV.
        daily_pnl: Today's P&L in currency units.
        daily_pnl_pct: Today's P&L as percentage.
        total_return_pct: Inception-to-date return %.
        sharpe: Annualised Sharpe ratio.
        max_drawdown_pct: Maximum drawdown % (negative number).
    """
    cols = st.columns(6)

    with cols[0]:
        render_metric_card(
            "Portfolio Value",
            _fmt_currency(total_value, currency),
            help_text="Current mark-to-market NAV",
        )
    with cols[1]:
        render_metric_card(
            "Daily P&L",
            _fmt_currency(daily_pnl, currency),
            delta=_fmt_pct(daily_pnl_pct),
            help_text="Today's unrealised + realised gain/loss",
        )
    with cols[2]:
        render_metric_card(
            "Total Return",
            _fmt_pct(total_return_pct),
            delta=_fmt_pct(total_return_pct),
            help_text="Inception-to-date return",
        )
    with cols[3]:
        render_metric_card(
            "Sharpe Ratio",
            f"{sharpe:.2f}",
            help_text="Annualised Sharpe (risk-free = 4.5%)",
        )
    with cols[4]:
        render_metric_card(
            "Max Drawdown",
            _fmt_pct(max_drawdown_pct),
            delta=_fmt_pct(max_drawdown_pct),
            help_text="Largest peak-to-trough decline",
        )
    with cols[5]:
        win_rate = 58.3  # placeholder until trading module connected
        render_metric_card(
            "Win Rate",
            _fmt_pct(win_rate),
            help_text="% of closed trades that were profitable",
        )


def render_asset_metrics(
    symbol: str,
    last_price: float,
    change_pct: float,
    volume: int,
    market_cap: float | None = None,
    currency: str = "VND",
) -> None:
    """Render a compact row of metrics for a single asset.

    Args:
        symbol: Ticker symbol.
        last_price: Latest trade price.
        change_pct: Day change as percentage.
        volume: Session volume.
        market_cap: Optional market capitalisation.
        currency: Display currency code.
    """
    st.markdown(f"#### {symbol}")
    cols = st.columns(4)

    with cols[0]:
        render_metric_card(
            "Last Price",
            _fmt_currency(last_price, currency),
            delta=_fmt_pct(change_pct),
        )
    with cols[1]:
        render_metric_card("Volume", f"{volume:,}")
    with cols[2]:
        render_metric_card("Day Change", _fmt_pct(change_pct))
    with cols[3]:
        if market_cap is not None:
            billions = market_cap / 1e9
            render_metric_card("Mkt Cap", f"{billions:.1f}B {currency}")
        else:
            render_metric_card("Mkt Cap", "N/A")
