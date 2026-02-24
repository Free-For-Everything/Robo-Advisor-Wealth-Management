"""Page 1 — Portfolio Overview: KPI cards, allocation pie, equity curve, positions table."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

_SRC = Path(__file__).parent.parent.parent  # src/
_UI = Path(__file__).parent.parent           # src/ui/

# ── Module loader helper ───────────────────────────────────────────────────────
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


# ── Demo data (session_state cache) ───────────────────────────────────────────
def _build_demo_data() -> None:
    if "portfolio_demo" in st.session_state:
        return

    rng = np.random.default_rng(42)
    n = 252
    dates = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="B")

    # Equity curve
    returns = rng.normal(0.0005, 0.012, n)
    equity = pd.Series(10_000_000 * np.cumprod(1 + returns), index=dates, name="NAV")

    # Benchmark (VN-Index proxy)
    bench_ret = rng.normal(0.0003, 0.011, n)
    benchmark = pd.Series(10_000_000 * np.cumprod(1 + bench_ret), index=dates, name="VN-Index")

    # Daily P&L
    daily_pnl = equity.diff().fillna(0)

    # Open positions
    symbols = ["VNM", "VIC", "HPG", "TCB", "FPT", "MSN", "BID"]
    qty = rng.integers(100, 2000, len(symbols)) * 100
    avg_cost = rng.uniform(20_000, 80_000, len(symbols))
    last_price = avg_cost * rng.uniform(0.88, 1.18, len(symbols))
    mkt_value = qty * last_price
    unreal_pnl = (last_price - avg_cost) * qty
    pnl_pct = (last_price / avg_cost - 1) * 100
    total_mv = mkt_value.sum()

    positions = pd.DataFrame({
        "Symbol": symbols,
        "Qty": qty,
        "Avg Cost": avg_cost,
        "Last Price": last_price,
        "Market Value": mkt_value,
        "Unrealised P&L": unreal_pnl,
        "P&L %": pnl_pct,
        "Weight %": mkt_value / total_mv * 100,
    })

    # Allocation
    sectors = ["Banking", "Real Estate", "Consumer", "Technology", "Energy", "Industry"]
    sector_weights = rng.dirichlet(np.ones(len(sectors))) * 100

    st.session_state["portfolio_demo"] = {
        "equity": equity,
        "benchmark": benchmark,
        "daily_pnl": daily_pnl,
        "positions": positions,
        "allocation_labels": sectors,
        "allocation_values": sector_weights.tolist(),
        "total_value": float(equity.iloc[-1]),
        "daily_pnl_val": float(daily_pnl.iloc[-1]),
        "daily_pnl_pct": float(returns[-1] * 100),
        "total_return_pct": float((equity.iloc[-1] / equity.iloc[0] - 1) * 100),
        "sharpe": float(returns.mean() / returns.std() * np.sqrt(252)),
        "max_dd_pct": float(((equity / equity.cummax()) - 1).min() * 100),
    }


# ── Render ─────────────────────────────────────────────────────────────────────
_build_demo_data()
d = st.session_state["portfolio_demo"]

metric_cards = _load("components/metric-cards.py", "metric_cards")
data_tables  = _load("components/data-tables.py",  "data_tables")
port_charts  = _load("charts/portfolio-charts.py", "portfolio_charts")

st.title("Portfolio Overview")
st.caption("Demo data — connect live data sources to display real positions.")
st.markdown("---")

# ── KPI row ────────────────────────────────────────────────────────────────────
metric_cards.render_portfolio_summary(
    total_value=d["total_value"],
    daily_pnl=d["daily_pnl_val"],
    daily_pnl_pct=d["daily_pnl_pct"],
    total_return_pct=d["total_return_pct"],
    sharpe=d["sharpe"],
    max_drawdown_pct=d["max_dd_pct"],
)

st.markdown("---")

# ── Charts row ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Sector Allocation")
    pie = port_charts.create_allocation_pie(
        d["allocation_labels"], d["allocation_values"]
    )
    st.plotly_chart(pie, use_container_width=True)

with col_right:
    st.subheader("Equity Curve")
    eq_fig = port_charts.create_equity_curve(
        equity_series=d["equity"],
        benchmark_series=d["benchmark"],
    )
    st.plotly_chart(eq_fig, use_container_width=True)

st.markdown("---")

# ── Positions table ────────────────────────────────────────────────────────────
st.subheader("Open Positions")
data_tables.render_positions_table(d["positions"])
