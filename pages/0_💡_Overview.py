import streamlit as st
from datetime import datetime

# ==============================================================
# 🌍 Page Config
# ==============================================================
st.set_page_config(
    page_title="Renewable Energy Financial Analyst | Overview",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================
# 🌟 Global Styling & Header
# ==============================================================
st.markdown("""
<style>
@keyframes glowPulse {
  0% { text-shadow: 0 0 4px #00d4ff, 0 0 10px #00d4ff, 0 0 20px #00d4ff; }
  100% { text-shadow: 0 0 2px #00d4ff, 0 0 6px #00d4ff, 0 0 12px #00d4ff; }
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.main-title {
  font-size: 3rem;
  color: #00d4ff;
  text-align: center;
  animation: glowPulse 2s ease-in-out infinite alternate;
  margin-top: 100px;
  letter-spacing: 1px;
}
.subtitle {
  text-align: center;
  color: #b0b0b0;
  font-size: 1rem;
  margin-top: -10px;
  animation: fadeIn 1s ease both;
}
.feature-card {
  background-color: #1c1f24;
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.1);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.25);
}
[data-testid="stSidebar"] {
    background-color: #111418;
    border-right: 1px solid rgba(0, 212, 255, 0.2);
}
[data-testid="stSidebarNav"]::before {
    content: "🚀 Renewable Energy Financial Analyst";
    margin-left: 20px;
    margin-top: 20px;
    font-size: 0.9rem;
    color: #00d4ff;
    letter-spacing: 0.5px;
}
</style>

<h1 class="main-title">Renewable Energy Financial Analyst</h1>
<p class="subtitle">AI-Driven Multi-Agent Research Suite ⚙️</p>
""", unsafe_allow_html=True)

# ==============================================================
# 🌐 Feature Overview Section
# ==============================================================
st.divider()
st.markdown("### 🌟 Key Features")

c1, c2, c3 = st.columns(3)
c1.markdown("""
<div class="feature-card">
    <h3>💼 Executive Summary Pro+</h3>
    <p>Generates structured AI-driven reports with confidence analysis, market outlooks, and agent consensus metrics.</p>
</div>
""", unsafe_allow_html=True)

c2.markdown("""
<div class="feature-card">
    <h3>📊 Analytics Dashboard</h3>
    <p>Interactive visualization suite for trend tracking, delta comparison, and performance monitoring across runs.</p>
</div>
""", unsafe_allow_html=True)

c3.markdown("""
<div class="feature-card">
    <h3>📁 Run History & Archive</h3>
    <p>View historical results, track model stability, and export detailed analytics across multiple simulation cycles.</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================
# 🧭 Navigation Links
# ==============================================================
st.divider()
st.markdown("### 🧭 Quick Navigation")

colA, colB = st.columns(2)
with colA:
    if st.button("💼 Go to Executive Summary Pro+", use_container_width=True):
        st.switch_page("pages/1_📈_Executive_Summary_ProPlus.py")
with colB:
    if st.button("📊 Open Analytics Dashboard", use_container_width=True):
        st.switch_page("pages/2_📊_Analytics_Dashboard.py")

# ==============================================================
# 🕒 Footer / Last Updated
# ==============================================================
st.markdown("---")
last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(
    f"<div style='text-align:center;font-size:13px;color:gray;'>⏱️ Last updated: <b>{last_refresh}</b></div>",
    unsafe_allow_html=True
)
