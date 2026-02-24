"""Main entry point for the Robo-Advisor Streamlit dashboard.

Run with:
    uv run streamlit run src/ui/app.py
"""

import streamlit as st

# ── Page config must be the FIRST streamlit call ──────────────────────────────
st.set_page_config(
    page_title="Robo-Advisor | Wealth Management",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "100% local Robo-Advisor for Vietnam market — built with Streamlit + Plotly",
    },
)

# ── Global CSS overrides ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide default Streamlit header/footer */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Custom scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1e293b; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }

/* Card-style metric boxes */
[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px 16px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

# ── Landing page ───────────────────────────────────────────────────────────────
st.title("Robo-Advisor — Wealth Management")
st.caption("100% local AI-driven trading platform for Vietnam market")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info("**Portfolio Overview**\n\nNAV, P&L, allocation breakdown and open positions.")
with col2:
    st.info("**Analytics**\n\nCandlestick charts, MACD, RRG rotation and VSA signals.")
with col3:
    st.info("**Risk Metrics**\n\nVaR gauge, efficient frontier, margin monitor, drawdown.")
with col4:
    st.info("**AI Alerts**\n\nAgent signals, sentiment scores and notification history.")

st.markdown("---")
st.markdown(
    "Navigate using the **sidebar** on the left. "
    "Each page loads demo data by default — connect live data sources via the config panel."
)

# ── Sidebar branding ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Robo-Advisor")
    st.markdown("*Vietnam Market Edition*")
    st.markdown("---")
    st.markdown("**Navigate to:**")
    st.markdown("- Portfolio Overview")
    st.markdown("- Analytics")
    st.markdown("- Risk Metrics")
    st.markdown("- AI Alerts")
    st.markdown("---")
    st.caption("v0.1.0 — demo mode")
