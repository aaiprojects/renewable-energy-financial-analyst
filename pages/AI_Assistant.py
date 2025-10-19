# pages/2_🤖_AI_Assistant.py — Natural Language AI Assistant
import streamlit as st
import pandas as pd
from uuid import uuid4

# Try to load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.config.settings import Settings
from src.components.navigation import render_navigation_bar
from src.components.hide_sidebar import hide_sidebar_completely

# Try to import enhanced components
try:
    from src.agent.nl_orchestrator import NLOrchestrator
    NL_AVAILABLE = True
except ImportError:
    NL_AVAILABLE = False

st.set_page_config(page_title="AI Assistant", layout="wide")

# Hide sidebar completely - MUST be first thing after page config
hide_sidebar_completely()

# Navigation Bar
render_navigation_bar(current_page="AI Assistant")

# Header
st.title("🤖 AI Financial Assistant")
st.caption("📡 Ask questions about renewable energy stocks using real-time data sources")

if not NL_AVAILABLE:
    st.error("⚠️ AI Assistant unavailable - missing dependencies")
    st.info("The Natural Language Orchestrator component is not available. Please check your environment configuration.")
    st.stop()

# Enhanced query examples
with st.expander("💡 Example Queries", expanded=False):
    st.markdown("""
    **📈 Chart & Visualization Queries:**
    - "Show me FSLR's price performance over the last 3 months"
    - "Compare solar stocks vs wind stocks performance"
    - "Create a technical analysis chart for ENPH"
    
    **📊 Analysis & Research:**
    - "What's the latest news sentiment around solar policy?"
    - "Analyze FSLR's recent SEC filings"
    - "Show me renewable energy sector overview with real market data"
    
    **📰 Enhanced with Real Data:**
    - "Latest developments in wind energy using NewsAPI"
    - "Fundamental analysis of NEE with SEC EDGAR data"
    - "Macroeconomic impact on renewable energy sector"
    """)

# Query input
user_query = st.text_area(
    "What would you like to analyze?",
    placeholder="e.g., 'Show me recent news sentiment for FSLR' or 'Compare ENPH vs RUN using real data'",
    height=100,
    help="Ask anything about renewable energy stocks - now powered by real NewsAPI, SEC EDGAR, and FRED data"
)

col1, col2 = st.columns([1, 4])
with col1:
    analyze_button = st.button("🔍 Analyze Query", type="primary")
with col2:
    if st.button("🔄 Clear"):
        st.rerun()

if analyze_button and user_query.strip():
    cfg = Settings()
    
    try:
        nl_orch = NLOrchestrator(cfg)
        
        with st.spinner("Processing your query with real data sources..."):
            result = nl_orch.process_natural_language_query(user_query)
            
            if result.get("success", False):
                # Show success with enhanced data indicator
                st.success("✅ Analysis Complete - Enhanced with Real Data")
                st.info(f"**Understanding:** {result.get('explanation', '')}")
                
                # Show data sources used
                if result.get("enhanced_data"):
                    st.caption("🔗 Data Sources: " + ", ".join(result.get("data_sources", [])))
                
                # Display results based on analysis type
                analysis_type = result.get("analysis_type")
                
                if analysis_type in ["price_chart", "comparison", "technical_analysis", "sector_overview"]:
                    # Show chart
                    chart = result.get("chart")
                    if chart:
                        # Update chart to use full container width when Plotly is available
                        if hasattr(chart, "update_layout"):
                            chart.update_layout(autosize=True)
                            chart_key = f"chart-{analysis_type}-{uuid4()}"
                            st.plotly_chart(chart, use_container_width=True, key=chart_key)
                        elif isinstance(chart, dict):
                            st.warning(chart.get("message", "Plot unavailable. Install plotly>=5.17.0 for chart support."))
                        else:
                            st.warning("Chart format not supported in this environment.")
                    
                    # Show summary
                    summary = result.get("summary")
                    if summary:
                        st.markdown(f"**Summary:** {summary}")
                
                elif analysis_type == "fundamental_analysis":
                    # Show fundamental analysis with SEC filings
                    summary = result.get("summary")
                    if summary:
                        st.markdown(f"**Summary:** {summary}")
                    
                    # Show filing analysis if available
                    filing_analysis = result.get("filing_analysis")
                    if filing_analysis:
                        st.markdown(f"**Analysis:** {filing_analysis}")
                    
                    # Show SEC filings data
                    filings_data = result.get("filings_data", [])
                    if filings_data:
                        st.subheader("📋 Recent SEC Filings")
                        for i, filing in enumerate(filings_data, 1):
                            with st.expander(f"Filing {i}: {filing.get('form', 'Unknown')} - {filing.get('filedAt', 'Unknown Date')}", expanded=False):
                                st.write(f"**Form Type:** {filing.get('form', 'N/A')}")
                                st.write(f"**Filed Date:** {filing.get('filedAt', 'N/A')}")
                                st.write(f"**Accession Number:** {filing.get('accessionNumber', 'N/A')}")
                                st.write(f"**Primary Document:** {filing.get('primaryDocument', 'N/A')}")
                                if filing.get('reportUrl'):
                                    st.write(f"**SEC Report:** [View Filing]({filing.get('reportUrl')})")
                    else:
                        st.info("No recent SEC filings found or unable to retrieve filing data.")
                
                elif analysis_type in ["news_sentiment"]:
                    # Show crew analyses
                    crew_analyses = result.get("crew_analyses", [])
                    if crew_analyses:
                        st.subheader("📰 Enhanced Analysis with Real Data")
                        for i, analysis in enumerate(crew_analyses, 1):
                            with st.expander(f"Analysis {i}: {analysis.get('ticker', 'Unknown')}", expanded=True):
                                st.write(analysis.get("crew_output", "No analysis available"))
                                if analysis.get("context_provided"):
                                    st.caption("✅ Enhanced with real-time context data")
                    
                    # Show sector news
                    news_headlines = result.get("news_headlines", [])
                    if news_headlines:
                        st.subheader("📈 Real-Time Headlines")
                        for headline in news_headlines:
                            st.write(f"- [{headline.get('title', 'No title')}]({headline.get('url', '#')}) · *{headline.get('tag', '')}*")
                
                elif analysis_type == "detailed_analysis":
                    # Show detailed report with enhanced data
                    detailed_report = result.get("detailed_report", {})
                    if detailed_report:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Recommendation", detailed_report.get("recommendation", "WATCH"))
                        with col2:
                            st.metric("Confidence", f"{round(detailed_report.get('confidence', 0.5)*100)}%")
                        
                        scores = detailed_report.get("scores", {})
                        if scores:
                            st.subheader("📊 Scoring Breakdown")
                            score_df = pd.DataFrame([scores], index=[detailed_report.get("ticker", "Company")])
                            st.dataframe(score_df, use_container_width=True)
                        
                        st.subheader("📋 Executive Summary")
                        st.write(detailed_report.get("summary", "No summary available."))
                        
                        # Show enhanced data sources
                        if "data_sources" in detailed_report:
                            st.subheader("📊 Real Data Sources")
                            data_sources = detailed_report["data_sources"]
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("News Articles", data_sources.get("news_articles", 0))
                                st.metric("SEC Filings", data_sources.get("sec_filings", 0))
                            
                            with col2:
                                st.metric("Macro Indicators", data_sources.get("macro_indicators", 0))
                                st.metric("Price History", f"{data_sources.get('price_history_days', 0)} days")
                
                elif analysis_type == "general_analysis":
                    # Show general analysis results
                    st.subheader("📊 Analysis Results")
                    summary = result.get("summary", "")
                    if summary:
                        st.markdown(summary)
                    else:
                        st.write("Analysis completed successfully.")
                
                # Show general summary if available for other types
                elif "summary" in result and analysis_type not in ["detailed_analysis", "general_analysis"]:
                    st.markdown(f"**Analysis:** {result['summary']}")
            
            else:
                # Show error
                st.error(f"❌ Error: {result.get('error', 'Unknown error occurred')}")
                if result.get('explanation'):
                    st.info(f"**Note:** {result['explanation']}")
        
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.info("Please check your API configuration or try a simpler query.")

elif analyze_button:
    st.warning("⚠️ Please enter a query to analyze.")

# API Status in main content area
with st.expander("🔧 AI Assistant Status & Configuration", expanded=False):
    cfg = Settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🤖 Component Status**")
        api_status = {
            "Natural Language": "✅" if NL_AVAILABLE else "❌",
            "NewsAPI": "✅" if cfg.newsapi_key else "❌",
            "FRED": "✅" if cfg.fred_api_key else "❌", 
            "SEC EDGAR": "✅",
            "YFinance": "✅"
        }
        
        for api, status in api_status.items():
            st.write(f"{status} {api}")
    
    with col2:
        st.markdown("**💡 Configuration Tips**")
        if not NL_AVAILABLE:
            st.error("⚠️ NL Orchestrator missing")
        if not cfg.newsapi_key:
            st.info("Set NEWSAPI_KEY for enhanced news analysis")
        if not cfg.fred_api_key:
            st.info("Set FRED_API_KEY for macro data")
        if NL_AVAILABLE and cfg.newsapi_key and cfg.fred_api_key:
            st.success("All AI components ready!")
    
    st.divider()
    st.info("💡 **Tip**: The AI Assistant can create charts, analyze filings, and provide real-time insights using multiple data sources.")