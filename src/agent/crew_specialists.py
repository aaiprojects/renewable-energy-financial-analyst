from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew
from ..tools.crewai_tools_imp import (
    SectorHeadlinesTool, 
    TickerNewsTool,
    PricesHistoryTool, 
    FilingsTool, 
    MacroSeriesTool
)

SYSTEM_NEWS = (
    "You are a News/Policy Analyst focused on renewable energy. "
    "Analyze news articles, classify by type (earnings/policy/esg/tech), extract KPIs (MW capacity, subsidies), "
    "assess sentiment, and summarize with direct citations to source URLs."
)
SYSTEM_EARN = (
    "You are an Earnings/Fundamentals Analyst specializing in renewable energy companies. "
    "Parse SEC filings (10-K, 10-Q), extract guidance changes, margin trends, capacity expansion plans, "
    "revenue breakdowns, and key financial metrics. Provide quantitative analysis with specific figures."
)
SYSTEM_MKT = (
    "You are a Market/Technical Analyst for renewable energy stocks. "
    "Analyze price trends, compute technical indicators, assess momentum and volatility, "
    "consider macroeconomic factors affecting the renewable sector, and provide actionable insights."
)

def build_crew() -> Crew:
    news_agent = Agent(
        role="News/Policy Analyst",
        goal=SYSTEM_NEWS,
        backstory=(
            "You specialize in tracking renewable energy policy developments, ESG trends, "
            "technology breakthroughs, and regulatory changes. You excel at identifying market-moving "
            "information and connecting policy changes to investment implications."
        ),
        allow_delegation=False,
        verbose=False,
        tools=[SectorHeadlinesTool(), TickerNewsTool()],
    )

    earnings_agent = Agent(
        role="Earnings/Fundamentals Analyst",
        goal=SYSTEM_EARN,
        backstory=(
            "You are an expert in financial statement analysis for renewable energy companies. "
            "You understand the unique metrics of solar, wind, and storage companies including "
            "capacity factors, LCOE trends, and project pipeline valuations."
        ),
        allow_delegation=False,
        verbose=False,
        tools=[FilingsTool(), MacroSeriesTool()],
    )

    market_agent = Agent(
        role="Market/Technical Analyst", 
        goal=SYSTEM_MKT,
        backstory=(
            "You specialize in technical analysis of renewable energy stocks with deep understanding "
            "of sector correlations, commodity price impacts (oil, natural gas), and policy-driven "
            "volatility patterns. You excel at identifying entry/exit points and risk assessment."
        ),
        allow_delegation=False,
        verbose=False,
        tools=[PricesHistoryTool(), MacroSeriesTool()],
    )

    t_news = Task(
        description=(
            "Analyze recent news and policy developments for {ticker} over the last {days} days. "
            "Focus on: 1) Policy/regulatory changes affecting renewable energy, "
            "2) Company-specific announcements and developments, "
            "3) ESG and sustainability trends, 4) Technology and innovation updates. "
            "Provide sentiment assessment and cite specific sources."
        ),
        agent=news_agent,
        expected_output=(
            "Structured analysis with: \n"
            "- 4-6 bullet points covering key developments\n"
            "- Category tags (policy/earnings/esg/tech/regulatory)\n"
            "- Sentiment score (positive/neutral/negative)\n"
            "- Source URLs for key stories\n"
            "- Investment implications summary"
        )
    )
    
    t_earn = Task(
        description=(
            "Analyze recent SEC filings and fundamental metrics for {ticker}. "
            "Extract key financial data: revenue growth, margin trends, guidance changes, "
            "capacity additions, project pipeline, debt levels, and cash flow. "
            "Compare against renewable energy sector benchmarks."
        ),
        agent=earnings_agent,
        expected_output=(
            "Fundamental analysis report with:\n"
            "- Key financial metrics and trends\n"
            "- Guidance changes and management commentary\n"
            "- Capacity/project pipeline analysis\n"
            "- Peer comparison insights\n"
            "- Valuation assessment\n"
            "- Risk factors identification"
        )
    )
    
    t_mkt = Task(
        description=(
            "Perform technical analysis for {ticker} including price trends, momentum indicators, "
            "volatility assessment, and correlation with renewable energy sector and broader market. "
            "Consider macroeconomic factors like interest rates, oil prices, and policy environment."
        ),
        agent=market_agent,
        expected_output=(
            "Technical analysis summary with:\n"
            "- Price trend analysis (short/medium/long term)\n"
            "- Key technical levels (support/resistance)\n"
            "- Momentum and volatility assessment\n"
            "- Sector correlation analysis\n"
            "- Macroeconomic impact assessment\n"
            "- Trading recommendation with risk factors"
        )
    )

    return Crew(agents=[news_agent, earnings_agent, market_agent], tasks=[t_news, t_earn, t_mkt])

def run_crew(ticker: str, days: int = 30, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run the CrewAI specialist analysis with enhanced context.
    
    Args:
        ticker: Stock ticker symbol
        days: Analysis lookback period
        context: Additional context from orchestrator (prices, news, filings, macro data)
    
    Returns:
        Dictionary containing crew analysis results
    """
    crew = build_crew()
    
    # Prepare inputs with enhanced context
    inputs = {
        "ticker": ticker, 
        "days": days,
        "context": context or {}
    }
    
    try:
        result = crew.kickoff(inputs=inputs)
        return {
            "ticker": ticker,
            "days": days,
            "crew_output": str(result),
            "analysis_type": "comprehensive",
            "data_sources_used": ["news", "filings", "prices", "macro"],
            "context_provided": context is not None
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "crew_output": f"Error in crew analysis: {str(e)}",
            "analysis_type": "error",
            "error": str(e)
        }
