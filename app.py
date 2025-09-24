# app.py — Streamlit UI (strict: LangGraph + CrewAI only)
import streamlit as st
import pandas as pd

from src.config.settings import Settings
from src.config.watchlist import WATCHLIST
from src.tools.prices import PricesTool
from src.tools.news import NewsTool
from src.agent.orchestrator_lg import LGOrchestrator  # strict import

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

tab_overview, tab_deepdive = st.tabs(["📊 Overview", "🔍 Deep Dive"])

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
