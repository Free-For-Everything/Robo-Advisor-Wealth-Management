"""Sidebar filter widgets for the Robo-Advisor dashboard."""

from datetime import date, timedelta

import streamlit as st

# ── Default option sets ────────────────────────────────────────────────────────
_VN_SYMBOLS = [
    "VNM", "VIC", "VHM", "HPG", "MSN", "TCB", "BID", "VCB",
    "FPT", "MWG", "GAS", "SAB", "CTG", "ACB", "SSI",
]
_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W"]
_ASSET_CLASSES = ["Stock", "ETF", "Bond", "Crypto", "Forex", "Commodity"]


def render_symbol_selector(
    symbols: list[str] | None = None,
    default: str = "VNM",
    key: str = "symbol_selector",
) -> str:
    """Render a selectbox for choosing a trading symbol.

    Returns the selected symbol string.
    """
    opts = symbols or _VN_SYMBOLS
    idx = opts.index(default) if default in opts else 0
    return st.sidebar.selectbox("Symbol", opts, index=idx, key=key)


def render_date_range(
    default_days: int = 90,
    key_prefix: str = "date",
) -> tuple[date, date]:
    """Render start/end date pickers in the sidebar.

    Returns (start_date, end_date).
    """
    end_default = date.today()
    start_default = end_default - timedelta(days=default_days)

    st.sidebar.markdown("**Date Range**")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start = st.date_input("From", value=start_default, key=f"{key_prefix}_start")
    with col2:
        end = st.date_input("To", value=end_default, key=f"{key_prefix}_end")

    if start > end:
        st.sidebar.warning("Start date must be before end date.")
        start = end - timedelta(days=1)

    return start, end  # type: ignore[return-value]


def render_timeframe_selector(
    timeframes: list[str] | None = None,
    default: str = "1D",
    key: str = "timeframe_selector",
) -> str:
    """Render a radio group for OHLCV timeframe selection.

    Returns the selected timeframe string.
    """
    opts = timeframes or _TIMEFRAMES
    idx = opts.index(default) if default in opts else 6
    return st.sidebar.radio("Timeframe", opts, index=idx, key=key, horizontal=True)


def render_asset_class_filter(
    classes: list[str] | None = None,
    key: str = "asset_class_filter",
) -> list[str]:
    """Render a multiselect for asset class filtering.

    Returns list of selected asset class strings.
    """
    opts = classes or _ASSET_CLASSES
    return st.sidebar.multiselect(
        "Asset Classes",
        opts,
        default=["Stock", "ETF"],
        key=key,
    )
