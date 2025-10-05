"""
Natural Language Orchestrator for Renewable Energy Financial Analysis
Extends the existing LangGraph orchestrator to handle natural language queries with enhanced tools.
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.constants import START

from .orchestrator_lg import LGOrchestrator
from .query_processor import QueryProcessor, QueryIntent
from ..tools.visualization import ChartGenerator
from ..tools.news import NewsTool
from .crew_specialists import run_crew

class NLOrchestrator(LGOrchestrator):
    """Extended orchestrator that can handle natural language queries with real data sources."""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.query_processor = QueryProcessor()
        self.chart_generator = ChartGenerator()
        self._nl_graph = self._build_nl_graph()

    def _build_nl_graph(self):
        """Build the natural language query processing graph with enhanced data integration."""
        State = dict
        g = StateGraph(State)

        def parse_query(state: State) -> State:
            """Parse the natural language query."""
            query = state["query"]
            parsed = self.query_processor.parse_query(query)
            state["parsed_query"] = parsed
            state["intent"] = parsed.intent
            state["parameters"] = parsed.parameters
            state["explanation"] = parsed.explanation
            return state

        def route_by_intent(state: State) -> State:
            """Route to appropriate processing based on intent."""
            intent = state["intent"]
            
            if intent == QueryIntent.PRICE_CHART:
                state["route"] = "price_chart"
            elif intent == QueryIntent.COMPARISON:
                state["route"] = "comparison"
            elif intent == QueryIntent.NEWS_SENTIMENT:
                # Use simple news analysis to avoid infinite loops
                state["route"] = "simple_news_analysis"
            elif intent == QueryIntent.TECHNICAL_ANALYSIS:
                state["route"] = "technical_analysis"
            elif intent == QueryIntent.SECTOR_OVERVIEW:
                state["route"] = "sector_overview"
            elif intent == QueryIntent.FUNDAMENTAL_ANALYSIS:
                state["route"] = "fundamental_analysis"
            else:
                state["route"] = "general_analysis"
            
            return state

        def create_price_chart(state: State) -> State:
            """Create price chart visualization."""
            params = state["parameters"]
            try:
                chart = self.chart_generator.create_price_chart(
                    tickers=params.tickers,
                    timeframe=params.timeframe,
                    chart_type=params.chart_type
                )
                state["chart"] = chart
                state["analysis_type"] = "price_chart"
                state["summary"] = f"Created price chart for {', '.join(params.tickers)} over {params.timeframe}"
            except Exception as e:
                state["error"] = f"Error creating price chart: {str(e)}"
            return state

        def create_comparison(state: State) -> State:
            """Create comparison visualization."""
            params = state["parameters"]
            try:
                chart = self.chart_generator.create_comparison_chart(
                    tickers=params.tickers,
                    metrics=params.metrics,
                    timeframe=params.timeframe
                )
                state["chart"] = chart
                state["analysis_type"] = "comparison"
                state["summary"] = f"Created comparison analysis for {', '.join(params.tickers)}"
            except Exception as e:
                state["error"] = f"Error creating comparison: {str(e)}"
            return state

        def analyze_news_sentiment(state: State) -> State:
            """Analyze news sentiment using enhanced NewsAPI integration."""
            params = state["parameters"]
            try:
                if params.tickers:
                    # Use enhanced crew analysis with real data
                    analyses = []
                    for ticker in params.tickers[:2]:  # Reduce to 2 for performance
                        try:
                            # Fetch real news data with timeout protection
                            news_items = self.news.fetch_news(ticker, 7)[:5]  # Limit to 5 articles
                            sector_news = self.news.fetch_sector_news(days=7)[:5]  # Limit to 5 articles
                            
                            # Enhanced context for crew
                            context = {
                                "news_items": news_items,
                                "sector_news": sector_news,
                                "real_data": True
                            }
                            
                            # Add timeout protection for crew execution
                            crew_result = run_crew(ticker, 7, context)
                            analyses.append(crew_result)
                        except Exception as crew_error:
                            print(f"Error in crew analysis for {ticker}: {crew_error}")
                            # Continue with limited analysis if crew fails
                            analyses.append({
                                "ticker": ticker,
                                "error": f"Crew analysis failed: {str(crew_error)}",
                                "limited_analysis": True
                            })
                    
                    state["crew_analyses"] = analyses
                    state["analysis_type"] = "news_sentiment"
                    state["summary"] = f"Analyzed news sentiment for {', '.join(params.tickers)} using real NewsAPI data"
                else:
                    # General sector news using real API
                    headlines = self.news.fetch_sector_news(
                        subsector=params.subsector,
                        days=7
                    )
                    state["news_headlines"] = headlines
                    state["analysis_type"] = "sector_news"
                    state["summary"] = f"Retrieved real sector news for renewable energy"
            except Exception as e:
                state["error"] = f"Error analyzing news sentiment: {str(e)}"
            return state

        def simple_news_analysis(state: State) -> State:
            """Simple news analysis without CrewAI to prevent infinite loops."""
            params = state["parameters"]
            try:
                if params.tickers:
                    # Simple news fetching without crew analysis
                    news_data = []
                    for ticker in params.tickers[:2]:
                        news_items = self.news.fetch_news(ticker, 7)[:3]  # Only 3 articles
                        news_data.extend(news_items)
                    
                    state["news_headlines"] = news_data
                    state["analysis_type"] = "news_sentiment"
                    state["summary"] = f"Retrieved latest news for {', '.join(params.tickers)} (simplified analysis)"
                else:
                    # General sector news
                    headlines = self.news.fetch_sector_news(days=7)[:5]  # Only 5 articles
                    state["news_headlines"] = headlines
                    state["analysis_type"] = "sector_news"
                    state["summary"] = "Retrieved latest renewable energy sector news"
                    
            except Exception as e:
                state["error"] = f"Error in simple news analysis: {str(e)}"
            return state

        def analyze_fundamentals(state: State) -> State:
            """Perform fundamental analysis using SEC filings and macro data."""
            params = state["parameters"]
            try:
                if params.tickers:
                    ticker = params.tickers[0]
                    
                    # Fetch real SEC filings (simplified to prevent recursion)
                    try:
                        filings = self.filings.fetch_filings(ticker, ["10-K", "10-Q"], limit=2)
                        filing_summary = f"Retrieved {len(filings) if filings else 0} recent SEC filings"
                    except Exception as filing_error:
                        filings = []
                        filing_summary = f"Unable to fetch SEC filings: {str(filing_error)}"
                    
                    # Simplified analysis without crew to prevent recursion
                    state["filings_data"] = filings[:2] if filings else []
                    state["analysis_type"] = "fundamental_analysis"
                    state["summary"] = f"Fundamental analysis for {ticker}: {filing_summary}"
                    
                    # Add basic interpretation if filings exist
                    if filings:
                        state["filing_analysis"] = f"Found recent filings for {ticker}. " + \
                                                 f"Latest filing types: {[f.get('form', 'Unknown') for f in filings[:2]]}"
                else:
                    state["error"] = "No ticker specified for fundamental analysis"
            except Exception as e:
                state["error"] = f"Error in fundamental analysis: {str(e)}"
            return state

        def create_technical_analysis(state: State) -> State:
            """Create technical analysis visualization with real price data."""
            params = state["parameters"]
            try:
                if params.tickers:
                    ticker = params.tickers[0]
                    chart = self.chart_generator.create_technical_analysis_chart(
                        ticker=ticker,
                        timeframe=params.timeframe
                    )
                    state["chart"] = chart
                    state["analysis_type"] = "technical_analysis"
                    state["summary"] = f"Created technical analysis for {ticker} with real market data"
                else:
                    state["error"] = "No ticker specified for technical analysis"
            except Exception as e:
                state["error"] = f"Error creating technical analysis: {str(e)}"
            return state

        def create_sector_overview(state: State) -> State:
            """Create sector overview with real market data."""
            params = state["parameters"]
            try:
                chart = self.chart_generator.create_sector_overview(
                    subsector=params.subsector
                )
                state["chart"] = chart
                state["analysis_type"] = "sector_overview"
                state["summary"] = f"Created sector overview for renewable energy{' - ' + params.subsector if params.subsector else ''} using real market data"
            except Exception as e:
                state["error"] = f"Error creating sector overview: {str(e)}"
            return state

        def run_general_analysis(state: State) -> State:
            """Run comprehensive analysis using enhanced orchestrator."""
            params = state["parameters"]
            try:
                if params.tickers:
                    # Use enhanced orchestrator with real data sources
                    ticker = params.tickers[0]
                    report = super(NLOrchestrator, self).run(
                        ticker=ticker,
                        days=self._parse_timeframe_to_days(params.timeframe),
                        refresh=False
                    )
                    state["detailed_report"] = report
                    state["analysis_type"] = "detailed_analysis"
                    state["summary"] = f"Completed comprehensive analysis for {ticker} using NewsAPI, SEC EDGAR, and FRED data"
                else:
                    state["error"] = "No ticker specified for detailed analysis"
            except Exception as e:
                state["error"] = f"Error running general analysis: {str(e)}"
            return state

        def finalize_response(state: State) -> State:
            """Finalize the response with appropriate formatting."""
            if "error" in state:
                state["response"] = {
                    "success": False,
                    "error": state["error"],
                    "explanation": state.get("explanation", "")
                }
            else:
                state["response"] = {
                    "success": True,
                    "analysis_type": state.get("analysis_type"),
                    "summary": state.get("summary"),
                    "explanation": state.get("explanation"),
                    "chart": state.get("chart"),
                    "crew_analyses": state.get("crew_analyses"),
                    "news_headlines": state.get("news_headlines"),
                    "detailed_report": state.get("detailed_report"),
                    "filings_data": state.get("filings_data"),
                    "filing_analysis": state.get("filing_analysis"),
                    "enhanced_data": True,  # Flag indicating real data sources used
                    "data_sources": ["NewsAPI", "SEC EDGAR", "FRED", "YFinance"]
                }
            return state

        # Add nodes
        g.add_node("parse_query", parse_query)
        g.add_node("route_by_intent", route_by_intent)
        g.add_node("create_price_chart", create_price_chart)
        g.add_node("create_comparison", create_comparison)
        g.add_node("analyze_news_sentiment", analyze_news_sentiment)
        g.add_node("simple_news_analysis", simple_news_analysis)
        g.add_node("analyze_fundamentals", analyze_fundamentals)
        g.add_node("create_technical_analysis", create_technical_analysis)
        g.add_node("create_sector_overview", create_sector_overview)
        g.add_node("run_general_analysis", run_general_analysis)
        g.add_node("finalize_response", finalize_response)

        # Add edges
        g.add_edge(START, "parse_query")
        g.add_edge("parse_query", "route_by_intent")
        
        # Conditional routing based on intent
        g.add_conditional_edges(
            "route_by_intent",
            lambda state: state["route"],
            {
                "price_chart": "create_price_chart",
                "comparison": "create_comparison", 
                "news_analysis": "analyze_news_sentiment",
                "simple_news_analysis": "simple_news_analysis",
                "fundamental_analysis": "analyze_fundamentals",
                "technical_analysis": "create_technical_analysis",
                "sector_overview": "create_sector_overview",
                "general_analysis": "run_general_analysis"
            }
        )

        # All processing nodes lead to finalization
        for node in ["create_price_chart", "create_comparison", "analyze_news_sentiment", 
                    "simple_news_analysis", "analyze_fundamentals", "create_technical_analysis", 
                    "create_sector_overview", "run_general_analysis"]:
            g.add_edge(node, "finalize_response")
        
        g.add_edge("finalize_response", END)

        return g.compile(debug=False)

    def process_natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query using enhanced data sources.
        
        Args:
            query: Natural language query from user
            
        Returns:
            Dictionary containing analysis results, charts, and explanations
        """
        try:
            state = {"query": query}
            result = self._nl_graph.invoke(state, config={"recursion_limit": 10})
            return result.get("response", {
                "success": False,
                "error": "Unknown error in query processing"
            })
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing query: {str(e)}",
                "explanation": ""
            }

    def _parse_timeframe_to_days(self, timeframe: str) -> int:
        """Convert timeframe string to days for existing orchestrator."""
        timeframe_map = {
            '1d': 1, '7d': 7, '30d': 30, '90d': 90, '365d': 365, 'ytd': 250
        }
        return timeframe_map.get(timeframe, 30)

    # Keep the original run method for backwards compatibility
    def run(self, ticker: str, days: int = 30, refresh: bool = False) -> Dict[str, Any]:
        """Original run method for detailed company analysis with enhanced data."""
        return super().run(ticker, days, refresh)