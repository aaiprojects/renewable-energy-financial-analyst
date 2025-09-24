from typing import Dict, Any
from crewai import Agent, Task, Crew
from ..tools.crewai_tools_imp import SectorHeadlinesTool, PricesHistoryTool

SYSTEM_NEWS = (
    "You are a News/Policy Analyst focused on renewable energy. "
    "Classify news (earnings/policy/esg/tech), extract KPIs (MW, subsidies), and summarize with citations."
)
SYSTEM_EARN = (
    "You are an Earnings/Fundamentals Analyst. Parse filings and earnings for guidance deltas, margins, and capacity plans."
)
SYSTEM_MKT = (
    "You are a Market/Technical Analyst. Compute simple indicators and produce a momentum assessment."
)

def build_crew() -> Crew:
    news_agent = Agent(
        role="News/Policy Analyst",
        goal=SYSTEM_NEWS,
        backstory=(
            "You specialize in tracking renewable policy and headlines. "
            "You write concise, evidence-backed briefs and tag items by topic."
        ),
        allow_delegation=False,
        verbose=False,
        tools=[SectorHeadlinesTool()],   # crewai_tools instances
    )

    earnings_agent = Agent(
        role="Earnings Analyst",
        goal=SYSTEM_EARN,
        backstory=(
            "You read filings, extract guidance changes, margins, capacity plans, and normalize KPIs."
        ),
        allow_delegation=False,
        verbose=False,
    )

    market_agent = Agent(
        role="Market/Technical Analyst",
        goal=SYSTEM_MKT,
        backstory=(
            "You compute simple technical indicators and turn them into a momentum assessment."
        ),
        allow_delegation=False,
        verbose=False,
        tools=[PricesHistoryTool()],
    )

    t_news = Task(
        description="Summarize the last {days} days of renewable-related news for {ticker}. Return 3-5 bullets.",
        agent=news_agent,
        expected_output="Bulleted summary with brief tags (policy/earnings/esg/tech) and 1-2 source URLs if available."
    )
    t_earn = Task(
        description="Outline recent earnings/fundamentals highlights for {ticker} (guidance deltas, margins, capacity).",
        agent=earnings_agent,
        expected_output="Bulleted KPIs and a one-paragraph interpretation."
    )
    t_mkt  = Task(
        description="Provide a short technical snapshot for {ticker} (trend, momentum, notable levels).",
        agent=market_agent,
        expected_output="3-5 bullets describing trend and momentum with a simple conclusion."
    )

    return Crew(agents=[news_agent, earnings_agent, market_agent], tasks=[t_news, t_earn, t_mkt])

def run_crew(ticker: str, days: int = 30) -> Dict[str, Any]:
    crew = build_crew()
    result = crew.kickoff(inputs={"ticker": ticker, "days": days})
    return {"ticker": ticker, "crew_output": str(result)}
