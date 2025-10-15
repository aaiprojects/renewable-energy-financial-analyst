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
        self.filings = FilingsTool()
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
            state["news_items"] = self.news.fetch_news(t, d)
            return state

        def route_items(state: State) -> State:
            state["routes"] = self.router.route(state.get("news_items", []))
            return state

        def specialists(state: State) -> State:
            analyses: List[Dict[str, Any]] = [run_crew(state["ticker"], state["days"])]
            state["analyses"] = analyses
            return state

        def synthesize(state: State) -> State:
            report = {
                "ticker": state["ticker"],
                "summary": "Synthesis placeholder via LangGraph orchestrator.",
                "scores": {"valuation": 0.0, "momentum": 0.0, "news": 0.0, "macro": 0.0},
                "recommendation": "WATCH",
                "confidence": 0.55,
                "citations": [],
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
        g.add_node("route", route_items)
        g.add_node("specialists", specialists)
        g.add_node("synthesize", synthesize)
        g.add_node("evaluate", evaluate)
        g.add_node("optimize", optimize)
        # Entry point
        g.add_edge(START, "fetch_prices")  # or: g.set_entry_point("fetch_prices")

        g.add_edge("fetch_prices", "fetch_news")
        g.add_edge("fetch_news", "route")
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
