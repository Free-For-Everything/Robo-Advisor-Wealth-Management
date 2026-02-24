"""Page 3 — Risk Metrics: VaR gauge, margin monitor, efficient frontier, Kelly table."""

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


# ── Demo data builders ─────────────────────────────────────────────────────────

def _build_equity_series(n: int = 252) -> pd.Series:
    rng = np.random.default_rng(7)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="B")
    rets = rng.normal(0.0005, 0.012, n)
    return pd.Series(10_000_000 * np.cumprod(1 + rets), index=dates)


def _build_efficient_frontier(n_portfolios: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(13)
    vol = rng.uniform(5, 30, n_portfolios)
    returns = -0.3 * (vol - 12) ** 2 / 20 + 18 + rng.normal(0, 1.5, n_portfolios)
    sharpe = returns / vol
    return pd.DataFrame({"volatility": vol, "returns": returns, "sharpe": sharpe})


def _build_kelly_table() -> pd.DataFrame:
    rng = np.random.default_rng(55)
    symbols = ["VNM", "HPG", "TCB", "FPT", "VIC", "MSN"]
    win_rate = rng.uniform(0.45, 0.70, len(symbols))
    avg_win  = rng.uniform(1.5, 4.0,  len(symbols))
    avg_loss = rng.uniform(0.8, 1.5,  len(symbols))
    kelly_f  = win_rate - (1 - win_rate) / (avg_win / avg_loss)
    half_k   = kelly_f * 0.5
    return pd.DataFrame({
        "Symbol":    symbols,
        "Win Rate":  (win_rate * 100).round(1),
        "Avg Win %": avg_win.round(2),
        "Avg Loss %": avg_loss.round(2),
        "Kelly f":   kelly_f.round(4),
        "Half-Kelly": half_k.round(4),
        "Rec. Size %": (np.clip(half_k, 0, 0.25) * 100).round(1),
    })


# ── Load modules ───────────────────────────────────────────────────────────────
risk_charts  = _load("charts/risk-charts.py",      "risk_charts")
risk_md      = _load("charts/risk-charts-margin-drawdown.py", "risk_charts_md")
port_charts  = _load("charts/portfolio-charts.py", "portfolio_charts")

# ── Page ───────────────────────────────────────────────────────────────────────
st.title("Risk Metrics")
st.caption("VaR · Margin Monitor · Efficient Frontier · Drawdown · Kelly Sizing")
st.markdown("---")

equity = _build_equity_series()

# ── Row 1: VaR gauge + Margin monitor ─────────────────────────────────────────
col_var, col_margin = st.columns(2)

with col_var:
    st.subheader("Value at Risk (95%)")
    # Compute 1-day historical VaR from equity curve
    daily_rets = equity.pct_change().dropna()
    var_95 = float(-np.percentile(daily_rets, 5) * 100)  # positive pct
    fig_var = risk_charts.create_var_gauge(var_pct=var_95, limit_pct=5.0, confidence=0.95)
    st.plotly_chart(fig_var, use_container_width=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        var_99 = float(-np.percentile(daily_rets, 1) * 100)
        st.metric("VaR 99%", f"{var_99:.2f}%")
    with col_b:
        cvar = float(-daily_rets[daily_rets <= np.percentile(daily_rets, 5)].mean() * 100)
        st.metric("CVaR 95%", f"{cvar:.2f}%")
    with col_c:
        vol_ann = float(daily_rets.std() * np.sqrt(252) * 100)
        st.metric("Ann. Vol", f"{vol_ann:.1f}%")

with col_margin:
    st.subheader("Margin Monitor")
    fig_margin = risk_md.create_margin_monitor(
        used_margin=3_200_000,
        total_margin=10_000_000,
        maintenance_margin=5_000_000,
    )
    st.plotly_chart(fig_margin, use_container_width=True)

    col_d, col_e, col_f = st.columns(3)
    with col_d:
        st.metric("Used Margin", "3,200,000 ₫")
    with col_e:
        st.metric("Free Margin", "6,800,000 ₫")
    with col_f:
        st.metric("Margin Level", "312.5%")

st.markdown("---")

# ── Row 2: Efficient frontier + Drawdown ──────────────────────────────────────
col_ef, col_dd = st.columns(2)

with col_ef:
    st.subheader("Efficient Frontier")
    ef_df = _build_efficient_frontier()
    current_vol  = float(daily_rets.std() * np.sqrt(252) * 100)
    current_ret  = float(daily_rets.mean() * 252 * 100)
    fig_ef = risk_charts.create_efficient_frontier(
        ef_df,
        current_point=(current_vol, current_ret),
    )
    st.plotly_chart(fig_ef, use_container_width=True)

with col_dd:
    st.subheader("Drawdown Chart")
    fig_dd = risk_md.create_drawdown_chart(equity)
    st.plotly_chart(fig_dd, use_container_width=True)

st.markdown("---")

# ── Kelly sizing table ─────────────────────────────────────────────────────────
st.subheader("Kelly Position Sizing")
kelly_df = _build_kelly_table()
st.dataframe(
    kelly_df.style
    .format({
        "Win Rate": "{:.1f}%",
        "Avg Win %": "{:.2f}",
        "Avg Loss %": "{:.2f}",
        "Kelly f": "{:.4f}",
        "Half-Kelly": "{:.4f}",
        "Rec. Size %": "{:.1f}%",
    })
    .map(
        lambda v: "color: #10b981" if isinstance(v, float) and v > 0
        else "color: #ef4444" if isinstance(v, float) and v <= 0
        else "",
        subset=["Kelly f", "Half-Kelly"],
    ),
    use_container_width=True,
    height=260,
)
st.caption("Half-Kelly sizing is recommended over full Kelly to reduce variance.")
