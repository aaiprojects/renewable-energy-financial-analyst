"""
Natural Language Query Processor for Renewable Energy Financial Analysis
Parses user queries and extracts intent, parameters, and routing information.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class QueryIntent(Enum):
    PRICE_CHART = "price_chart"
    COMPARISON = "comparison" 
    NEWS_SENTIMENT = "news_sentiment"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    SECTOR_OVERVIEW = "sector_overview"
    COMPANY_RESEARCH = "company_research"
    UNKNOWN = "unknown"

@dataclass
class QueryParameters:
    tickers: List[str]
    timeframe: Optional[str] = "30d"
    chart_type: Optional[str] = "line"
    metrics: List[str] = None
    subsector: Optional[str] = None
    comparison_type: Optional[str] = None

@dataclass
class ParsedQuery:
    intent: QueryIntent
    parameters: QueryParameters
    confidence: float
    raw_query: str
    explanation: str

class QueryProcessor:
    def __init__(self):
        # Known renewable energy tickers from watchlist
        self.renewable_tickers = [
            'FSLR', 'ENPH', 'RUN', 'NEE', 'BEPC', 'VWDRY', 'DNNGY',
            'TSLA', 'SPWR', 'SEDG', 'JKS', 'MAXN', 'NOVA', 'CSIQ'
        ]
        
        # Intent patterns
        self.intent_patterns = {
            QueryIntent.PRICE_CHART: [
                r'show.*price.*chart|chart.*price|plot.*price|price.*performance|stock.*chart',
                r'price.*over.*time|historical.*price|price.*trend'
            ],
            QueryIntent.COMPARISON: [
                r'compare.*vs|compare.*with|comparison.*between|vs\.|versus',
                r'which.*better|best.*performing|top.*stock|rank.*companies'
            ],
            QueryIntent.NEWS_SENTIMENT: [
                r'news.*sentiment|sentiment.*analysis|recent.*news|latest.*news',
                r'media.*coverage|press.*release|announcement|headline'
            ],
            QueryIntent.TECHNICAL_ANALYSIS: [
                r'technical.*analysis|indicators|moving.*average|rsi|macd',
                r'support.*resistance|trend.*analysis|momentum|volatility'
            ],
            QueryIntent.FUNDAMENTAL_ANALYSIS: [
                r'fundamental|earnings|revenue|profit|margin|valuation',
                r'p/e.*ratio|financial.*health|balance.*sheet|cash.*flow',
                r'sec.*filing|10-k|10-q|annual.*report|quarterly.*report|filings'
            ],
            QueryIntent.SECTOR_OVERVIEW: [
                r'sector.*overview|industry.*analysis|renewable.*energy.*sector',
                r'solar.*industry|wind.*industry|clean.*energy.*market'
            ]
        }
        
        # Timeframe patterns
        self.timeframe_patterns = {
            r'today|1\s*day?': '1d',
            r'week|7\s*days?': '7d', 
            r'month|30\s*days?': '30d',
            r'quarter|3\s*months?': '90d',
            r'year|12\s*months?': '365d',
            r'ytd|year.*to.*date': 'ytd'
        }
        
        # Chart type patterns
        self.chart_patterns = {
            r'candlestick|ohlc': 'candlestick',
            r'bar.*chart': 'bar',
            r'line.*chart|line': 'line',
            r'area.*chart': 'area'
        }

    def parse_query(self, query: str) -> ParsedQuery:
        """Main parsing function that processes a natural language query."""
        query_lower = query.lower()
        
        # Extract intent
        intent = self._extract_intent(query_lower)
        
        # Extract parameters
        tickers = self._extract_tickers(query_lower)
        timeframe = self._extract_timeframe(query_lower)
        chart_type = self._extract_chart_type(query_lower)
        metrics = self._extract_metrics(query_lower)
        subsector = self._extract_subsector(query_lower)
        comparison_type = self._extract_comparison_type(query_lower)
        
        parameters = QueryParameters(
            tickers=tickers,
            timeframe=timeframe,
            chart_type=chart_type,
            metrics=metrics or [],
            subsector=subsector,
            comparison_type=comparison_type
        )
        
        # Calculate confidence and generate explanation
        confidence = self._calculate_confidence(intent, parameters, query_lower)
        explanation = self._generate_explanation(intent, parameters)
        
        return ParsedQuery(
            intent=intent,
            parameters=parameters,
            confidence=confidence,
            raw_query=query,
            explanation=explanation
        )

    def _extract_intent(self, query: str) -> QueryIntent:
        """Extract the primary intent from the query."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        return QueryIntent.UNKNOWN

    def _extract_tickers(self, query: str) -> List[str]:
        """Extract ticker symbols from the query."""
        tickers = []
        
        # Look for explicit ticker mentions
        for ticker in self.renewable_tickers:
            if re.search(rf'\b{ticker}\b', query, re.IGNORECASE):
                tickers.append(ticker)
        
        # Look for company name mentions
        company_mappings = {
            'first solar': 'FSLR',
            'enphase': 'ENPH', 
            'sunrun': 'RUN',
            'nextera': 'NEE',
            'brookfield': 'BEPC',
            'vestas': 'VWDRY',
            'orsted': 'DNNGY',
            'tesla': 'TSLA'
        }
        
        for company, ticker in company_mappings.items():
            if company in query and ticker not in tickers:
                tickers.append(ticker)
        
        # If no specific tickers found but query mentions sector terms
        if not tickers:
            if any(term in query for term in ['solar', 'wind', 'renewable', 'clean energy']):
                # Return default watchlist tickers
                return self.renewable_tickers[:5]  # Top 5 for performance
        
        return tickers

    def _extract_timeframe(self, query: str) -> str:
        """Extract timeframe from the query."""
        for pattern, timeframe in self.timeframe_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return timeframe
        return "30d"  # Default

    def _extract_chart_type(self, query: str) -> str:
        """Extract chart type preference from the query."""
        for pattern, chart_type in self.chart_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return chart_type
        return "line"  # Default

    def _extract_metrics(self, query: str) -> List[str]:
        """Extract specific metrics requested in the query."""
        metrics = []
        metric_patterns = {
            'price': r'price|stock.*price',
            'volume': r'volume|trading.*volume',
            'returns': r'returns?|performance|gain|loss',
            'volatility': r'volatility|risk',
            'correlation': r'correlation|correlated',
            'moving_average': r'moving.*average|ma\b|sma|ema'
        }
        
        for metric, pattern in metric_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                metrics.append(metric)
        
        return metrics

    def _extract_subsector(self, query: str) -> Optional[str]:
        """Extract renewable energy subsector from query."""
        subsectors = {
            'solar': r'solar|photovoltaic|pv',
            'wind': r'wind|turbine',
            'utility': r'utility|utilities',
            'storage': r'battery|storage|energy.*storage'
        }
        
        for subsector, pattern in subsectors.items():
            if re.search(pattern, query, re.IGNORECASE):
                return subsector
        return None

    def _extract_comparison_type(self, query: str) -> Optional[str]:
        """Extract type of comparison requested."""
        if re.search(r'performance|returns|gains', query, re.IGNORECASE):
            return 'performance'
        elif re.search(r'valuation|p/e|price.*ratio', query, re.IGNORECASE):
            return 'valuation'
        elif re.search(r'volatility|risk', query, re.IGNORECASE):
            return 'risk'
        return None

    def _calculate_confidence(self, intent: QueryIntent, parameters: QueryParameters, query: str) -> float:
        """Calculate confidence score for the parsed query."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence if intent is clearly identified
        if intent != QueryIntent.UNKNOWN:
            confidence += 0.3
        
        # Boost confidence if specific tickers are found
        if parameters.tickers:
            confidence += 0.2
        
        # Boost confidence if timeframe is specified
        if any(pattern in query for pattern in ['day', 'week', 'month', 'year']):
            confidence += 0.1
        
        return min(1.0, confidence)

    def _generate_explanation(self, intent: QueryIntent, parameters: QueryParameters) -> str:
        """Generate human-readable explanation of what will be analyzed."""
        explanations = {
            QueryIntent.PRICE_CHART: f"I'll create a price chart for {', '.join(parameters.tickers or ['renewable energy stocks'])} over the {parameters.timeframe}",
            QueryIntent.COMPARISON: f"I'll compare {', '.join(parameters.tickers or ['renewable energy companies'])} across key metrics",
            QueryIntent.NEWS_SENTIMENT: f"I'll analyze recent news sentiment for {', '.join(parameters.tickers or ['the renewable energy sector'])}",
            QueryIntent.TECHNICAL_ANALYSIS: f"I'll perform technical analysis on {', '.join(parameters.tickers or ['renewable energy stocks'])}",
            QueryIntent.FUNDAMENTAL_ANALYSIS: f"I'll analyze fundamentals for {', '.join(parameters.tickers or ['renewable energy companies'])}",
            QueryIntent.SECTOR_OVERVIEW: "I'll provide an overview of the renewable energy sector",
            QueryIntent.UNKNOWN: "I'll try to provide relevant renewable energy market analysis"
        }
        
        return explanations.get(intent, "I'll analyze the renewable energy market data")