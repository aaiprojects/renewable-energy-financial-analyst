# pages/1_📈_Executive_Summary_Pro+.py
import streamlit as st
import pandas as pd
import glob
import os
import altair as alt
from src.dashboard.generate_dashboard import load_current_and_previous_runs, compute_confidence_deltas
from src.components.navigation import render_navigation_bar
from src.components.hide_sidebar import hide_sidebar_completely

st.set_page_config(page_title="Executive Summary Pro+", layout="wide")

# Hide sidebar completely - MUST be first thing after page config
hide_sidebar_completely()

# Navigation Bar
render_navigation_bar(current_page="Executive Summary")

# ---- Global styling & animation ----
st.markdown("""
<style>
.card {
  padding: 18px;
  border-radius: 14px;
  margin-bottom: 12px;
  transition: all 0.25s ease-in-out;
  animation: fadeInUp 0.4s ease both;
  box-shadow: 0 0 0 rgba(0,0,0,0);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(255,255,255,0.08);
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Table row hover */
.dataframe tbody tr {
  animation: fadeInUp 0.4s ease both;
  transition: background-color 0.2s ease;
}
.dataframe tbody tr:hover {
  background-color: rgba(255,255,255,0.05);
}

/* Glow hover for charts */
.stAltairChart {
  transition: all 0.6s ease-in-out;
}
.stAltairChart:hover {
  transform: scale(1.01);
  box-shadow: 0 0 25px rgba(0, 255, 200, 0.2);
}
</style>
""", unsafe_allow_html=True)

st.title("💼 Executive Summary Dashboard — Pro+ Edition")
st.caption("Compare AI research runs, interpret deltas, and export insights with dynamic visuals.")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    ticker_search = st.text_input("🔍 Search Ticker")
    outlook_filter = st.selectbox("📈 Market Outlook", ["All", "Positive", "Negative", "Neutral"])
    view_mode = st.radio("🪟 View Mode", ["Cards", "Table"])
    st.markdown("---")
    st.caption("💡 Tip: Use multi-word search (e.g., ENPH SEDG) to view multiple tickers.")

# Load run summaries
try:
    current, previous, _ = load_current_and_previous_runs()
    
    # Check if no current analysis data exists - trigger auto-analysis
    if not current:
        with st.spinner("� Generating comprehensive analysis for all watchlist stocks..."):
            # Import required components
            from src.config.watchlist import WATCHLIST
            from src.config.settings import Settings
            from src.agent.orchestrator_lg import LGOrchestrator
            
            # Initialize orchestrator
            cfg = Settings()
            orch = LGOrchestrator(cfg)
            
            # Run analysis for each watchlist stock
            for w in WATCHLIST:
                try:
                    result = orch.run(ticker=w.ticker, days=30, refresh=True)
                except Exception as e:
                    # Silently continue on errors to avoid disrupting the flow
                    continue
        
        # Reload data after analysis
        current, previous, _ = load_current_and_previous_runs()
    
    df = compute_confidence_deltas(current, previous)
    st.write("✅ Data preview:", df.head())
    st.write("Row count:", len(df))

except Exception as e:
    st.error(f"Error loading summaries: {e}")
    st.stop()

# ==============================================================
# 🧮 Run Health Summary
# ==============================================================
try:
    num_up = sum(df["Delta"] > 0)
    num_down = sum(df["Delta"] < 0)
    num_flat = sum(df["Delta"] == 0)
    avg_delta = df["Delta"].mean()

    st.markdown("### 🧠 Run Health Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("↑ Improved", int(num_up))
    c2.metric("↓ Declined", int(num_down))
    c3.metric("→ No Change", int(num_flat))
    c4.metric("Avg Δ Confidence", f"{avg_delta:.2f}%")
    st.divider()
except Exception as e:
    st.warning(f"⚠️ Unable to compute run health summary: {e}")

# Apply filters
if ticker_search:
    tickers = [t.strip().upper() for t in ticker_search.split()]
    df = df[df["Ticker"].str.upper().isin(tickers)]
if outlook_filter != "All":
    df = df[df["Outlook"] == outlook_filter]

# ==============================================================
# 📈 Confidence Trend Visualization
# ==============================================================
st.markdown("### 📈 Confidence Trend Over Time")

try:
    trend_chart = (
        alt.Chart(df)
        .mark_line(interpolate="monotone", point=alt.OverlayMarkDef(filled=True, size=80), strokeWidth=3)
        .encode(
            x=alt.X("Run Timestamp:T", title="Run Timestamp"),
            y=alt.Y("Confidence:Q", title="Confidence (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Ticker:N", legend=alt.Legend(title="Ticker")),
            tooltip=[
                alt.Tooltip("Ticker:N"),
                alt.Tooltip("Run Timestamp:T"),
                alt.Tooltip("Confidence:Q", format=".2f"),
                alt.Tooltip("Delta:Q", title="Δ Confidence", format="+.2f"),
            ],
        )
        .interactive()
        .properties(height=350)
    )

    gradient = (
        alt.Chart(df)
        .mark_area(interpolate="monotone", opacity=0.15, line={'color': 'transparent'})
        .encode(x="Run Timestamp:T", y="Confidence:Q", color="Ticker:N")
    )

    st.altair_chart((gradient + trend_chart).configure_view(strokeWidth=0), use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ Could not render trend chart: {e}")

# ==============================================================
# 📉 Confidence Δ Visualization
# ==============================================================
st.markdown("### 📉 Confidence Δ Across Runs")

try:
    delta_chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, opacity=0.9)
        .encode(
            x=alt.X("Run Timestamp:T", title="Run Timestamp"),
            y=alt.Y("Delta:Q", title="Δ Confidence (%)"),
            color=alt.condition(
                alt.datum.Delta > 0,
                alt.value("#00E676"),  # green for up
                alt.value("#FF5252")   # red for down
            ),
            tooltip=[
                alt.Tooltip("Ticker:N"),
                alt.Tooltip("Run Timestamp:T"),
                alt.Tooltip("Delta:Q", title="Δ Confidence (%)", format="+.2f"),
            ],
        )
        .properties(height=300)
    )

    bg = alt.Chart(df).mark_rect(opacity=0.05, color="#999").encode(x="Run Timestamp:T")
    st.altair_chart((bg + delta_chart).configure_view(strokeWidth=0), use_container_width=True)
    st.divider()
except Exception as e:
    st.warning(f"⚠️ Could not render Δ chart: {e}")

# ==============================================================
# 🧾 Current Summaries
# ==============================================================
st.markdown("### 📊 Current Executive Summaries")

if view_mode == "Cards":
    for _, row in df.iterrows():
        # Gradient background based on trend
        if row["Delta"] > 0:
            bg = "linear-gradient(90deg, rgba(34,197,94,0.2), rgba(34,197,94,0.05))"
        elif row["Delta"] < 0:
            bg = "linear-gradient(90deg, rgba(239,68,68,0.2), rgba(239,68,68,0.05))"
        else:
            bg = "linear-gradient(90deg, rgba(156,163,175,0.2), rgba(156,163,175,0.05))"

        st.markdown(f"""
        <div class='card' style='background:{bg};'>
            <h4>{row['Ticker']}</h4>
            <p><b>Outlook:</b> {row['Outlook']} &nbsp; | &nbsp;
               <b>Confidence:</b> {row['Confidence']}%</p>
            <p><b>Change:</b> {row['Delta']}% &nbsp; {row['Direction']}</p>
            <details><summary><b>Interpretation</b></summary>
            <p>{row['Interpretation']}</p></details>
        </div>
        """, unsafe_allow_html=True)
