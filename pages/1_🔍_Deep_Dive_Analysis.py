# pages/1_🔍_Deep_Dive_Analysis.py — Deep Dive Stock Analysis
import streamlit as st
import pandas as pd

# Try to load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.config.settings import Settings
from src.config.watchlist import WATCHLIST
from src.agent.orchestrator_lg import LGOrchestrator
from src.components.navigation import render_navigation_bar
from src.components.hide_sidebar import hide_sidebar_completely

st.set_page_config(page_title="Deep Dive Analysis", layout="wide")

# Hide sidebar completely - MUST be first thing after page config
hide_sidebar_completely()

# Navigation Bar
render_navigation_bar(current_page="Deep Dive")

# Header
st.title("🔍 Deep Dive Analysis")
st.caption("📡 Comprehensive stock analysis powered by LangGraph + CrewAI with real-time data sources")

# Analysis Settings in main content area
with st.expander("⚙️ Analysis Settings & Configuration", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Stock Filters**")
        subsectors = sorted({w.subsector for w in WATCHLIST})
        regions = sorted({w.region for w in WATCHLIST})
        sel_subsector = st.multiselect("Subsector", subsectors, default=subsectors, key="dd_subsector")
        sel_region = st.multiselect("Region", regions, default=regions, key="dd_region")
    
    with col2:
        st.markdown("**🔍 Analysis Parameters**")
        dd_days = st.number_input("Lookback (days)", min_value=7, max_value=120, value=30, step=1)
        dd_refresh = st.checkbox("Refresh (ignore cache)", value=False)
    
    with col3:
        st.markdown("**🔧 Data Sources**")
        cfg = Settings()
        
        api_status = {
            "NewsAPI": "✅" if cfg.newsapi_key else "❌",
            "FRED": "✅" if cfg.fred_api_key else "❌", 
            "SEC EDGAR": "✅",
            "YFinance": "✅"
        }
        
        for api, status in api_status.items():
            st.write(f"{status} {api}")
        
        if not cfg.newsapi_key:
            st.info("💡 Set NEWSAPI_KEY for news")
        if not cfg.fred_api_key:
            st.info("💡 Set FRED_API_KEY for macro data")

# Ensure default values are always available
if 'sel_subsector' not in locals() or not sel_subsector:
    sel_subsector = sorted({w.subsector for w in WATCHLIST})
if 'sel_region' not in locals() or not sel_region:
    sel_region = sorted({w.region for w in WATCHLIST})

# Main content
st.subheader("Company Analysis (LangGraph + CrewAI)")

# Filter watchlist
wl_filtered = [w for w in WATCHLIST if w.subsector in sel_subsector and w.region in sel_region]

if not wl_filtered:
    st.warning("⚠️ No companies match the current filters. Please adjust your filter settings.")
    st.stop()

# Individual analysis
options = [f"{w.ticker} — {w.name}" for w in wl_filtered]

if not options:
    st.warning("⚠️ No companies available for analysis. Please check your filter settings.")
    st.stop()

choice = st.selectbox("Select a company", options, index=0)

if choice is None or choice == "":
    st.warning("⚠️ Please select a company to analyze.")
    st.stop()

selected_ticker = choice.split(" — ")[0]

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Run Deep Dive"):
        cfg = Settings()
        orch = LGOrchestrator(cfg)
        with st.spinner(f"Running analysis for {selected_ticker}..."):
            report = orch.run(ticker=selected_ticker, days=int(dd_days), refresh=dd_refresh)
        st.success("Analysis complete.")
        st.metric("Recommendation", report.get("recommendation", "WATCH"))
        st.metric("Confidence", f"{round(report.get('confidence', 0.5)*100)}%")
        scores = report.get("scores", {})
        if scores:
            st.write(pd.DataFrame([scores], index=[report.get("ticker", selected_ticker)]))
        st.subheader("Executive Summary")
        st.write(report.get("summary", "No summary available."))
        st.subheader("Citations")
        citations = report.get("citations", [])
        if citations:
            for url in citations:
                st.write(f"- {url}")
        else:
            st.info("No citations available")

with col2:
    if st.button("🎯 Run All Watchlist", help="Analyze all stocks in the watchlist (may take several minutes)"):
        cfg = Settings()
        orch = LGOrchestrator(cfg)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_stocks = len(wl_filtered)
        analyzed = 0
        
        for i, w in enumerate(wl_filtered):
            status_text.text(f"Analyzing {w.ticker} ({w.name})...")
            progress_bar.progress((i) / total_stocks)
            
            try:
                with st.spinner(f"Running analysis for {w.ticker}..."):
                    report = orch.run(ticker=w.ticker, days=int(dd_days), refresh=dd_refresh)
                analyzed += 1
                st.success(f"✅ {w.ticker}: {report.get('recommendation', 'N/A')} ({round(report.get('confidence', 0)*100)}%)")
            except Exception as e:
                st.error(f"❌ {w.ticker}: Analysis failed - {str(e)}")
            
            progress_bar.progress((i + 1) / total_stocks)
        
        status_text.text("Analysis complete!")
        st.success(f"🎉 Analyzed {analyzed}/{total_stocks} stocks. Check the Executive Summary dashboard!")

st.divider()

# Show results if individual analysis was run
if 'report' in locals():
    # Enhanced data sources info
    if "data_sources" in report:
        st.subheader("📊 Data Sources Used")
        data_sources = report["data_sources"]
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("News Articles", data_sources.get("news_articles", 0))
            st.metric("SEC Filings", data_sources.get("sec_filings", 0))
        
        with col2:
            st.metric("Macro Indicators", data_sources.get("macro_indicators", 0))
            st.metric("Price History Days", data_sources.get("price_history_days", 0))