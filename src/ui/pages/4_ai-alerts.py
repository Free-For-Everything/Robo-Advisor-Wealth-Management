"""Page 4 — AI Alerts: agent signals, sentiment scores, notification history."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
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

def _build_agent_signals() -> pd.DataFrame:
    rng = np.random.default_rng(21)
    symbols   = ["VNM", "HPG", "TCB", "FPT", "VIC", "MSN", "BID", "SSI"]
    agents    = ["RL Agent", "Mean-Reversion", "Momentum", "RRG Signal", "VSA Agent"]
    actions   = ["BUY", "SELL", "HOLD"]
    now       = datetime.now()
    rows = []
    for i, sym in enumerate(symbols):
        rows.append({
            "Time":       (now - timedelta(minutes=rng.integers(1, 120))).strftime("%H:%M"),
            "Symbol":     sym,
            "Agent":      rng.choice(agents),
            "Action":     rng.choice(actions, p=[0.4, 0.3, 0.3]),
            "Confidence": round(float(rng.uniform(0.55, 0.98)), 2),
            "Price":      round(float(rng.uniform(20_000, 80_000)), 0),
            "Target":     round(float(rng.uniform(22_000, 88_000)), 0),
            "Stop":       round(float(rng.uniform(18_000, 72_000)), 0),
        })
    return pd.DataFrame(rows)


def _build_sentiment_scores() -> pd.DataFrame:
    rng = np.random.default_rng(33)
    symbols = ["VNM", "HPG", "TCB", "FPT", "VIC", "MSN", "BID", "VCB", "SSI", "MWG"]
    scores  = rng.uniform(-1, 1, len(symbols))
    sources = rng.integers(10, 80, len(symbols))
    return pd.DataFrame({
        "Symbol":      symbols,
        "Sentiment":   scores.round(3),
        "Sources":     sources,
        "Trending":    rng.choice(["Up", "Down", "Flat"], len(symbols)),
        "Last Update": [f"{rng.integers(1,59)}m ago" for _ in symbols],
    })


def _build_notification_history() -> pd.DataFrame:
    rng = np.random.default_rng(44)
    now  = datetime.now()
    types = ["Signal", "Risk Alert", "News", "System", "Order Fill"]
    msgs  = [
        "BUY signal for VNM (RL Agent, conf=0.87)",
        "VaR limit 80% utilised — review positions",
        "Q4 earnings beat: FPT +12% guidance raise",
        "Data pipeline reconnected — ClickHouse OK",
        "Order #1042 filled: HPG 500 @ 28,400",
        "SELL signal for TCB (Mean-Reversion, conf=0.72)",
        "Margin level approaching maintenance threshold",
        "Sentiment spike detected: BID (score=+0.82)",
        "New RSI divergence: VIC daily chart",
        "Kafka consumer lag > 1000 — check broker",
    ]
    rows = []
    for i in range(10):
        rows.append({
            "Time":    (now - timedelta(minutes=rng.integers(1, 480))).strftime("%Y-%m-%d %H:%M"),
            "Type":    rng.choice(types),
            "Message": msgs[i],
            "Channel": rng.choice(["Telegram", "Dashboard", "Email"]),
            "Status":  rng.choice(["Sent", "Sent", "Sent", "Failed"], p=[0.8, 0.07, 0.07, 0.06]),
        })
    return pd.DataFrame(rows).sort_values("Time", ascending=False)


def _build_sentiment_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of sentiment scores per symbol."""
    _theme_path = _UI / "theme" / "chart-theme.py"
    if "chart_theme" not in sys.modules:
        import importlib.util
        spec = importlib.util.spec_from_file_location("chart_theme", _theme_path)
        mod  = importlib.util.module_from_spec(spec)   # type: ignore[arg-type]
        sys.modules["chart_theme"] = mod
        spec.loader.exec_module(mod)                   # type: ignore[union-attr]
    t = sys.modules["chart_theme"]

    colors = [t.BULLISH if v >= 0 else t.BEARISH for v in df["Sentiment"]]
    fig = go.Figure(go.Bar(
        x=df["Sentiment"], y=df["Symbol"],
        orientation="h",
        marker_color=colors,
        text=df["Sentiment"].round(2),
        textposition="outside",
        hovertemplate="%{y}: %{x:.3f}<extra></extra>",
    ))
    fig.add_vline(x=0, line={"color": t.BG_TERTIARY, "width": 1})
    fig.update_layout(
        title={"text": "NLP Sentiment Scores", "x": 0.5},
        xaxis={"range": [-1.2, 1.2], "title": "Score"},
        height=380,
        showlegend=False,
        margin={"l": 80, "r": 60, "t": 50, "b": 40},
    )
    t.apply_theme(fig)
    return fig


# ── Page layout ────────────────────────────────────────────────────────────────
st.title("AI Alerts & Signals")
st.caption("Live agent outputs, NLP sentiment, and notification log — demo data shown.")
st.markdown("---")

# ── Row 1: Agent signals + Sentiment bar ──────────────────────────────────────
col_sig, col_sent = st.columns([3, 2])

with col_sig:
    st.subheader("Agent Signals")
    signals_df = _build_agent_signals()

    def _color_action(val: str) -> str:
        return (
            "color: #10b981; font-weight:bold" if val == "BUY"
            else "color: #ef4444; font-weight:bold" if val == "SELL"
            else "color: #94a3b8"
        )

    st.dataframe(
        signals_df.style
        .map(_color_action, subset=["Action"])
        .format({"Confidence": "{:.0%}", "Price": "{:,.0f}", "Target": "{:,.0f}", "Stop": "{:,.0f}"}),
        use_container_width=True,
        height=320,
    )

with col_sent:
    sent_df = _build_sentiment_scores()
    fig_sent = _build_sentiment_bar(sent_df)
    st.plotly_chart(fig_sent, use_container_width=True)

st.markdown("---")

# ── Row 2: Sentiment table + Notification history ─────────────────────────────
col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader("Sentiment Detail")
    st.dataframe(
        sent_df.style
        .map(
            lambda v: "color: #10b981" if isinstance(v, float) and v > 0.2
            else "color: #ef4444" if isinstance(v, float) and v < -0.2
            else "color: #94a3b8",
            subset=["Sentiment"],
        )
        .format({"Sentiment": "{:+.3f}"}),
        use_container_width=True,
        height=300,
    )

with col_t2:
    st.subheader("Notification History")
    notif_df = _build_notification_history()

    def _color_status(val: str) -> str:
        return "color: #10b981" if val == "Sent" else "color: #ef4444"

    def _color_type(val: str) -> str:
        return "color: #ef4444; font-weight:bold" if val == "Risk Alert" else ""

    st.dataframe(
        notif_df.style
        .map(_color_status, subset=["Status"])
        .map(_color_type,   subset=["Type"]),
        use_container_width=True,
        height=300,
    )
