# src/tools/crewai_tools.py
from __future__ import annotations

from typing import List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool  # ✅ correct import for CrewAI >= 0.28

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
    description: str = "Fetch sector-wide renewable headlines (stub; replace with NewsAPI)."
    args_schema: Type[BaseModel] = SectorHeadlinesArgs

    def _run(self, subsector: str = "", days: int = 7) -> List[dict]:  # type: ignore[override]
        from .news import NewsTool
        return NewsTool().fetch_sector_news(subsector=subsector or None, days=days)

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
