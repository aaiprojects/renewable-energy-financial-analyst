# src/tools/crewai_tools.py
from __future__ import annotations

from typing import List, Optional, Type, Union
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import pandas as pd

# ---- Sector headlines tool ----

class SectorHeadlinesArgs(BaseModel):
    subsector: Optional[str] = Field(
        default="",
        description="Subsector like 'Solar' or 'Wind' (optional).",
    )
    days: int = Field(
        default=7, ge=1, le=120,
        description="Lookback window in days.",
    )

class SectorHeadlinesTool(BaseTool):
    name: str = "sector_headlines"
    description: str = (
        "Fetch sector-wide renewable headlines. "
        "Note: NewsAPI free tier allows up to 100 requests/day, 1000/month, 1/sec."
        "Articles have a 24 hour delay."
    )  
    args_schema: Type[BaseModel] = SectorHeadlinesArgs

    def _run(self, subsector: str = "", days: int = 7) -> List[dict]:  # type: ignore[override]
        from .news import NewsTool
        return NewsTool().fetch_sector_news(subsector=subsector or None, days=days)

# ---- Ticker-Specific News tool ----

class TickerNewsArgs(BaseModel):
    ticker: str = Field(..., description="Ticker symbol or keyword, e.g., FSLR")
    days: int = Field(default=30, ge=1, le=90, description="Lookback window in days")

class TickerNewsTool(BaseTool):
    name: str = "ticker_news"
    description: str = (
        "Fetch recent news articles related to a specific ticker symbol. "
        "Note: NewsAPI free tier allows up to 100 requests/day, 1000/month, 1/sec."
        "Articles have a 24 hour delay."
    )    
    args_schema: Type[BaseModel] = TickerNewsArgs

    def _run(self, ticker: str, days: int = 30) -> List[dict]:  # type: ignore[override]
        from .news import NewsTool
        return NewsTool().fetch_news(ticker, days)
    
# ---- Prices history tool ----

class PricesHistoryArgs(BaseModel):
    ticker: str = Field(..., description="Ticker symbol, e.g., FSLR")
    days: int = Field(default=30, ge=1, le=365, description="Lookback window in days")

class PricesHistoryTool(BaseTool):
    name: str = "prices_history"
    description: str = "Fetch recent OHLCV history for a ticker (compact JSON output)."
    args_schema: Type[BaseModel] = PricesHistoryArgs

    def _run(self, ticker: str, days: int = 30) -> List[dict]:  # type: ignore[override]
        from .prices import PricesTool
        df = PricesTool().fetch_history(ticker, days)
        return [] if df is None else df.tail(5).to_dict(orient="records")

# ---- Filings tool ----

class FilingsArgs(BaseModel):
    ticker: str = Field(..., description="Ticker symbol, e.g., FSLR")
    filing_type: Union[str, List[str]] = Field(default="10-K", description="SEC filing type, e.g., '10-K', '10-Q', or a list like ['10-K', '10-Q']")
    limit: int = Field(default=5, ge=1, le=20, description="Number of filings to fetch (max 20)")

class FilingsTool(BaseTool):
    name: str = "filings"
    description: str = "Fetch recent SEC filings metadata for a given ticker and filing type."
    args_schema: Type[BaseModel] = FilingsArgs

    def _run(
        self,
        ticker: str,
        filing_type: Union[str, List[str]] = "10-K",
        limit: int = 5,
    ) -> List[dict]:  # type: ignore[override]
        from .filings import FilingsTool
        return FilingsTool().fetch_filings(ticker, filing_type, limit)

# ---- Macro data tool ----
class MacroSeriesArgs(BaseModel):
    series_id: str = Field(..., description="FRED series ID, e.g., 'GDP'")
    start_date: Optional[str] = Field(
        default=None,
        description="Start date in 'YYYY-MM-DD' format (optional).",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date in 'YYYY-MM-DD' format (optional).",
    )

class MacroSeriesTool(BaseTool):
    name: str = "macro_series"
    description: str = "Fetch macroeconomic time series from FRED (Federal Reserve Economic Data). Returns the last 5 records as a dictionary."
    args_schema: Type[BaseModel] = MacroSeriesArgs

    def _run(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:  # type: ignore[override]
        from .macro import MacroTool
        df = MacroTool().fetch_series(series_id, start_date, end_date)
        if df is None:
            return []
        if isinstance(df, pd.Series):
            df = df.to_frame(name=series_id)
        return df.tail(5).to_dict(orient="records")