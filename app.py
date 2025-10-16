# app.py — Streamlit UI Landing Page
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from src.config.settings import Settings
from src.config.watchlist import WATCHLIST
from src.tools.prices import PricesTool
from src.tools.news import NewsTool

# Import navigation components
from src.components.navigation import render_navigation_bar
from src.components.hide_sidebar import hide_sidebar_completely

# Try to import enhanced components
try:
    from src.agent.nl_orchestrator import NLOrchestrator
    NL_AVAILABLE = True
except ImportError:
    NL_AVAILABLE = False

st.set_page_config(page_title="Renewable Energy Financial Analyst", layout="wide")

# Hide sidebar
hide_sidebar_completely()

# CSS Styling for Navigation Tiles
st.markdown("""
<style>
.nav-tile {
  background: linear-gradient(135deg, #0f1419 0%, #1c2833 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(0, 212, 255, 0.3);
  transition: all 0.3s ease;
  margin: 10px;
  cursor: pointer;
}
.nav-tile:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
}
.nav-tile h3 {
  color: #00d4ff;
  margin-bottom: 10px;
  font-size: 1.3rem;
}
.nav-tile p {
  color: #b0b0b0;
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🔆 Renewable Energy Financial Analyst — Enhanced with Real Data Sources")
st.caption("📡 Now powered by NewsAPI, SEC EDGAR, and FRED for real-time analysis")

# Navigation Bar
render_navigation_bar(current_page="Home")

# Navigation Tiles
st.markdown("## 🎯 Choose Your Analysis Path")
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.markdown("""
    <div class="nav-tile">
        <h3>🔍 Deep Dive Analysis</h3>
        <p>Comprehensive stock analysis using LangGraph + CrewAI with real-time data sources. Individual company research and batch processing.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Deep Dive", key="landing_deep_dive", type="primary", width="stretch"):
        st.switch_page("pages/1_🔍_Deep_Dive_Analysis.py")

with nav_col2:
    st.markdown("""
    <div class="nav-tile">
        <h3>📊 Executive Summary Pro+</h3>
        <p>View confidence trends and executive summaries with interactive charts. Track analysis history and performance metrics.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Dashboard", key="landing_executive", type="primary", width="stretch"):
        st.switch_page("pages/1_Executive_Summary_ProPlus.py")

with nav_col3:
    st.markdown("""
    <div class="nav-tile">
        <h3>🤖 AI Assistant</h3>
        <p>Natural language queries with real-time data. Ask questions and get charts, analysis, and insights powered by multiple APIs.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Assistant", key="landing_ai_assistant", type="primary", width="stretch"):
        if NL_AVAILABLE:
            st.switch_page("pages/2_🤖_AI_Assistant.py")
        else:
            st.error("⚠️ AI Assistant unavailable - missing dependencies")

st.divider()

# Market Overview Section
st.markdown("## 📊 Live Market Overview")

# Market filters in main content area
with st.expander("🔧 Market Filters & Data Sources", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Market Filters**")
        subsectors = sorted({w.subsector for w in WATCHLIST})
        regions = sorted({w.region for w in WATCHLIST})
        sel_subsector = st.multiselect("Subsector", subsectors, default=subsectors, key="main_subsector")
        sel_region = st.multiselect("Region", regions, default=regions, key="main_region")
    
    with col2:
        st.markdown("**🔧 Data Sources Status**")
        cfg = Settings()
        
        # Check API configurations
        api_status = {
            "NewsAPI": "✅" if cfg.newsapi_key else "❌",
            "FRED": "✅" if cfg.fred_api_key else "❌", 
            "SEC EDGAR": "✅",  # Always available
            "YFinance": "✅",   # Always available
        }
        
        for source, status in api_status.items():
            st.text(f"{status} {source}")
    
    with col3:
        st.markdown("**⚡ Quick Actions**")
        if st.button("🎯 Run Quick Analysis", help="Launch Deep Dive for quick analysis"):
            st.switch_page("pages/1_🔍_Deep_Dive_Analysis.py")

# Market Snapshot
st.subheader("Market Snapshot")
cfg = Settings()
prices = PricesTool()
news = NewsTool(api_key=cfg.newsapi_key)

# Handle filter defaults
if 'main_subsector' not in st.session_state:
    st.session_state.main_subsector = subsectors
if 'main_region' not in st.session_state:
    st.session_state.main_region = regions

# Use filters
sel_subsector = st.session_state.get('main_subsector', subsectors)
sel_region = st.session_state.get('main_region', regions)

wl_filtered = [w for w in WATCHLIST if w.subsector in sel_subsector and w.region in sel_region]
df_quotes = prices.batch_quotes([w.ticker for w in wl_filtered])
if df_quotes is not None and len(df_quotes) > 0:
    meta = pd.DataFrame([{"ticker": w.ticker, "name": w.name, "subsector": w.subsector, "region": w.region} for w in wl_filtered])
    df = meta.merge(df_quotes, on="ticker", how="left").sort_values(by="pct_change", ascending=False, na_position="last")
    st.dataframe(df, use_container_width=True)
    st.caption("Top Movers (by % change)")
    st.table(df.head(5)[["ticker", "name", "pct_change"]].fillna("N/A"))
else:
    st.info("Quotes unavailable in this environment.")

st.caption("Recent News")
headlines = news.fetch_sector_news(days=3)
if headlines:
    for item in headlines[:5]:
        st.write(f"- {item.get('title', 'No title')}")
else:
    st.info("News unavailable in this environment")

# Footer
st.markdown("---")
st.caption("💡 Navigate using the tiles above to access different analysis tools and features.")