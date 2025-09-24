from typing import Any, Dict, List
from langchain.tools import tool
from .prices import PricesTool
from .news import NewsTool
from .macro import MacroTool
from .filings import FilingsTool

@tool
def fetch_prices_tool(ticker: str, days: int = 30) -> Any:
    """Fetch OHLCV history for a ticker over N days."""
    return PricesTool().fetch_history(ticker, days)

@tool
def fetch_sector_headlines(subsector: str = "", days: int = 7) -> List[Dict]:
    """Fetch sector-wide renewable headlines (stub uses NewsTool.fetch_sector_news)."""
    return NewsTool().fetch_sector_news(subsector=subsector or None, days=days)

@tool
def fetch_filings_tool(ticker: str, form: str = "10-Q") -> Any:
    """Fetch company filings (stub)."""
    return FilingsTool().__class__.__name__

@tool
def fetch_macro_tool(series: str = "CPI") -> Any:
    """Fetch macro series from FRED (stub)."""
    return MacroTool().__class__.__name__
