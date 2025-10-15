import streamlit as st
import pandas as pd
from src.dashboard.generate_dashboard import load_current_and_previous_runs, compute_confidence_deltas

# ==============================================================
# 🌟 Page Config
# ==============================================================

st.set_page_config(
    page_title="Analytics Dashboard — Executive Summary Pro+",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================
# 🎯 Header & Navigation
# ==============================================================

st.markdown(
    """
    <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            background: #1e1e1e;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            text-align: center;
            color: #fafafa;
        }
        .metric-title {
            font-size: 1.2em;
            color: #9ca3af;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Executive Summary Analytics")
st.caption("Interactive insights into confidence trends, outlook balance, and run performance.")

st.sidebar.header("🧭 Navigation")
st.sidebar.markdown("[🏠 Executive Summary ProPlus](./1_Executive_Summary_ProPlus)")
st.sidebar.markdown("[📊 Analytics Dashboard](./2_📊_Analytics_Dashboard)")
st.sidebar.markdown("---")

# ==============================================================
# 📂 Load Data
# ==============================================================

try:
    current, previous, _ = load_current_and_previous_runs()
    df = compute_confidence_deltas(current, previous)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if df.empty:
    st.warning("⚠️ No summary data found. Please run agents to generate summaries first.")
    st.stop()

# ==============================================================
# ⚙️ Chart Toggles
# ==============================================================

st.sidebar.subheader("📊 Chart Controls")
show_conf = st.sidebar.checkbox("Show Confidence Chart", True)
show_delta = st.sidebar.checkbox("Show Δ Confidence Chart", True)
show_outlook = st.sidebar.checkbox("Show Outlook Breakdown", True)

# ==============================================================
# 🧮 Top-Level Metrics
# ==============================================================

num_tickers = len(df)
avg_conf = df["Confidence"].mean()
avg_delta = df["Delta"].mean()
num_up = sum(df["Delta"] > 0)
num_down = sum(df["Delta"] < 0)
num_flat = sum(df["Delta"] == 0)

st.markdown("### 🧮 Run Overview")

metric_cols = st.columns(5)
metrics = [
    ("🏢 Companies", num_tickers),
    ("📈 Avg Confidence", f"{avg_conf:.2f}%"),
    ("⚡ Avg Δ Confidence", f"{avg_delta:.2f}%"),
    ("🟢 Improved", int(num_up)),
    ("🔴 Declined", int(num_down)),
]
for col, (label, val) in zip(metric_cols, metrics):
    col.markdown(f"<div class='metric-card'><div class='metric-title'>{label}</div><h2>{val}</h2></div>", unsafe_allow_html=True)

st.divider()

# ==============================================================
# 📊 Charts Section
# ==============================================================

if show_conf:
    st.markdown("### 📈 Confidence Distribution")
    st.bar_chart(df.set_index("Ticker")["Confidence"])

if show_delta:
    st.markdown("### 📉 Confidence Δ (Change from Previous Run)")
    st.bar_chart(df.set_index("Ticker")["Delta"])

if show_outlook:
    st.markdown("### 🧠 Outlook Breakdown")

    outlook_counts = df["Outlook"].value_counts()
    outlook_data = pd.DataFrame({
        "Outlook": outlook_counts.index,
        "Count": outlook_counts.values
    })
    st.dataframe(outlook_data, hide_index=True, use_container_width=True)

    try:
        import altair as alt
        chart = (
            alt.Chart(outlook_data)
            .mark_arc(innerRadius=60)
            .encode(
                theta="Count",
                color="Outlook",
                tooltip=["Outlook", "Count"]
            )
            .properties(width=350, height=350)
        )
        st.altair_chart(chart, use_container_width=False)
    except Exception:
        st.info("Install Altair for interactive charts: `pip install altair`")

st.divider()

# ==============================================================
# 🧾 Table + Export
# ==============================================================

st.markdown("### 📋 Detailed Data Table")
st.dataframe(df, use_container_width=True)
st.download_button(
    "⬇️ Export Analytics Data (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    "executive_summary_analytics.csv",
    "text/csv",
)

st.success("✅ Analytics dashboard loaded successfully.")
