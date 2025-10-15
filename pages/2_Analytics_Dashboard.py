import streamlit as st
import pandas as pd
import altair as alt
from src.dashboard.generate_dashboard import load_current_and_previous_runs, compute_confidence_deltas
from datetime import datetime

# ==============================================================
# 🌍 Page Config & Header Branding
# ==============================================================
st.set_page_config(
    page_title="Renewable Energy Financial Analyst | Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@keyframes glowPulse {
  0% { text-shadow: 0 0 4px #00d4ff, 0 0 10px #00d4ff, 0 0 20px #00d4ff; }
  100% { text-shadow: 0 0 2px #00d4ff, 0 0 6px #00d4ff, 0 0 12px #00d4ff; }
}
.main-title {
  font-size: 2.7rem;
  color: #00d4ff;
  text-align: center;
  animation: glowPulse 2s ease-in-out infinite alternate;
  margin-top: 40px;
  letter-spacing: 1px;
}
.subtitle {
  text-align: center;
  color: #b0b0b0;
  font-size: 1rem;
  margin-top: -10px;
}
.metric-card {
  padding: 18px;
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
[data-testid="stSidebar"] {
    background-color: #111418;
    border-right: 1px solid rgba(0, 212, 255, 0.2);
}
[data-testid="stSidebarNav"]::before {
    content: "📊 Analytics Dashboard — REFA Suite";
    margin-left: 20px;
    margin-top: 20px;
    font-size: 0.9rem;
    color: #00d4ff;
    letter-spacing: 0.5px;
}
</style>

<h1 class="main-title">Renewable Energy Financial Analyst</h1>
<p class="subtitle">Executive Summary Analytics | Confidence, Trends & Market Signals ⚙️</p>
""", unsafe_allow_html=True)

st.divider()

# ==============================================================
# 🧭 Sidebar Navigation
# ==============================================================
st.sidebar.header("🧭 Navigation")
st.sidebar.markdown("[🌍 Executive Summary ProPlus](./1_📈_Executive_Summary_ProPlus)")
st.sidebar.markdown("[📊 Analytics Dashboard](./2_📊_Analytics_Dashboard)")
st.sidebar.markdown("---")

st.sidebar.subheader("📊 Chart Controls")
show_conf = st.sidebar.checkbox("Show Confidence Chart", True)
show_delta = st.sidebar.checkbox("Show Δ Confidence Chart", True)
show_outlook = st.sidebar.checkbox("Show Outlook Breakdown", True)

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
# 🧮 Summary Metrics
# ==============================================================
num_tickers = len(df)
avg_conf = df["Confidence"].mean()
avg_delta = df["Delta"].mean()
num_up = sum(df["Delta"] > 0)
num_down = sum(df["Delta"] < 0)
num_flat = sum(df["Delta"] == 0)

st.markdown("### 🧠 Run Overview Summary")

metric_cols = st.columns(5)
metrics = [
    ("🏢 Companies", num_tickers),
    ("📈 Avg Confidence", f"{avg_conf:.2f}%"),
    ("⚡ Avg Δ Confidence", f"{avg_delta:.2f}%"),
    ("🟢 Improved", int(num_up)),
    ("🔴 Declined", int(num_down)),
]
for col, (label, val) in zip(metric_cols, metrics):
    col.markdown(
        f"<div class='metric-card'><div class='metric-title'>{label}</div><h2>{val}</h2></div>",
        unsafe_allow_html=True
    )

st.divider()

# ==============================================================
# 📊 Charts
# ==============================================================
if show_conf:
    st.markdown("### 📈 Confidence Distribution")
    try:
        st.bar_chart(df.set_index("Ticker")["Confidence"])
    except Exception as e:
        st.warning(f"⚠️ Could not render confidence chart: {e}")

if show_delta:
    st.markdown("### 📉 Confidence Δ (Change from Previous Run)")
    try:
        st.bar_chart(df.set_index("Ticker")["Delta"])
    except Exception as e:
        st.warning(f"⚠️ Could not render delta chart: {e}")

if show_outlook:
    st.markdown("### 🧠 Outlook Breakdown")
    outlook_counts = df["Outlook"].value_counts()
    outlook_data = pd.DataFrame({
        "Outlook": outlook_counts.index,
        "Count": outlook_counts.values
    })
    st.dataframe(outlook_data, hide_index=True, use_container_width=True)

    try:
        chart = (
            alt.Chart(outlook_data)
            .mark_arc(innerRadius=60)
            .encode(
                theta="Count",
                color=alt.Color("Outlook", scale=alt.Scale(domain=["Positive","Neutral","Negative"],
                                                          range=["#00d4ff","#aaaaaa","#ff6b6b"])),
                tooltip=["Outlook", "Count"]
            )
            .properties(width=350, height=350)
        )
        st.altair_chart(chart, use_container_width=False)
    except Exception as e:
        st.info("Install Altair for interactive charts: `pip install altair`")

st.divider()

# ==============================================================
# 🧾 Table + Export
# ==============================================================
st.markdown("### 📋 Detailed Data Table")
st.dataframe(df, use_container_width=True)

st.download_button(
    label="⬇️ Export Analytics Data (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="executive_summary_analytics.csv",
    mime="text/csv",
    use_container_width=True
)

# ==============================================================
# 🔄 Footer / Refresh Timestamp
# ==============================================================
last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(
    f"<div style='font-size:12px;color:gray;text-align:right;margin-top:20px;'>🔄 Refreshed: <b>{last_refresh}</b></div>",
    unsafe_allow_html=True
)
