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

# Remove top padding to push navigation to very top
st.markdown("""
<style>
.main .block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)

# Navigation Bar (moved to top)
render_navigation_bar(current_page="Home")

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

/* Center align the navigation buttons - comprehensive selectors */
div[data-testid="column"] > div:has(button[key*="landing_"]) {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

/* Additional centering for nested columns */
div[data-testid="column"] div[data-testid="column"] > div:has(button[key*="landing_"]) {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 15px;
}

/* Ensure button containers are centered */
div[data-testid="stVerticalBlock"]:has(button[key*="landing_"]) {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Center the button element itself */
button[key*="landing_"] {
  margin: 0 auto !important;
  display: block !important;
}

/* Style navigation buttons to match tile text color (#00d4ff) */
div[data-testid="stVerticalBlock"] button[kind="primary"],
div[data-testid="column"] button[kind="primary"],
button[data-testid="baseButton-primary"] {
  background: linear-gradient(135deg, #0f1419 0%, #1c2833 100%) !important;
  border: 2px solid #00d4ff !important;
  color: #00d4ff !important;
  transition: all 0.3s ease !important;
  font-weight: bold !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  min-height: 38px !important;
  height: 38px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 0.875rem !important;
}

div[data-testid="stVerticalBlock"] button[kind="primary"]:hover,
div[data-testid="column"] button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
  background: linear-gradient(135deg, #00d4ff 0%, #0080cc 100%) !important;
  border-color: #00d4ff !important;
  color: #0f1419 !important;
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4) !important;
  transform: translateY(-2px) !important;
}

div[data-testid="stVerticalBlock"] button[kind="primary"]:active,
div[data-testid="column"] button[kind="primary"]:active,
button[data-testid="baseButton-primary"]:active {
  background: linear-gradient(135deg, #0080cc 0%, #006699 100%) !important;
  transform: translateY(0px) !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🔆 Renewable Energy Financial Analyst — Enhanced with Real Data Sources")
st.caption("📡 Now powered by NewsAPI, SEC EDGAR, and FRED for real-time analysis")

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
    
    # Center the button using columns with better ratio
    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    with btn_col:
        if st.button("🔍 Deep Dive", key="landing_deep_dive", type="primary", use_container_width=True):
            st.switch_page("pages/Deep_Dive_Analysis.py")

with nav_col2:
    st.markdown("""
    <div class="nav-tile">
        <h3>📊 Executive Summary Pro+</h3>
        <p>View confidence trends and executive summaries with interactive charts. Track analysis history and performance metrics.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the button using columns with better ratio
    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    with btn_col:
        if st.button("📊 Executive", key="landing_executive", type="primary", use_container_width=True):
            st.switch_page("pages/Executive_Summary_ProPlus.py")

with nav_col3:
    st.markdown("""
    <div class="nav-tile">
        <h3>🤖 AI Assistant</h3>
        <p>Natural language queries with real-time data. Ask questions and get charts, analysis, and insights powered by multiple APIs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the button using columns with better ratio
    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    with btn_col:
        if st.button("🤖 Assistant", key="landing_ai_assistant", type="primary", use_container_width=True):
            if NL_AVAILABLE:
                st.switch_page("pages/AI_Assistant.py")
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
            st.switch_page("pages/Deep_Dive_Analysis.py")

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
        title = item.get('title', 'No title')
        url = item.get('url', '')
        description = item.get('description', '')
        
        if url:
            # Create clickable hyperlink with description as tooltip
            st.markdown(f"- 📰 **[{title}]({url})**", unsafe_allow_html=True)
            if description:
                st.caption(f"   ↳ {description[:120]}{'...' if len(description) > 120 else ''}")
        else:
            st.write(f"- 📰 {title}")
else:
    st.info("News unavailable in this environment")

# Footer
st.markdown("---")
st.caption("💡 Navigate using the tiles above to access different analysis tools and features.")