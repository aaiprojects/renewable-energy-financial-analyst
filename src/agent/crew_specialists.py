import inspect, os, re, json, logging, time
import litellm
from time import sleep
from typing import Dict, Any
from crewai import Agent, Task, Crew
from ..tools.crewai_tools_imp import SectorHeadlinesTool, PricesHistoryTool
from .financial_agent import FinancialAgent
from .news_agent import NewsAgent
from datetime import datetime
import shutil

import os
print("Using API key:", os.getenv("OPENAI_API_KEY")[:15], "...")
print("Org:", os.getenv("OPENAI_ORG"))
print("Project:", os.getenv("OPENAI_PROJECT"))


print("🧩 running latest crew_specialists version")
print("🚀 executing:", os.path.abspath(__file__))

# ---------------------------------------------------------------------
# 🧠 Logging Setup
# ---------------------------------------------------------------------
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------------------------------------------------------------
# ⚙️ Terminal Colors
# ---------------------------------------------------------------------
class Color:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

# ---------------------------------------------------------------------
# 🧩 System Prompts
# ---------------------------------------------------------------------
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

# ---------------------------------------------------------------------
# ⚙️ Aggregator Logic
# ---------------------------------------------------------------------
def aggregate_agent_outputs(agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Combine all agent outputs into a unified Executive Summary with weighted confidence and Market Outlook."""
    executive_summary = {
        "agents": {},
        "overall_summary": "",
        "confidence": {},
        "market_outlook": ""
    }

    total_weighted_conf = 0
    total_weights = 0

    for agent, output in agent_outputs.items():
        text = output.get("summary", "")
        confidence = 0

        # --- heuristic scoring ---
        if re.search(r"\d{2,}", text):  # numeric metrics present
            confidence += 0.3
        if any(word in text.lower() for word in ["growth", "decline", "forecast", "sentiment", "estimate", "trend"]):
            confidence += 0.3
        if len(text.split()) > 40:
            confidence += 0.4

        confidence = round(min(confidence, 1.0), 2)

        # --- weighting logic ---
        weight = 1.0
        if "momentum" in agent.lower():
            weight = 1.3
        elif "valuation" in agent.lower():
            weight = 1.2

        weighted_conf = confidence * weight
        total_weighted_conf += weighted_conf
        total_weights += weight

        executive_summary["agents"][agent] = {
            "summary": text,
            "confidence": confidence,
            "weight": weight
        }

    # --- weighted average confidence ---
    avg_conf = round(total_weighted_conf / total_weights, 2) if total_weights else 0
    executive_summary["confidence"]["overall"] = avg_conf

    # --- market outlook classification ---
    if avg_conf >= 0.8:
        outlook = "🟢 Bullish"
        color = Color.GREEN
    elif avg_conf >= 0.6:
        outlook = "🟡 Neutral / Watchlist"
        color = Color.YELLOW
    else:
        outlook = "🔴 Bearish / Caution"
        color = Color.RED

    executive_summary["market_outlook"] = outlook

    # --- formatted summary ---
    combined_text = "\n\n".join(
        [f"**{agent}** (conf: {data['confidence']}, w={data['weight']}): {data['summary']}"
         for agent, data in executive_summary["agents"].items()]
    )

    executive_summary["overall_summary"] = (
        combined_text + f"\n\n**Overall Confidence:** {avg_conf}  \n**Market Outlook:** {outlook}"
    )

    # --- CLI printout with color ---
    print("\n🧠 EXECUTIVE SUMMARY\n")
    print(combined_text)
    print(f"\n**Overall Confidence:** {avg_conf}")
    print(f"{color}**Market Outlook:** {outlook}{Color.RESET}\n")

    return executive_summary

# ---------------------------------------------------------------------
# ⚙️ Crew Builder
# ---------------------------------------------------------------------
def build_crew() -> Crew:
    earnings_agent = Agent(
        role="Earnings Analyst",
        goal=SYSTEM_EARN,
        backstory="You read filings, extract guidance changes, margins, capacity plans, and normalize KPIs.",
        allow_delegation=False,
        verbose=False,
    )

    news_agent = Agent(
        role="News & Sentiment Analyst",
        goal=SYSTEM_NEWS,
        backstory="You summarize renewable energy headlines and policy updates, tagging by topic.",
        allow_delegation=False,
        verbose=False,
        tools=[SectorHeadlinesTool()],
    )

    market_agent = Agent(
        role="Market/Technical Analyst",
        goal=SYSTEM_MKT,
        backstory="You compute simple technical indicators and assess momentum.",
        allow_delegation=False,
        verbose=False,
        tools=[PricesHistoryTool()],
    )

    financial_agent = Agent(
        role="Financial Analyst",
        goal="You assess company financial performance—revenues, margins, and capital efficiency.",
        backstory="You provide concise, data-driven financial summaries for renewable energy companies.",
        allow_delegation=False,
        verbose=False,
        tools=[PricesHistoryTool()],
    )

    momentum_agent = Agent(
        role="Momentum Analyst",
        goal="You analyze RSI, MACD, and moving averages to gauge short-term strength or weakness.",
        backstory="You interpret momentum signals to validate trading timing and trend strength.",
        allow_delegation=False,
        verbose=False,
        tools=[PricesHistoryTool()],
    )

    valuation_agent = Agent(
        role="Valuation Analyst",
        goal="You estimate fair value based on valuation ratios (P/E, P/B, growth).",
        backstory="You assess over/undervaluation based on company fundamentals and market context.",
        allow_delegation=False,
        verbose=False,
        tools=[PricesHistoryTool()],
    )

    t_news = Task(
        description="Summarize the last {days} days of renewable-related news for {ticker}. Return 3–5 bullets.",
        agent=news_agent,
        expected_output="Bulleted summary with brief tags and 1–2 source URLs."
    )
    t_earn = Task(
        description="Outline recent earnings/fundamentals highlights for {ticker} (guidance deltas, margins, capacity).",
        agent=earnings_agent,
        expected_output="Bulleted KPIs and a short interpretation."
    )
    t_mkt = Task(
        description="Provide a short technical snapshot for {ticker} (trend, momentum, notable levels).",
        agent=market_agent,
        expected_output="3–5 bullets describing trend and momentum with a simple conclusion."
    )
    t_fin = Task(
        description="Summarize key financial indicators for {ticker} — focus on revenue, profit, margins, and capital efficiency.",
        agent=financial_agent,
        expected_output="3–5 concise bullets and a one-line interpretation."
    )
    t_momentum = Task(
        description="Analyze short-term momentum for {ticker} using RSI, MACD, and moving averages.",
        agent=momentum_agent,
        expected_output="3–5 bullets explaining momentum, strength/weakness, and a one-line conclusion."
    )
    t_valuation = Task(
        description="Provide a valuation snapshot for {ticker} based on key ratios (P/E, P/B, growth).",
        agent=valuation_agent,
        expected_output="3–5 concise bullets and an over/under-valued call."
    )

    return Crew(
        agents=[earnings_agent, market_agent, news_agent, financial_agent, momentum_agent, valuation_agent],
        tasks=[t_news, t_earn, t_mkt, t_fin, t_momentum, t_valuation],
    )
# ---------------------------------------------------------------------
# 🚀 Crew Runner — reusable + executable
# ---------------------------------------------------------------------
def run_crew(
    tickers=None,
    days: int = 30,
    archive_old: bool = True,
    clean_start: bool = True,
    max_tickers_per_run: int = 2,
    max_agent_retries: int = 2,
    skip_if_json_exists: bool = True,
    stop_on_rate_limit: bool = True,
):
    """
    Runs the full Executive Summary generation crew workflow.
    Safe to import and call from orchestrator_lg or Streamlit.
    """
    print("⚙️ Running crew execution from run_crew()...")
    from datetime import datetime
    import glob, os, shutil, time, json, logging
    from src.agent.crew_specialists import build_crew, aggregate_agent_outputs
    from crewai import Crew

    if tickers is None:
        tickers = ["FSLR", "ENPH", "SEDG", "RUN", "SPWR"]

    crew = build_crew()
    processed_count = 0

    # --- ARCHIVE OLD SUMMARIES ---
    if archive_old:
        old_files = glob.glob("executive_summary_*.json") + glob.glob("executive_summary_*.md")
        if old_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            archive_dir = os.path.join("archive", timestamp)
            os.makedirs(archive_dir, exist_ok=True)
            print(f"📦 Archiving {len(old_files)} old summaries to {archive_dir}/")
            for f in old_files:
                shutil.move(f, os.path.join(archive_dir, os.path.basename(f)))
            print("✅ Archive complete.\n")

    # --- CLEAN START OPTION ---
    if clean_start:
        old_files = glob.glob("executive_summary_*.json") + glob.glob("executive_summary_*.md")
        if old_files:
            print(f"🧹 Cleaning up {len(old_files)} old summary files...")
            for f in old_files:
                os.remove(f)
            print("✅ Old summaries cleared.\n")

    for ticker in tickers:
        if processed_count >= max_tickers_per_run:
            print(f"✅ Reached limit of {max_tickers_per_run} tickers. Exiting cleanly.")
            break

        json_path = f"executive_summary_{ticker}.json"
        if skip_if_json_exists and os.path.exists(json_path):
            print(f"⚠️ Skipping {ticker} — summary file already exists.")
            continue

        print(f"\n🔄 Running Executive Summary for {ticker}")
        all_outputs = {}
        rate_limit_hit = False

        for task in crew.tasks:
            print(f"▶️ Running task for: {task.agent.role}")
            success = False

            for attempt in range(max_tickers_per_run):
                try:
                    single_crew = Crew(agents=[task.agent], tasks=[task])
                    result = single_crew.kickoff(inputs={"ticker": ticker, "days": days})
                    summary = result.get("summary", "") if isinstance(result, dict) else str(result)
                    logging.info(f"[{task.agent.role}] Summary for {ticker}: {summary[:200]}...")
                    all_outputs[task.agent.role] = {"summary": summary}
                    success = True
                    break
                except Exception as e:
                    error_msg = str(e)
                    print(f"⚠️ Error running {task.agent.role} (Attempt {attempt+1}/{max_tickers_per_run}): {error_msg}")
                    if "RateLimitError" in error_msg:
                        rate_limit_hit = True
                        if stop_on_rate_limit:
                            print("🚫 Rate limit hit — stopping early.")
                            break
                    wait_time = 15 * (attempt + 1)
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

            if rate_limit_hit or not success:
                all_outputs[task.agent.role] = {"summary": f"Error: {error_msg if not success else 'RateLimit'}"}

            if rate_limit_hit and stop_on_rate_limit:
                break

            print("⏳ Waiting 8s before next agent...")
            time.sleep(8)

        # save JSON only if some outputs exist
        if all_outputs:
            exec_summary = aggregate_agent_outputs(all_outputs)
            with open(json_path, "w") as f:
                json.dump(exec_summary, f, indent=2)
            print(f"📁 Saved summary to {json_path}")
            processed_count += 1
        else:
            print(f"⚠️ No outputs for {ticker}")

        if rate_limit_hit and stop_on_rate_limit:
            print("🛑 Stopping due to persistent rate limits.")
            break


# ---------------------------------------------------------------------
# 🚀 Main Execution (only if run directly)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    run_crew()
