"""Styled data table components for positions and trade history."""

from __future__ import annotations

import pandas as pd
import streamlit as st

# ── Colour helpers ─────────────────────────────────────────────────────────────
_GREEN = "color: #10b981"
_RED = "color: #ef4444"
_NEUTRAL = "color: #94a3b8"


def _color_pnl(val: float) -> str:
    if val > 0:
        return _GREEN
    if val < 0:
        return _RED
    return _NEUTRAL


def _color_side(val: str) -> str:
    return _GREEN if str(val).upper() == "BUY" else _RED


def _style_positions(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Apply conditional formatting to the positions DataFrame."""
    return (
        df.style
        .map(_color_pnl, subset=["Unrealised P&L", "P&L %"])
        .format({
            "Avg Cost": "{:,.0f}",
            "Last Price": "{:,.0f}",
            "Unrealised P&L": "{:+,.0f}",
            "P&L %": "{:+.2f}%",
            "Market Value": "{:,.0f}",
            "Weight %": "{:.1f}%",
        })
    )


def _style_trades(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Apply conditional formatting to the trades DataFrame."""
    return (
        df.style
        .map(_color_side, subset=["Side"])
        .map(_color_pnl, subset=["Realised P&L"])
        .format({
            "Price": "{:,.0f}",
            "Qty": "{:,}",
            "Value": "{:,.0f}",
            "Realised P&L": "{:+,.0f}",
            "Commission": "{:,.0f}",
        })
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def render_positions_table(positions_df: pd.DataFrame) -> None:
    """Render open positions table with P&L conditional colouring.

    Expected columns: Symbol, Qty, Avg Cost, Last Price, Market Value,
                      Unrealised P&L, P&L %, Weight %
    """
    if positions_df.empty:
        st.info("No open positions.")
        return

    required = {"Symbol", "Qty", "Avg Cost", "Last Price",
                "Market Value", "Unrealised P&L", "P&L %", "Weight %"}
    missing = required - set(positions_df.columns)
    if missing:
        st.warning(f"Positions table missing columns: {missing}")
        st.dataframe(positions_df, use_container_width=True)
        return

    styled = _style_positions(positions_df)
    st.dataframe(styled, use_container_width=True, height=300)


def render_trades_table(trades_df: pd.DataFrame, max_rows: int = 50) -> None:
    """Render trade history table with side and P&L colouring.

    Expected columns: DateTime, Symbol, Side, Price, Qty, Value,
                      Realised P&L, Commission
    """
    if trades_df.empty:
        st.info("No trade history.")
        return

    display_df = trades_df.head(max_rows).copy()

    required = {"DateTime", "Symbol", "Side", "Price", "Qty",
                "Value", "Realised P&L", "Commission"}
    missing = required - set(display_df.columns)
    if missing:
        st.warning(f"Trades table missing columns: {missing}")
        st.dataframe(display_df, use_container_width=True)
        return

    styled = _style_trades(display_df)
    st.dataframe(styled, use_container_width=True, height=350)
