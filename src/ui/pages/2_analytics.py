"""Page 2 — Analytics: Candlestick + MACD, RRG, VSA signals."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

_UI = Path(__file__).parent.parent  # src/ui/


def _load(rel_path: str, alias: str):
    if alias in sys.modules:
        return sys.modules[alias]
    import importlib.util
    p = _UI / rel_path
    spec = importlib.util.spec_from_file_location(alias, p)
    mod = importlib.util.module_from_spec(spec)   # type: ignore[arg-type]
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)                  # type: ignore[union-attr]
    return mod


# ── Demo data ──────────────────────────────────────────────────────────────────
def _build_ohlcv(symbol: str, n: int = 180) -> pd.DataFrame:
    """Generate synthetic OHLCV data for a symbol."""
    rng = np.random.default_rng(hash(symbol) % (2**31))
    dates = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="B")
    close = 50_000 * np.cumprod(1 + rng.normal(0.0004, 0.015, n))
    high  = close * (1 + rng.uniform(0.002, 0.02, n))
    low   = close * (1 - rng.uniform(0.002, 0.02, n))
    open_ = low + rng.uniform(0, 1, n) * (high - low)
    vol   = rng.integers(500_000, 5_000_000, n).astype(float)
    return pd.DataFrame({"open": open_, "high": high, "low": low,
                         "close": close, "volume": vol}, index=dates)


def _build_rrg_data() -> pd.DataFrame:
    """Generate synthetic RRG data for a basket of VN30 symbols."""
    rng = np.random.default_rng(99)
    symbols = ["VNM", "VIC", "VHM", "HPG", "MSN", "TCB", "BID", "VCB", "FPT", "MWG"]
    n_periods = 8
    rows = []
    for sym in symbols:
        rs_r = 96 + rng.uniform(0, 10)
        rs_m = 96 + rng.uniform(0, 10)
        for p in range(n_periods):
            rows.append({
                "symbol": sym,
                "period": p,
                "rs_ratio": rs_r + rng.normal(0, 0.4) * p,
                "rs_momentum": rs_m + rng.normal(0, 0.4) * p,
            })
    return pd.DataFrame(rows)


def _build_vsa_signals() -> pd.DataFrame:
    """Generate synthetic VSA signal table."""
    rng = np.random.default_rng(77)
    symbols = ["VNM", "HPG", "VIC", "TCB", "FPT"]
    signal_types = ["Stopping Volume", "No Supply", "Absorption", "Climax Buy", "Climax Sell"]
    dates = pd.date_range(end=pd.Timestamp.today(), periods=len(symbols), freq="B")
    return pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"),
        "Symbol": symbols,
        "Signal": rng.choice(signal_types, len(symbols)),
        "Close": rng.uniform(20_000, 80_000, len(symbols)).round(0),
        "Volume Ratio": rng.uniform(1.2, 3.5, len(symbols)).round(2),
        "Spread": rng.choice(["Wide", "Narrow", "Average"], len(symbols)),
        "Strength": rng.choice(["Strong", "Weak", "Neutral"], len(symbols)),
    })


# ── Sidebar controls ───────────────────────────────────────────────────────────
sidebar_filters = _load("components/sidebar-filters.py", "sidebar_filters")

with st.sidebar:
    st.markdown("### Analytics Controls")
    symbol = sidebar_filters.render_symbol_selector(key="analytics_symbol")
    timeframe = sidebar_filters.render_timeframe_selector(key="analytics_tf")
    start_date, end_date = sidebar_filters.render_date_range(key_prefix="analytics")

# ── Page content ───────────────────────────────────────────────────────────────
st.title("Analytics")
st.caption("Candlestick + MACD — RRG — VSA Signals")
st.markdown("---")

candle_chart = _load("charts/candlestick-chart.py", "candlestick_chart")
rrg_chart    = _load("charts/rrg-chart.py",         "rrg_chart")

tab_candle, tab_rrg, tab_vsa = st.tabs(["Candlestick / MACD", "RRG", "VSA Signals"])

# ── Tab 1: Candlestick ─────────────────────────────────────────────────────────
with tab_candle:
    ohlcv = _build_ohlcv(symbol)
    # Apply date filter
    ohlcv = ohlcv[
        (ohlcv.index.date >= start_date) &   # type: ignore[operator]
        (ohlcv.index.date <= end_date)        # type: ignore[operator]
    ]
    if ohlcv.empty:
        st.warning("No data in selected date range.")
    else:
        fig = candle_chart.create_candlestick(ohlcv, symbol=symbol, show_macd=True)
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: RRG ─────────────────────────────────────────────────────────────────
with tab_rrg:
    rrg_df = _build_rrg_data()
    fig_rrg = rrg_chart.create_rrg_chart(rrg_df, tail_length=6,
                                          title="VN30 Relative Rotation Graph")
    st.plotly_chart(fig_rrg, use_container_width=True)
    st.caption(
        "RRG quadrants: **Leading** (top-right) → **Weakening** (top-left) → "
        "**Lagging** (bottom-left) → **Improving** (bottom-right)"
    )

# ── Tab 3: VSA Signals ─────────────────────────────────────────────────────────
with tab_vsa:
    vsa_df = _build_vsa_signals()
    st.subheader("Volume Spread Analysis Signals")
    st.markdown("Detected patterns based on price spread, volume, and close position.")
    st.dataframe(
        vsa_df.style.map(
            lambda v: "color: #10b981" if v in ("Strong", "No Supply", "Stopping Volume")
            else "color: #ef4444" if v in ("Weak", "Climax Sell")
            else "color: #94a3b8",
            subset=["Signal", "Strength"],
        ),
        use_container_width=True,
        height=300,
    )
