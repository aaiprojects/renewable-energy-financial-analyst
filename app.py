# app.py — Streamlit UI (strict: LangGraph + CrewAI only)
import streamlit as st
import pandas as pd

from src.config.settings import Settings
from src.config.watchlist import WATCHLIST
from src.tools.prices import PricesTool
from src.tools.news import NewsTool
from src.agent.orchestrator_lg import LGOrchestrator  # strict import
from src.agent.nl_orchestrator import NLOrchestrator

st.set_page_config(page_title="Renewable Energy Financial Analyst", layout="wide")
st.title("🔆 Renewable Energy Financial Analyst — Sector Dashboard")

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

tab_overview, tab_deepdive, tab_assistant = st.tabs(["📊 Overview", "🔍 Deep Dive", "🤖 AI Assistant"])

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
        st.dataframe(df, use_container_width=True)
        st.caption("Top Movers (by % change)")
        st.table(df.head(5)[["ticker", "name", "pct_change"]].fillna("N/A"))
    else:
        st.info("Quotes unavailable in this environment.")

    st.subheader("Sector Headlines (last 7 days)")
    for h in news.fetch_sector_news():
        st.write(f"- [{h['title']}]({h['url']}) · *{h.get('tag','')}*")

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
        for url in report.get("citations", []):
            st.write(f"- {url}")

# AI Assistant
with tab_assistant:
    st.subheader("🤖 AI Financial Assistant")
    st.caption("Ask questions about renewable energy stocks, request charts, or get insights")
    
    # Query examples
    with st.expander("💡 Example Queries", expanded=False):
        st.markdown("""
        **📈 Chart & Visualization Queries:**
        - "Show me FSLR's price performance over the last 3 months"
        - "Compare solar stocks vs wind stocks performance"
        - "Create a technical analysis chart for ENPH"
        
        **📊 Comparison & Analysis:**
        - "Which renewable energy company has the best returns this year?"
        - "Compare FSLR and RUN volatility"
        - "Show me the renewable energy sector overview"
        
        **📰 News & Sentiment:**
        - "What's the recent news sentiment around solar policy?"
        - "Latest developments in wind energy sector"
        - "ESG news for renewable energy companies"
        """)
    
    # Query input
    user_query = st.text_area(
        "What would you like to analyze?",
        placeholder="e.g., 'Compare FSLR vs ENPH price performance over 6 months'",
        height=100,
        help="Ask anything about renewable energy stocks, markets, or request specific charts and analysis"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("🔍 Analyze Query", type="primary")
    with col2:
        if st.button("🔄 Clear"):
            st.rerun()
    
    if analyze_button and user_query.strip():
        cfg = Settings()
        nl_orch = NLOrchestrator(cfg)
        
        with st.spinner("Processing your query..."):
            try:
                result = nl_orch.process_natural_language_query(user_query)
                
                if result.get("success", False):
                    # Show explanation
                    st.success("✅ Analysis Complete")
                    st.info(f"**Understanding:** {result.get('explanation', '')}")
                    
                    # Display results based on analysis type
                    analysis_type = result.get("analysis_type")
                    
                    if analysis_type in ["price_chart", "comparison", "technical_analysis", "sector_overview"]:
                        # Show chart
                        chart = result.get("chart")
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)
                        
                        # Show summary
                        summary = result.get("summary")
                        if summary:
                            st.markdown(f"**Summary:** {summary}")
                    
                    elif analysis_type == "news_sentiment":
                        # Show crew analyses
                        crew_analyses = result.get("crew_analyses", [])
                        if crew_analyses:
                            st.subheader("📰 News & Sentiment Analysis")
                            for i, analysis in enumerate(crew_analyses, 1):
                                with st.expander(f"Analysis {i}: {analysis.get('ticker', 'Unknown')}", expanded=True):
                                    st.write(analysis.get("crew_output", "No analysis available"))
                        
                        # Show sector news
                        news_headlines = result.get("news_headlines", [])
                        if news_headlines:
                            st.subheader("📈 Sector Headlines")
                            for headline in news_headlines:
                                st.write(f"- [{headline.get('title', 'No title')}]({headline.get('url', '#')}) · *{headline.get('tag', '')}*")
                    
                    elif analysis_type == "detailed_analysis":
                        # Show detailed report
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
                st.info("Please try rephrasing your query or contact support.")
    
    elif analyze_button:
        st.warning("⚠️ Please enter a query to analyze.")
