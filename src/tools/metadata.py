from dataclasses import dataclass
from typing import Optional, Dict
try:
    import yfinance as yf
except Exception:
    yf = None

RENEWABLE_KEYWORDS = ["solar","wind","renewable","clean energy","alternative energy","hydrogen","fuel cell","energy storage","battery","green utility","clean power"]

@dataclass
class TickerMetadata:
    ticker: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    long_name: Optional[str] = None

class MetadataTool:
    def __init__(self):
        self._cache: Dict[str, TickerMetadata] = {}

    def get_metadata(self, ticker: str) -> TickerMetadata:
        if ticker in self._cache:
            return self._cache[ticker]
        if yf is None:
            md = TickerMetadata(ticker=ticker)
            self._cache[ticker] = md
            return md   
        t = yf.Ticker(ticker)
        sector = industry = long_name = None
        try:
            fi = getattr(t, "fast_info", None)
            _ = fi.get("last_price") if isinstance(fi, dict) else None
        except Exception:
            pass
        try:
            info: Dict = getattr(t, "info", {}) or {}
            sector = info.get("sector")
            industry = info.get("industry")
            long_name = info.get("longName") or info.get("shortName")
        except Exception:
            pass
        md = TickerMetadata(ticker=ticker, sector=sector, industry=industry, long_name=long_name)
        self._cache[ticker] = md
        return md

    def is_renewables(self, md: TickerMetadata) -> bool:
        text = " ".join([(md.sector or ""), (md.industry or ""), (md.long_name or "")]).lower()
        return any(k in text for k in RENEWABLE_KEYWORDS) or (md.sector or "").lower() in ("utilities",)
