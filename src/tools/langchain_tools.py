from typing import Any, Dict, List, Union, Optional
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
def fetch_sector_headlines(subsector: str = "", region: Optional[str] = None, days: int = 7) -> List[Dict]:
    """Fetch sector-wide renewable headlines using NewsTool.fetch_sector_news."""
    return NewsTool().fetch_sector_news(subsector=subsector or None, region=region, days=days)

@tool
def fetch_filings_tool(
    ticker: str,
    filing_type: Union[str, List[str]] = "10-K",
    limit: int = 5
) -> Any:
    """Fetch company filings using FilingsTool."""
    return FilingsTool().fetch_filings(ticker, filing_type, limit)

@tool
def fetch_macro_tool(
    series_id: str = "CPI",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Any:
    """Fetch macro series from FRED using MacroTool."""
    return MacroTool().fetch_series(series_id, start_date, end_date)
