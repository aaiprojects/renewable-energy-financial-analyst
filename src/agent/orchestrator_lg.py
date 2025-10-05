from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from .router import Router
from .evaluator import Evaluator
from .optimizer import Optimizer
from .memory import Memory
from ..tools.prices import PricesTool
from ..tools.news import NewsTool
from ..tools.macro import MacroTool
from ..tools.filings import FilingsTool
from ..tools.metadata import MetadataTool
from .crew_specialists import run_crew
from langgraph.graph import StateGraph, END
from langgraph.constants import START

class LGOrchestrator:
    def __init__(self, settings):
        self.settings = settings
        self.router = Router()
        self.evaluator = Evaluator()
        self.optimizer = Optimizer()
        self.memory = Memory()
        self.prices = PricesTool()
        self.news = NewsTool(api_key=settings.newsapi_key)
        self.macro = MacroTool(api_key=settings.fred_api_key)
        self.filings = FilingsTool(user_agent=settings.sec_user_agent)
        self.meta = MetadataTool()
        self._graph = self._build_graph()

    def _build_graph(self):
        State = dict
        g = StateGraph(State)

        def fetch_prices(state: State) -> State:
            t, d = state["ticker"], state["days"]
            state["prices"] = self.prices.fetch_history(t, d)
            return state

        def fetch_news(state: State) -> State:
            t, d = state["ticker"], state["days"]
            # Fetch both ticker-specific and sector news
            state["news_items"] = self.news.fetch_news(t, d)
            state["sector_news"] = self.news.fetch_sector_news(days=min(d, 7))  # Limit sector news to 7 days
            return state

        def fetch_filings(state: State) -> State:
            t = state["ticker"]
            # Fetch recent 10-K and 10-Q filings
            state["filings"] = self.filings.fetch_filings(t, ["10-K", "10-Q"], limit=3)
            return state

        def fetch_macro_data(state: State) -> State:
            # Fetch relevant macroeconomic indicators
            try:
                # Key indicators for renewable energy sector
                gdp_data = self.macro.fetch_series("GDP", end_date=None)
                interest_rates = self.macro.fetch_series("FEDFUNDS", end_date=None)
                oil_prices = self.macro.fetch_series("DCOILWTICO", end_date=None)
                
                state["macro_data"] = {
                    "gdp": gdp_data.tail(4).to_dict() if gdp_data is not None else {},
                    "interest_rates": interest_rates.tail(12).to_dict() if interest_rates is not None else {},
                    "oil_prices": oil_prices.tail(30).to_dict() if oil_prices is not None else {}
                }
            except Exception as e:
                state["macro_data"] = {"error": f"Failed to fetch macro data: {str(e)}"}
            return state

        def route_items(state: State) -> State:
            # Enhanced routing with multiple data sources
            all_items = state.get("news_items", []) + state.get("sector_news", [])
            state["routes"] = self.router.route(all_items)
            return state

        def specialists(state: State) -> State:
            # Pass enhanced data context to crew specialists
            context = {
                "ticker": state["ticker"],
                "days": state["days"],
                "prices": state.get("prices"),
                "news_items": state.get("news_items", []),
                "sector_news": state.get("sector_news", []),
                "filings": state.get("filings", []),
                "macro_data": state.get("macro_data", {}),
                "routes": state.get("routes", [])
            }
            analyses: List[Dict[str, Any]] = [run_crew(state["ticker"], state["days"], context)]
            state["analyses"] = analyses
            return state

        def synthesize(state: State) -> State:
            # Enhanced synthesis with real data
            ticker = state["ticker"]
            news_count = len(state.get("news_items", []))
            filings_count = len(state.get("filings", []))
            
            # Calculate basic scores based on available data
            news_score = min(0.8, news_count * 0.1) if news_count > 0 else 0.3
            macro_score = 0.6 if state.get("macro_data", {}) and "error" not in state.get("macro_data", {}) else 0.4
            filings_score = min(0.9, filings_count * 0.3) if filings_count > 0 else 0.5
            
            # Get price-based momentum score
            prices_df = state.get("prices")
            momentum_score = 0.5
            if prices_df is not None and not prices_df.empty and len(prices_df) > 1:
                start_price = float(prices_df['Close'].iloc[0])
                end_price = float(prices_df['Close'].iloc[-1])
                if start_price > 0:
                    return_pct = (end_price - start_price) / start_price
                    momentum_score = max(0.1, min(0.9, 0.5 + return_pct))
            
            # Collect citations
            citations = []
            for item in state.get("news_items", [])[:3]:
                if item.get("url"):
                    citations.append(item["url"])
            
            for filing in state.get("filings", [])[:2]:
                if filing.get("reportUrl"):
                    citations.append(filing["reportUrl"])
            
            # Generate recommendation based on scores
            avg_score = (news_score + macro_score + filings_score + momentum_score) / 4
            if avg_score >= 0.7:
                recommendation = "BUY"
            elif avg_score >= 0.5:
                recommendation = "WATCH"
            else:
                recommendation = "AVOID"
            
            report = {
                "ticker": ticker,
                "summary": f"Comprehensive analysis for {ticker} based on {news_count} news items, {filings_count} SEC filings, macroeconomic data, and price trends. Enhanced with real-time data sources.",
                "scores": {
                    "valuation": filings_score,
                    "momentum": momentum_score,
                    "news": news_score,
                    "macro": macro_score
                },
                "recommendation": recommendation,
                "confidence": avg_score,
                "citations": citations,
                "data_sources": {
                    "news_articles": news_count,
                    "sec_filings": filings_count,
                    "macro_indicators": len(state.get("macro_data", {})),
                    "price_history_days": len(prices_df) if prices_df is not None else 0
                }
            }
            state["report"] = report
            return state

        def evaluate(state: State) -> State:
            score, critique = self.evaluator.score(state["report"])
            state["score"], state["critique"] = score, critique
            return state

        def optimize(state: State) -> State:
            if state.get("score", 0) < 0.8:
                state["report"] = self.optimizer.refine(state["report"], state.get("critique", ""))
            state["iterations"] = state.get("iterations", 0) + 1
            return state

        g.add_node("fetch_prices", fetch_prices)
        g.add_node("fetch_news", fetch_news)
        g.add_node("fetch_filings", fetch_filings)
        g.add_node("fetch_macro_data", fetch_macro_data)
        g.add_node("route", route_items)
        g.add_node("specialists", specialists)
        g.add_node("synthesize", synthesize)
        g.add_node("evaluate", evaluate)
        g.add_node("optimize", optimize)
        
        # Entry point - start with prices
        g.add_edge(START, "fetch_prices")
        
        # Parallel data fetching
        g.add_edge("fetch_prices", "fetch_news")
        g.add_edge("fetch_news", "fetch_filings")
        g.add_edge("fetch_filings", "fetch_macro_data")
        
        # Continue with analysis
        g.add_edge("fetch_macro_data", "route")
        g.add_edge("route", "specialists")
        g.add_edge("specialists", "synthesize")
        g.add_edge("synthesize", "evaluate")
        g.add_conditional_edges(
            "evaluate",
            # Return a *label* that exists in the path_map below
            lambda s: "optimize" if (s.get("score", 0) < 0.8 and s.get("iterations", 0) < 2) else "__end__",
            {
                "optimize": "optimize",
                "__end__": END,   # <- map the stop label to END
            },
        )
        g.add_edge("optimize", "synthesize")

        return g.compile()

    def run(self, ticker: str, days: int = 30, refresh: bool = False) -> Dict[str, Any]:
        md = self.meta.get_metadata(ticker)
        state = {"ticker": ticker, "days": days, "metadata": {"sector": md.sector, "industry": md.industry, "name": md.long_name}}
        out = self._graph.invoke(state)
        self.memory.update_from_run({"ticker": ticker, "score": out.get("score"), "critique": out.get("critique")})
        return out.get("report", {})
