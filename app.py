# app.py — Streamlit UI (strict: LangGraph + CrewAI only)
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()  # 👈 ensures .env is read before anything else

from src.config.settings import Settings
from src.config.watchlist import WATCHLIST
from src.tools.prices import PricesTool
from src.tools.news import NewsTool
from src.agent.orchestrator_lg import LGOrchestrator  # strict import

# Try to import enhanced components
try:
    from src.agent.nl_orchestrator import NLOrchestrator
    NL_AVAILABLE = True
except ImportError:
    NL_AVAILABLE = False

st.set_page_config(page_title="Renewable Energy Financial Analyst", layout="wide")
st.title("🔆 Renewable Energy Financial Analyst — Enhanced with Real Data Sources")
st.caption("📡 Now powered by NewsAPI, SEC EDGAR, and FRED for real-time analysis")


# Sidebar
with st.sidebar:
    st.header("Filters")
    subsectors = sorted({w.subsector for w in WATCHLIST})
    regions = sorted({w.region for w in WATCHLIST})
    sel_subsector = st.multiselect("Subsector", subsectors, default=subsectors)
    sel_region = st.multiselect("Region", regions, default=regions)
    st.divider()
    st.caption("Deep Dive Settings")
    dd_days = st.number_input("Lookback (days)", min_value=7, max_value=120, value=30, step=1)
    dd_refresh = st.checkbox("Refresh (ignore cache)", value=False)

if NL_AVAILABLE:
    tab_overview, tab_deepdive, tab_assistant = st.tabs(["📊 Overview", "🔍 Deep Dive", "🤖 AI Assistant"])
else:
    tab_overview, tab_deepdive = st.tabs(["📊 Overview", "🔍 Deep Dive"])
    st.sidebar.warning("⚠️ AI Assistant unavailable - missing dependencies")

# Overview
with tab_overview:
    st.subheader("Market Snapshot")
    cfg = Settings()
    prices = PricesTool()
    news = NewsTool(api_key=cfg.newsapi_key)

    wl_filtered = [w for w in WATCHLIST if w.subsector in sel_subsector and w.region in sel_region]
    df_quotes = prices.batch_quotes([w.ticker for w in wl_filtered])
    if df_quotes is not None and len(df_quotes) > 0:
        meta = pd.DataFrame([{"ticker": w.ticker, "name": w.name, "subsector": w.subsector, "region": w.region} for w in wl_filtered])
        df = meta.merge(df_quotes, on="ticker", how="left").sort_values(by="pct_change", ascending=False, na_position="last")
        st.dataframe(df, width='stretch')
        st.caption("Top Movers (by % change)")
        st.table(df.head(5)[["ticker", "name", "pct_change"]].fillna("N/A"))
    else:
        st.info("Quotes unavailable in this environment.")

    st.subheader("Sector Headlines (last 7 days)")
    headlines = news.fetch_sector_news()
    if headlines:
        for h in headlines:
            st.write(f"- [{h.get('title', 'No title')}]({h.get('url', '#')}) · *{h.get('tag', 'news')}*")
    else:
        st.info("No recent headlines available (check NewsAPI configuration)")

# Enhanced Data Sources Info
with st.sidebar:
    st.divider()
    st.caption("🔧 Data Sources")
    cfg = Settings()
    
    # Check API configurations
    api_status = {
        "NewsAPI": "✅" if cfg.newsapi_key else "❌",
        "FRED": "✅" if cfg.fred_api_key else "❌", 
        "SEC EDGAR": "✅",  # Always available
        "YFinance": "✅"   # Always available
    }
    
    for api, status in api_status.items():
        st.write(f"{status} {api}")
    
    if not cfg.newsapi_key:
        st.info("💡 Set NEWSAPI_KEY for real news data")
    if not cfg.fred_api_key:
        st.info("💡 Set FRED_API_KEY for macro data")

# Deep Dive
with tab_deepdive:
    st.subheader("Company Analysis (LangGraph + CrewAI)")
    options = [f"{w.ticker} — {w.name}" for w in (wl_filtered or WATCHLIST)]
    choice = st.selectbox("Select a company", options)
    selected_ticker = choice.split(" — ")[0]

    if st.button("Run Deep Dive"):
        cfg = Settings()
        orch = LGOrchestrator(cfg)   # strict: must exist/import
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

# AI Assistant Tab (if available)
if NL_AVAILABLE:
    with tab_assistant:
        st.subheader("🤖 AI Financial Assistant")
        st.caption("Ask questions about renewable energy stocks using real-time data sources")
        
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
                                # Update chart to use full container width
                                chart.update_layout(autosize=True)
                                st.plotly_chart(chart)
                            
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
                                    st.dataframe(score_df, width='stretch')
                                
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
                        
                        # Show general summary if available
                        if "summary" in result and analysis_type not in ["detailed_analysis"]:
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
